# Contexto de mano para perfil academy

## Estado del repo

- Ruta: C:\Users\guill\Documents\Personal_Projects\Programacion\Academia\002WM_CODE_ACADEMY_PRO
- Rama: master, sincronizada con origin/master
- git status: limpio
- Ultimo commit: 48d67cf "Ciclo inscripcion->clase->contenido: inscripcion al aprobar el pago, alta de clases y temario en admin, grabacion de clase y orden del temario por arrastre"

## Tarea en curso

Corregir el control de acceso al temario y la gestion de cupos por clase en CodeAcademy Pro.

### Problemas identificados

1. Temario: actualmente cualquier usuario autenticado con rol student/teacher/admin ve TODO el temario de cualquier curso, aunque no haya comprado. Debe verse completo solo si:
   - Tiene una inscripcion pagada/active o payment_approved para ESE curso, o
   - Es admin/coordinator/teacher del curso.
   Sin sesion o sin inscripcion: solo el primer modulo.

2. Cupos: el limite global (system_settings.global_max_students_per_class) esta en 100. Debe ser 20.

3. Contador de cupos: nunca debe mostrar 0. Cuando una clase se llena, el frontend debe mostrar un aviso de "nueva clase proxima" hasta que el admin cree otra.

4. Notificacion: cuando un curso acumule 5 inscritos activos y NO tenga ninguna clase activa, notificar a los admins. Forma: dentro de la plataforma (campana) y por correo (ambas).

### Decisiones confirmadas por el usuario

- Maximo por clase: 20 alumnos.
- "Se reinicia" = frontend nunca muestra 0; muestra aviso de nueva clase proxima.
- Notificacion = plataforma + correo.

### Plan tecnico

1. Migracion 026:
   - Actualizar system_settings.global_max_students_per_class a 20.
   - Crear tabla notifications con RLS.
2. Modelo Notification en backend/app/models/notification.py.
3. Servicio de notificaciones (backend/app/services/notification_service.py):
   - Crear notificacion en plataforma.
   - Encolar email para admins via EmailQueue / ARQ.
4. Ajustar course_service._get_course_classes_summary para:
   - Nunca devolver 0 cupos si hay clases.
   - Devolver flag needs_more_classes cuando todas las clases estan llenas.
5. En payment_router.approve_payment, despues de crear/activar una inscripcion:
   - Si el curso tiene 0 clases activas y acaba de llegar a 5 inscritos activos, disparar notificacion a admins.
6. Nuevo endpoint GET /courses/{slug}/access (auth opcional) que devuelva:
   - can_view_full_syllabus: bool
   - enrollment_status: str | null
   - role_for_course: str | null
7. Tests de integracion extendiendo backend/tests/test_enrollment_lifecycle_and_recording.py.
8. Frontend:
   - Reemplazar canSeeFullSyllabus en frontend/src/app/courses/[slug]/page.tsx por llamada a /courses/{slug}/access.
   - Ajustar mensajes de cupos y clases segun needs_more_classes.
9. Verificar: pytest, tsc --noEmit, next build.

### Archivos clave

- backend/app/models/course_class.py
- backend/app/models/course.py
- backend/app/models/payment.py
- backend/app/models/system.py
- backend/app/services/course_service.py
- backend/app/services/course_class_service.py
- backend/app/services/enrollment_service.py
- backend/app/services/email_service.py
- backend/app/services/background_jobs.py
- backend/app/api/v1/payments/router.py
- backend/app/api/v1/courses/router.py
- backend/app/api/v1/notifications/router.py
- backend/app/repositories/enrollment_repository.py
- backend/app/repositories/course_class_repository.py
- backend/app/db/rls.py
- backend/tests/test_enrollment_lifecycle_and_recording.py
- frontend/src/app/courses/[slug]/page.tsx
- database/migrations/025_enrollment_class_lifecycle_and_recording.sql

### Convenciones del proyecto

- Backend: FastAPI + SQLAlchemy 2.0 async, capas api/v1 -> services -> repositories -> models.
- RLS forzado en PostgreSQL; los endpoints autenticados usan get_rls_db.
- Endpoints publicos usan get_db; para auth opcional existe get_rls_db_optional.
- Tests de integracion en backend/tests/ con base academy_test, redis 6379.
- TEST_DB_RESET=1 reconstruye migraciones 001->NNN + seed.
- Frontend: Next.js 16 App Router, hooks por recurso, toasts.
- Commits/push solo cuando el usuario lo pida.

### Comandos de verificacion

- Backend tests (en WSL): cd backend && TEST_DB_RESET=1 venv/bin/python -m pytest tests/test_enrollment_lifecycle_and_recording.py -v
- Frontend typecheck: cd frontend && npx tsc --noEmit
- Frontend build: cd frontend && npx next build

## Notas

- El sistema de notificaciones actual (backend/app/api/v1/notifications/router.py) es un stub vacio; hay que construirlo.
- EmailQueue ya existe en backend/app/models/system.py y hay servicio ARQ en backend/app/services/background_jobs.py.
- El email_service ya tiene plantillas; se puede agregar una nueva o encolar con template generico.
