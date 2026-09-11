-- ============================================================================
-- CodeAcademy Pro — Schema Changes for New Payment Flow
-- Payment now has direct course_id (not only through enrollment).
-- enrollment_id becomes nullable (set only on approval).
-- ============================================================================

-- 1. Add course_id to payments (direct reference)
ALTER TABLE payments ADD COLUMN IF NOT EXISTS course_id UUID REFERENCES courses(id) ON DELETE RESTRICT;

-- 2. Make enrollment_id nullable
ALTER TABLE payments ALTER COLUMN enrollment_id DROP NOT NULL;

-- 3. Backfill course_id from existing enrollments (if any data exists)
UPDATE payments p
SET course_id = e.course_id
FROM enrollments e
WHERE p.enrollment_id = e.id
AND p.course_id IS NULL;

-- 4. Add index for the new column
CREATE INDEX IF NOT EXISTS ix_payments_student_course ON payments (student_id, course_id);
