# 🔌 API Endpoints — CodeAcademy Pro

## Convenciones

- **Base URL**: `/api/v1`
- **Formato**: JSON
- **Auth**: Bearer JWT en `Authorization`
- **Paginación**: `?page=1&per_page=20`
- **Roles**: 🌐 Público | 🎓 Alumno | 👨‍🏫 Docente | 🔑 Admin | 🔒 Autenticado

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

## Modules — `/api/v1/modules`

| Método | Ruta | Rol | Descripción |
|--------|------|-----|-------------|
| POST | `/` | 👨‍🏫🔑 | Crear módulo |
| PUT | `/{id}` | 👨‍🏫🔑 | Editar |
| DELETE | `/{id}` | 👨‍🏫🔑 | Eliminar |
| GET | `/course/{course_id}` | 🔒 | Módulos de un curso |

---

## Lessons — `/api/v1/lessons`

| Método | Ruta | Rol | Descripción |
|--------|------|-----|-------------|
| POST | `/` | 👨‍🏫🔑 | Crear lección |
| PUT | `/{id}` | 👨‍🏫🔑 | Editar |
| DELETE | `/{id}` | 👨‍🏫🔑 | Eliminar |
| GET | `/module/{module_id}` | 🔒 | Lecciones de módulo |
| POST | `/{id}/recorded-class` | 👨‍🏫 | Agregar clase grabada |
| POST | `/{id}/progress` | 🎓 | Actualizar progreso |

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
| GET | `/progress` | 🎓 | Mi progreso general |
| GET | `/progress/course/{id}` | 🎓 | Progreso en curso |
| GET | `/profile` | 🎓 | Mi perfil |
| PUT | `/profile` | 🎓 | Editar perfil |
| GET | `/certificates` | 🎓 | Mis certificados |
| GET | `/ratings` | 🎓 | Mis calificaciones |
| GET | `/highlights` | 🎓 | Mi estado destacado |

---

## Teachers — `/api/v1/teachers`

| Método | Ruta | Rol | Descripción |
|--------|------|-----|-------------|
| GET | `/courses` | 👨‍🏫 | Mis cursos |
| GET | `/courses/{id}/students` | 👨‍🏫 | Alumnos de mi curso |
| GET | `/courses/{id}/students/{sid}/progress` | 👨‍🏫 | Progreso alumno |
| POST | `/students/{id}/rate` | 👨‍🏫 | Calificar alumno |
| POST | `/students/{id}/highlight` | 👨‍🏫 | Marcar destacado |
| GET | `/stats` | 👨‍🏫 | Mis estadísticas |

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
