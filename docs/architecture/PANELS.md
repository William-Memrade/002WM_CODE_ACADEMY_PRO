# 📊 Paneles — CodeAcademy Pro

## Panel Admin

### Dashboard
| Widget | Datos | Fuente |
|--------|-------|--------|
| Total Alumnos | Count users con rol student | `users` + `user_roles` |
| Total Docentes | Count users con rol teacher | `users` + `user_roles` |
| Total Cursos | Count cursos activos | `courses` |
| Total Ingresos | Sum pagos aprobados | `payments` |
| Pagos Pendientes | Count pagos pending_review | `payments` |
| Cursos Activos | Count cursos is_active | `courses` |
| Cursos Populares | Top 5 por inscripciones | `enrollments` JOIN `courses` |
| Actividad Reciente | Últimos audit logs | `audit_logs` |

### Módulos
- **Gestión Cursos**: CRUD + activar/desactivar, asignar docente
- **Gestión Docentes**: Crear, editar, desactivar
- **Gestión Alumnos**: Listar, bloquear, ver progreso
- **Gestión Pagos**: Pendientes, aprobar, rechazar con vista de comprobante
- **Gestión Certificados**: Emitir, listar emitidos
- **Gestión Categorías**: CRUD
- **Feedback**: Reseñas + sugerencias
- **Alumnos Top**: Destacados + listos para evaluación
- **Auditoría**: Logs filtrados por acción, usuario, fecha
- **Feature Flags**: Activar/desactivar features sin deploy
- **Configuración**: System settings

---

## Panel Docente

### Dashboard
| Widget | Datos |
|--------|-------|
| Cursos Asignados | Count cursos del docente |
| Total Alumnos | Count alumnos en sus cursos |
| Calificación Promedio | Avg de reviews de sus cursos |
| Reseñas Recientes | Últimas 5 reviews |

### Módulos
- **Mis Cursos**: ✅ `/teacher/courses` — cursos que imparte (titular o con clase asignada) con conteos reales (módulos, lecciones, clases, alumnos) y progreso medio
- **Gestión Temario**: ✅ `/teacher/courses/{id}/curriculum` — alta, edición y borrado de módulos y lecciones; el backend exige ser docente del curso (`ensure_course_manager`)
- **Alumnos**: ✅ `/teacher/students` — inscritos en sus clases, con edición del progreso (0-100 %); sin clase asignada el progreso se ve pero no se edita
- **Clases en Vivo**: ✅ `/teacher/classes` — CRUD con link de reunión y asistencia
- **Subir Videos**: ⏳ pendiente (no hay almacenamiento de vídeo)
- **Historial Cambios**: ⏳ backend sí (content versioning), sin UI
- ⏳ Calificar alumnos, estrellas y destacados (tablas `student_ratings`/`reviews` creadas, sin endpoints)

---

## Panel Alumno

### Dashboard
| Widget | Datos |
|--------|-------|
| Cursos Inscritos | Mis enrollments activos |
| Progreso General | Avg de progress_percentage |
| Próximas Clases | Live classes siguientes |
| Notificaciones | No leídas |
| Certificados | Count certificados |

### Módulos
- **Catálogo**: Buscar, filtrar, ver detalle de cursos
- **Mis Cursos**: ✅ `/student/courses` — inscripciones activas con la barra de progreso que escribe su docente
- ⏳ **Aula Virtual** (lecciones, vídeos, progreso por lección)
- ✅ **Pagos**: Subir comprobante, estado, historial
- ⏳ **Perfil**: Editar datos, avatar, ver estrellas, estado destacado
- ⏳ **Certificados**: Descargar PDF (la página existe, pero está vacía)
- ⏳ **Feedback**: Escribir reseñas, enviar sugerencias

---

## Navegación Frontend (Next.js App Router)

```
/ (landing público)
/courses (catálogo público)
/courses/{slug} (detalle público)
/login
/register

/student/dashboard
/student/courses
/student/courses/{id}
/student/payments
/student/profile
/student/certificates
/student/notifications

/teacher/dashboard
/teacher/courses
/teacher/courses/{id}/curriculum (temario: módulos y lecciones)
/teacher/students
/teacher/classes
/teacher/classes/{id}/attendance

/admin/dashboard
/admin/courses
/admin/teachers
/admin/students
/admin/payments
/admin/certificates
/admin/categories
/admin/feedback
/admin/audit
/admin/feature-flags
/admin/settings
```
