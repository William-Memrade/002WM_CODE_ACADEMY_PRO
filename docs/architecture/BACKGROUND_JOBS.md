# ⚡ Background Jobs — CodeAcademy Pro

## Motor: ARQ (Async Redis Queue)

Lightweight, Python async nativo, sin overhead de Celery. Migración a Celery posible en el futuro.

## Tareas

| Tarea | Trigger | Prioridad |
|-------|---------|-----------|
| `send_email` | Acción de negocio | Alta |
| `generate_certificate_pdf` | Admin emite certificado | Media |
| `recalculate_metrics` | Cron cada 5 min | Baja |
| `cleanup_expired_tokens` | Cron cada 1h | Baja |
| `cleanup_old_versions` | Cron diario | Baja |
| `process_payment_reminder` | Cron cada 6h | Media |
| `send_live_class_reminder` | Cron cada 15 min | Alta |

## Reintentos
- Backoff exponencial: 30s, 60s, 120s, 300s
- Máximo 3 intentos (configurable)
- Tareas fallidas → tabla `background_jobs` con status `failed`

## Dead Letter Queue
Jobs que agotan reintentos se registran en BD para inspección manual por admin.

## Worker en Docker
Mismo codebase, mismo Dockerfile, diferente comando: `arq app.services.background_jobs.WorkerSettings`
