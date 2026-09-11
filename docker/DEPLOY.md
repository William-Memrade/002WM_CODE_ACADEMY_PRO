# Despliegue — CodeAcademy Pro

Runbook de contenedores y despliegue. Todo se ejecuta con el Docker que está
**dentro de WSL Ubuntu** (en Windows no hay CLI de docker: `C:\Program Files\Docker`
está vacío y `C:\ProgramData\DockerDesktop\install-cli-log-admin.txt` muestra que la
instalación del CLI quedó incompleta).

Atajo: `wsl -e bash -lc "cd /mnt/c/Users/guill/Documents/Personal_Projects/Programacion/Academia/002WM_CODE_ACADEMY_PRO/docker && ..."`

## Archivos

| Archivo | Para qué |
|---|---|
| `docker-compose.yml` | **El único compose.** Stack completo con imágenes de producción + servicio `migrate`. Nombres genéricos (`academy-backend`, `academy-postgres`, …), sin sufijos de ambiente. |
| `Dockerfile.backend` | Imagen del backend y del worker. **Contexto = raíz del repo** (necesita `database/migrations`). |
| `Dockerfile.frontend` | Imagen del frontend Next.js multi-stage (`next build` + `next start`). **Contexto = `frontend/`**. |
| `render.yaml` | Blueprint de Render: 2 web services + Key Value (worker comentado). |
| `../.dockerignore`, `../frontend/.dockerignore` | Evitan que `venv/`, `node_modules/`, `.env` y `uploads/` entren en las imágenes. |
| `../backend/scripts/apply_migrations.py` | Migrador idempotente (tabla de control `schema_migrations`). |
| `../backend/scripts/check_schema_drift.py` | Compara los modelos con la base real. Detecta columnas/tablas que el ORM usa y las migraciones no crean. |
| `../backend/scripts/smoke_api.py` | Recorre todos los GET de la API y reporta errores 5xx. Sirve igual contra local o contra Render. |

---

## 1. Levantar el stack

```bash
cd docker
docker compose up -d --build
```

Requiere que exista `backend/.env`: de ahí salen los secretos (JWT, SMTP, Supabase).
El bloque `environment:` del compose solo sobreescribe los **hosts** de
`DATABASE_URL` / `DATABASE_RLS_URL` / `REDIS_URL` para que apunten a los servicios
`postgres` y `redis` en vez de a `localhost`.

| Servicio | URL |
|---|---|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| Docs de la API | http://localhost:8000/api/docs (con `DEBUG=true`) |
| Bandeja de correo (Mailhog) | http://localhost:8025 |
| Postgres | `localhost:5433` (5433 para no chocar con un postgres local) |

Arranque: `postgres` y `redis` sanos → `migrate` aplica las migraciones pendientes y
siembra los datos demo → recién ahí arrancan `backend` y `worker`. Si `migrate` falla,
el backend **no** arranca (a propósito: es el chequeo de esquema del despliegue).

Usuarios demo que crea el seed (`backend/scripts/seed_data.py`):
`admin@codeacademypro.com / Admin123!` · `ana.garcia@codeacademypro.com / Teacher123!` ·
`estudiante@codeacademypro.com / Student123!` — **cambiar antes de compartir la URL**.

Para que la app envíe correo al Mailhog local: en `backend/.env`
`SMTP_HOST=mailhog`, `SMTP_PORT=1025`, `SMTP_USE_TLS=false`.

Operación:

```bash
docker compose logs -f backend worker
docker compose run --rm migrate                       # aplicar migraciones pendientes
docker compose exec backend python scripts/apply_migrations.py --status
docker compose exec backend python scripts/check_schema_drift.py
docker compose run --rm backend python scripts/smoke_api.py --base-url http://backend:8000
docker compose down -v                                # borrar contenedores y datos
```

---

## 2. La cadena de migraciones estaba rota (y quedó arreglada)

Estado real: **la cadena de migraciones nunca se ejecutó sobre una base vacía**. La
base local se generó en algún momento con `Base.metadata.create_all()` del ORM, así
que tenía tablas y columnas que las migraciones no crean, y el hueco era invisible.
En una base nueva (Render + Supabase, por ejemplo) la cadena moría en la 005.

Lo que se encontró y cómo se cerró (todo aditivo: nada borra ni renombra datos):

| Hallazgo | Síntoma en base nueva | Arreglo |
|---|---|---|
| `users.status` usada por el modelo, el registro y `/admin/users`, sin migración que la cree | 004 abortaba con `column "status" does not exist` | `004_performance_indexes.sql`: los índices van guardados con un chequeo de existencia. La columna la agrega `023_add_missing_columns.sql` |
| Tablas `students` y `teachers` sin migración | 005 abortaba con `relation "students" does not exist` (y 010/011/013 fallarían después) | `004a_add_student_teacher_tables.sql` (antes de 005 a propósito) |
| `feature_flags.flag_metadata` (el ORM no puede mapear `metadata`, es reservado) | 015 abortaba con `column "flag_metadata" does not exist` | `014a_add_flag_metadata.sql` (antes de 015) |
| Timestamps y columnas que faltaban: `background_jobs.updated_at`, `email_queue.updated_at`, `roles.updated_at`, `system_settings.created_at`, `payment_proofs.created_at`/`updated_at` | fallos del ORM al consultar esas tablas | `023_add_missing_columns.sql` |

Residuo aceptado (columnas viejas que ningún modelo declara, no rompen nada):
`users.is_active`, `feature_flags.metadata`, `payment_proofs.uploaded_at`.

Comprobado: 001→023 aplican limpias sobre una base vacía, el seed corre y
`python scripts/check_schema_drift.py` responde **"esquema alineado con los modelos"**.

> Nota: `check_schema_drift.py` es la herramienta para no volver a caer en esto. Si
> alguien agrega una columna al ORM sin migración, lo dice en segundos; y si una base
> ya existente se marcó con `--baseline`, sirve para verificar qué falta de verdad.

---

## 3. Render + Supabase (la arquitectura real, 0 €)

Son **dos servicios web** (la API y la web son procesos separados).

### 3.1 Supabase
1. Crear proyecto (free): nombre `codeacademy-pro`, región la misma que Render.
2. **Connect → Session pooler** y copiar la cadena. La conexión directa de los
   proyectos free es **IPv6-only**; el pooler (`aws-0-<region>.pooler.supabase.com:5432`)
   es IPv4 y es el que usa Render. El usuario es `postgres.<project-ref>`.
3. Convertirla al formato de SQLAlchemy (driver asyncpg), **sin parámetros de ssl**
   (asyncpg negocia TLS por defecto):

```
postgresql+asyncpg://postgres.<ref>:<PASSWORD>@aws-0-<region>.pooler.supabase.com:5432/postgres
```

4. **Storage → New bucket** → `academy-storage` (privado). Copiar `Project URL` y la
   `service_role key` (Settings → API). La service_role key va **solo** en el backend.

### 3.2 Aplicar las migraciones a Supabase
Desde WSL, con la imagen ya construida:

```bash
cd docker
DATABASE_URL='postgresql+asyncpg://postgres.<ref>:<PASSWORD>@aws-0-<region>.pooler.supabase.com:5432/postgres' \
  docker compose run --rm --no-deps -e DATABASE_URL="$DATABASE_URL" migrate
```

Aplica `001`→`023` en orden, registra cada archivo en `schema_migrations` y ejecuta el
seed. Si una migración falla, se detiene en esa y no registra nada.
Después, verificar contra la base remota:

```bash
DATABASE_URL='...' docker compose run --rm --no-deps -e DATABASE_URL="$DATABASE_URL" \
  backend python scripts/check_schema_drift.py
```

> `--baseline` (marcar migraciones como aplicadas sin ejecutarlas) es solo para una
> base que ya tenía tablas creadas por el ORM. Después de un `--baseline` hay que
> correr `check_schema_drift.py`: lo más probable es que falten justo las cosas de la
> tabla de arriba.

### 3.3 Render
Dos web services, ambos con runtime **Docker** (nada que construir a mano: Render
construye las imágenes desde el repo).

**API**
```
Root Directory:            (vacío)
Dockerfile Path:           docker/Dockerfile.backend
Docker Context Directory:  .
Health Check Path:         /health
```

**Web**
```
Root Directory:            (vacío)
Dockerfile Path:           docker/Dockerfile.frontend
Docker Context Directory:  frontend
Environment:               API_PROXY_TARGET = https://<api>.onrender.com
```

Definí `API_PROXY_TARGET` **antes del primer build**: Next resuelve las `rewrites` en
build time y las deja horneadas en la imagen, así que si cambia la URL del backend hay
que **redeployar el front** (no alcanza con reiniciar). Por eso conviene crear primero
la API, copiar su URL, y después la web.

Alternativa más rápida: `New → Blueprint → repo → Blueprint Path: docker/render.yaml`
(configura los dos servicios, el Key Value y las variables de una vez; el campo de
ruta admite subcarpetas). En cualquiera de los dos caminos, **primero hay que hacer
push**: Render lee el repo remoto, no el disco local.

Variables que hay que cargar en el dashboard (nunca en git): `DATABASE_URL`,
`DATABASE_RLS_URL`, `SUPABASE_URL`, `SUPABASE_KEY` y las de SMTP si usás correo real.
`JWT_SECRET` lo genera Render. Para la fase de pruebas, `DATABASE_RLS_URL` = el mismo
valor que `DATABASE_URL` (ver §5.4).

Verificación después del deploy:

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://<api>.onrender.com/health
python scripts/smoke_api.py --base-url https://<api>.onrender.com
```

---

## 4. Plan free: qué funciona y qué no

| Función | Free | Nota |
|---|---|---|
| Registro/login/JWT, RBAC, cursos, módulos, inscripciones, clases, asistencia | ✅ | Verificado: 28/28 endpoints GET en verde con los 3 roles |
| Pagos (subir comprobante, aprobar/rechazar) | ⚠️ | El flujo anda, pero **los archivos no persisten** hasta pasar a Storage (§5.1) |
| Reseñas, notificaciones in-app, auditoría, feature flags, content versioning | ✅ | Completo |
| Emails (verificación, reset, avisos) | ❌ | Sin SMTP real ni worker (§5.2/§5.3) |
| PDFs de certificados, métricas de dashboard, limpieza, recordatorios | ❌ | Dependen del worker ARQ (§5.3) |
| RLS reforzado | ❌ | Queda en modo aviso (§5.4) |
| Primer acceso tras inactividad | ⚠️ | Render duerme a los 15 min; el primer request tarda ~1 min |

Límites: **750 horas-instancia por workspace al mes, compartidas entre servicios**
(dos servicios siempre despiertos las agotan en ~15,6 días y Render suspende hasta el
mes siguiente), 100 GB de ancho de banda, y **Supabase pausa el proyecto a los 7 días
sin actividad**.

UptimeRobot: alcanza con monitorear la **web** (≈720 h/mes, deja margen) y dejar que
la API despierte sola al primer uso. Para el monitor de la API usar un endpoint que
toque la base (`/health` solo consulta Redis, así que no evita la pausa de Supabase);
`/api/v1/courses/<slug>` sirve porque el detalle de curso no está cacheado, a
diferencia de `/categories`.

---

## 5. Pendientes de código antes de un despliegue "de verdad"

### 5.1 Uploads a disco local → Supabase Storage (o S3)
`backend/app/api/v1/payments/router.py:34` y `:41` escriben en `uploads/proofs` y
`uploads/qr` (relativas al CWD). En Render el filesystem es efímero: se pierden en
cada deploy/reinicio y con más de una instancia dan 404 aleatorios. `boto3` y
`supabase` están en `requirements.txt` pero **ningún módulo los usa**. Hay que cambiar
2 puntos de escritura y los 3 endpoints que sirven los archivos (`FileResponse` desde
disco) por URLs firmadas.

### 5.2 Emails
`email_service.py` usa `smtplib` contra `SMTP_HOST=localhost:1025` (Mailhog). Para la
nube: SMTP real (Resend/Brevo/SendGrid) con `SMTP_USE_TLS=true`, `SMTP_USER` y
`SMTP_PASSWORD`; mejor todavía `aiosmtplib` para no bloquear el hilo.

### 5.3 Worker ARQ
No existe como servicio en el plan free de Render. Opciones: (a) descomentar el bloque
`type: worker` de `render.yaml` con plan `starter` (~7 $/mes); (b) workaround sin
coste: un tercer web service free cuyo comando levante `arq` en segundo plano **y**
sirva un `/health` con un HTTP mínimo (si el proceso no abre puerto, Render lo marca
caído).

### 5.4 RLS
`backend/app/db/session.py:29-40` lanza `RuntimeError` al arrancar si
`ENVIRONMENT=production` y `DATABASE_RLS_URL` está vacío. Para activar RLS de verdad
hay que darle contraseña al rol de aplicación (migración `009`), setear
`DATABASE_RLS_URL` con ese rol y pasar `ENVIRONMENT=production` (que además exige
`CORS_ORIGINS` en HTTPS y sin localhost — `config.py:189-199`).

### 5.5 Ruido cosmético
Al correr el seed aparece `(trapped) error reading bcrypt version` (passlib 1.7.4 vs
bcrypt ≥ 4.1). No rompe nada — el hash y el login funcionan —, se silencia pinneando
`bcrypt==4.0.1` en `requirements.txt`.

---

## 6. Alternativa inmediata (sin coste, sin migrar nada)

Para que el equipo pruebe **hoy**, exponiendo tu stack local:

```bash
# 1) stack local levantado (WSL)
cd docker && docker compose up -d
# 2) túnel público
wsl -e bash -lc "cloudflared tunnel --url http://localhost:3000"
```

Añadir la URL `https://<algo>.trycloudflare.com` a `CORS_ORIGINS` en `backend/.env`,
reiniciar el backend y compartir el enlace. Contras: tu PC debe estar encendida y
todos trabajan sobre tu base local (para resets: `backend/scripts/reset_db.py`).
