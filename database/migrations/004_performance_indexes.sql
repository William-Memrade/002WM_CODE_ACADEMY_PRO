-- ============================================================================
-- CodeAcademy Pro — Performance Optimization Indexes
-- Run after 002_indexes.sql
-- These indexes match the ORM model definitions for optimal query performance.
-- ============================================================================

-- Users: status field (replaces the old is_active column)
--
-- OJO: users.status NO lo crea esta migración. La agrega
-- 023_add_users_status.sql, que corre después. En una base nueva la columna
-- todavía no existe, así que los índices van guardados para que la cadena no se
-- rompa acá (antes fallaba con: column "status" does not exist).
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
         WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'status'
    ) THEN
        EXECUTE 'CREATE INDEX IF NOT EXISTS ix_users_status ON users(status)';
        EXECUTE 'CREATE INDEX IF NOT EXISTS ix_users_status_deleted ON users(status, deleted_at)';
    END IF;
END $$;

-- User Roles: composite unique index for role checking
CREATE UNIQUE INDEX IF NOT EXISTS ix_user_roles_user_role ON user_roles(user_id, role_id);

-- Enrollments: composite index for student-course lookups
CREATE INDEX IF NOT EXISTS ix_enrollments_student_course ON enrollments(student_id, course_id);

-- Courses: composite index for active catalog queries
CREATE INDEX IF NOT EXISTS ix_courses_active_deleted ON courses(is_active, deleted_at);

-- Payments: enrollment lookup
CREATE INDEX IF NOT EXISTS ix_payments_enrollment ON payments(enrollment_id);
