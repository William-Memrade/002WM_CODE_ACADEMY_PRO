# 🗺️ Roadmap de Desarrollo — CodeAcademy Pro

> **Estado verificado contra el código:** 2026-09-11.
> Leyenda: `[x]` implementado y verificado · `[~]` parcial (ver nota) · `[ ]` pendiente.

## Fase 1: MVP Core (Sprints 1-4) — ~8 semanas

### Sprint 1: Fundación
- [x] Arquitectura documentada
- [x] Proyecto backend (FastAPI scaffold) — 12 routers bajo `/api/v1`
- [x] Base de datos: schema + migraciones — `001_initial_schema.sql` + 23 migraciones
- [x] Auth: registro, login, JWT, refresh — `api/v1/auth/router.py`
- [x] RBAC básico (admin, coordinator, teacher, student) — `middlewares/rbac.py`

### Sprint 2: Cursos + Inscripciones
- [x] CRUD cursos (admin)
- [x] Categorías
- [x] Módulos y lecciones — modelos `Module`/`Lesson`; alta (`POST /courses/{id}/modules`, `POST /courses/modules/{id}/lessons`), edición (`PUT /courses/modules|lessons/{id}`), borrado (`DELETE`) y temario completo (`GET /courses/{id}/modules`). Escribir exige ser el docente del curso: `ensure_course_manager` (`middlewares/rbac.py`); verificado en `backend/tests/test_teacher_curriculum_progress.py`
- [x] Catálogo público de cursos
- [x] Inscripción de alumnos — `Enrollment` + flujo de pago (`submit-proof` / `assign-class`)
- [x] Asignación docentes a cursos

### Sprint 3: Pagos + Contenido
- [x] Flujo de pago manual completo — `api/v1/payments/router.py`
- [x] Upload de comprobantes — `PaymentProof` + validación de MIME real
- [x] Aprobación/rechazo por admin
- [ ] Clases grabadas (upload + streaming) — modelos `RecordedClass`/`LiveClass` declarados pero sin usar: no hay endpoints ni storage de vídeo
- [x] Clases en vivo (links) — `PATCH /course-classes/{class_id}/meeting-link`
- [x] Progreso del alumno — `enrollments.progress_percentage` con endpoints y UI: el docente lo escribe (`PATCH /course-classes/{class_id}/students/{student_id}/progress`, 0-100, sella `completed_at` al 100) y el alumno lo lee (`GET /students/me/progress` + barra en `/student/courses`). La lista de alumnos de la clase expone el progreso
- [ ] Cálculo automático del progreso (lecciones vistas / total) — hoy es un porcentaje que marca el docente a mano; ver `FLOWS.md`

### Sprint 4: Frontend MVP
- [x] Proyecto Next.js scaffold — Next 16 App Router (`frontend/src/app`)
- [x] Landing page
- [x] Catálogo de cursos — `/courses` + `/courses/[slug]`
- [x] Auth pages (login, register) — + `change-password`
- [~] Panel alumno — dashboard, cursos, pagos y asistencia reales; notificaciones, certificados y perfil son placeholders
- [x] Panel admin — dashboard, pagos, cursos, clases, usuarios, docentes, categorías, auditoría, settings, feature flags
- [x] Panel docente — dashboard, cursos (`/teacher/courses`), clases, asistencia y alumnos (`/teacher/students`) reales, más el editor de temario (`/teacher/courses/[id]/curriculum`). Fuera de este item quedan vídeos, calificación y versiones

---

## Fase 2: Features Completas (Sprints 5-7) — ~6 semanas

### Sprint 5: Comunicación + Feedback
- [ ] Notificaciones in-app — router es esqueleto: 4 endpoints que devuelven listas vacías o `count: 0`
- [x] Sistema de emails transaccionales — SMTP + `EmailQueue` + worker ARQ, 7 plantillas (texto plano, sin HTML)
- [ ] Reseñas de cursos — tabla `reviews` creada y endpoints stub que devuelven `{}`
- [ ] Sugerencias — sin rastro en el código
- [ ] Certificados (emisión + PDF) — solo job stub, plantilla de email y evento de auditoría

### Sprint 6: Reputación + Observabilidad
- [ ] Calificación de alumnos (docente) — tabla `student_ratings` creada, sin modelo ni endpoints
- [~] Sistema de estrellas — `reviews.rating` (1-5) con constraint en BD; sin implementar ni exponer
- [ ] Alumnos destacados
- [ ] Alumnos listos evaluación externa
- [x] Logging estructurado — `core/observability.py` (structlog + correlation ID)
- [~] Health checks — `/health` real; `/health/ready` devuelve `ok` fijo (TODO en `main.py`)
- [~] Métricas Prometheus — `prometheus-fastapi-instrumentator` en requirements, no instrumentado en la app

### Sprint 7: Admin Avanzado
- [x] Auditoría completa — `AuditService` + `GET /audit-logs` con filtros y paginación
- [x] Feature flags
- [x] Content versioning
- [x] Background jobs (ARQ) — worker dedicado + modelos `BackgroundJob`/`EmailQueue`
- [x] Rate limiting
- [x] System settings

---

## Fase 3: Pulido + Producción (Sprints 8-9) — ~4 semanas

### Sprint 8: Testing + Security
- [~] Tests unitarios (>80% coverage backend) — 7 ficheros (password policy, security headers, CORS…); sin coverage ni umbral
- [x] Tests de integración API — `test_api_integration.py` + `tests/support.py` (Postgres/Redis, marcador `integration`); temario y progreso en `test_teacher_curriculum_progress.py` (14 casos: permisos, 404/403, rango 0-100, `completed_at` y RLS del docente)
- [ ] Tests E2E frontend (Playwright) — sin instalar y sin carpeta de tests
- [~] Security audit (OWASP checklist) — `SECURITY.md` + headers de seguridad + bumps de CVE (next/postcss/sharp); sin auditoría formal
- [ ] Performance testing (k6/locust) — solo `QueryProfilingMiddleware` (`X-Query-Count`, `X-DB-Time-Ms`)
- [ ] Fix de bugs

### Sprint 9: Deploy + Launch
- [x] Docker producción optimizado — `Dockerfile.backend`/`Dockerfile.frontend` + `docker-compose.yml` (postgres, redis, migrate, backend, worker, frontend, mailhog)
- [ ] CI/CD pipeline — no existe `.github/workflows` ni equivalente
- [ ] Monitoring (Grafana dashboards) — las métricas aún no se exponen
- [x] Documentación de deploy — `docker/DEPLOY.md` + `docker/render.yaml`
- [x] Seed data de producción — `backend/scripts/seed_data.py`, `bootstrap_db.py`
- [ ] Launch preparation

---

## Fase 4: Evolución (Post-Launch)

### V2 — Mejoras
- [ ] Pasarela de pago online (Stripe/PayPal)
- [ ] Sistema de cupones/descuentos
- [ ] Búsqueda full-text (PostgreSQL ts_vector)
- [ ] Internacionalización (i18n)
- [ ] PWA support
- [ ] Dark mode

### V3 — Expansión
- [ ] App móvil (React Native)
- [ ] IA Tutor (chatbot con RAG)
- [ ] Analytics avanzado (dashboards custom)
- [ ] Bolsa de empleo
- [ ] Integración empresas (B2B)
- [ ] API pública para partners

### V4 — Escala
- [ ] Migración a microservicios
- [ ] Event-driven architecture
- [ ] Kubernetes deployment
- [ ] Multi-tenancy
- [ ] CDN para video streaming
- [ ] Real-time features (WebSocket)

---

## Divergencias con el plan

Implementado y no previsto arriba:

- Panel Coordinador (`frontend/src/app/coordinator`): dashboard, clases y pagos.
- RLS a nivel de fila en Postgres (`app/db/rls.py`, `docs/architecture/rls_guide.md`).
- Middlewares extra: security headers, correlation ID, query profiling, captcha.
- Blueprint de Render para despliegue (`docker/render.yaml`).

Fuera de alcance:

- **Docker Compose de desarrollo** (retirado del Sprint 1): el repo mantiene un único `docker/docker-compose.yml` con imágenes de producción (postgres, redis, migrate, backend, worker, frontend, mailhog), suficiente para levantar el entorno local. No se creará una variante aparte.

---

## Bitácora: pasos no previstos (2026-09-11)

Trabajos que el plan original no contemplaba y que hubo que añadir para cerrar
"módulos y lecciones" y "progreso del alumno". Ya están hechos; se listan aquí
para que no se pierdan como trabajo invisible:

- **API de temario completa** — el plan sólo tenía el alta (POST). Se añadieron `GET /courses/{id}/modules`, `PUT/DELETE /courses/modules/{id}` y `PUT/DELETE /courses/lessons/{id}` sobre el router de cursos (no se creó un router `/modules` aparte, que era lo que insinuaba `API_ENDPOINTS.md`).
- **Autorización por recurso, no sólo por rol** — `ensure_course_manager` y `ensure_class_manager` en `middlewares/rbac.py`: sin ellos cualquier docente podía tocar el temario o el progreso de un curso ajeno en desarrollo (y en producción el INSERT chocaba con RLS, devolviendo un 500 en vez de un 403).
- **Migración `024_rls_teacher_curriculum_and_progress.sql`** — la política de 010 dejaba el borrado del temario y el UPDATE de `enrollments` sólo a `is_admin()`. Con RLS forzado (`DATABASE_RLS_URL`, obligatorio en producción) el docente habría recibido 204/200 sin cambiar nada; la migración lo arregla y de paso deja al docente de la clase ver su roster.
- **Endpoints agregados del panel docente** — `GET /teachers/me/courses` (con conteos y progreso medio, sin N+1) y `GET /teachers/me/students`.
- **Progreso manual + sellado de `completed_at`** — no estaba decidido si el progreso se calculaba o se marcaba; se implementó manual (0-100) con `completed_at` reversible, y el cálculo automático queda como pendiente en el Sprint 3.
- **Utilidades de frontend** — `hooks/useTeacherData.ts`, `hooks/useStudentProgress.ts` y la página nueva `/teacher/courses/[id]/curriculum`; las páginas `/teacher/courses` y `/teacher/students` se reescribieron y `/student/courses` ganó la barra de progreso.
- **Tests de integración del lote** — `backend/tests/test_teacher_curriculum_progress.py` (14 casos) con montaje/desmontaje de la inscripción por SQL, porque no existe endpoint de alta de inscripciones.
- **Reparto de responsabilidades entre capas** — `EnrollmentRepository`/`EnrollmentService` nuevos; `CourseService` absorbió el CRUD del temario y `CourseClassService` devuelve el progreso en el roster.
