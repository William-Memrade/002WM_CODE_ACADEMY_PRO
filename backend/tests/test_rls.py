"""
CodeAcademy Pro — Row Level Security Tests
Validates that RLS policies enforce data isolation by role and ownership.

These tests connect directly to PostgreSQL as 'academy_app' (non-superuser)
and verify that SET LOCAL + RLS policies work as expected.

Se corren contra la base de pruebas (tests/support.py: `academy_test`, creada con el
migrador real, que es el que crea el rol academy_app y las políticas). Si PostgreSQL
no está levantado, la suite se salta con el comando para levantarlo en vez de fallar.

Run with:
    pytest tests/test_rls.py -v
"""

import os
import uuid

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Use the RLS-enforced role — NOT the postgres superuser.
# Apunta por defecto a la base de pruebas (tests/support.py); se puede pisar con
# RLS_TEST_DB_URL para correr esta suite contra otra base.
from tests import support

# Estos tests van contra PostgreSQL real: son capa de integración. El marker permite que
# `pytest -m "not integration"` corra sólo lo unitario, sin necesitar servicios.
pytestmark = pytest.mark.integration

TEST_DB_URL = os.getenv("RLS_TEST_DB_URL", support.TEST_RLS_DATABASE_URL)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def set_rls_context(session: AsyncSession, user_id: str, role: str):
    """Simulate the FastAPI middleware that sets RLS context."""
    await session.execute(text("SELECT set_config('app.current_user_id', :uid, true)"), {"uid": user_id})
    await session.execute(text("SELECT set_config('app.current_user_role', :role, true)"), {"role": role})


async def clear_rls_context(session: AsyncSession):
    """Clear RLS context (simulates a connection without auth)."""
    await session.execute(text("SELECT set_config('app.current_user_id', '', true)"))
    await session.execute(text("SELECT set_config('app.current_user_role', '', true)"))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def db(prepared_database: str):
    """
    Sesión de prueba que hace rollback al terminar (nunca commitea).

    Depende de `prepared_database` (conftest): así correr solo este archivo también
    deja la base creada, migrada y sembrada, en vez de depender de que otro test
    la haya preparado antes.

    El engine se crea acá y no a nivel de módulo: un engine de módulo queda atado
    al event loop del primer test que lo usa, y a partir del segundo pytest-asyncio
    falla con "got Future attached to a different loop". Se usa NullPool porque el
    engine vive lo que dura un test: no hay nada que reciclar.
    """
    engine = create_async_engine(TEST_DB_URL, echo=False, poolclass=NullPool)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    try:
        async with session_factory() as session:
            try:
                yield session
            finally:
                # Rollback EXPLÍCITO: `async with session.begin()` haría COMMIT al
                # salir, y estos tests insertan usuarios/roles/cursos de prueba que
                # no pueden quedar en la base (la corrida siguiente chocaría con la
                # clave única de users.email).
                await session.rollback()
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def seed_users(db: AsyncSession):
    """
    Create test users with different roles and return their IDs.
    Uses raw SQL to bypass any RLS restrictions during setup.
    """
    # We're connected as academy_app which respects RLS.
    # For INSERT on users, the policy allows when app_user_id() IS NULL (no context set).
    admin_id = str(uuid.uuid4())
    teacher_user_id = str(uuid.uuid4())
    student1_id = str(uuid.uuid4())
    student2_id = str(uuid.uuid4())

    # Insert users (no RLS context = registration flow, allowed by policy)
    for uid, email, username, fname in [
        (admin_id, "admin_test@test.com", "admin_test", "Admin"),
        (teacher_user_id, "teacher_test@test.com", "teacher_test", "Teacher"),
        (student1_id, "student1_test@test.com", "student1_test", "Student1"),
        (student2_id, "student2_test@test.com", "student2_test", "Student2"),
    ]:
        await db.execute(text("""
            INSERT INTO users (id, email, username, password_hash, first_name, last_name, status)
            VALUES (:id, :email, :username, 'hash', :fname, 'Test', 'active')
        """), {"id": uid, "email": email, "username": username, "fname": fname})

    # Assign roles (requires admin context)
    await set_rls_context(db, admin_id, "admin")

    # Get role IDs
    roles = {}
    for role_name in ["admin", "teacher", "student"]:
        result = await db.execute(
            text("SELECT id FROM roles WHERE name = :n"), {"n": role_name}
        )
        row = result.one_or_none()
        if row:
            roles[role_name] = str(row.id)

    # Assign roles
    if "admin" in roles:
        await db.execute(text(
            "INSERT INTO user_roles (id, user_id, role_id) VALUES (:id, :uid, :rid)"
        ), {"id": str(uuid.uuid4()), "uid": admin_id, "rid": roles["admin"]})
    if "teacher" in roles:
        await db.execute(text(
            "INSERT INTO user_roles (id, user_id, role_id) VALUES (:id, :uid, :rid)"
        ), {"id": str(uuid.uuid4()), "uid": teacher_user_id, "rid": roles["teacher"]})
    if "student" in roles:
        await db.execute(text(
            "INSERT INTO user_roles (id, user_id, role_id) VALUES (:id, :uid, :rid)"
        ), {"id": str(uuid.uuid4()), "uid": student1_id, "rid": roles["student"]})
        await db.execute(text(
            "INSERT INTO user_roles (id, user_id, role_id) VALUES (:id, :uid, :rid)"
        ), {"id": str(uuid.uuid4()), "uid": student2_id, "rid": roles["student"]})

    # Create teacher profile
    teacher_profile_id = str(uuid.uuid4())
    await db.execute(text("""
        INSERT INTO teachers (id, user_id, is_active)
        VALUES (:id, :uid, true)
    """), {"id": teacher_profile_id, "uid": teacher_user_id})

    # Create a course assigned to the teacher
    course_id = str(uuid.uuid4())
    await db.execute(text("""
        INSERT INTO courses (id, title, slug, description, teacher_id, price, is_active)
        VALUES (:id, 'Test Course', :slug, 'desc', :tid, 99.99, true)
    """), {"id": course_id, "slug": f"test-course-{uuid.uuid4().hex[:8]}", "tid": teacher_profile_id})

    # Enroll student1 in the course
    enrollment_id = str(uuid.uuid4())
    await db.execute(text("""
        INSERT INTO enrollments (id, student_id, course_id, status)
        VALUES (:id, :sid, :cid, 'active')
    """), {"id": enrollment_id, "sid": student1_id, "cid": course_id})

    # Create payment for student1
    payment_id = str(uuid.uuid4())
    await db.execute(text("""
        INSERT INTO payments (id, student_id, course_id, enrollment_id, amount, status)
        VALUES (:id, :sid, :cid, :eid, 99.99, 'approved')
    """), {"id": payment_id, "sid": student1_id, "cid": course_id, "eid": enrollment_id})

    # Create payment for student2 (different course scenario — pending)
    payment2_id = str(uuid.uuid4())
    await db.execute(text("""
        INSERT INTO payments (id, student_id, course_id, amount, status)
        VALUES (:id, :sid, :cid, 99.99, 'pending')
    """), {"id": payment2_id, "sid": student2_id, "cid": course_id})

    return {
        "admin_id": admin_id,
        "teacher_user_id": teacher_user_id,
        "teacher_profile_id": teacher_profile_id,
        "student1_id": student1_id,
        "student2_id": student2_id,
        "course_id": course_id,
        "enrollment_id": enrollment_id,
        "payment1_id": payment_id,
        "payment2_id": payment2_id,
    }


# ---------------------------------------------------------------------------
# Tests: Payment Isolation (Tier 1 — Critical)
# ---------------------------------------------------------------------------

class TestPaymentRLS:
    """Verify that students can only see their own payments."""

    @pytest.mark.asyncio
    async def test_student_sees_own_payments(self, db, seed_users):
        """Student1 can see their own payment."""
        await set_rls_context(db, seed_users["student1_id"], "student")
        result = await db.execute(text("SELECT id FROM payments"))
        rows = result.fetchall()
        payment_ids = [str(r.id) for r in rows]
        assert seed_users["payment1_id"] in payment_ids
        assert seed_users["payment2_id"] not in payment_ids

    @pytest.mark.asyncio
    async def test_student_cannot_see_other_payments(self, db, seed_users):
        """Student2 cannot see Student1's payment."""
        await set_rls_context(db, seed_users["student2_id"], "student")
        result = await db.execute(text("SELECT id FROM payments"))
        rows = result.fetchall()
        payment_ids = [str(r.id) for r in rows]
        assert seed_users["payment1_id"] not in payment_ids
        assert seed_users["payment2_id"] in payment_ids

    @pytest.mark.asyncio
    async def test_admin_sees_all_payments(self, db, seed_users):
        """Admin can see all payments."""
        await set_rls_context(db, seed_users["admin_id"], "admin")
        result = await db.execute(text("SELECT id FROM payments"))
        rows = result.fetchall()
        payment_ids = [str(r.id) for r in rows]
        assert seed_users["payment1_id"] in payment_ids
        assert seed_users["payment2_id"] in payment_ids

    @pytest.mark.asyncio
    async def test_student_cannot_insert_payment_for_other(self, db, seed_users):
        """Student1 cannot create a payment on behalf of Student2 (WITH CHECK)."""
        await set_rls_context(db, seed_users["student1_id"], "student")
        with pytest.raises(Exception):
            await db.execute(text("""
                INSERT INTO payments (id, student_id, course_id, amount, status)
                VALUES (:id, :sid, :cid, 50.00, 'pending')
            """), {
                "id": str(uuid.uuid4()),
                "sid": seed_users["student2_id"],  # NOT the current user
                "cid": seed_users["course_id"],
            })

    @pytest.mark.asyncio
    async def test_student_cannot_update_payments(self, db, seed_users):
        """Students cannot UPDATE payments (admin only)."""
        await set_rls_context(db, seed_users["student1_id"], "student")
        result = await db.execute(text("""
            UPDATE payments SET status = 'approved'
            WHERE id = :pid RETURNING id
        """), {"pid": seed_users["payment1_id"]})
        # Should affect 0 rows (policy blocks the UPDATE)
        assert result.rowcount == 0


# ---------------------------------------------------------------------------
# Tests: Enrollment Isolation (Tier 1)
# ---------------------------------------------------------------------------

class TestEnrollmentRLS:
    """Verify enrollment visibility rules."""

    @pytest.mark.asyncio
    async def test_student_sees_own_enrollments(self, db, seed_users):
        """Student1 sees their enrollment."""
        await set_rls_context(db, seed_users["student1_id"], "student")
        result = await db.execute(text("SELECT id FROM enrollments"))
        rows = result.fetchall()
        assert len(rows) == 1
        assert str(rows[0].id) == seed_users["enrollment_id"]

    @pytest.mark.asyncio
    async def test_other_student_cannot_see_enrollment(self, db, seed_users):
        """Student2 cannot see Student1's enrollment."""
        await set_rls_context(db, seed_users["student2_id"], "student")
        result = await db.execute(text("SELECT id FROM enrollments"))
        rows = result.fetchall()
        assert len(rows) == 0

    @pytest.mark.asyncio
    async def test_teacher_sees_course_enrollments(self, db, seed_users):
        """Teacher can see enrollments for their courses."""
        await set_rls_context(db, seed_users["teacher_user_id"], "teacher")
        result = await db.execute(text("SELECT id FROM enrollments"))
        rows = result.fetchall()
        assert len(rows) >= 1

    @pytest.mark.asyncio
    async def test_student_cannot_insert_enrollment(self, db, seed_users):
        """Students cannot create enrollments (admin only via payment approval)."""
        await set_rls_context(db, seed_users["student1_id"], "student")
        with pytest.raises(Exception):
            await db.execute(text("""
                INSERT INTO enrollments (id, student_id, course_id, status)
                VALUES (:id, :sid, :cid, 'active')
            """), {
                "id": str(uuid.uuid4()),
                "sid": seed_users["student1_id"],
                "cid": seed_users["course_id"],
            })


# ---------------------------------------------------------------------------
# Tests: User Update Isolation (Tier 1)
# ---------------------------------------------------------------------------

class TestUserRLS:
    """Verify users can only modify their own records."""

    @pytest.mark.asyncio
    async def test_student_can_update_own_profile(self, db, seed_users):
        """Student can update their own bio."""
        await set_rls_context(db, seed_users["student1_id"], "student")
        result = await db.execute(text("""
            UPDATE users SET bio = 'Updated bio' WHERE id = :uid RETURNING id
        """), {"uid": seed_users["student1_id"]})
        assert result.rowcount == 1

    @pytest.mark.asyncio
    async def test_student_cannot_update_other_profile(self, db, seed_users):
        """Student cannot update another user's profile."""
        await set_rls_context(db, seed_users["student1_id"], "student")
        result = await db.execute(text("""
            UPDATE users SET bio = 'Hacked' WHERE id = :uid RETURNING id
        """), {"uid": seed_users["student2_id"]})
        assert result.rowcount == 0

    @pytest.mark.asyncio
    async def test_admin_can_update_any_profile(self, db, seed_users):
        """Admin can update any user's profile."""
        await set_rls_context(db, seed_users["admin_id"], "admin")
        result = await db.execute(text("""
            UPDATE users SET bio = 'Admin update' WHERE id = :uid RETURNING id
        """), {"uid": seed_users["student1_id"]})
        assert result.rowcount == 1

    @pytest.mark.asyncio
    async def test_student_cannot_delete_users(self, db, seed_users):
        """Students cannot delete users."""
        await set_rls_context(db, seed_users["student1_id"], "student")
        result = await db.execute(text("""
            DELETE FROM users WHERE id = :uid RETURNING id
        """), {"uid": seed_users["student2_id"]})
        assert result.rowcount == 0


# ---------------------------------------------------------------------------
# Tests: System Tables (Tier 4)
# ---------------------------------------------------------------------------

class TestSystemRLS:
    """Verify system table access controls."""

    @pytest.mark.asyncio
    async def test_student_cannot_read_audit_logs(self, db, seed_users):
        """Students cannot access audit logs."""
        await set_rls_context(db, seed_users["student1_id"], "student")
        result = await db.execute(text("SELECT id FROM audit_logs"))
        rows = result.fetchall()
        assert len(rows) == 0

    @pytest.mark.asyncio
    async def test_student_sees_only_public_settings(self, db, seed_users):
        """Students can only see public system settings."""
        await set_rls_context(db, seed_users["student1_id"], "student")
        result = await db.execute(text(
            "SELECT key, is_public FROM system_settings"
        ))
        rows = result.fetchall()
        for row in rows:
            assert row.is_public is True, f"Non-public setting '{row.key}' visible to student"

    @pytest.mark.asyncio
    async def test_student_cannot_modify_user_roles(self, db, seed_users):
        """Students cannot escalate privileges by inserting user_roles."""
        await set_rls_context(db, seed_users["student1_id"], "student")
        # Get admin role id
        result = await db.execute(text("SELECT id FROM roles WHERE name = 'admin'"))
        admin_role = result.one_or_none()
        if admin_role:
            with pytest.raises(Exception):
                await db.execute(text("""
                    INSERT INTO user_roles (id, user_id, role_id)
                    VALUES (:id, :uid, :rid)
                """), {
                    "id": str(uuid.uuid4()),
                    "uid": seed_users["student1_id"],
                    "rid": str(admin_role.id),
                })


# ---------------------------------------------------------------------------
# Tests: No-Context Behavior
# ---------------------------------------------------------------------------

class TestNoContextRLS:
    """Verify behavior when no RLS context is set (unauthenticated requests)."""

    @pytest.mark.asyncio
    async def test_no_context_cannot_see_payments(self, db, seed_users):
        """Without RLS context, no payments are visible."""
        await clear_rls_context(db)
        result = await db.execute(text("SELECT id FROM payments"))
        rows = result.fetchall()
        assert len(rows) == 0

    @pytest.mark.asyncio
    async def test_no_context_cannot_see_enrollments(self, db, seed_users):
        """Without RLS context, no enrollments are visible."""
        await clear_rls_context(db)
        result = await db.execute(text("SELECT id FROM enrollments"))
        rows = result.fetchall()
        assert len(rows) == 0

    @pytest.mark.asyncio
    async def test_no_context_can_see_active_courses(self, db, seed_users):
        """Without RLS context, active courses are visible (public catalog)."""
        await clear_rls_context(db)
        result = await db.execute(text(
            "SELECT id FROM courses WHERE is_active = true AND deleted_at IS NULL"
        ))
        rows = result.fetchall()
        # The seed creates an active course
        assert len(rows) >= 1


# ---------------------------------------------------------------------------
# Tests: Teacher Isolation (Tier 3)
# ---------------------------------------------------------------------------

class TestTeacherRLS:
    """Verify teachers can only see/edit their own courses."""

    @pytest.mark.asyncio
    async def test_teacher_sees_own_courses(self, db, seed_users):
        """Teacher can see their assigned course (active or not)."""
        await set_rls_context(db, seed_users["teacher_user_id"], "teacher")
        result = await db.execute(text(
            "SELECT id FROM courses WHERE id = :cid"
        ), {"cid": seed_users["course_id"]})
        rows = result.fetchall()
        assert len(rows) == 1

    @pytest.mark.asyncio
    async def test_teacher_cannot_see_other_teacher_courses(self, db, seed_users):
        """Teacher cannot see inactive courses from another teacher."""
        # Create a second teacher and an INACTIVE course
        other_teacher_uid = str(uuid.uuid4())
        other_teacher_pid = str(uuid.uuid4())
        other_course_id = str(uuid.uuid4())

        await set_rls_context(db, seed_users["admin_id"], "admin")
        await db.execute(text(
            "INSERT INTO users (id, email, username, password_hash, first_name, last_name, status) "
            "VALUES (:id, :email, :username, 'hash', 'Other', 'Teacher', 'active')"
        ), {"id": other_teacher_uid, "email": "other_teacher@test.com", "username": "other_teacher"})
        await db.execute(text(
            "INSERT INTO teachers (id, user_id, is_active) VALUES (:id, :uid, true)"
        ), {"id": other_teacher_pid, "uid": other_teacher_uid})
        await db.execute(text(
            "INSERT INTO courses (id, title, slug, description, teacher_id, price, is_active) "
            "VALUES (:id, 'Secret Course', :slug, 'hidden', :tid, 99.99, false)"
        ), {"id": other_course_id, "slug": f"secret-{uuid.uuid4().hex[:8]}", "tid": other_teacher_pid})

        # Switch to original teacher — should NOT see the inactive other course
        await set_rls_context(db, seed_users["teacher_user_id"], "teacher")
        result = await db.execute(text(
            "SELECT id FROM courses WHERE id = :cid"
        ), {"cid": other_course_id})
        rows = result.fetchall()
        assert len(rows) == 0, "Teacher should NOT see another teacher's inactive course"

    @pytest.mark.asyncio
    async def test_teacher_can_update_own_course(self, db, seed_users):
        """Teacher can update their own course."""
        await set_rls_context(db, seed_users["teacher_user_id"], "teacher")
        result = await db.execute(text(
            "UPDATE courses SET description = 'Updated' WHERE id = :cid RETURNING id"
        ), {"cid": seed_users["course_id"]})
        assert result.rowcount == 1

    @pytest.mark.asyncio
    async def test_teacher_cannot_create_courses(self, db, seed_users):
        """Teachers cannot INSERT courses (admin only)."""
        await set_rls_context(db, seed_users["teacher_user_id"], "teacher")
        with pytest.raises(Exception):
            await db.execute(text(
                "INSERT INTO courses (id, title, slug, description, teacher_id, price, is_active) "
                "VALUES (:id, 'Rogue Course', :slug, 'rogue', :tid, 0, true)"
            ), {
                "id": str(uuid.uuid4()),
                "slug": f"rogue-{uuid.uuid4().hex[:8]}",
                "tid": seed_users["teacher_profile_id"],
            })


# ---------------------------------------------------------------------------
# Tests: Registration Flow (user_roles_insert policy)
# ---------------------------------------------------------------------------

class TestRegistrationRLS:
    """Verify the registration flow works under RLS."""

    @pytest.mark.asyncio
    async def test_registration_can_assign_user_role(self, db, seed_users):
        """Registration (no RLS context) can assign the 'user' base role."""
        await clear_rls_context(db)
        new_user_id = str(uuid.uuid4())
        await db.execute(text(
            "INSERT INTO users (id, email, username, password_hash, first_name, last_name, status) "
            "VALUES (:id, :email, :username, 'hash', 'New', 'User', 'pending')"
        ), {"id": new_user_id, "email": f"new_{uuid.uuid4().hex[:6]}@test.com", "username": f"new_{uuid.uuid4().hex[:6]}"})

        # Get the 'user' role ID
        result = await db.execute(text("SELECT id FROM roles WHERE name = 'user'"))
        user_role = result.one_or_none()
        if user_role:
            # This should succeed — the policy allows 'user' role without context
            await db.execute(text(
                "INSERT INTO user_roles (id, user_id, role_id) VALUES (:id, :uid, :rid)"
            ), {"id": str(uuid.uuid4()), "uid": new_user_id, "rid": str(user_role.id)})

    @pytest.mark.asyncio
    async def test_registration_cannot_assign_admin_role(self, db, seed_users):
        """Registration (no RLS context) CANNOT assign the 'admin' role."""
        await clear_rls_context(db)
        new_user_id = str(uuid.uuid4())
        await db.execute(text(
            "INSERT INTO users (id, email, username, password_hash, first_name, last_name, status) "
            "VALUES (:id, :email, :username, 'hash', 'Evil', 'User', 'pending')"
        ), {"id": new_user_id, "email": f"evil_{uuid.uuid4().hex[:6]}@test.com", "username": f"evil_{uuid.uuid4().hex[:6]}"})

        result = await db.execute(text("SELECT id FROM roles WHERE name = 'admin'"))
        admin_role = result.one_or_none()
        if admin_role:
            with pytest.raises(Exception):
                await db.execute(text(
                    "INSERT INTO user_roles (id, user_id, role_id) VALUES (:id, :uid, :rid)"
                ), {"id": str(uuid.uuid4()), "uid": new_user_id, "rid": str(admin_role.id)})


# ---------------------------------------------------------------------------
# Tests: System Context (Worker)
# ---------------------------------------------------------------------------

class TestSystemContextRLS:
    """Verify the 'system' role used by the ARQ worker."""

    @pytest.mark.asyncio
    async def test_system_can_read_email_queue(self, db, seed_users):
        """System role can read email_queue."""
        await set_rls_context(db, "", "system")
        # Should not raise — system can SELECT from email_queue
        result = await db.execute(text("SELECT COUNT(*) FROM email_queue"))
        count = result.scalar()
        assert count is not None  # Just proves the query executes

    @pytest.mark.asyncio
    async def test_system_can_read_background_jobs(self, db, seed_users):
        """System role can read background_jobs."""
        await set_rls_context(db, "", "system")
        result = await db.execute(text("SELECT COUNT(*) FROM background_jobs"))
        count = result.scalar()
        assert count is not None

    @pytest.mark.asyncio
    async def test_student_cannot_read_email_queue(self, db, seed_users):
        """Students cannot access email_queue."""
        await set_rls_context(db, seed_users["student1_id"], "student")
        result = await db.execute(text("SELECT COUNT(*) FROM email_queue"))
        count = result.scalar()
        assert count == 0

    @pytest.mark.asyncio
    async def test_student_cannot_read_background_jobs(self, db, seed_users):
        """Students cannot access background_jobs."""
        await set_rls_context(db, seed_users["student1_id"], "student")
        result = await db.execute(text("SELECT COUNT(*) FROM background_jobs"))
        count = result.scalar()
        assert count == 0

