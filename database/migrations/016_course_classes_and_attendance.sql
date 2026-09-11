-- 016_course_classes_and_attendance.sql
-- Phase 1: New academic/commercial architecture
-- Creates course_classes, attendance_records, adds columns to courses/enrollments/payments,
-- adds coordinator role, creates global_max_students_per_class setting.
-- Backfills existing data safely.
-- NOTE: Reordered so course_classes is created before enrollments references it.

BEGIN;

-- ── 1. Add new columns to courses ───────────────────────────────────────────
ALTER TABLE courses
    ADD COLUMN IF NOT EXISTS duration_months INTEGER,
    ADD COLUMN IF NOT EXISTS full_payment_discount_pct NUMERIC(5,2) DEFAULT 0;

-- NOTE: existing columns teacher_id, max_students, starts_at, ends_at are kept
-- as legacy/deprecated but no longer used as source of truth.

-- ── 2. Create course_classes table (MUST exist before enrollments FK) ───────
CREATE TABLE IF NOT EXISTS course_classes (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id          UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    teacher_id         UUID REFERENCES teachers(id) ON DELETE SET NULL,
    created_by         UUID REFERENCES users(id) ON DELETE SET NULL,
    name               VARCHAR(255) NOT NULL,
    slug               VARCHAR(120) UNIQUE NOT NULL,
    description        TEXT,
    schedule_info      VARCHAR(500),
    starts_at          TIMESTAMPTZ,
    ends_at            TIMESTAMPTZ,
    status             VARCHAR(20) DEFAULT 'active',
    meeting_platform   VARCHAR(50),
    meeting_url        VARCHAR(500),
    is_published       BOOLEAN DEFAULT FALSE,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_course_classes_course_id ON course_classes(course_id);
CREATE INDEX IF NOT EXISTS ix_course_classes_teacher_id ON course_classes(teacher_id);
CREATE INDEX IF NOT EXISTS ix_course_classes_status ON course_classes(status);
CREATE INDEX IF NOT EXISTS ix_course_classes_created_by ON course_classes(created_by);

-- Trigger helper function (used by course_classes and attendance_records)
CREATE OR REPLACE FUNCTION update_course_classes_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_course_classes_updated_at ON course_classes;
CREATE TRIGGER trg_course_classes_updated_at
    BEFORE UPDATE ON course_classes
    FOR EACH ROW
    EXECUTE FUNCTION update_course_classes_updated_at();

-- ── 3. Add new columns to enrollments (course_classes now exists) ───────────
ALTER TABLE enrollments
    ADD COLUMN IF NOT EXISTS course_class_id UUID REFERENCES course_classes(id) ON DELETE SET NULL;

-- ── 4. Add new columns to payments ──────────────────────────────────────────
ALTER TABLE payments
    ADD COLUMN IF NOT EXISTS payment_plan VARCHAR(20) DEFAULT 'full',
    ADD COLUMN IF NOT EXISTS expected_amount NUMERIC(10,2),
    ADD COLUMN IF NOT EXISTS duration_months INTEGER,
    ADD COLUMN IF NOT EXISTS monthly_amount NUMERIC(10,2),
    ADD COLUMN IF NOT EXISTS full_amount NUMERIC(10,2);

-- ── 5. Create attendance_records table ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS attendance_records (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_class_id  UUID NOT NULL REFERENCES course_classes(id) ON DELETE CASCADE,
    student_id       UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    teacher_id       UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    session_date     DATE NOT NULL,
    status           VARCHAR(20) NOT NULL DEFAULT 'present',
    notes            TEXT,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_attendance_class_student_date UNIQUE (course_class_id, student_id, session_date)
);

CREATE INDEX IF NOT EXISTS ix_attendance_course_class_session ON attendance_records(course_class_id, session_date);
CREATE INDEX IF NOT EXISTS ix_attendance_student ON attendance_records(student_id);
CREATE INDEX IF NOT EXISTS ix_attendance_teacher ON attendance_records(teacher_id);

-- Trigger for updated_at on attendance_records
DROP TRIGGER IF EXISTS trg_attendance_records_updated_at ON attendance_records;
CREATE TRIGGER trg_attendance_records_updated_at
    BEFORE UPDATE ON attendance_records
    FOR EACH ROW
    EXECUTE FUNCTION update_course_classes_updated_at();

-- ── 6. Backfill: create default classes for courses with enrollments ────────
-- For each course that has at least one enrollment, create a default class
-- copying legacy teacher_id, starts_at, ends_at if present.
-- Idempotent: skips if a default class slug already exists for the course.
INSERT INTO course_classes (
    course_id, teacher_id, name, slug, description,
    starts_at, ends_at, status, is_published, created_at, updated_at
)
SELECT
    c.id,
    c.teacher_id,
    COALESCE(c.title || ' — Clase Principal', 'Clase Principal'),
    COALESCE(c.slug || '-clase-principal', gen_random_uuid()::text),
    'Clase default migrada automáticamente desde datos del curso.',
    c.starts_at,
    c.ends_at,
    'active',
    c.is_active,
    NOW(),
    NOW()
FROM courses c
WHERE c.deleted_at IS NULL
  AND EXISTS (
      SELECT 1 FROM enrollments e
      WHERE e.course_id = c.id AND e.status = 'active'
  )
  AND NOT EXISTS (
      SELECT 1 FROM course_classes cc
      WHERE cc.course_id = c.id AND cc.slug = c.slug || '-clase-principal'
  );

-- ── 7. Backfill: assign existing enrollments to default classes ────────────
UPDATE enrollments e
SET course_class_id = cc.id
FROM course_classes cc
WHERE e.course_id = cc.course_id
  AND cc.slug LIKE '%-clase-principal'
  AND e.course_class_id IS NULL;

-- ── 8. Add index on enrollments.course_class_id ─────────────────────────────
CREATE INDEX IF NOT EXISTS ix_enrollments_course_class_id ON enrollments(course_class_id);

-- ── 9. Add coordinator role ───────────────────────────────────────────────
INSERT INTO roles (id, name, description)
VALUES (
    gen_random_uuid(),
    'coordinator',
    'Coordinador académico — crea clases, asigna docentes, gestiona cupos y envía alertas'
)
ON CONFLICT (name) DO NOTHING;

-- ── 10. Create global_max_students_per_class setting ──────────────────────
-- Copy value from existing global_max_students_per_course if it exists
INSERT INTO system_settings (id, key, value, description, is_public)
SELECT
    gen_random_uuid(),
    'global_max_students_per_class',
    value,
    'Máximo global de alumnos por clase/grupo',
    TRUE
FROM system_settings
WHERE key = 'global_max_students_per_course'
  AND NOT EXISTS (
      SELECT 1 FROM system_settings WHERE key = 'global_max_students_per_class'
  )
UNION ALL
SELECT
    gen_random_uuid(),
    'global_max_students_per_class',
    '100',
    'Máximo global de alumnos por clase/grupo',
    TRUE
WHERE NOT EXISTS (
    SELECT 1 FROM system_settings WHERE key = 'global_max_students_per_class'
)
  AND NOT EXISTS (
      SELECT 1 FROM system_settings WHERE key = 'global_max_students_per_course'
  );

-- Ensure the new key is public
UPDATE system_settings
SET is_public = TRUE
WHERE key = 'global_max_students_per_class';

-- Keep old key for backward compatibility (do NOT delete)

-- ── 11. Update existing payments to mark payment_plan ────────────────────────
UPDATE payments
SET payment_plan = 'full'
WHERE payment_plan IS NULL;

COMMIT;
