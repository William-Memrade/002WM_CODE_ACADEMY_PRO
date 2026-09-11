# 📧 Emails — CodeAcademy Pro

## Emails Transaccionales

| Template | Trigger | Datos |
|----------|---------|-------|
| `welcome` | Registro | nombre, verify_url |
| `verify_email` | Registro | verify_url |
| `password_reset` | Forgot password | reset_url |
| `payment_approved` | Admin aprueba | curso, monto |
| `payment_rejected` | Admin rechaza | curso, motivo |
| `enrollment_confirmed` | Pago aprobado | curso, fechas |
| `live_class_reminder` | 1h antes | curso, link, hora |
| `certificate_issued` | Admin emite | curso, download_url |

## Motor
- SMTP genérico configurable
- Proveedores soportados: SendGrid, Amazon SES, Resend, cualquier SMTP
- Templates: Jinja2 (HTML + texto plano)
- Cola: Todos pasan por background job ARQ

## Dev Local
- Mailhog en Docker (puerto 8025)
- UI web para ver emails enviados sin salir a internet

## Tabla `email_queue`
Estados: `pending` → `sent` | `failed`
Máximo 3 reintentos con backoff exponencial.
