-- Migration 021: Unique constraint for class name per course
-- Ensures no two classes in the same course can have the same name

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'uq_course_class_name_per_course'
          AND conrelid = 'course_classes'::regclass
    ) THEN
        -- Clean up existing duplicates before adding constraint
        -- Keeps the oldest record and soft-deletes duplicates
        WITH duplicates AS (
            SELECT id,
                   ROW_NUMBER() OVER (
                       PARTITION BY course_id, name
                       ORDER BY created_at ASC, id ASC
                   ) AS rn
            FROM course_classes
            WHERE deleted_at IS NULL
        )
        UPDATE course_classes
        SET deleted_at = NOW()
        WHERE id IN (
            SELECT id FROM duplicates WHERE rn > 1
        );

        ALTER TABLE course_classes
        ADD CONSTRAINT uq_course_class_name_per_course
        UNIQUE (course_id, name);
    END IF;
END
$$;
