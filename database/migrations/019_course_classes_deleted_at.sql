-- 019_course_classes_deleted_at.sql
-- Add soft delete support to course_classes
-- Safe and idempotent

BEGIN;

ALTER TABLE course_classes
    ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ NULL;

-- Ensure existing rows have NULL deleted_at (already default, but explicit)
UPDATE course_classes SET deleted_at = NULL WHERE deleted_at IS NOT NULL AND status != 'deleted';

COMMIT;
