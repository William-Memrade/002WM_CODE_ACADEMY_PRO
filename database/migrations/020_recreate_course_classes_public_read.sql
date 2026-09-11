-- 020_recreate_course_classes_public_read.sql
-- Re-create the public read RLS policy for course_classes after is_published was removed.
-- Safe and idempotent.

BEGIN;

DROP POLICY IF EXISTS course_classes_public_read ON course_classes;

CREATE POLICY course_classes_public_read ON course_classes
FOR SELECT
USING (
    (status = 'active' AND deleted_at IS NULL)
    OR is_admin()
);

COMMIT;
