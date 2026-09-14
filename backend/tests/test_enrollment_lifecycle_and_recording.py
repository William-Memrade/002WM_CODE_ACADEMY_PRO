"""
Ciclo de vida de la inscripción y grabación de clase (end-to-end por HTTP).

Cubre el recorrido que el alumno y el admin ven en la interfaz:

  1. El alumno sube el comprobante          → pago 'pending_review'
  2. El admin confirma el pago              → pago 'approved'; si no hay clase con cupo
                                              queda 'approved_pending_class' y la
                                              inscripción nace en 'payment_approved'
                                              (el alumno YA ve el curso, en espera de clase)
  3. El admin crea la clase y la asigna     → la MISMA inscripción pasa a 'active'
                                              (nunca dos filas por alumno y curso)
  4. El docente publica el enlace de la clase y la grabación → el alumno los ve

Los datos base son el seed; lo que no tiene endpoint público (el pago pendiente) se
inserta con `superuser_session`, pero todo lo demás se ejercita por HTTP con el rol RLS
real de cada actor.

Marcador `integration`: requiere Postgres y Redis levantados (ver conftest.py).
"""

import uuid

import pytest
import pytest_asyncio
from sqlalchemy import text

from tests import support

pytestmark = pytest.mark.integration


# ── Montaje ──────────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def pending_payment(api_client, tokens, superuser_session):
    """
    Curso recién creado (sin ninguna clase) + pago pendiente del alumno demo.

    Es exactamente el escenario que dejaba al alumno sin ver el curso: se inscribe en un
    curso que todavía no tiene clase con cupo.
    """
    student_id = (
        await superuser_session.execute(
            text("SELECT id FROM users WHERE email = :email"),
            {"email": support.DEMO_USERS["student"][0]},
        )
    ).scalar_one()

    admin_headers = support.auth_headers(tokens["admin"])
    created = await api_client.post(
        "/api/v1/courses",
        json={
            "title": f"Curso sin clases {uuid.uuid4().hex[:8]}",
            "description": "Curso creado por las pruebas del ciclo de inscripción.",
            "price": "49.99",
        },
        headers=admin_headers,
    )
    assert created.status_code == 201, created.text
    course_id = created.json()["id"]

    # El curso nace inactivo (borrador): sin activarlo, RLS (`courses_select` exige
    # is_active) lo esconde al alumno y no vería la inscripción. Activarlo es lo que hace
    # el admin al publicarlo.
    activated = await api_client.patch(
        f"/api/v1/courses/{course_id}/activate", headers=admin_headers
    )
    assert activated.status_code == 200, activated.text

    payment_id = (
        await superuser_session.execute(
            text(
                """
                INSERT INTO payments (student_id, course_id, amount, currency,
                                      payment_method, status)
                VALUES (:student_id, :course_id, 49.99, 'USD', 'bank_transfer', 'pending')
                RETURNING id
                """
            ),
            {"student_id": student_id, "course_id": course_id},
        )
    ).scalar_one()
    await superuser_session.commit()

    try:
        yield {
            "course_id": course_id,
            "payment_id": str(payment_id),
            "student_id": str(student_id),
            "admin_token": tokens["admin"],
            "admin_headers": admin_headers,
            "student_headers": support.auth_headers(tokens["student"]),
            "teacher_headers": support.auth_headers(tokens["teacher"]),
        }
    finally:
        # El orden importa: payments.enrollment_id apunta a enrollments y las FK de
        # courses son RESTRICT, así que se borra de dentro hacia fuera.
        for statement in (
            "DELETE FROM payment_proofs WHERE payment_id IN (SELECT id FROM payments WHERE course_id = :cid)",
            "DELETE FROM payments WHERE course_id = :cid",
            "DELETE FROM enrollments WHERE course_id = :cid",
            "DELETE FROM course_classes WHERE course_id = :cid",
            "DELETE FROM modules WHERE course_id = :cid",
            "DELETE FROM courses WHERE id = :cid",
        ):
            await superuser_session.execute(text(statement), {"cid": course_id})
        await superuser_session.commit()


async def _create_class(api_client, payment_course) -> dict:
    """Crea la clase del curso por HTTP (POST /courses/{id}/classes) como admin."""
    response = await api_client.post(
        f"/api/v1/courses/{payment_course['course_id']}/classes",
        json={
            "name": f"Grupo pruebas {uuid.uuid4().hex[:6]}",
            "days_of_week": ["mon", "wed"],
            "start_time": "18:00:00",
            "end_time": "20:00:00",
        },
        headers=payment_course["admin_headers"],
    )
    assert response.status_code in (200, 201), response.text
    return response.json()


async def _assign_teacher(api_client, payment_course, class_id: str, teacher_id: str) -> None:
    """Asigna el docente de la clase (PATCH /course-classes/{id}/assign-teacher)."""
    response = await api_client.patch(
        f"/api/v1/course-classes/{class_id}/assign-teacher",
        json={"teacher_id": teacher_id},
        headers=payment_course["admin_headers"],
    )
    assert response.status_code == 200, response.text


async def _teacher_id_of(subject: str, superuser_session) -> str:
    return str(
        (
            await superuser_session.execute(
                text(
                    """
                    SELECT t.id FROM teachers t
                    JOIN users u ON u.id = t.user_id
                    WHERE u.email = :email
                    """
                ),
                {"email": subject},
            )
        ).scalar_one()
    )


async def _enrollment_rows(superuser_session, course_id: str) -> list[dict]:
    rows = await superuser_session.execute(
        text(
            """
            SELECT status, course_class_id FROM enrollments
            WHERE course_id = :cid ORDER BY created_at
            """
        ),
        {"cid": course_id},
    )
    return [dict(row._mapping) for row in rows]


async def _insert_pending_payment(superuser_session, student_id: str, course_id: str) -> str:
    """Un pago pendiente más para el mismo alumno y curso (segundo envío, mensualidad…)."""
    payment_id = (
        await superuser_session.execute(
            text(
                """
                INSERT INTO payments (student_id, course_id, amount, currency,
                                      payment_method, status)
                VALUES (:student_id, :course_id, 49.99, 'USD', 'bank_transfer', 'pending')
                RETURNING id
                """
            ),
            {"student_id": student_id, "course_id": course_id},
        )
    ).scalar_one()
    await superuser_session.commit()
    return str(payment_id)


def _item_for(items: list[dict], course_id: str) -> dict:
    """La inscripción de ese curso en la lista del alumno (falla con mensaje legible)."""
    matches = [item for item in items if item["course_id"] == course_id]
    assert matches, f"el alumno no ve ninguna inscripción del curso {course_id}: {items}"
    return matches[0]


# ── Pruebas ──────────────────────────────────────────────────────────────────

async def test_aprobar_un_pago_sin_clases_deja_la_inscripcion_en_espera_de_asignacion(
    api_client, pending_payment, superuser_session
):
    """
    Confirmar el pago de un curso sin clases no puede fallar ni dejar al alumno a ciegas.

    Antes: `payments.status` no admitía 'approved_pending_class' (CHECK de 001) y, sin
    clase con cupo, tampoco se creaba la fila de `enrollments`: el admin veía un error y
    el alumno no veía nada.
    """
    response = await api_client.post(
        f"/api/v1/payments/{pending_payment['payment_id']}/approve",
        json={},
        headers=pending_payment["admin_headers"],
    )
    assert response.status_code == 200, response.text
    approved = response.json()
    assert approved["status"] == "approved_pending_class"
    assert approved["enrollment_id"], "el pago confirmado debe apuntar a su inscripción"

    rows = await _enrollment_rows(superuser_session, pending_payment["course_id"])
    assert len(rows) == 1
    assert rows[0]["status"] == "payment_approved"
    assert rows[0]["course_class_id"] is None

    # El alumno ya ve el curso, y con el estado que dispara el aviso "en espera de
    # asignación de clase".
    mine = await api_client.get("/api/v1/students/me/progress", headers=pending_payment["student_headers"])
    assert mine.status_code == 200, mine.text
    item = _item_for(mine.json()["items"], pending_payment["course_id"])
    assert item["status"] == "payment_approved"
    assert item["course_class_id"] is None
    assert item["course_title"]

    # Todavía sin clases asignadas.
    classes = await api_client.get(
        "/api/v1/students/me/classes", headers=pending_payment["student_headers"]
    )
    assert classes.status_code == 200
    assert all(c["course_id"] != pending_payment["course_id"] for c in classes.json()["items"])


async def test_asignar_clase_activa_la_misma_inscripcion_sin_duplicarla(
    api_client, pending_payment, superuser_session
):
    """Del pago aprobado sin clase a la clase asignada: una sola fila de inscripción."""
    await api_client.post(
        f"/api/v1/payments/{pending_payment['payment_id']}/approve",
        json={},
        headers=pending_payment["admin_headers"],
    )

    course_class = await _create_class(api_client, pending_payment)
    assigned = await api_client.post(
        f"/api/v1/payments/{pending_payment['payment_id']}/assign-class",
        json={"course_class_id": course_class["id"]},
        headers=pending_payment["admin_headers"],
    )
    assert assigned.status_code == 200, assigned.text
    assert assigned.json()["status"] == "approved"

    rows = await _enrollment_rows(superuser_session, pending_payment["course_id"])
    assert len(rows) == 1, "no debe duplicarse la inscripción al asignar la clase"
    assert rows[0]["status"] == "active"
    assert str(rows[0]["course_class_id"]) == course_class["id"]

    # Y el alumno lo ve activo, con su clase.
    mine = await api_client.get("/api/v1/students/me/progress", headers=pending_payment["student_headers"])
    item = _item_for(mine.json()["items"], pending_payment["course_id"])
    assert item["status"] == "active"
    assert item["course_class_id"] == course_class["id"]

    classes = await api_client.get(
        "/api/v1/students/me/classes", headers=pending_payment["student_headers"]
    )
    assert any(c["course_id"] == pending_payment["course_id"] for c in classes.json()["items"])


async def test_el_docente_publica_el_enlace_y_la_grabacion_y_el_alumno_los_ve(
    api_client, pending_payment, superuser_session
):
    """
    Con la clase ya asignada, el docente publica enlace en vivo y grabación; el alumno de
    esa clase los ve. Un tercero (el propio alumno) no puede publicar.
    """
    await api_client.post(
        f"/api/v1/payments/{pending_payment['payment_id']}/approve",
        json={},
        headers=pending_payment["admin_headers"],
    )
    teacher_id = await _teacher_id_of(support.DEMO_USERS["teacher"][0], superuser_session)
    course_class = await _create_class(api_client, pending_payment)
    await _assign_teacher(api_client, pending_payment, course_class["id"], teacher_id)
    await api_client.post(
        f"/api/v1/payments/{pending_payment['payment_id']}/assign-class",
        json={"course_class_id": course_class["id"]},
        headers=pending_payment["admin_headers"],
    )

    # El docente es dueño de la clase: publica el enlace en vivo y la grabación.
    recorded = await api_client.patch(
        f"/api/v1/course-classes/{course_class['id']}/recording-link",
        json={
            "recording_platform": "drive",
            "recording_url": "https://drive.google.com/file/d/grabacion-clase-1/view",
        },
        headers=pending_payment["teacher_headers"],
    )
    assert recorded.status_code == 200, recorded.text
    assert recorded.json()["recording_url"].endswith("grabacion-clase-1/view")

    live = await api_client.patch(
        f"/api/v1/course-classes/{course_class['id']}/meeting-link",
        json={"meeting_platform": "zoom", "meeting_url": "https://zoom.us/j/123456789"},
        headers=pending_payment["teacher_headers"],
    )
    assert live.status_code == 200, live.text

    classes = await api_client.get(
        "/api/v1/students/me/classes", headers=pending_payment["student_headers"]
    )
    mine = next(c for c in classes.json()["items"] if c["id"] == course_class["id"])
    assert mine["recording_url"].endswith("grabacion-clase-1/view")
    assert mine["meeting_url"] == "https://zoom.us/j/123456789"

    # El alumno no publica enlaces.
    forbidden = await api_client.patch(
        f"/api/v1/course-classes/{course_class['id']}/recording-link",
        json={"recording_platform": "drive", "recording_url": "https://example.com/x"},
        headers=pending_payment["student_headers"],
    )
    assert forbidden.status_code == 403

    # El docente puede retirar la grabación (cadena vacía = borrar).
    cleared = await api_client.patch(
        f"/api/v1/course-classes/{course_class['id']}/recording-link",
        json={"recording_platform": "", "recording_url": ""},
        headers=pending_payment["teacher_headers"],
    )
    assert cleared.status_code == 200, cleared.text
    assert cleared.json()["recording_url"] is None


async def test_un_docente_ajeno_no_publica_enlaces_en_esa_clase(
    api_client, pending_payment, superuser_session
):
    """La autorización es por pertenencia: otro docente recibe 403 aunque tenga el rol."""
    await api_client.post(
        f"/api/v1/payments/{pending_payment['payment_id']}/approve",
        json={},
        headers=pending_payment["admin_headers"],
    )
    course_class = await _create_class(api_client, pending_payment)  # sin docente asignado

    response = await api_client.patch(
        f"/api/v1/course-classes/{course_class['id']}/recording-link",
        json={"recording_platform": "drive", "recording_url": "https://example.com/x"},
        headers=pending_payment["teacher_headers"],
    )
    assert response.status_code == 403


async def test_rechazar_un_pago_no_rompe_la_inscripcion_de_quien_ya_esta_cursando(
    api_client, pending_payment, superuser_session
):
    """
    Rechazar un pago sólo afecta a inscripciones que esperaban clase.

    Quien ya está cursando (inscripción activa con clase) sigue cursando aunque el admin
    rechace un pago nuevo del mismo curso: bajar su estado a 'payment_rejected' le cerraría
    el curso desde la barra de tareas del alumno.
    """
    # Un pago pendiente sin aprobar: no hay inscripción que reflejar.
    rejected = await api_client.post(
        f"/api/v1/payments/{pending_payment['payment_id']}/reject",
        json={"notes": "El comprobante no coincide con el monto."},
        headers=pending_payment["admin_headers"],
    )
    assert rejected.status_code == 200, rejected.text
    assert await _enrollment_rows(superuser_session, pending_payment["course_id"]) == []

    # Ahora un alumno con clase: pago aprobado (hay clase con cupo) → inscripción activa.
    course_class = await _create_class(api_client, pending_payment)
    second_payment = await _insert_pending_payment(
        superuser_session, pending_payment["student_id"], pending_payment["course_id"]
    )
    approved = await api_client.post(
        f"/api/v1/payments/{second_payment}/approve",
        json={},
        headers=pending_payment["admin_headers"],
    )
    assert approved.status_code == 200, approved.text
    rows = await _enrollment_rows(superuser_session, pending_payment["course_id"])
    assert len(rows) == 1 and rows[0]["status"] == "active"

    # Un tercer pago (mensualidad) rechazado no le quita la clase al alumno.
    third_payment = await _insert_pending_payment(
        superuser_session, pending_payment["student_id"], pending_payment["course_id"]
    )
    rejected_again = await api_client.post(
        f"/api/v1/payments/{third_payment}/reject",
        json={"notes": "Mensualidad fuera de plazo."},
        headers=pending_payment["admin_headers"],
    )
    assert rejected_again.status_code == 200, rejected_again.text

    rows = await _enrollment_rows(superuser_session, pending_payment["course_id"])
    assert len(rows) == 1
    assert rows[0]["status"] == "active"
    assert str(rows[0]["course_class_id"]) == course_class["id"]


# ── Control de acceso al temario ───────────────────────────────────────────────────

async def test_usuario_no_autenticado_ve_solo_el_primer_modulo(
    api_client, pending_payment
):
    """El detalle público siempre muestra todos los módulos, pero el endpoint /access indica
    que un visitante anónimo no debe desbloquear el temario completo."""
    response = await api_client.get(
        f"/api/v1/courses/{pending_payment['course_id']}/access"
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["can_view_full_syllabus"] is False
    assert data["enrollment_status"] is None
    assert data["role_for_course"] is None


async def test_alumno_con_pago_aprobado_ve_temario_completo(
    api_client, pending_payment
):
    """Una inscripción payment_approved (sin clase todavía) ya permite ver el temario."""
    await api_client.post(
        f"/api/v1/payments/{pending_payment['payment_id']}/approve",
        json={},
        headers=pending_payment["admin_headers"],
    )
    response = await api_client.get(
        f"/api/v1/courses/{pending_payment['course_id']}/access",
        headers=pending_payment["student_headers"],
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["can_view_full_syllabus"] is True
    assert data["enrollment_status"] == "payment_approved"
    assert data["role_for_course"] == "student"


async def test_alumno_sin_inscripcion_no_ve_temario_completo(
    api_client, pending_payment, superuser_session
):
    """Un alumno autenticado pero sin inscripción paga para este curso no ve todo el temario."""
    response = await api_client.get(
        f"/api/v1/courses/{pending_payment['course_id']}/access",
        headers=pending_payment["student_headers"],
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["can_view_full_syllabus"] is False
    assert data["enrollment_status"] is None
    assert data["role_for_course"] is None


async def test_admin_y_docente_ven_el_temario_completo(
    api_client, pending_payment
):
    """Admin y teacher tienen acceso total al temario del curso."""
    admin_access = await api_client.get(
        f"/api/v1/courses/{pending_payment['course_id']}/access",
        headers=pending_payment["admin_headers"],
    )
    assert admin_access.status_code == 200
    assert admin_access.json()["can_view_full_syllabus"] is True
    assert admin_access.json()["role_for_course"] == "admin"

    teacher_access = await api_client.get(
        f"/api/v1/courses/{pending_payment['course_id']}/access",
        headers=pending_payment["teacher_headers"],
    )
    assert teacher_access.status_code == 200
    assert teacher_access.json()["can_view_full_syllabus"] is True
    assert teacher_access.json()["role_for_course"] == "teacher"


# ── Cupos por clase ─────────────────────────────────────────────────────────────────

async def test_el_cupo_global_por_clase_es_20(superuser_session):
    """La configuración global máxima de alumnos por clase debe ser 20."""
    value = (
        await superuser_session.execute(
            text("SELECT value FROM system_settings WHERE key = 'global_max_students_per_class'")
        )
    ).scalar()
    assert int(value) == 20


async def test_cuando_una_clase_se_llena_el_contador_nunca_es_cero(
    api_client, pending_payment, superuser_session
):
    """Una clase llena no debe mostrar 0 cupos; debe proyectar la próxima clase."""
    course_class = await _create_class(api_client, pending_payment)

    # Llenar la clase hasta 20 alumnos usando inserciones directas (más rápido que
    # aprobar 20 pagos por HTTP) para forzar el escenario de "clase completa".
    student_emails = []
    for i in range(20):
        email = f"filler_student_{i}_{uuid.uuid4().hex[:6]}@test.local"
        student_emails.append(email)
        user_id = (
            await superuser_session.execute(
                text(
                    """
                    INSERT INTO users (email, password_hash, first_name, last_name, status)
                    VALUES (:email, 'x', 'Filler', 'Student', 'active')
                    ON CONFLICT (email) DO NOTHING
                    RETURNING id
                    """
                ),
                {"email": email},
            )
        ).scalar_one_or_none()
        if user_id is None:
            user_id = (
                await superuser_session.execute(
                    text("SELECT id FROM users WHERE email = :email"),
                    {"email": email},
                )
            ).scalar_one()
        role_id = (
            await superuser_session.execute(
                text("SELECT id FROM roles WHERE name = 'student'")
            )
        ).scalar_one()
        await superuser_session.execute(
            text(
                """
                INSERT INTO user_roles (user_id, role_id)
                VALUES (:uid, :rid)
                ON CONFLICT DO NOTHING
                """
            ),
            {"uid": user_id, "rid": role_id},
        )
        await superuser_session.execute(
            text(
                """
                INSERT INTO enrollments (student_id, course_id, course_class_id, status, approved_at)
                VALUES (:uid, :cid, :ccid, 'active', NOW())
                ON CONFLICT (student_id, course_id) DO NOTHING
                """
            ),
            {"uid": user_id, "cid": pending_payment["course_id"], "ccid": course_class["id"]},
        )
    await superuser_session.commit()

    detail = await api_client.get(
        f"/api/v1/courses/{pending_payment['course_id']}"
    )
    assert detail.status_code == 200, detail.text
    data = detail.json()
    assert data["needs_more_classes"] is True
    assert data["has_available_classes"] is False
    assert data["total_available_slots"] == 20
    assert data["raw_available_slots"] == 0
    assert len(data["available_classes"]) == 1
    assert data["available_classes"][0]["is_full"] is True
    assert data["available_classes"][0]["available_slots"] == 20
    assert data["available_classes"][0]["global_max"] == 20


# ── Notificación a admins ──────────────────────────────────────────────────────────

async def test_se_notifica_a_admins_cuando_un_curso_llega_a_5_inscritos_sin_clases(
    api_client, tokens, superuser_session, pending_payment
):
    """Al 5to pago aprobado sin clases activas, los admins reciben notificación y email encolado."""
    admin_user_id = (
        await superuser_session.execute(
            text("SELECT id FROM users WHERE email = :email"),
            {"email": support.DEMO_USERS["admin"][0]},
        )
    ).scalar_one()

    # Crear 5 alumnos ficticios con pagos pendientes para el mismo curso.
    payment_ids = []
    for i in range(5):
        email = f"notify_student_{i}_{uuid.uuid4().hex[:6]}@test.local"
        user_id = (
            await superuser_session.execute(
                text(
                    """
                    INSERT INTO users (email, password_hash, first_name, last_name, status)
                    VALUES (:email, 'x', 'Notify', 'Student', 'active')
                    RETURNING id
                    """
                ),
                {"email": email},
            )
        ).scalar_one()
        role_id = (
            await superuser_session.execute(
                text("SELECT id FROM roles WHERE name = 'student'")
            )
        ).scalar_one()
        await superuser_session.execute(
            text(
                """
                INSERT INTO user_roles (user_id, role_id) VALUES (:uid, :rid)
                ON CONFLICT DO NOTHING
                """
            ),
            {"uid": user_id, "rid": role_id},
        )
        payment_id = (
            await superuser_session.execute(
                text(
                    """
                    INSERT INTO payments (student_id, course_id, amount, currency,
                                          payment_method, status)
                    VALUES (:uid, :cid, 49.99, 'USD', 'bank_transfer', 'pending')
                    RETURNING id
                    """
                ),
                {"uid": user_id, "cid": pending_payment["course_id"]},
            )
        ).scalar_one()
        payment_ids.append(str(payment_id))
    await superuser_session.commit()

    # Aprobar los primeros 4 no debe generar notificación.
    for pid in payment_ids[:4]:
        response = await api_client.post(
            f"/api/v1/payments/{pid}/approve", json={}, headers=pending_payment["admin_headers"]
        )
        assert response.status_code == 200, response.text

    notifications_before = (
        await superuser_session.execute(
            text("SELECT COUNT(*) FROM notifications WHERE user_id = :uid"),
            {"uid": admin_user_id},
        )
    ).scalar()
    assert notifications_before == 0

    # Al aprobar el 5to se dispara la notificación.
    response = await api_client.post(
        f"/api/v1/payments/{payment_ids[4]}/approve", json={}, headers=pending_payment["admin_headers"]
    )
    assert response.status_code == 200, response.text

    notifications_after = (
        await superuser_session.execute(
            text("SELECT COUNT(*) FROM notifications WHERE user_id = :uid"),
            {"uid": admin_user_id},
        )
    ).scalar()
    assert notifications_after == 1

    email_jobs = (
        await superuser_session.execute(
            text(
                "SELECT COUNT(*) FROM email_queue WHERE template_name = 'admin_alert_course_needs_class'"
            )
        )
    ).scalar()
    assert email_jobs >= 1

    # Listar notificaciones como admin.
    notifications_resp = await api_client.get(
        "/api/v1/notifications", headers=pending_payment["admin_headers"]
    )
    assert notifications_resp.status_code == 200, notifications_resp.text
    items = notifications_resp.json()["items"]
    assert any("necesita una clase" in n["title"] for n in items)
