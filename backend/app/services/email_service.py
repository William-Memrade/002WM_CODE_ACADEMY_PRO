"""
CodeAcademy Pro — Email Service
Transactional email sending via SMTP with Jinja2 templates.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import structlog

from app.core.config import get_settings

settings = get_settings()
logger = structlog.get_logger()

# ── Email Templates (inline for MVP, extract to files later) ─────────────────

TEMPLATES = {
    "user_assignment": {
        "subject": "Asignacion de Usuario {app_name}",
        "body": (
            "Bienvenido/a {first_name} es un placer que formes parte del equipo de {app_name}, "
            "tu usuario y contraseña temporal es el siguiente "
            "usuario {email} contraseña {temp_password}\n\n"
            "Esta contraseña te permitira el acceso, pero al iniciar sesion sera obligatorio "
            "que la cambies por una nueva contraseña."
        ),
    },
    "welcome": {
        "subject": "¡Bienvenido a {app_name}!",
        "body": "Hola {first_name},\n\nTu cuenta ha sido creada exitosamente.\n\n¡Bienvenido a {app_name}!",
    },
    "verify_email": {
        "subject": "Verifica tu email - {app_name}",
        "body": "Hola {first_name},\n\nVerifica tu email haciendo clic en:\n{verify_url}\n\nEste link expira en 24 horas.",
    },
    "payment_approved": {
        "subject": "Pago aprobado - {course_title}",
        "body": "Hola {first_name},\n\nTu pago para el curso '{course_title}' ha sido aprobado.\n\n¡Ya puedes acceder al contenido!",
    },
    "payment_rejected": {
        "subject": "Pago rechazado - {course_title}",
        "body": "Hola {first_name},\n\nTu pago para el curso '{course_title}' fue rechazado.\n\nMotivo: {reason}\n\nPuedes subir un nuevo comprobante.",
    },
    "certificate_issued": {
        "subject": "Certificado emitido - {course_title}",
        "body": "Hola {first_name},\n\n¡Felicidades! Tu certificado para '{course_title}' está listo.\n\nDescárgalo en tu panel.",
    },
    "live_class_reminder": {
        "subject": "Clase en vivo en 1 hora - {class_title}",
        "body": "Hola {first_name},\n\nRecordatorio: la clase '{class_title}' comienza en 1 hora.\n\nLink: {meeting_url}",
    },
    "admin_alert_course_needs_class": {
        "subject": "Curso '{course_title}' necesita una clase",
        "body": (
            "Hola {first_name},\n\n"
            "El curso '{course_title}' ha alcanzado 5 inscripciones activas y no tiene "
            "ninguna clase activa.\n\n"
            "Por favor, creá una clase y asigná a los estudiantes lo antes posible.\n\n"
            "ID del curso: {course_id}"
        ),
    },
}


async def send_email(
    to_email: str,
    template: str,
    template_data: dict | None = None,
) -> bool:
    """
    Send a transactional email using SMTP.

    Args:
        to_email: Recipient email address
        template: Template name (key in TEMPLATES)
        template_data: Data to interpolate into template

    Returns:
        True if sent successfully, False otherwise
    """
    data = template_data or {}
    data.setdefault("app_name", settings.APP_NAME)

    tmpl = TEMPLATES.get(template)
    if not tmpl:
        logger.error("email_template_not_found", template=template)
        return False

    try:
        subject = tmpl["subject"].format(**data)
        body = tmpl["body"].format(**data)
    except KeyError as e:
        logger.error("email_template_render_error", template=template, missing_key=str(e))
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        if settings.SMTP_USE_TLS:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
            server.starttls()
        else:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)

        if settings.SMTP_USER:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

        server.sendmail(settings.SMTP_FROM_EMAIL, to_email, msg.as_string())
        server.quit()

        logger.info("email_sent", to=to_email, template=template)
        return True

    except Exception as e:
        logger.error("email_send_error", to=to_email, template=template, error=str(e))
        return False
