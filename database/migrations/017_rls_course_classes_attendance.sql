-- 017_rls_course_classes_attendance.sql
-- RLS policies for course_classes and attendance_records.
-- NOTE: This migration is provided for completeness.
-- If RLS deployment is deferred, run it later; RBAC enforcement in endpoints
-- provides interim protection.

BEGIN;

-- Enable RLS on new tables
ALTER TABLE course_classes ENABLE ROW LEVEL SECURITY;
ALTER TABLE attendance_records ENABLE ROW LEVEL SECURITY;

-- course_classes policies
-- Admin: full access
CREATE POLICY course_classes_admin_all ON course_classes FOR ALL
    USING (is_admin()) WITH CHECK (is_admin());

-- Coordinator: can manage classes they created or all classes
CREATE POLICY course_classes_coordinator_manage ON course_classes FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM user_roles ur
            JOIN roles r ON r.id = ur.role_id
            WHERE ur.user_id = app_user_id() AND r.name = 'coordinator'
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM user_roles ur
            JOIN roles r ON r.id = ur.role_id
            WHERE ur.user_id = app_user_id() AND r.name = 'coordinator'
        )
    );

-- Teacher: can read classes assigned to them, update meeting_url
CREATE POLICY course_classes_teacher_read ON course_classes FOR SELECT
    USING (
        teacher_id IN (
            SELECT t.id FROM teachers t WHERE t.user_id = app_user_id()
        )
        OR is_admin()
        OR EXISTS (
            SELECT 1 FROM user_roles ur
            JOIN roles r ON r.id = ur.role_id
            WHERE ur.user_id = app_user_id() AND r.name = 'coordinator'
        )
    );

-- Public / student: can read published classes
CREATE POLICY course_classes_public_read ON course_classes FOR SELECT
    USING (is_published = TRUE OR is_admin());

-- attendance_records policies
-- Admin: full access
CREATE POLICY attendance_admin_all ON attendance_records FOR ALL
    USING (is_admin()) WITH CHECK (is_admin());

-- Teacher: can read/insert for their own classes
CREATE POLICY attendance_teacher_class ON attendance_records FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM course_classes cc
            JOIN teachers t ON t.id = cc.teacher_id
            WHERE cc.id = attendance_records.course_class_id
              AND t.user_id = app_user_id()
        )
        OR is_admin()
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM course_classes cc
            JOIN teachers t ON t.id = cc.teacher_id
            WHERE cc.id = attendance_records.course_class_id
              AND t.user_id = app_user_id()
        )
        OR is_admin()
    );

-- Student: can only see their own attendance
CREATE POLICY attendance_student_own ON attendance_records FOR SELECT
    USING (
        student_id = app_user_id()
        OR is_admin()
        OR EXISTS (
            SELECT 1 FROM course_classes cc
            JOIN teachers t ON t.id = cc.teacher_id
            WHERE cc.id = attendance_records.course_class_id
              AND t.user_id = app_user_id()
        )
    );

COMMIT;
