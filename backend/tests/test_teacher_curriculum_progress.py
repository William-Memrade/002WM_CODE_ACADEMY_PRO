"""
CodeAcademy Pro — Pruebas de integración: temario del docente y progreso del alumno.

Qué prueban (capa 2: app completa en proceso, SQLAlchemy y RLS reales):

  * módulos y lecciones — alta, edición y borrado por el docente del curso, y el
    403 cuando quien llama no es el docente;
  * progreso del alumno — el docente lo edita, el alumno lo lee, y el valor
    escrito llega de verdad a PostgreSQL (no basta con que la API diga 200);
  * panel del docente — `/teachers/me/courses` y `/teachers/me/students`.

Montaje: la inscripción no tiene endpoint de alta (nace al aprobar un pago), así
que se inserta con la conexión de superusuario y se borra al terminar. Es
utillaje de prueba para aislar lo que se está probando, no un atajo del código de
producción: los endpoints se ejercitan siempre por HTTP con el rol RLS real.

Ver docs/architecture/TESTING.md (plan por capas) antes de añadir casos aquí.
"""

import uuid

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from tests import support
from tests.support import DEMO_USERS, auth_headers

pytestmark = pytest.mark.integration


# ── Utillaje: conexión de superusuario para montar y limpiar ─────────────────
# `superuser_session` vive en conftest.py: la comparten las pruebas de temario y las
# del ciclo de inscripción.

async def _seeded_ids(session: AsyncSession) -> dict:
    """IDs de los usuarios demo y del primer curso del docente del seed."""
    student = (
        await session.execute(
            text("SELECT id FROM users WHERE email = :e"), {"e": DEMO_USERS["student"][0]}
        )
    ).scalar_one()
    teacher_email = DEMO_USERS["teacher"][0]
    teacher_profile = (
        await session.execute(
            text(
                "SELECT t.id FROM teachers t JOIN users u ON u.id = t.user_id "
                "WHERE u.email = :e"
            ),
            {"e": teacher_email},
        )
    ).scalar_one()
    course = (
        await session.execute(
            text(
                "SELECT id, title FROM courses WHERE teacher_id = :t AND deleted_at IS NULL "
                "ORDER BY created_at LIMIT 1"
            ),
            {"t": teacher_profile},
        )
    ).one_or_none()
    if course is None:
        pytest.skip("el seed no dejó ningún curso asignado al docente demo")
    return {
        "student_id": student,
        "teacher_id": teacher_profile,
        "course_id": course.id,
        "course_title": course.title,
    }


@pytest_asyncio.fixture
async def teacher_course(api_client, tokens, superuser_session):
    """
    Montaje: un curso del docente con una clase suya y el alumno demo inscrito.

    Se reutiliza el curso del seed (con su temario) en vez de crear uno: así las
    pruebas de módulos/lecciones trabajan sobre contenido real.
    """
    ids = await _seeded_ids(superuser_session)
    admin_headers = auth_headers(tokens["admin"])

    response = await api_client.post(
        f"/api/v1/courses/{ids['course_id']}/classes",
        json={
            "name": f"Clase de prueba {uuid.uuid4().hex[:8]}",
            "days_of_week": ["mon", "wed"],
            "start_time": "18:00:00",
            "end_time": "20:00:00",
            "meeting_platform": "meet",
            "meeting_url": "https://example.com/clase-de-prueba",
        },
        headers=admin_headers,
    )
    assert response.status_code == 201, response.text
    class_id = response.json()["id"]

    assign = await api_client.patch(
        f"/api/v1/course-classes/{class_id}/assign-teacher",
        json={"teacher_id": str(ids["teacher_id"])},
        headers=admin_headers,
    )
    assert assign.status_code == 200, assign.text

    # Inscripción activa (idempotente: uq_enrollments es (student_id, course_id))
    enrollment_id = (
        await superuser_session.execute(
            text(
                """
                INSERT INTO enrollments (student_id, course_id, course_class_id, status, progress_percentage)
                VALUES (:student, :course, :class, 'active', 0)
                ON CONFLICT (student_id, course_id) DO UPDATE
                    SET course_class_id = EXCLUDED.course_class_id,
                        status = 'active',
                        progress_percentage = 0
                RETURNING id
                """
            ),
            {
                "student": ids["student_id"],
                "course": ids["course_id"],
                "class": class_id,
            },
        )
    ).scalar_one()
    await superuser_session.commit()

    try:
        yield {
            **ids,
            "class_id": class_id,
            "enrollment_id": str(enrollment_id),
            "teacher_headers": auth_headers(tokens["teacher"]),
            "student_headers": auth_headers(tokens["student"]),
            "admin_headers": admin_headers,
        }
    finally:
        await superuser_session.execute(
            text("DELETE FROM enrollments WHERE id = :id"), {"id": enrollment_id}
        )
        await superuser_session.execute(
            text("DELETE FROM course_classes WHERE id = :id"), {"id": class_id}
        )
        await superuser_session.commit()


# ── Temario: módulos y lecciones ────────────────────────────────────────────

async def test_docente_lista_el_temario_del_curso(api_client, teacher_course):
    response = await api_client.get(
        f"/api/v1/courses/{teacher_course['course_id']}/modules",
        headers=teacher_course["teacher_headers"],
    )
    assert response.status_code == 200, response.text
    items = response.json()["items"]
    assert items, "el curso del seed debería tener módulos"
    # La vista del docente incluye el contenido de la lección (la pública no).
    first_lesson = items[0]["lessons"][0]
    assert "content" in first_lesson


async def test_docente_crea_edita_y_borra_modulo_y_leccion(api_client, teacher_course):
    course_id = teacher_course["course_id"]
    headers = teacher_course["teacher_headers"]

    created_module = await api_client.post(
        f"/api/v1/courses/{course_id}/modules",
        json={"course_id": str(course_id), "title": "Módulo de prueba", "sort_order": 99},
        headers=headers,
    )
    assert created_module.status_code == 201, created_module.text
    module_id = created_module.json()["id"]

    created_lesson = await api_client.post(
        f"/api/v1/courses/modules/{module_id}/lessons",
        json={"module_id": str(module_id), "title": "Lección de prueba", "sort_order": 1},
        headers=headers,
    )
    assert created_lesson.status_code == 201, created_lesson.text
    lesson_id = created_lesson.json()["id"]

    # Edición de la lección: título, contenido y publicación.
    updated_lesson = await api_client.put(
        f"/api/v1/courses/lessons/{lesson_id}",
        json={"title": "Lección editada", "content": "Contenido nuevo", "is_published": False},
        headers=headers,
    )
    assert updated_lesson.status_code == 200, updated_lesson.text
    assert updated_lesson.json()["title"] == "Lección editada"
    assert updated_lesson.json()["content"] == "Contenido nuevo"
    assert updated_lesson.json()["is_published"] is False

    # Edición del módulo.
    updated_module = await api_client.put(
        f"/api/v1/courses/modules/{module_id}",
        json={"title": "Módulo editado", "is_published": True},
        headers=headers,
    )
    assert updated_module.status_code == 200, updated_module.text
    assert updated_module.json()["title"] == "Módulo editado"
    assert updated_module.json()["is_published"] is True

    # El borrado de la lección es 204 y se nota en el temario.
    assert (
        await api_client.delete(f"/api/v1/courses/lessons/{lesson_id}", headers=headers)
    ).status_code == 204
    assert (
        await api_client.delete(f"/api/v1/courses/modules/{module_id}", headers=headers)
    ).status_code == 204

    listing = await api_client.get(f"/api/v1/courses/{course_id}/modules", headers=headers)
    module_ids = [m["id"] for m in listing.json()["items"]]
    assert module_id not in module_ids


async def test_el_temario_es_solo_para_admin_y_docente(api_client, teacher_course):
    """El rol de alumno no entra al temario, ni para leer ni para escribir."""
    course_id = teacher_course["course_id"]
    headers = teacher_course["student_headers"]

    assert (
        await api_client.get(f"/api/v1/courses/{course_id}/modules", headers=headers)
    ).status_code == 403
    assert (
        await api_client.put(
            f"/api/v1/courses/modules/{uuid.uuid4()}", json={"title": "Hack"}, headers=headers
        )
    ).status_code == 403
    assert (
        await api_client.delete(f"/api/v1/courses/modules/{uuid.uuid4()}", headers=headers)
    ).status_code == 403


async def test_editar_un_modulo_inexistente_da_404(api_client, teacher_course):
    response = await api_client.put(
        f"/api/v1/courses/modules/{uuid.uuid4()}",
        json={"title": "No existe"},
        headers=teacher_course["teacher_headers"],
    )
    assert response.status_code == 404


# ── Panel del docente ───────────────────────────────────────────────────────

async def test_docente_ve_sus_cursos_con_conteos(api_client, teacher_course):
    response = await api_client.get(
        "/api/v1/teachers/me/courses", headers=teacher_course["teacher_headers"]
    )
    assert response.status_code == 200, response.text
    items = response.json()["items"]
    course = next((c for c in items if c["id"] == str(teacher_course["course_id"])), None)
    assert course is not None, "el curso del docente no aparece en su panel"
    assert course["modules_count"] >= 1
    assert course["lessons_count"] >= 1
    assert course["classes_count"] >= 1
    assert course["students_count"] >= 1


async def test_el_panel_del_docente_no_es_para_alumnos(api_client, teacher_course):
    response = await api_client.get(
        "/api/v1/teachers/me/courses", headers=teacher_course["student_headers"]
    )
    assert response.status_code == 403


async def test_docente_ve_sus_alumnos_con_progreso(api_client, teacher_course):
    response = await api_client.get(
        "/api/v1/teachers/me/students", headers=teacher_course["teacher_headers"]
    )
    assert response.status_code == 200, response.text
    row = next(
        (
            s
            for s in response.json()["items"]
            if s["enrollment_id"] == teacher_course["enrollment_id"]
        ),
        None,
    )
    assert row is not None, "la inscripción montada no aparece en la lista del docente"
    assert row["student_id"] == str(teacher_course["student_id"])
    assert row["course_title"] == teacher_course["course_title"]
    assert row["progress_percentage"] == 0


# ── Progreso del alumno ─────────────────────────────────────────────────────

async def test_el_alumno_ve_su_progreso(api_client, teacher_course):
    response = await api_client.get(
        "/api/v1/students/me/progress", headers=teacher_course["student_headers"]
    )
    assert response.status_code == 200, response.text
    row = next(
        (
            p
            for p in response.json()["items"]
            if p["enrollment_id"] == teacher_course["enrollment_id"]
        ),
        None,
    )
    assert row is not None
    assert row["course_class_id"] == teacher_course["class_id"]


async def test_el_docente_edita_el_progreso_y_llega_a_la_base(
    api_client, teacher_course, superuser_session
):
    """El 200 no basta: el valor tiene que estar escrito en PostgreSQL (RLS incluido)."""
    response = await api_client.patch(
        f"/api/v1/course-classes/{teacher_course['class_id']}"
        f"/students/{teacher_course['student_id']}/progress",
        json={"progress_percentage": 42.5},
        headers=teacher_course["teacher_headers"],
    )
    assert response.status_code == 200, response.text
    assert response.json()["progress_percentage"] == 42.5

    stored = (
        await superuser_session.execute(
            text("SELECT progress_percentage FROM enrollments WHERE id = :id"),
            {"id": teacher_course["enrollment_id"]},
        )
    ).scalar_one()
    assert float(stored) == 42.5

    student_view = await api_client.get(
        "/api/v1/students/me/progress", headers=teacher_course["student_headers"]
    )
    row = next(
        p
        for p in student_view.json()["items"]
        if p["enrollment_id"] == teacher_course["enrollment_id"]
    )
    assert row["progress_percentage"] == 42.5


async def test_el_cien_por_ciento_marca_completado_y_es_reversible(
    api_client, teacher_course
):
    url = (
        f"/api/v1/course-classes/{teacher_course['class_id']}"
        f"/students/{teacher_course['student_id']}/progress"
    )
    headers = teacher_course["teacher_headers"]

    done = await api_client.patch(url, json={"progress_percentage": 100}, headers=headers)
    assert done.status_code == 200, done.text
    assert done.json()["completed_at"] is not None

    # Bajar el porcentaje deshace la marca: no es un estado terminal.
    back = await api_client.patch(url, json={"progress_percentage": 30}, headers=headers)
    assert back.status_code == 200, back.text
    assert back.json()["completed_at"] is None


async def test_progreso_fuera_de_rango_da_422(api_client, teacher_course):
    response = await api_client.patch(
        f"/api/v1/course-classes/{teacher_course['class_id']}"
        f"/students/{teacher_course['student_id']}/progress",
        json={"progress_percentage": 150},
        headers=teacher_course["teacher_headers"],
    )
    assert response.status_code == 422


async def test_el_alumno_no_edita_su_propio_progreso(api_client, teacher_course):
    response = await api_client.patch(
        f"/api/v1/course-classes/{teacher_course['class_id']}"
        f"/students/{teacher_course['student_id']}/progress",
        json={"progress_percentage": 100},
        headers=teacher_course["student_headers"],
    )
    assert response.status_code == 403


async def test_un_docente_no_edita_progreso_en_una_clase_que_no_imparte(
    api_client, teacher_course
):
    """Ser docente del curso no basta: el progreso lo escribe quien da la clase."""
    admin_headers = teacher_course["admin_headers"]
    response = await api_client.post(
        f"/api/v1/courses/{teacher_course['course_id']}/classes",
        json={
            "name": f"Clase sin docente {uuid.uuid4().hex[:8]}",
            "days_of_week": ["fri"],
            "start_time": "09:00:00",
            "end_time": "10:00:00",
        },
        headers=admin_headers,
    )
    assert response.status_code == 201, response.text
    other_class_id = response.json()["id"]

    try:
        attempt = await api_client.patch(
            f"/api/v1/course-classes/{other_class_id}"
            f"/students/{teacher_course['student_id']}/progress",
            json={"progress_percentage": 10},
            headers=teacher_course["teacher_headers"],
        )
        assert attempt.status_code == 403
    finally:
        await api_client.delete(
            f"/api/v1/course-classes/{other_class_id}", headers=admin_headers
        )


async def test_progreso_de_una_clase_inexistente_da_404(api_client, teacher_course):
    response = await api_client.patch(
        f"/api/v1/course-classes/{uuid.uuid4()}"
        f"/students/{teacher_course['student_id']}/progress",
        json={"progress_percentage": 10},
        headers=teacher_course["admin_headers"],
    )
    assert response.status_code == 404


async def test_progreso_de_un_alumno_sin_inscripcion_da_404(api_client, teacher_course):
    response = await api_client.patch(
        f"/api/v1/course-classes/{teacher_course['class_id']}"
        f"/students/{uuid.uuid4()}/progress",
        json={"progress_percentage": 10},
        headers=teacher_course["admin_headers"],
    )
    assert response.status_code == 404


# ── Orden del temario (sort_order, drag & drop del editor) ────────────────────

async def _modules(api_client, course_id, headers) -> list[dict]:
    response = await api_client.get(f"/api/v1/courses/{course_id}/modules", headers=headers)
    assert response.status_code == 200, response.text
    return response.json()["items"]


async def _new_module(api_client, course_id, headers, title: str) -> str:
    response = await api_client.post(
        f"/api/v1/courses/{course_id}/modules",
        json={"course_id": str(course_id), "title": title},
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


async def _new_lesson(api_client, module_id, headers, title: str) -> str:
    response = await api_client.post(
        f"/api/v1/courses/modules/{module_id}/lessons",
        json={"module_id": str(module_id), "title": title},
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


async def test_el_orden_de_los_modulos_se_reescribe_de_cero_a_n(api_client, teacher_course):
    """
    El editor manda la lista en su orden final; el backend reescribe `sort_order` 0..n-1.

    `sort_order` es orden, no identidad: por eso se puede invertir el temario sin tocar
    los ids ni renumerar a mano.
    """
    course_id = teacher_course["course_id"]
    headers = teacher_course["teacher_headers"]
    original = [m["id"] for m in await _modules(api_client, course_id, headers)]

    extra = []
    for index in range(max(0, 3 - len(original))):
        extra.append(await _new_module(api_client, course_id, headers, f"Módulo orden {index}"))

    try:
        current = [m["id"] for m in await _modules(api_client, course_id, headers)]
        assert len(current) >= 3
        reversed_ids = list(reversed(current))

        response = await api_client.patch(
            f"/api/v1/courses/{course_id}/modules/order",
            json={"ordered_ids": reversed_ids},
            headers=headers,
        )
        assert response.status_code == 200, response.text
        items = response.json()["items"]
        assert [m["id"] for m in items] == reversed_ids
        assert [m["sort_order"] for m in items] == list(range(len(reversed_ids)))

        # Persiste: una lectura nueva devuelve el mismo orden.
        again = await _modules(api_client, course_id, headers)
        assert [m["id"] for m in again] == reversed_ids
    finally:
        if original:
            await api_client.patch(
                f"/api/v1/courses/{course_id}/modules/order",
                json={"ordered_ids": original},
                headers=headers,
            )
        for module_id in extra:
            await api_client.delete(f"/api/v1/courses/modules/{module_id}", headers=headers)


async def test_una_leccion_nueva_puede_quedar_primera_sin_renumerar(api_client, teacher_course):
    """
    Caso del usuario: añadir una lección que debe ir al inicio.

    El alta no calcula el orden (todas nacen con 0), así que basta con reordenar la lista
    enviando la nueva primero: queda en 0 y el resto se desplaza solo.
    """
    course_id = teacher_course["course_id"]
    headers = teacher_course["teacher_headers"]

    module_id = await _new_module(api_client, course_id, headers, "Módulo reordenable")
    try:
        first = await _new_lesson(api_client, module_id, headers, "Lección A")
        second = await _new_lesson(api_client, module_id, headers, "Lección B")
        newcomer = await _new_lesson(api_client, module_id, headers, "Lección al inicio")

        response = await api_client.patch(
            f"/api/v1/courses/modules/{module_id}/lessons/order",
            json={"ordered_ids": [newcomer, first, second]},
            headers=headers,
        )
        assert response.status_code == 200, response.text
        lessons = next(
            m["lessons"] for m in response.json()["items"] if m["id"] == module_id
        )
        assert [l["id"] for l in lessons] == [newcomer, first, second]
        assert [l["sort_order"] for l in lessons] == [0, 1, 2]
    finally:
        await api_client.delete(f"/api/v1/courses/modules/{module_id}", headers=headers)


async def test_reordenar_con_un_id_ajeno_da_400(api_client, teacher_course):
    """Un id que no es del curso se rechaza: no se reordena a ciegas."""
    course_id = teacher_course["course_id"]
    headers = teacher_course["teacher_headers"]

    response = await api_client.patch(
        f"/api/v1/courses/{course_id}/modules/order",
        json={"ordered_ids": [str(uuid.uuid4())]},
        headers=headers,
    )
    assert response.status_code == 400

    module_id = await _new_module(api_client, course_id, headers, "Módulo para orden")
    try:
        response = await api_client.patch(
            f"/api/v1/courses/modules/{module_id}/lessons/order",
            json={"ordered_ids": [str(uuid.uuid4())]},
            headers=headers,
        )
        assert response.status_code == 400
    finally:
        await api_client.delete(f"/api/v1/courses/modules/{module_id}", headers=headers)


async def test_solo_admin_y_docente_reordenan_el_temario(api_client, teacher_course):
    """El alumno no mueve el temario del curso."""
    course_id = teacher_course["course_id"]
    response = await api_client.patch(
        f"/api/v1/courses/{course_id}/modules/order",
        json={"ordered_ids": [str(uuid.uuid4())]},
        headers=teacher_course["student_headers"],
    )
    assert response.status_code == 403


async def test_borrar_un_modulo_con_lecciones_lo_hace_en_cascada(
    api_client, teacher_course, superuser_session
):
    """
    Regresión: borrar un módulo que tiene lecciones dentro.

    El ORM intentaba `UPDATE lessons SET module_id = NULL` (violación de NOT NULL) en vez
    de dejar que la FK borre en cascada, así que el borrado desde el editor devolvía 500.
    """
    from sqlalchemy import text

    course_id = teacher_course["course_id"]
    headers = teacher_course["teacher_headers"]

    module_id = await _new_module(api_client, course_id, headers, "Módulo con lecciones")
    lesson_ids = [
        await _new_lesson(api_client, module_id, headers, f"Lección {index}")
        for index in (1, 2)
    ]

    response = await api_client.delete(f"/api/v1/courses/modules/{module_id}", headers=headers)
    assert response.status_code == 204, response.text

    remaining = (
        await superuser_session.execute(
            text("SELECT count(*) FROM lessons WHERE id = ANY(:ids)"),
            {"ids": lesson_ids},
        )
    ).scalar_one()
    assert remaining == 0, "las lecciones del módulo se van con él"

    module_ids = [m["id"] for m in await _modules(api_client, course_id, headers)]
    assert module_id not in module_ids
