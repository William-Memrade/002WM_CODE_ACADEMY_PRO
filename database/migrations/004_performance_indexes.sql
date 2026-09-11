-- ============================================================================
-- CodeAcademy Pro — Performance Optimization Indexes
-- Run after 002_indexes.sql
-- These indexes match the ORM model definitions for optimal query performance.
-- ============================================================================

-- Users: status field (replaces the old is_active column)
CREATE INDEX IF NOT EXISTS ix_users_status ON users(status);
CREATE INDEX IF NOT EXISTS ix_users_status_deleted ON users(status, deleted_at);

-- User Roles: composite unique index for role checking
CREATE UNIQUE INDEX IF NOT EXISTS ix_user_roles_user_role ON user_roles(user_id, role_id);

-- Enrollments: composite index for student-course lookups
CREATE INDEX IF NOT EXISTS ix_enrollments_student_course ON enrollments(student_id, course_id);

-- Courses: composite index for active catalog queries
CREATE INDEX IF NOT EXISTS ix_courses_active_deleted ON courses(is_active, deleted_at);

-- Payments: enrollment lookup
CREATE INDEX IF NOT EXISTS ix_payments_enrollment ON payments(enrollment_id);
