-- 025_enrollment_class_lifecycle_and_recording.sql
--
-- Cierra cuatro huecos del ciclo inscripción → clase → contenido:
--
--   0. `chk_payments_status` (001) sólo admitía pending | pending_review | approved |
--      rejected, pero el código escribe 'approved_pending_class' al aprobar un pago
--      cuando no hay clase con cupo: esa rama reventaba con violación de CHECK, así que
--      el admin no podía confirmar un pago de un curso sin clases (justo el caso del
--      curso recién creado). Aquí se amplía el CHECK a los estados que usa la API.
--
--   1. `enrollments` deja de existir sólo cuando hay clase con cupo. El pago aprobado
--      sin clase deja la inscripción en 'payment_approved' y el alumno ve el curso con
--      el aviso "en espera de asignación de clase" (antes no se creaba fila y el alumno
--      no veía nada). Los valores ya permitidos por chk_enrollments_status cubren el
--      ciclo completo: payment_pending_review → payment_approved → active, y
--      payment_rejected. No hace falta DDL: `course_class_id` ya era NULLABLE, así que
--      la inscripción puede nacer sin clase y recibirla después.
--
--   2. `course_classes.recording_url` (+ plataforma y marca de tiempo): el docente de la
--      clase publica la grabación de la sesión, además del enlace de la clase en vivo.
--
--   3. RLS: el docente de la clase podía LEER course_classes (017) pero no actualizar
--      sus propios enlaces; como las tablas tienen FORCE ROW LEVEL SECURITY, el
--      PATCH del enlace de clase habría afectado 0 filas sin error. Se le concede
--      UPDATE sobre las clases que imparte. Qué columnas puede tocar lo sigue
--      decidiendo la capa API (sólo expone meeting-url y recording-link); el WITH CHECK
--      impide que reasigne la clase a otro docente o la mueva de curso.

-- ── 1. Estados reales de pago (el CHECK de 001 se quedó corto) ──────────────

ALTER TABLE payments DROP CONSTRAINT IF EXISTS chk_payments_status;

ALTER TABLE payments
    ADD CONSTRAINT chk_payments_status CHECK (
        status IN (
            'pending',                 -- recién creado, sin comprobante
            'pending_review',          -- comprobante subido, esperando al admin
            'approved_pending_class',  -- cobrado: falta asignarle clase
            'approved',                -- cobrado y con clase
            'rejected'
        )
    );

-- ── 2. Grabación de la clase ────────────────────────────────────────────────

ALTER TABLE course_classes
    ADD COLUMN IF NOT EXISTS recording_platform    VARCHAR(50),
    ADD COLUMN IF NOT EXISTS recording_url         VARCHAR(500),
    ADD COLUMN IF NOT EXISTS recording_updated_at  TIMESTAMP WITH TIME ZONE;

COMMENT ON COLUMN course_classes.recording_url IS
    'Enlace a la grabación de la clase (la publica el docente de la clase o un admin).';

-- ── 2. RLS: el docente de la clase puede actualizar sus enlaces ─────────────

DROP POLICY IF EXISTS course_classes_teacher_update ON course_classes;

CREATE POLICY course_classes_teacher_update ON course_classes FOR UPDATE
    USING (
        deleted_at IS NULL
        AND EXISTS (
            SELECT 1 FROM teachers t
            WHERE t.id = course_classes.teacher_id
              AND t.user_id = app_user_id()
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM teachers t
            WHERE t.id = course_classes.teacher_id
              AND t.user_id = app_user_id()
        )
    );

-- ── 3. Verificación rápida (a mano, si se aplica una sola vez) ──────────────
--
--   SELECT column_name, data_type FROM information_schema.columns
--   WHERE table_name = 'course_classes' AND column_name LIKE 'recording%';
--
--   SELECT policyname, cmd FROM pg_policies
--   WHERE tablename = 'course_classes' ORDER BY policyname;
--
--   -- Inscripciones aprobadas sin clase (esperando asignación):
--   SELECT e.id, e.status, e.course_class_id, u.email
--   FROM enrollments e JOIN users u ON u.id = e.student_id
--   WHERE e.status = 'payment_approved';
