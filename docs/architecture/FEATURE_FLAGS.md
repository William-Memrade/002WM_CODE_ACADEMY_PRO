# 🚩 Feature Flags — CodeAcademy Pro

## Diseño

- Tabla `feature_flags` en BD
- Cache Redis con TTL 60s
- CRUD admin sin deploy

## Flags Iniciales

| Key | Default | Descripción |
|-----|---------|-------------|
| `manual_payments` | true | Pagos por transferencia bancaria |
| `live_classes` | true | Clases en vivo habilitadas |
| `certificates` | true | Emisión de certificados |
| `student_highlights` | true | Sistema de alumnos destacados |
| `email_notifications` | true | Emails transaccionales |
| `content_versioning` | true | Versionado de contenido |
| `online_payments` | false | Pagos online (futuro) |
| `ai_tutor` | false | IA tutor (futuro) |
| `job_board` | false | Bolsa de empleo (futuro) |

## Uso en Código
```python
if await feature_flags.is_enabled("live_classes"):
    # Mostrar sección de clases en vivo
```

## Granularidad Futura
Preparado para: por usuario, por rol, porcentaje (A/B testing). No implementado inicialmente.
