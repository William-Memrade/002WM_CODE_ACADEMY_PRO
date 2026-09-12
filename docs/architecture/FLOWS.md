# 🔄 Flujos de Negocio — CodeAcademy Pro

## 1. Flujo de Inscripción + Pago Manual

> **Implementación actual (2026-09-11).** El diagrama describe el diseño previsto; lo que
> hace el código hoy es:
>
> 1. El alumno **no** publica `/enrollments`: sube el comprobante con
>    `POST /payments/submit-proof` (curso + plan + archivo) y nace un `payments` en
>    `pending`/`pending_review`. Todavía **no hay inscripción**, así que el curso no
>    aparece en «Mis Cursos»: sólo el pago, como *pendiente de confirmación*.
> 2. Al aprobar (`POST /payments/{id}/approve`) se crea la inscripción **siempre**:
>    - con clase y cupo → `enrollments.status = active` y `course_class_id` asignado;
>    - sin clase con cupo → `enrollments.status = payment_approved` con `course_class_id`
>      NULL y el pago en `approved_pending_class`. El alumno ya ve el curso con el aviso
>      *en espera de asignación de clase*.
> 3. `POST /payments/{id}/assign-class` **reutiliza esa misma fila** (la activa) en vez de
>    crear otra: `uq_enrollments (student_id, course_id)` admite una sola por alumno y curso.
> 4. Rechazar (`POST /payments/{id}/reject`) sólo marca `payment_rejected` la inscripción
>    **sin clase**; una inscripción `active` (el alumno ya está cursando) no se degrada al
>    rechazar un pago nuevo del mismo curso.
>
> Recordatorio: la ficha del curso sólo es visible para el alumno si el curso está
> `is_active` (política `courses_select`), así que un curso en borrador con pago aprobado
> todavía no se puede abrir aunque la inscripción exista.

```mermaid
sequenceDiagram
    participant A as Alumno
    participant FE as Frontend
    participant API as Backend API
    participant DB as Database
    participant S3 as Storage
    participant N as Notificaciones
    participant AD as Admin

    A->>FE: Selecciona curso
    FE->>API: POST /enrollments {course_id}
    API->>DB: Crear enrollment (pending_payment)
    API->>DB: Crear payment (pending)
    API->>N: Notificar alumno (datos bancarios)
    API-->>FE: enrollment_id + payment_info

    Note over A: Alumno realiza transferencia bancaria

    A->>FE: Sube comprobante
    FE->>API: POST /payments/{id}/upload-proof (file)
    API->>API: Validar archivo (MIME, tamaño)
    API->>S3: Guardar comprobante
    API->>DB: Crear payment_proof
    API->>DB: Payment → pending_review
    API->>DB: Enrollment → payment_pending_review
    API->>N: Notificar admin (pago pendiente)
    API-->>FE: OK

    AD->>FE: Revisa comprobante
    FE->>API: GET /payments/pending

    alt Aprueba
        AD->>API: POST /payments/{id}/approve
        API->>DB: Payment → approved
        API->>DB: Enrollment → active
        API->>N: Notificar alumno (aprobado)
        API->>DB: Audit log (payment_approved)
    else Rechaza
        AD->>API: POST /payments/{id}/reject
        API->>DB: Payment → rejected
        API->>DB: Enrollment → payment_rejected
        API->>N: Notificar alumno (rechazado)
        API->>DB: Audit log (payment_rejected)
        Note over A: Puede subir nuevo comprobante
    end
```

### Estados de Inscripción
```
(subir comprobante) → payment_pending_review
      ↓ aprobar sin clase con cupo        ↓ aprobar con clase y cupo
   payment_approved ──assign-class──→ active → completed
                                        ↘ cancelled (desde activo o en espera)
      ↓ rechazar (sólo si no hay clase)
   payment_rejected ──nuevo comprobante──→ payment_pending_review
```

---

## 2. Flujo de Clases en Vivo

```mermaid
sequenceDiagram
    participant D as Docente
    participant API as Backend
    participant DB as Database
    participant N as Notificaciones
    participant A as Alumnos

    D->>API: POST /live-classes {course_id, meeting_url, scheduled_at}
    API->>DB: Crear live_class (scheduled)
    API->>N: Notificar alumnos inscritos (clase programada)

    Note over API: Background job: recordatorio 1h antes

    API->>N: Recordatorio alumnos (1h antes)

    D->>API: PATCH /live-classes/{id}/status {status: "live"}
    API->>DB: live_class → live
    API->>N: Notificar alumnos (clase en curso)

    A->>API: GET /live-classes/{id}
    API-->>A: meeting_url (solo si enrollment active)

    D->>API: PATCH /live-classes/{id}/status {status: "completed"}
    API->>DB: live_class → completed

    opt Grabación disponible
        D->>API: PUT /live-classes/{id} {recording_url}
        API->>DB: Actualizar recording_url
        API->>N: Notificar alumnos (grabación disponible)
    end
```

---

## 3. Flujo de Clases Grabadas

```mermaid
sequenceDiagram
    participant D as Docente
    participant API as Backend
    participant S3 as Storage
    participant DB as Database
    participant A as Alumno

    D->>API: POST /lessons/{id}/recorded-class (video file)
    API->>API: Validar archivo (MIME, tamaño)
    API->>S3: Upload video
    API->>DB: Crear recorded_class
    API-->>D: OK

    A->>API: GET /lessons/{lesson_id}
    API->>API: Verificar enrollment activo
    API->>S3: Generar signed URL (1h expiry)
    API-->>A: lesson + video_signed_url

    A->>API: POST /lessons/{id}/progress {time_spent, position}
    API->>DB: Upsert student_progress
    API->>DB: Recalcular enrollment.progress_percentage
```

### Acceso a Videos
- Solo alumnos con enrollment `active`
- URLs pre-firmadas con expiración de 1 hora
- No se expone la URL directa del storage
- Tracking de progreso por cada lección

---

## 4. Flujo de Progreso del Alumno

```mermaid
sequenceDiagram
    participant A as Alumno
    participant API as Backend
    participant DB as Database

    A->>API: POST /lessons/{id}/progress
    Note right of API: {status: "completed", time_spent: 1800, position: 0}
    API->>DB: Upsert student_progress
    API->>DB: Contar lecciones completadas del curso
    API->>DB: Total lecciones del curso
    API->>DB: progress = (completadas / total) * 100
    API->>DB: UPDATE enrollment SET progress_percentage

    alt Progreso = 100%
        API->>DB: enrollment → completed
        API->>DB: Notificar admin (alumno completó curso)
        Note over API: Candidato para certificado
    end
```

### Cálculo de Progreso
```
progress_percentage = (lecciones_completed / total_lecciones_curso) * 100
```

- Se recalcula en cada actualización de progreso
- Se almacena en `enrollments.progress_percentage` (desnormalización)
- Dashboard muestra barra de progreso desde este campo

> **Estado real (2026-09-11):** la fórmula de arriba **no** está implementada. Hoy
> el progreso es un porcentaje que el docente de la clase escribe a mano
> (`PATCH /course-classes/{class_id}/students/{student_id}/progress`, 0-100) y el
> alumno lo lee (`GET /students/me/progress`). No existe `student_progress` ni
> seguimiento por lección, así que no hay nada que recalcular; al llegar a 100 se
> sella `enrollments.completed_at` (y se limpia si el porcentaje baja). La
> automatización está pendiente en el Sprint 3 del `ROADMAP.md`.

---

## 5. Sistema de Reputación de Alumnos

### Componentes

| Componente | Quién otorga | Descripción |
|------------|-------------|-------------|
| **Estrellas** (0-5) | Docente | Calificación por curso |
| **Score** (0-100) | Docente | Nota numérica |
| **Destacado** | Docente | Alumno sobresale en un curso |
| **Listo para evaluación** | Docente | Preparado para evaluación externa |

### Flujo de calificación
```
Docente → POST /teachers/students/{id}/rate
  → { course_id, score: 95, stars: 5, feedback: "Excelente trabajo" }
  → DB: Upsert student_ratings
  → Notificar alumno

Docente → POST /teachers/students/{id}/highlight
  → { course_id, type: "outstanding", notes: "..." }
  → DB: Insert student_highlights
  → Notificar alumno + admin
```

### Perfil de reputación del alumno
```json
{
  "total_stars": 23,
  "avg_score": 92.5,
  "courses_completed": 5,
  "certificates": 4,
  "is_outstanding_in": ["Python Avanzado", "React"],
  "ready_for_evaluation_in": ["Python Avanzado"]
}
```

---

## 6. Flujo de Certificados

```mermaid
sequenceDiagram
    participant AD as Admin
    participant API as Backend
    participant DB as Database
    participant JOB as Background Job
    participant S3 as Storage
    participant A as Alumno

    AD->>API: POST /admin/certificates/issue
    Note right of AD: {student_id, course_id}
    API->>API: Verificar enrollment completed
    API->>DB: Crear certificate (code único)
    API->>JOB: Generar PDF certificado
    JOB->>S3: Upload PDF
    JOB->>DB: Update certificate.file_url
    API->>DB: Notificar alumno
    API->>DB: Audit log (certificate_issued)

    A->>API: GET /students/certificates
    API-->>A: Lista de certificados con URLs
```

---

## 7. Flujo de Notificaciones

### Tipos de notificación
| Tipo | Trigger | Destinatario |
|------|---------|-------------|
| `payment_pending` | Alumno sube comprobante | Admin |
| `payment_approved` | Admin aprueba pago | Alumno |
| `payment_rejected` | Admin rechaza pago | Alumno |
| `enrollment_confirmed` | Pago aprobado | Alumno |
| `live_class_scheduled` | Docente crea clase | Alumnos del curso |
| `live_class_reminder` | 1h antes de clase | Alumnos del curso |
| `live_class_started` | Docente inicia clase | Alumnos del curso |
| `certificate_issued` | Admin emite certificado | Alumno |
| `student_highlighted` | Docente marca destacado | Alumno |
| `new_review` | Alumno deja reseña | Docente |

### Canales
1. **In-app** (siempre): Tabla `notifications`, visible en frontend
2. **Email** (configurable): Via `email_queue` + background job
