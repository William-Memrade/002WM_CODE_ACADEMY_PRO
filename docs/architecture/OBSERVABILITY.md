# 👁️ Observabilidad — CodeAcademy Pro

## Logging Estructurado

### Librería: `structlog`

Logs en formato JSON para fácil parsing por log aggregators.

```python
import structlog

logger = structlog.get_logger()

# Ejemplo
logger.info("payment_approved",
    payment_id=str(payment_id),
    student_id=str(student_id),
    amount=99.99,
    approved_by=str(admin_id)
)

# Output JSON:
# {"event": "payment_approved", "payment_id": "uuid", "amount": 99.99, ...}
```

### Correlation IDs
- Cada request genera un `X-Request-ID` único
- Se propaga en todos los logs del request
- Se incluye en headers de respuesta
- Permite trazar un request completo

### Niveles
| Nivel | Uso |
|-------|-----|
| DEBUG | Desarrollo, queries DB |
| INFO | Acciones de negocio (login, pago, inscripción) |
| WARNING | Rate limits, validaciones fallidas |
| ERROR | Errores recuperables (email fail, storage timeout) |
| CRITICAL | Errores irrecuperables (DB down, config inválida) |

---

## Health Checks

### `GET /health` (Liveness)
```json
{ "status": "ok", "timestamp": "2026-01-01T00:00:00Z" }
```

### `GET /health/ready` (Readiness)
```json
{
  "status": "ok",
  "checks": {
    "database": { "status": "ok", "latency_ms": 5 },
    "redis": { "status": "ok", "latency_ms": 2 },
    "storage": { "status": "ok" }
  }
}
```
Si cualquier check falla → HTTP 503.

---

## Métricas Prometheus

### Librería: `prometheus-fastapi-instrumentator`

Métricas automáticas: request duration, count, status codes.

### Métricas custom
- `academy_active_users` (gauge)
- `academy_pending_payments` (gauge)
- `academy_enrollments_total` (counter)
- `academy_payments_approved_total` (counter)
- `academy_background_jobs_processed` (counter)
- `academy_email_sent_total` (counter)

### Endpoint: `GET /metrics`
Acceso restringido por IP o token interno.

---

## Tracing (Futuro)
- Preparado para OpenTelemetry
- `X-Request-ID` como trace ID
- Instrumentación de SQLAlchemy + Redis + HTTP calls
