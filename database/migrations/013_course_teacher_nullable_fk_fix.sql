-- ============================================================================-- CodeAcademy Pro — FK Fix: teacher_id nullable + ON DELETE SET NULL
-- Depends on: 011_fix_courses_teacher_fk.sql, 012_make_course_teacher_optional.sql
--
-- IDEMPOTENT: Safe to re-run. Detects current state before acting.
-- ============================================================================

BEGIN;

-- 1. Ensure teacher_id is nullable (idempotent)
ALTER TABLE courses ALTER COLUMN teacher_id DROP NOT NULL;

-- 2. Change ON DELETE from RESTRICT to SET NULL
--    If a teacher is deleted, their courses become unassigned (teacher_id = NULL)
--    instead of blocking the deletion.
DO $$
DECLARE
    fk_name TEXT;
    fk_action TEXT;
BEGIN
    -- Find the existing FK constraint name and action
    SELECT con.conname, (confupdtype::text || confdeltype::text) INTO fk_name, fk_action
    FROM pg_constraint con
    JOIN pg_class rel ON rel.oid = con.conrelid
    JOIN pg_class frel ON frel.oid = con.confrelid
    WHERE rel.relname = 'courses'
      AND con.contype = 'f'
      AND con.conkey = ARRAY[(
          SELECT a.attnum FROM pg_attribute a
          WHERE a.attrelid = rel.oid AND a.attname = 'teacher_id'
      )]
      AND frel.relname = 'teachers';

    IF fk_name IS NULL THEN
        RAISE NOTICE 'No FK found on courses.teacher_id. Creating new FK with ON DELETE SET NULL.';
        ALTER TABLE courses
            ADD CONSTRAINT fk_courses_teacher_id
            FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE SET NULL;
    ELSIF fk_action != 'SN' THEN  -- 'S' = SET, 'N' = NULL
        RAISE NOTICE 'Existing FK % has action % (not SET NULL). Replacing...', fk_name, fk_action;
        EXECUTE format('ALTER TABLE courses DROP CONSTRAINT %I', fk_name);
        ALTER TABLE courses
            ADD CONSTRAINT fk_courses_teacher_id
            FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE SET NULL;
    ELSE
        RAISE NOTICE 'FK % already has ON DELETE SET NULL. No changes needed.', fk_name;
    END IF;
END $$;

COMMIT;
