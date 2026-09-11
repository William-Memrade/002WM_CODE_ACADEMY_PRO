# Pruebas y Calidad

Estado de la red de seguridad de CodeAcademy Pro: qué se prueba hoy, con qué comando,
y el plan por capas con lo que falta. Los números de este documento salen de correr la
suite, no de estimaciones.

- **Capa 0 (arreglar lo roto): hecha** — Día 1.
- **Capa 1 (unitarias puras): 105 casos en verde** — Día 1.
- **Capa 2 (integración HTTP + base efímera): infraestructura hecha, 9 casos base** — Día 1.
- Capas 3-6: planificadas, ver *Plan por capas*.

---

## 1. Cómo correr las pruebas

Todo el backend se prueba **desde WSL**, no desde Git Bash: `backend/venv` es un venv
creado en Linux para otra ruta y su `bin/python` no existe en Windows. Además, las
pruebas de RLS e integración necesitan PostgreSQL y Redis.

```bash
# 1) Dependencias (una vez)
wsl -e bash -lc "cd /mnt/c/.../002WM_CODE_ACADEMY_PRO/backend && venv/bin/python -m pip install -r requirements-dev.txt"

# 2) Servicios: PostgreSQL (docker compose, puerto 5433) y Redis (base 15 para pruebas)
wsl -e bash -lc "cd /mnt/c/.../002WM_CODE_ACADEMY_PRO/docker && docker compose up -d postgres redis"
wsl -e bash -lc "docker run -d --rm --name ca-test-redis -p 6379:6379 redis:7-alpine"

# 3) Suite completa
wsl -e bash -lc "cd /mnt/c/.../002WM_CODE_ACADEMY_PRO/backend && venv/bin/python -m pytest tests/ -q"

# Sólo lo unitario (sin servicios, 5 s)
wsl -e bash -lc "cd /mnt/c/.../002WM_CODE_ACADEMY_PRO/backend && venv/bin/python -m pytest tests/ -q -m 'not integration'"

# Sólo integración + RLS
wsl -e bash -lc "cd /mnt/c/.../002WM_CODE_ACADEMY_PRO/backend && venv/bin/python -m pytest tests/ -q -m integration"

# Reconstruir la base de pruebas desde cero (cuando cambian migraciones)
wsl -e bash -lc "cd /mnt/c/.../002WM_CODE_ACADEMY_PRO/backend && TEST_DB_RESET=1 venv/bin/python -m pytest tests/ -q"

# Herramienta de humo contra un deploy real (lee /openapi.json del entorno)
wsl -e bash -lc "cd /mnt/c/.../002WM_CODE_ACADEMY_PRO/backend && venv/bin/python scripts/smoke_api.py"
```

Si faltan PostgreSQL o Redis, las capas de integración y RLS **se saltan con el comando
para levantarlos** en el mensaje; nunca fallan en masa por infraestructura ausente.

### Variables de la capa de integración

| Variable | Default | Para qué |
|---|---|---|
| `TEST_ADMIN_DATABASE_URL` | `postgresql+asyncpg://postgres:password@localhost:5433/postgres` | Superusuario: crea y migra la base de pruebas |
| `TEST_DB_NAME` | `academy_test` | Nombre de la base de pruebas (separada de `academy_db`) |
| `TEST_REDIS_URL` | `redis://localhost:6379/15` | Redis del rate limiter en pruebas |
| `TEST_DB_RESET=1` | — | Borra el esquema y rehace migraciones + seed antes de correr |
| `RLS_TEST_DB_URL` | derivada (`academy_app` sobre `academy_test`) | Rol con RLS para `test_rls.py` |

`backend/tests/support.py` es la fuente de estas constantes; `backend/tests/conftest.py`
las aplica **antes** de importar la app (los settings son un singleton cacheado y el
engine se crea en import-time).

---

## 2. Qué hay hoy

| Archivo | Casos | Qué cubre | Necesita servicios |
|---|---|---|---|
| `tests/test_security_headers.py` | 45 | Cabeceras por entorno (HSTS, CSP, X-Frame-Options…) | No |
| `tests/test_cors.py` | 35 | Matriz de orígenes permitidos/rechazados | No |
| `tests/test_courses_optional_teacher.py` | 18 | `course_service.update` con/sin docente | No |
| `tests/test_password_policy.py` | 7 | Reglas y bordes de longitud (8-50) | No |
| `tests/test_rls.py` | 29 | Aislamiento por rol y propiedad, con la base aplicando RLS | Sí |
| `tests/test_api_integration.py` | 9 | App completa en proceso: health, contrato, login, `/users/me`, RBAC | Sí |
| `tests/test_teacher_curriculum_progress.py` | 14 | Temario (alta/edición/borrado + 403 de otro docente) y progreso (docente escribe, alumno lee, rango 0-100, `completed_at`) | Sí |

Total: **158 casos** (105 sin servicios, 53 con servicios) en ~25 s. Otras herramientas
que no son pytest: `scripts/smoke_api.py` (humo contra un deploy) y
`scripts/check_schema_drift.py` (modelos del ORM vs base real).

Lo que **no** existe todavía:

- Frontend: cero infraestructura de prueba (`package.json` sólo tiene `next lint`).
- CI: no hay `.github/workflows`. Nada corre solo.
- Estrés/carga: nada.
- Base de staging: Supabase free no tiene branches; los tests de escritura van contra
  base local/efímera, nunca contra el deploy.

---

## 3. Plan por capas

Dicen qué compra cada capa, de más barata a más cara.

### Capa 0 — Arreglar lo roto (hecha)

Dos fallos que envenenaban cualquier pipeline futuro:

1. `test_password_policy` esperaba rechazo a los 20 caracteres, pero el máximo real es
   50 (`PASSWORD_MAX_LENGTH`). El contrato estaba desactualizado, no el código.
2. `test_rls` no podía pasar: apuntaba a `localhost:5432` (el compose publica **5433**)
   y el engine estaba creado a nivel de módulo, así que a partir del segundo test
   fallaba con *"got Future attached to a different loop"*.

### Capa 1 — Unitarias puras (hecha, huecos)

Corren en cada push sin secretos ni servicios. Ya cubren cabeceras, CORS, política de
contraseñas y `course_service`. **Hueco**: `app/services/` casi sin tests directos
(`auth_service`, `feature_flags`, `captcha_service`, `content_versioning`, cálculo de
progreso). Son funciones con lógica y se prueban en milisegundos.

### Capa 2 — Integración HTTP + base efímera (infraestructura hecha)

Es la capa que permite afirmar *"el flujo sigue funcionando"* con evidencia:
middleware → router → servicio → SQLAlchemy → RLS → PostgreSQL real, sin servidor ni
puerto (`httpx.ASGITransport`). La base (`academy_test`) se crea, migra y siembra con
el migrador y el seed reales, en la primera corrida y desde cero.

Empezó con 9 casos (cimientos: health, contrato, login, `/users/me`, RBAC admin). El
valor completo llega con los flujos de la capa 4.

### Capa 3 — Contrato y regresión de endpoints

- `docs/architecture/API_ENDPOINTS.md` documenta método, ruta, rol y rate limit de cada
  endpoint, pero **nada lo verifica contra el código**; ya se desincronizó una vez.
- Extender el humo a POST/PATCH/PUT/DELETE, resolviendo las rutas con `{id}` en orden
  crear → leer → actualizar → borrar, con datos desechables.
- Afirmar el rol por endpoint: 200 con el rol correcto, 401/403 con los otros. Convierte
  la documentación en prueba y detecta escaladas de privilegio.
- Congelar `openapi.json` en el repo: si alguien toca el contrato, sale en el diff.
- Opcional: `schemathesis` sobre el `openapi.json` (encuentra 500 con payloads raros).

### Capa 4 — Flujos de negocio (E2E)

Los 5-6 críticos, cada uno con pasos: registro → verificación (leyendo `email_queue`,
sin SMTP), login por rol, inscripción → comprobante → aprobación → acceso al curso,
clase + asistencia, reset de contraseña, expiración/refresh de token.

Con el worker ARQ ausente, los flujos que terminan en email o PDF se prueban **hasta la
cola** (la fila queda en `email_queue` / `background_jobs`). Es valor real y es honesto:
no se puede probar lo que no corre.

### Capa 5 — Frontend

Playwright con 3-5 humos de navegación por rol (login → panel → listado → detalle)
contra el stack docker local. **No contra Render free.** Y después de cablear las ~7
páginas que hoy son mock (si no, se prueba humo de datos inventados).

### Capa 6 — Estrés / carga

k6 (binario, script corto) o Locust si se prefiere Python.

| Escenario | Carga | Umbral |
|---|---|---|
| Humo de carga (cada deploy) | 1-2 VUs, 1 min | error rate < 1% |
| Carga | 50-100 VUs, 5 min | p95 < 500 ms lectura, < 1.5 s login |
| Pico | subida a 200 VUs, 30 s | sin 5xx, recuperación tras el pico |
| Sostenido | 10 VUs, 30 min | sin fuga de conexiones/memoria |

Datos para dimensionarlo: pool de 10 conexiones por proceso (`DB_POOL_SIZE=5` +
`DB_MAX_OVERFLOW=5`), rate limit 100/min por IP (login 10, registro 5, forgot 3,
refresh 30). Probar el rate limiter a propósito (que devuelva 429 al pasarse y que
vuelva a atender al minuto) es parte del estrés.

**No** hacer: cientos de VUs contra Render free (se mide el throttle de Render, no la
app), carga contra el Supabase de producción, ni POST masivo contra el deploy (escribe
datos reales).

### Capa 7 — Checklist manual (mientras falten las capas 2-4)

8-10 puntos, 5 minutos: login por rol, catálogo, inscribirse, subir comprobante, aprobar,
ver curso, cerrar sesión. Documentado, no en la cabeza de una persona.

---

## 4. Día 1 — qué se hizo

| Archivo | Cambio |
|---|---|
| `backend/tests/support.py` | **Nuevo.** Configuración y helpers de la capa de integración: URLs de la base de pruebas, arranque de servicios, migraciones + seed, login por rol |
| `backend/tests/conftest.py` | **Nuevo.** Fixtures `prepared_database`, `api_client` (ASGITransport), `tokens` |
| `backend/tests/test_api_integration.py` | **Nuevo.** 9 casos base de integración |
| `backend/tests/test_rls.py` | Engine por test (`NullPool`), rollback explícito, URL por variable de entorno, skip si falta la base |
| `backend/tests/test_password_policy.py` | Contrato alineado al código (8-50) + casos de borde |
| `backend/app/core/password_policy.py` | Docstring 8-20 → 8-50 y lista de caracteres especiales real (`_!?*`) |
| `backend/pytest.ini` | `asyncio_mode=auto`, loop de fixtures por función, markers `integration`/`slow` |
| `backend/requirements-dev.txt` | **Nuevo.** Dependencias de desarrollo |
| `backend/requirements.txt` | Se quitaron `pytest`, `pytest-asyncio`, `ruff` (van en dev). `httpx` se queda: lo usa `captcha_service` en runtime |

Evidencia:

| | Antes | Después |
|---|---|---|
| Suite completa | 103 pasan, **1 falla, 29 errores** | **143 pasan, 0 fallan** |
| `test_rls.py` | 29 errores (no conectaba) | 29 pasan |
| Sin servicios levantados | errores de conexión | 105 pasan, 38 se saltan con instrucciones |
| Base de pruebas | no existía | se crea y se siembra desde cero en ~8 s |

### Trampas que quedaron documentadas en el código

- **Un engine por test**: un engine a nivel de módulo queda atado al event loop del
  primer test; a partir del segundo, *"got Future attached to a different loop"*.
- **Rollback explícito**: `async with session.begin():` hace **COMMIT** al salir, no
  rollback. Con esa forma, la primera corrida dejaba usuarios de prueba en la base y la
  segunda chocaba con `users_email_key`.
- **`flushdb` de Redis en cada test**: los contadores del rate limiter viven en Redis, no
  en el objeto del limiter; si no se limpian, el quinto login de la corrida se lleva un
  429 y el test falla por el orden de ejecución, no por un bug.
- **`dispose()` del engine de la app al final de cada test**: es el singleton de la app
  con pool; reutilizar conexiones de un loop cerrado da *"Event loop is closed"*.
- **Base separada** (`academy_test`): las pruebas nunca escriben en `academy_db`.

---

## 5. Buzón de sugerencias / reporte de bugs

La mitad ya está en el esquema y no se usa:

- `database/migrations/001_initial_schema.sql:291` crea `suggestions` (`user_id`,
  `subject`, `message`, `status` pending/reviewed/archived, `admin_notes`, `created_at`).
- `database/migrations/010_rls_policies.sql:618` le pone RLS: cada usuario ve las suyas,
  el admin ve todas, sólo el admin actualiza y borra.
- **Falta todo lo demás**: no hay modelo SQLAlchemy, ni servicio, ni router. Y
  `frontend/src/app/admin/feedback/page.tsx` es un mock que no toca esa tabla.

Para que sirva de verdad, al esquema le falta: estados de triage más ricos, prioridad,
categoría (bug/idea/mejora), contexto del bug (url, navegador, rol, `correlation_id` —
ya lo genera `CorrelationIdMiddleware`), hilo de respuestas, aviso in-app (la tabla
`notifications` existe y no necesita worker), auditoría (`audit_service`, acción
`suggestion.update`), y anti-abuso (captcha + rate limit por ruta).

| Opción | Coste | Cuándo |
|---|---|---|
| **A. GitHub Issues** en el repo (plantillas bug/idea, labels, milestones) | ~0 | Si el buzón es para el equipo |
| **B. Buzón in-app mínimo** (tabla + 1 migración + 2 endpoints + 2 pantallas) | 1-2 días | Si debe reportar el usuario final — **recomendada** |
| **C. Sistema de tickets completo** (SLA, adjuntos, comentarios, email) | 1-2 semanas | No ahora: sin worker no hay email ni PDFs, sin Storage no hay capturas |

Híbrido B+A: el buzón in-app es la puerta del usuario; cuando el admin decide trabajarlo,
un botón lo manda a GitHub. El triage técnico vive en GitHub, el canal del usuario en la
app. **Riesgo real**: sin dueño ni triage, un buzón es un cementerio de tickets en tres
semanas. Antes de abrirlo hay que definir quién revisa y cada cuánto.

Ojo con un detalle de producción: hoy `DATABASE_RLS_URL` apunta a la conexión de
superusuario, así que **RLS no está aplicado en producción** (ver `docker/DEPLOY.md`
§5.4). El aislamiento hoy lo da el código, no la base.

---

## 6. Siguientes pasos

| Día | Trabajo |
|---|---|
| 2-3 | Los 5-6 flujos críticos de la capa 4 sobre la infraestructura del Día 1 + snapshot del `openapi.json` |
| 4 | Extender el humo a POST/PATCH/DELETE con aserciones de rol; GitHub Actions (push + nocturno contra el deploy) |
| 5 | k6 con humo/carga/pico y umbrales; documentar en `docker/DEPLOY.md` |
| Aparte | Buzón in-app (opción B), 1-2 días |

En CI, PostgreSQL y Redis entran como *services*; el job no debe depender de ningún venv
local (construye todo desde `requirements-dev.txt`). El humo nocturno contra Render paga
el cold start (~50 s): hay que calentar con reintento antes de medir, o el job fallará
por timeout y se va a ignorar.

### Límites asumidos

- Sin worker ARQ no se prueban de punta a punta certificados, PDFs ni emails.
- Supabase free no tiene branches: no hay staging en la nube; los tests de escritura
  corren contra base local y contra el deploy sólo lectura.
- Las pruebas de estrés contra Render free miden Render, no la aplicación.
