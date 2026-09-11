-- 018_course_classes_schedule_refactor.sql
-- Remove fixed dates from courses and course_classes.
-- Replace class datetime range with weekly recurring schedule (days_of_week + start_time/end_time).
-- Remove is_published and description from course_classes.
-- Auto-generate schedule_info from new structured fields.
-- Idempotent: all operations use IF EXISTS / IF NOT EXISTS.

BEGIN;

-- ── 1. Add new columns to course_classes ────────────────────────────────────
ALTER TABLE course_classes
    ADD COLUMN IF NOT EXISTS days_of_week JSONB NOT NULL DEFAULT '[]'::jsonb,
    ADD COLUMN IF NOT EXISTS start_time TIME NULL,
    ADD COLUMN IF NOT EXISTS end_time TIME NULL;

-- Ensure days_of_week is never null (default already set, but enforce)
ALTER TABLE course_classes ALTER COLUMN days_of_week SET DEFAULT '[]'::jsonb;

-- ── 2. Backfill legacy schedule data into new fields ──────────────────────
-- For any class that has starts_at/ends_at, derive a single day and time range.
-- This is best-effort; most legacy classes had schedule_info text already.
UPDATE course_classes
SET days_of_week = CASE
    WHEN starts_at IS NOT NULL THEN
        jsonb_build_array(
            lower(to_char(starts_at, 'dy'))
        )
    ELSE '[]'::jsonb
    END,
    start_time = starts_at::time,
    end_time = ends_at::time
WHERE (days_of_week = '[]'::jsonb OR days_of_week IS NULL)
  AND (starts_at IS NOT NULL OR ends_at IS NOT NULL);

-- ── 3. Regenerate schedule_info from structured fields where it was empty ──
UPDATE course_classes
SET schedule_info = COALESCE(
    NULLIF(schedule_info, ''),
    CASE
        WHEN days_of_week = '[]'::jsonb THEN NULL
        ELSE (
            array_to_string(
                ARRAY(
                    SELECT CASE v
                        WHEN 'mon' THEN 'Lunes'
                        WHEN 'tue' THEN 'Martes'
                        WHEN 'wed' THEN 'Miércoles'
                        WHEN 'thu' THEN 'Jueves'
                        WHEN 'fri' THEN 'Viernes'
                        WHEN 'sat' THEN 'Sábado'
                        WHEN 'sun' THEN 'Domingo'
                        ELSE v
                    END
                    FROM jsonb_array_elements_text(days_of_week) AS v
                ),
                ', '
            )
            || CASE
                WHEN start_time IS NOT NULL AND end_time IS NOT NULL
                THEN ' ' || to_char(start_time, 'HH24:MI') || '–' || to_char(end_time, 'HH24:MI')
                WHEN start_time IS NOT NULL
                THEN ' ' || to_char(start_time, 'HH24:MI')
                ELSE ''
            END
        )
    END
)
WHERE schedule_info IS NULL OR schedule_info = '';

-- ── 4. Drop RLS policies that depend on columns being removed ──────────
DROP POLICY IF EXISTS course_classes_public_read ON course_classes;

-- ── 5. Drop legacy columns from course_classes ────────────────────────────
ALTER TABLE course_classes
    DROP COLUMN IF EXISTS starts_at,
    DROP COLUMN IF EXISTS ends_at,
    DROP COLUMN IF EXISTS is_published,
    DROP COLUMN IF EXISTS description;

-- ── 6. Drop legacy columns from courses ───────────────────────────────────
ALTER TABLE courses
    DROP COLUMN IF EXISTS starts_at,
    DROP COLUMN IF EXISTS ends_at;

COMMIT;
