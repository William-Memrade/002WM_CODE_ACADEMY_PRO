# 🔌 API Endpoints — CodeAcademy Pro

## Convenciones

- **Base URL**: `/api/v1`
- **Formato**: JSON
- **Auth**: Bearer JWT en `Authorization`
- **Paginación**: `?page=1&per_page=20`
- **Roles**: 🌐 Público | 🎓 Alumno | 👨🏫 Docente | 🔑 Admin | 🔒 Autenticado
- **Estado**: las filas marcadas como ⏳ están planificadas y **no** existen todavía.
  Lo que no lleva marca es código en `backend/app/api/v1` y está cubierto por los
  tests de `backend/tests`.

---

## Auth — `/api/v1/auth`

| Método | Ruta | Rol | Descripción | Rate Limit |
|--------|------|-----|-------------|------------|
| POST | `/register` | 🌐 | Crear cuenta alumno | 5/min |
| POST | `/login` | 🌐 | Login → JWT + refresh | 10/min |
| POST | `/refresh` | 🔒 | Renovar access token | 30/min |
| POST | `/logout` | 🔒 | Invalidar refresh token | - |
| GET | `/verify-email` | 🌐 | Verificar email `?token=xxx` | 10/min |
| POST | `/forgot-password` | 🌐 | Solicitar reset password | 3/min |
| POST | `/reset-password` | 🌐 | Reset con token | 5/min |

---

## Courses — `/api/v1/courses`

| Método | Ruta | Rol | Descripción |
|--------|------|-----|-------------|
| GET | `/` | 🌐 | Listar cursos activos |
| GET | `/{slug}` | 🌐 | Detalle curso |
| POST | `/` | 🔑 | Crear curso |
| PUT | `/{id}` | 🔑👨‍🏫 | Editar curso |
| DELETE | `/{id}` | 🔑 | Soft delete |
| PATCH | `/{id}/activate` | 🔑 | Activar |
| PATCH | `/{id}/deactivate` | 🔑 | Desactivar |

Query: `?category={slug}&level={level}&search={text}&sort_by={field}&page={n}&per_page={n}`

---

## Enrollments — `/api/v1/enrollments`

| Método | Ruta | Rol | Descripción |
|--------|------|-----|-------------|
| POST | `/` | 🎓 | Inscribirse `{ "course_id": "uuid" }` |
| POST | `/{id}/cancel` | 🎓 | Cancelar inscripción |
| GET | `/my-courses` | 🎓 | Mis cursos |
| GET | `/{id}` | 🎓 | Detalle inscripción |

---

## Payments — `/api/v1/payments`

| Método | Ruta | Rol | Descripción |
|--------|------|-----|-------------|
| POST | `/{id}/upload-proof` | 🎓 | Subir comprobante (multipart, max 10MB) |
| GET | `/{id}/status` | 🎓🔑 | Estado de pago |
| GET | `/my-payments` | 🎓 | Historial pagos |
| POST | `/{id}/approve` | 🔑 | Aprobar pago |
| POST | `/{id}/reject` | 🔑 | Rechazar pago |
| GET | `/pending` | 🔑 | Pagos pendientes |

---

## Modules — dentro de `/api/v1/courses` (temario)

> Los módulos y lecciones van colgados del curso, no de un router propio: es el
> contrato que usan el frontend del docente y los tests. Quién puede escribir no
> depende sólo del rol: `ensure_course_manager` exige ser el docente del curso (o
> impartir alguna de sus clases). Otro docente recibe 403.

| Método | Ruta | Rol | Descripción |
|--------|------|-----|-------------|
| GET | `/courses/{course_id}/modules` | 👨🏫🔑 | Temario completo (incluye `content` de cada lección) |
| POST | `/courses/{course_id}/modules` | 👨🏫🔑 | Crear módulo |
| PATCH | `/courses/{course_id}/modules/order` | 👨🏫🔑 | Reordenar módulos: `{ "ordered_ids": [...] }` reescribe `sort_order` 0..n-1 |
| PUT | `/courses/modules/{id}` | 👨🏫🔑 | Editar (título, descripción, orden, publicado) |
| DELETE | `/courses/modules/{id}` | 👨🏫🔑 | Eliminar (arrastra sus lecciones: `ON DELETE CASCADE` + `passive_deletes` en el modelo) |

---

## Lessons — dentro de `/api/v1/courses`

| Método | Ruta | Rol | Descripción |
|--------|------|-----|-------------|
| POST | `/courses/modules/{module_id}/lessons` | 👨🏫🔑 | Crear lección |
| PATCH | `/courses/modules/{module_id}/lessons/order` | 👨🏫🔑 | Reordenar lecciones del módulo (`{ "ordered_ids": [...] }`) |
| PUT | `/courses/lessons/{id}` | 👨🏫🔑 | Editar (incluye `content`, `is_published`) |
| DELETE | `/courses/lessons/{id}` | 👨🏫🔑 | Eliminar |
| POST | `/courses/lessons/{id}/recorded-class` | 👨🏫 | ⏳ Clases grabadas (sin storage de vídeo) |
| POST | `/courses/lessons/{id}/progress` | 🎓 | ⏳ El progreso lo escribe el docente, no el alumno (ver abajo) |

---

## Course Classes — `/api/v1/course-classes` y `/api/v1/courses/{id}/classes`

| Método | Ruta | Rol | Descripción |
|--------|------|-----|-------------|
| POST | `/courses/{course_id}/classes` | 🔑🤝 | Crear clase |
| GET | `/courses/{course_id}/classes` | 🌐 | Clases de un curso |
| PATCH | `/course-classes/{class_id}` | 🔑🤝 | Editar clase |
| PATCH | `/course-classes/{class_id}/assign-teacher` | 🔑🤝 | Asignar docente |
| PATCH | `/course-classes/{class_id}/meeting-link` | 👨🏫🔑 | Enlace de la clase en vivo |
| PATCH | `/course-classes/{class_id}/recording-link` | 👨🏫🔑 | Grabación de la clase (`recording_url`, `recording_platform`; vacío = retirarla) |
| GET | `/course-classes/{class_id}/students` | 👨🏫🔑 | Alumnos de la clase (con `progress_percentage`) |
| PATCH | `/course-classes/{class_id}/students/{student_id}/progress` | 👨🏫🔑 | Marcar el progreso del alumno (0-100) |
| GET | `/teachers/me/classes` | 👨🏫 | Mis clases |

Al guardar `progress_percentage = 100` el backend sella `completed_at`; si el
porcentaje baja otra vez, se limpia (no es un estado terminal).

La grabación la puede publicar el docente titular de la clase o administración; el
alumno inscrito la recibe en `GET /students/me/classes` (campo `recording_url`) y la
ve en `/student/courses`.

---

## Live Classes — `/api/v1/live-classes`

| Método | Ruta | Rol | Descripción |
|--------|------|-----|-------------|
| POST | `/` | 👨‍🏫🔑 | Crear clase en vivo |
| PUT | `/{id}` | 👨‍🏫🔑 | Editar |
| DELETE | `/{id}` | 👨‍🏫🔑 | Eliminar |
| GET | `/course/{course_id}` | 🔒 | Clases de un curso |
| GET | `/upcoming` | 🎓 | Próximas clases |
| PATCH | `/{id}/status` | 👨‍🏫 | Cambiar estado |

---

## Reviews — `/api/v1/reviews`

| Método | Ruta | Rol | Descripción |
|--------|------|-----|-------------|
| POST | `/` | 🎓 | Crear reseña |
| PUT | `/{id}` | 🎓 | Editar mi reseña |
| DELETE | `/{id}` | 🎓🔑 | Eliminar |
| GET | `/course/{course_id}` | 🌐 | Reseñas de curso |

---

## Suggestions — `/api/v1/suggestions`

| Método | Ruta | Rol | Descripción |
|--------|------|-----|-------------|
| POST | `/` | 🔒 | Enviar sugerencia |
| GET | `/` | 🔑 | Listar (admin) |
| PATCH | `/{id}/status` | 🔑 | Cambiar estado |

---

## Students — `/api/v1/students`

| Método | Ruta | Rol | Descripción |
|--------|------|-----|-------------|
| GET | `/me/classes` | 🎓 | Mis clases (con docente, horario y enlace) |
| GET | `/me/attendance` | 🎓 | Mi asistencia |
| GET | `/me/progress` | 🎓 | Mis inscripciones con estado del ciclo de pago + progreso (`payment_approved` = en espera de clase, `active` = con clase). Es la fuente de `/student/courses` |
| GET | `/progress/course/{id}` | 🎓 | ⏳ Progreso detallado de un curso |
| GET | `/profile` | 🎓 | ⏳ Mi perfil |
| PUT | `/profile` | 🎓 | ⏳ Editar perfil |
| GET | `/certificates` | 🎓 | ⏳ Mis certificados |
| GET | `/ratings` | 🎓 | ⏳ Mis calificaciones |
| GET | `/highlights` | 🎓 | ⏳ Mi estado destacado |

---

## Teachers — `/api/v1/teachers`

| Método | Ruta | Rol | Descripción |
|--------|------|-----|-------------|
| GET | `/me/courses` | 👨🏫 | Mis cursos (titular o con clase asignada) + conteos y progreso medio |
| GET | `/me/students` | 👨🏫 | Alumnos de mis clases, con su progreso |
| GET | `/me/classes` | 👨🏫 | Mis clases |
| GET | `` | 🔑 | Listar docentes |
| GET | `/eligible-users` | 🔑 | Usuarios candidatos a docente |
| POST | `/{user_id}` | 🔑 | Dar de alta como docente |
| DELETE | `/{user_id}` | 🔑 | Quitar el rol de docente |
| GET | `/courses/{id}/students` | 👨🏫 | ⏳ Alumnos de un curso (hoy: `/course-classes/{id}/students`) |
| POST | `/students/{id}/rate` | 👨🏫 | ⏳ Calificar alumno |
| POST | `/students/{id}/highlight` | 👨🏫 | ⏳ Marcar destacado |
| GET | `/stats` | 👨🏫 | ⏳ Mis estadísticas |

---

## Admin — `/api/v1/admin`

| Método | Ruta | Rol | Descripción |
|--------|------|-----|-------------|
| GET | `/metrics` | 🔑 | Dashboard métricas |
| GET | `/users` | 🔑 | Listar usuarios |
| PATCH | `/users/{id}/block` | 🔑 | Bloquear |
| PATCH | `/users/{id}/unblock` | 🔑 | Desbloquear |
| POST | `/teachers` | 🔑 | Crear docente |
| PUT | `/teachers/{id}` | 🔑 | Editar docente |
| POST | `/certificates/issue` | 🔑 | Emitir certificado |
| GET | `/certificates` | 🔑 | Certificados emitidos |
| POST | `/categories` | 🔑 | Crear categoría |
| PUT | `/categories/{id}` | 🔑 | Editar categoría |
| GET | `/students/highlights` | 🔑 | Alumnos destacados |
| GET | `/students/ready-for-evaluation` | 🔑 | Listos evaluación |

---

## Notifications — `/api/v1/notifications`

| Método | Ruta | Rol | Descripción |
|--------|------|-----|-------------|
| GET | `/` | 🔒 | Mis notificaciones |
| PATCH | `/{id}/read` | 🔒 | Marcar leída |
| PATCH | `/read-all` | 🔒 | Marcar todas |
| GET | `/unread-count` | 🔒 | Count no leídas |

---

## Audit — `/api/v1/audit`

| Método | Ruta | Rol | Descripción |
|--------|------|-----|-------------|
| GET | `/logs` | 🔑 | Logs auditoría `?action=&user_id=&from=&to=` |

---

## Health & Observability

| Método | Ruta | Rol | Descripción |
|--------|------|-----|-------------|
| GET | `/health` | 🌐 | Liveness |
| GET | `/health/ready` | 🌐 | Readiness (DB+Redis+Storage) |
| GET | `/metrics` | 🌐* | Prometheus (*IP restricted) |

---

## Feature Flags — `/api/v1/admin/feature-flags`

| Método | Ruta | Rol | Descripción |
|--------|------|-----|-------------|
| GET | `/` | 🔑 | Listar flags |
| POST | `/` | 🔑 | Crear flag |
| PUT | `/{id}` | 🔑 | Editar |
| PATCH | `/{key}/toggle` | 🔑 | Toggle on/off |
| DELETE | `/{id}` | 🔑 | Eliminar |

---

## Content Versions — `/api/v1/content-versions`

| Método | Ruta | Rol | Descripción |
|--------|------|-----|-------------|
| GET | `/{entity_type}/{entity_id}` | 👨‍🏫🔑 | Historial versiones |
| GET | `/{entity_type}/{entity_id}/{ver}` | 👨‍🏫🔑 | Detalle versión |
| POST | `/{entity_type}/{entity_id}/restore/{ver}` | 🔑 | Restaurar versión |
