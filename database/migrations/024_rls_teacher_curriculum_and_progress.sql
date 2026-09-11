-- 024_rls_teacher_curriculum_and_progress.sql
-- RLS para el temario del docente (borrado de módulos/lecciones) y el progreso
-- de sus alumnos (UPDATE de enrollments).
--
-- Por qué existe: los endpoints
--   PUT/DELETE /courses/modules/{id}      (temario, docente del curso)
--   PUT/DELETE /courses/lessons/{id}      (temario, docente del curso)
--   PATCH /course-classes/{c}/students/{s}/progress   (progreso, docente de la clase)
-- se autorizan en la capa de aplicación (app/middlewares/rbac.py:
-- ensure_course_manager / ensure_class_manager). La política de 010 dejaba el
-- DELETE del temario y el UPDATE de `enrollments` solo a `is_admin()`, así que
-- con RLS forzado (DATABASE_RLS_URL, obligatorio en producción) esas escrituras
-- afectarían a 0 filas: la API respondería 204/200 sin haber cambiado nada.
--
-- No se tocan módulos/lecciones INSERT/UPDATE: el docente ya podía editarlos
-- desde 010. El coordinador gestiona clases (017), no temario — de ahí que las
-- políticas de modules/lessons sigan siendo admin + docente del curso.
--
-- Aplicar: python scripts/apply_migrations.py   (idempotente, tabla schema_migrations)

BEGIN;

-- ── modules: el docente del curso puede borrar sus módulos ─────────────────
DROP POLICY IF EXISTS modules_delete ON modules;
CREATE POLICY modules_delete ON modules FOR DELETE
    USING (
        is_admin()
        OR EXISTS (
            SELECT 1 FROM courses c
            JOIN teachers t ON t.id = c.teacher_id
            WHERE c.id = modules.course_id AND t.user_id = app_user_id()
        )
    );

-- ── lessons: el docente del curso puede borrar sus lecciones ───────────────
DROP POLICY IF EXISTS lessons_delete ON lessons;
CREATE POLICY lessons_delete ON lessons FOR DELETE
    USING (
        is_admin()
        OR EXISTS (
            SELECT 1 FROM modules m
            JOIN courses c ON c.id = m.course_id
            JOIN teachers t ON t.id = c.teacher_id
            WHERE m.id = lessons.module_id AND t.user_id = app_user_id()
        )
    );

-- ── enrollments: docente de la clase y coordinador ────────────────────────
-- SELECT: se añade el docente de la clase. Antes solo el titular del curso veía
-- las inscripciones, de modo que un docente con una clase asignada no veía su
-- propio listado de alumnos.
DROP POLICY IF EXISTS enrollments_select ON enrollments;
CREATE POLICY enrollments_select ON enrollments FOR SELECT
    USING (
        student_id = app_user_id()
        OR is_admin()
        OR EXISTS (
            SELECT 1 FROM courses c
            JOIN teachers t ON t.id = c.teacher_id
            WHERE c.id = enrollments.course_id AND t.user_id = app_user_id()
        )
        OR EXISTS (
            SELECT 1 FROM course_classes cc
            JOIN teachers t ON t.id = cc.teacher_id
            WHERE cc.id = enrollments.course_class_id AND t.user_id = app_user_id()
        )
        OR EXISTS (
            SELECT 1 FROM user_roles ur
            JOIN roles r ON r.id = ur.role_id
            WHERE ur.user_id = app_user_id() AND r.name = 'coordinator'
        )
    );

-- UPDATE: el progreso del alumno lo escribe quien imparte (docente del curso o
-- de la clase) y el coordinador, que también administra las clases.
DROP POLICY IF EXISTS enrollments_update ON enrollments;
CREATE POLICY enrollments_update ON enrollments FOR UPDATE
    USING (
        is_admin()
        OR EXISTS (
            SELECT 1 FROM courses c
            JOIN teachers t ON t.id = c.teacher_id
            WHERE c.id = enrollments.course_id AND t.user_id = app_user_id()
        )
        OR EXISTS (
            SELECT 1 FROM course_classes cc
            JOIN teachers t ON t.id = cc.teacher_id
            WHERE cc.id = enrollments.course_class_id AND t.user_id = app_user_id()
        )
        OR EXISTS (
            SELECT 1 FROM user_roles ur
            JOIN roles r ON r.id = ur.role_id
            WHERE ur.user_id = app_user_id() AND r.name = 'coordinator'
        )
    )
    WITH CHECK (
        is_admin()
        OR EXISTS (
            SELECT 1 FROM courses c
            JOIN teachers t ON t.id = c.teacher_id
            WHERE c.id = enrollments.course_id AND t.user_id = app_user_id()
        )
        OR EXISTS (
            SELECT 1 FROM course_classes cc
            JOIN teachers t ON t.id = cc.teacher_id
            WHERE cc.id = enrollments.course_class_id AND t.user_id = app_user_id()
        )
        OR EXISTS (
            SELECT 1 FROM user_roles ur
            JOIN roles r ON r.id = ur.role_id
            WHERE ur.user_id = app_user_id() AND r.name = 'coordinator'
        )
    );

COMMIT;
