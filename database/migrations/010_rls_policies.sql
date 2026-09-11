-- ============================================================================
-- CodeAcademy Pro — RLS Policies
-- Enables RLS and creates per-table policies.
-- Depends on: 009_rls_role_and_functions.sql
--
-- Design principles:
--   • USING  → filters existing rows (SELECT, UPDATE target, DELETE target)
--   • WITH CHECK → validates new/modified rows (INSERT, UPDATE new values)
--   • Every table with RLS uses FORCE so even the table owner is subject to policies.
--   • Admin bypass is via is_admin() in every policy.
--   • Auth queries (get_current_user) run BEFORE SET LOCAL, so users/user_roles/roles
--     have permissive SELECT to avoid breaking authentication.
--
-- IDEMPOTENCY: This migration can be safely re-run. All existing policies are
-- dropped before being recreated.
-- ============================================================================

-- Drop all existing RLS policies created by this migration (idempotency).
DO $$
DECLARE
    pol RECORD;
BEGIN
    FOR pol IN
        SELECT policyname, tablename FROM pg_policies
        WHERE schemaname = 'public'
    LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON %I', pol.policyname, pol.tablename);
    END LOOP;
END $$;

-- ============================================================================
-- TIER 1 — IDENTITY TABLES
-- ============================================================================

-- ── users ──────────────────────────────────────────────────────────────────
-- SELECT is permissive because auth queries run before RLS context is set.
-- The application layer controls which fields are exposed in responses.
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE users FORCE ROW LEVEL SECURITY;

CREATE POLICY users_select ON users FOR SELECT
    USING (true);

CREATE POLICY users_insert ON users FOR INSERT
    WITH CHECK (
        is_admin()
        OR app_user_id() IS NULL  -- registration (no context yet)
    );

CREATE POLICY users_update ON users FOR UPDATE
    USING (id = app_user_id() OR is_admin())
    WITH CHECK (id = app_user_id() OR is_admin());

CREATE POLICY users_delete ON users FOR DELETE
    USING (is_admin());

-- ── roles ──────────────────────────────────────────────────────────────────
ALTER TABLE roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE roles FORCE ROW LEVEL SECURITY;

CREATE POLICY roles_select ON roles FOR SELECT
    USING (true);

CREATE POLICY roles_write ON roles FOR ALL
    USING (is_admin())
    WITH CHECK (is_admin());

-- ── user_roles ─────────────────────────────────────────────────────────────
ALTER TABLE user_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_roles FORCE ROW LEVEL SECURITY;

CREATE POLICY user_roles_select ON user_roles FOR SELECT
    USING (true);

CREATE POLICY user_roles_insert ON user_roles FOR INSERT
    WITH CHECK (
        is_admin()
        -- Allow registration flow (no context set) but ONLY for the base 'user' role.
        -- This prevents privilege escalation: an unauthenticated caller cannot
        -- assign admin/teacher roles to themselves.
        OR (
            app_user_id() IS NULL
            AND role_id IN (SELECT id FROM roles WHERE name = 'user')
        )
    );

CREATE POLICY user_roles_update ON user_roles FOR UPDATE
    USING (is_admin())
    WITH CHECK (is_admin());

CREATE POLICY user_roles_delete ON user_roles FOR DELETE
    USING (is_admin());

-- ── teachers ───────────────────────────────────────────────────────────────
ALTER TABLE teachers ENABLE ROW LEVEL SECURITY;
ALTER TABLE teachers FORCE ROW LEVEL SECURITY;

CREATE POLICY teachers_select ON teachers FOR SELECT
    USING (true);

CREATE POLICY teachers_insert ON teachers FOR INSERT
    WITH CHECK (is_admin());

CREATE POLICY teachers_update ON teachers FOR UPDATE
    USING (user_id = app_user_id() OR is_admin())
    WITH CHECK (user_id = app_user_id() OR is_admin());

CREATE POLICY teachers_delete ON teachers FOR DELETE
    USING (is_admin());

-- ── students ───────────────────────────────────────────────────────────────
ALTER TABLE students ENABLE ROW LEVEL SECURITY;
ALTER TABLE students FORCE ROW LEVEL SECURITY;

CREATE POLICY students_select ON students FOR SELECT
    USING (user_id = app_user_id() OR is_admin());

CREATE POLICY students_insert ON students FOR INSERT
    WITH CHECK (is_admin());

CREATE POLICY students_update ON students FOR UPDATE
    USING (user_id = app_user_id() OR is_admin())
    WITH CHECK (user_id = app_user_id() OR is_admin());

CREATE POLICY students_delete ON students FOR DELETE
    USING (is_admin());


-- ============================================================================
-- TIER 2 — FINANCIAL TABLES (CRITICAL)
-- ============================================================================

-- ── payments ───────────────────────────────────────────────────────────────
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments FORCE ROW LEVEL SECURITY;

CREATE POLICY payments_select ON payments FOR SELECT
    USING (student_id = app_user_id() OR is_admin());

CREATE POLICY payments_insert ON payments FOR INSERT
    WITH CHECK (student_id = app_user_id() OR is_admin());

CREATE POLICY payments_update ON payments FOR UPDATE
    USING (is_admin())
    WITH CHECK (is_admin());

CREATE POLICY payments_delete ON payments FOR DELETE
    USING (is_admin());

-- ── payment_proofs ─────────────────────────────────────────────────────────
ALTER TABLE payment_proofs ENABLE ROW LEVEL SECURITY;
ALTER TABLE payment_proofs FORCE ROW LEVEL SECURITY;

CREATE POLICY payment_proofs_select ON payment_proofs FOR SELECT
    USING (
        is_admin()
        OR EXISTS (
            SELECT 1 FROM payments p
            WHERE p.id = payment_proofs.payment_id
              AND p.student_id = app_user_id()
        )
    );

CREATE POLICY payment_proofs_insert ON payment_proofs FOR INSERT
    WITH CHECK (
        is_admin()
        OR EXISTS (
            SELECT 1 FROM payments p
            WHERE p.id = payment_proofs.payment_id
              AND p.student_id = app_user_id()
        )
    );

CREATE POLICY payment_proofs_update ON payment_proofs FOR UPDATE
    USING (is_admin())
    WITH CHECK (is_admin());

CREATE POLICY payment_proofs_delete ON payment_proofs FOR DELETE
    USING (is_admin());

-- ── enrollments ────────────────────────────────────────────────────────────
ALTER TABLE enrollments ENABLE ROW LEVEL SECURITY;
ALTER TABLE enrollments FORCE ROW LEVEL SECURITY;

CREATE POLICY enrollments_select ON enrollments FOR SELECT
    USING (
        student_id = app_user_id()
        OR is_admin()
        OR EXISTS (
            SELECT 1 FROM courses c
            JOIN teachers t ON t.id = c.teacher_id
            WHERE c.id = enrollments.course_id
              AND t.user_id = app_user_id()
        )
    );

CREATE POLICY enrollments_insert ON enrollments FOR INSERT
    WITH CHECK (is_admin());

CREATE POLICY enrollments_update ON enrollments FOR UPDATE
    USING (is_admin())
    WITH CHECK (is_admin());

CREATE POLICY enrollments_delete ON enrollments FOR DELETE
    USING (is_admin());

-- ── payment_settings ───────────────────────────────────────────────────────
ALTER TABLE payment_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE payment_settings FORCE ROW LEVEL SECURITY;

CREATE POLICY payment_settings_select ON payment_settings FOR SELECT
    USING (true);  -- public: students need to see bank info for payments

CREATE POLICY payment_settings_insert ON payment_settings FOR INSERT
    WITH CHECK (is_admin());

CREATE POLICY payment_settings_update ON payment_settings FOR UPDATE
    USING (is_admin())
    WITH CHECK (is_admin());

CREATE POLICY payment_settings_delete ON payment_settings FOR DELETE
    USING (is_admin());


-- ============================================================================
-- TIER 3 — ACADEMIC CONTENT
-- ============================================================================

-- ── courses ────────────────────────────────────────────────────────────────
-- Public: active courses visible to all. Inactive: only admin/assigned teacher.
ALTER TABLE courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE courses FORCE ROW LEVEL SECURITY;

CREATE POLICY courses_select ON courses FOR SELECT
    USING (
        (is_active = true AND deleted_at IS NULL)  -- public catalog
        OR is_admin()
        OR EXISTS (
            SELECT 1 FROM teachers t
            WHERE t.id = courses.teacher_id AND t.user_id = app_user_id()
        )
    );

CREATE POLICY courses_insert ON courses FOR INSERT
    WITH CHECK (is_admin());

CREATE POLICY courses_update ON courses FOR UPDATE
    USING (
        is_admin()
        OR EXISTS (
            SELECT 1 FROM teachers t
            WHERE t.id = courses.teacher_id AND t.user_id = app_user_id()
        )
    )
    WITH CHECK (
        is_admin()
        OR EXISTS (
            SELECT 1 FROM teachers t
            WHERE t.id = courses.teacher_id AND t.user_id = app_user_id()
        )
    );

CREATE POLICY courses_delete ON courses FOR DELETE
    USING (is_admin());

-- ── categories ─────────────────────────────────────────────────────────────
-- Fully public catalog — no RLS needed.

-- ── modules ────────────────────────────────────────────────────────────────
ALTER TABLE modules ENABLE ROW LEVEL SECURITY;
ALTER TABLE modules FORCE ROW LEVEL SECURITY;

CREATE POLICY modules_select ON modules FOR SELECT
    USING (
        is_admin()
        OR EXISTS (
            SELECT 1 FROM courses c
            JOIN teachers t ON t.id = c.teacher_id
            WHERE c.id = modules.course_id AND t.user_id = app_user_id()
        )
        OR EXISTS (
            SELECT 1 FROM enrollments e
            JOIN courses c ON c.id = e.course_id
            WHERE c.id = modules.course_id
              AND e.student_id = app_user_id()
              AND e.status = 'active'
        )
        OR EXISTS (
            SELECT 1 FROM courses c
            WHERE c.id = modules.course_id
              AND c.is_active = true AND c.deleted_at IS NULL
              AND modules.is_published = true
        )
    );

CREATE POLICY modules_insert ON modules FOR INSERT
    WITH CHECK (
        is_admin()
        OR EXISTS (
            SELECT 1 FROM courses c
            JOIN teachers t ON t.id = c.teacher_id
            WHERE c.id = modules.course_id AND t.user_id = app_user_id()
        )
    );

CREATE POLICY modules_update ON modules FOR UPDATE
    USING (
        is_admin()
        OR EXISTS (
            SELECT 1 FROM courses c
            JOIN teachers t ON t.id = c.teacher_id
            WHERE c.id = modules.course_id AND t.user_id = app_user_id()
        )
    )
    WITH CHECK (
        is_admin()
        OR EXISTS (
            SELECT 1 FROM courses c
            JOIN teachers t ON t.id = c.teacher_id
            WHERE c.id = modules.course_id AND t.user_id = app_user_id()
        )
    );

CREATE POLICY modules_delete ON modules FOR DELETE
    USING (is_admin());

-- ── lessons ────────────────────────────────────────────────────────────────
ALTER TABLE lessons ENABLE ROW LEVEL SECURITY;
ALTER TABLE lessons FORCE ROW LEVEL SECURITY;

CREATE POLICY lessons_select ON lessons FOR SELECT
    USING (
        is_admin()
        OR EXISTS (
            SELECT 1 FROM modules m
            JOIN courses c ON c.id = m.course_id
            JOIN teachers t ON t.id = c.teacher_id
            WHERE m.id = lessons.module_id AND t.user_id = app_user_id()
        )
        OR lessons.is_free = true
        OR EXISTS (
            SELECT 1 FROM modules m
            JOIN enrollments e ON e.course_id = m.course_id
            WHERE m.id = lessons.module_id
              AND e.student_id = app_user_id()
              AND e.status = 'active'
        )
        -- Published lessons of active courses are visible for public syllabus.
        -- The application layer controls which fields (title vs content) are exposed.
        OR EXISTS (
            SELECT 1 FROM modules m
            JOIN courses c ON c.id = m.course_id
            WHERE m.id = lessons.module_id
              AND c.is_active = true AND c.deleted_at IS NULL
              AND m.is_published = true
              AND lessons.is_published = true
        )
    );

CREATE POLICY lessons_insert ON lessons FOR INSERT
    WITH CHECK (
        is_admin()
        OR EXISTS (
            SELECT 1 FROM modules m
            JOIN courses c ON c.id = m.course_id
            JOIN teachers t ON t.id = c.teacher_id
            WHERE m.id = lessons.module_id AND t.user_id = app_user_id()
        )
    );

CREATE POLICY lessons_update ON lessons FOR UPDATE
    USING (
        is_admin()
        OR EXISTS (
            SELECT 1 FROM modules m
            JOIN courses c ON c.id = m.course_id
            JOIN teachers t ON t.id = c.teacher_id
            WHERE m.id = lessons.module_id AND t.user_id = app_user_id()
        )
    )
    WITH CHECK (
        is_admin()
        OR EXISTS (
            SELECT 1 FROM modules m
            JOIN courses c ON c.id = m.course_id
            JOIN teachers t ON t.id = c.teacher_id
            WHERE m.id = lessons.module_id AND t.user_id = app_user_id()
        )
    );

CREATE POLICY lessons_delete ON lessons FOR DELETE
    USING (is_admin());

-- ── live_classes ───────────────────────────────────────────────────────────
ALTER TABLE live_classes ENABLE ROW LEVEL SECURITY;
ALTER TABLE live_classes FORCE ROW LEVEL SECURITY;

CREATE POLICY live_classes_select ON live_classes FOR SELECT
    USING (
        is_admin()
        OR EXISTS (
            SELECT 1 FROM courses c
            JOIN teachers t ON t.id = c.teacher_id
            WHERE c.id = live_classes.course_id AND t.user_id = app_user_id()
        )
        OR EXISTS (
            SELECT 1 FROM enrollments e
            WHERE e.course_id = live_classes.course_id
              AND e.student_id = app_user_id()
              AND e.status = 'active'
        )
    );

CREATE POLICY live_classes_write ON live_classes FOR INSERT
    WITH CHECK (
        is_admin()
        OR EXISTS (
            SELECT 1 FROM courses c
            JOIN teachers t ON t.id = c.teacher_id
            WHERE c.id = live_classes.course_id AND t.user_id = app_user_id()
        )
    );

CREATE POLICY live_classes_update ON live_classes FOR UPDATE
    USING (
        is_admin()
        OR EXISTS (
            SELECT 1 FROM courses c
            JOIN teachers t ON t.id = c.teacher_id
            WHERE c.id = live_classes.course_id AND t.user_id = app_user_id()
        )
    );

CREATE POLICY live_classes_delete ON live_classes FOR DELETE
    USING (is_admin());

-- ── recorded_classes ───────────────────────────────────────────────────────
ALTER TABLE recorded_classes ENABLE ROW LEVEL SECURITY;
ALTER TABLE recorded_classes FORCE ROW LEVEL SECURITY;

CREATE POLICY recorded_classes_select ON recorded_classes FOR SELECT
    USING (
        is_admin()
        OR EXISTS (
            SELECT 1 FROM lessons l
            JOIN modules m ON m.id = l.module_id
            JOIN courses c ON c.id = m.course_id
            JOIN teachers t ON t.id = c.teacher_id
            WHERE l.id = recorded_classes.lesson_id AND t.user_id = app_user_id()
        )
        OR EXISTS (
            SELECT 1 FROM lessons l
            JOIN modules m ON m.id = l.module_id
            JOIN enrollments e ON e.course_id = m.course_id
            WHERE l.id = recorded_classes.lesson_id
              AND e.student_id = app_user_id()
              AND e.status = 'active'
        )
    );

CREATE POLICY recorded_classes_write ON recorded_classes FOR INSERT
    WITH CHECK (
        is_admin()
        OR EXISTS (
            SELECT 1 FROM lessons l
            JOIN modules m ON m.id = l.module_id
            JOIN courses c ON c.id = m.course_id
            JOIN teachers t ON t.id = c.teacher_id
            WHERE l.id = recorded_classes.lesson_id AND t.user_id = app_user_id()
        )
    );

CREATE POLICY recorded_classes_update ON recorded_classes FOR UPDATE
    USING (
        is_admin()
        OR EXISTS (
            SELECT 1 FROM lessons l
            JOIN modules m ON m.id = l.module_id
            JOIN courses c ON c.id = m.course_id
            JOIN teachers t ON t.id = c.teacher_id
            WHERE l.id = recorded_classes.lesson_id AND t.user_id = app_user_id()
        )
    );

CREATE POLICY recorded_classes_delete ON recorded_classes FOR DELETE
    USING (is_admin());


-- ============================================================================
-- TIER 4 — PROGRESS & EVALUATIONS
-- ============================================================================

-- ── student_progress ───────────────────────────────────────────────────────
ALTER TABLE student_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_progress FORCE ROW LEVEL SECURITY;

CREATE POLICY student_progress_select ON student_progress FOR SELECT
    USING (
        student_id = app_user_id()
        OR is_admin()
        OR EXISTS (
            SELECT 1 FROM enrollments e
            JOIN courses c ON c.id = e.course_id
            JOIN teachers t ON t.id = c.teacher_id
            WHERE e.id = student_progress.enrollment_id
              AND t.user_id = app_user_id()
        )
    );

CREATE POLICY student_progress_insert ON student_progress FOR INSERT
    WITH CHECK (student_id = app_user_id() OR is_admin());

CREATE POLICY student_progress_update ON student_progress FOR UPDATE
    USING (student_id = app_user_id() OR is_admin())
    WITH CHECK (student_id = app_user_id() OR is_admin());

CREATE POLICY student_progress_delete ON student_progress FOR DELETE
    USING (is_admin());

-- ── student_ratings ────────────────────────────────────────────────────────
ALTER TABLE student_ratings ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_ratings FORCE ROW LEVEL SECURITY;

CREATE POLICY student_ratings_select ON student_ratings FOR SELECT
    USING (
        student_id = app_user_id()
        OR teacher_id = app_user_id()
        OR is_admin()
    );

CREATE POLICY student_ratings_insert ON student_ratings FOR INSERT
    WITH CHECK (teacher_id = app_user_id() OR is_admin());

CREATE POLICY student_ratings_update ON student_ratings FOR UPDATE
    USING (teacher_id = app_user_id() OR is_admin())
    WITH CHECK (teacher_id = app_user_id() OR is_admin());

CREATE POLICY student_ratings_delete ON student_ratings FOR DELETE
    USING (is_admin());

-- ── student_highlights ─────────────────────────────────────────────────────
ALTER TABLE student_highlights ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_highlights FORCE ROW LEVEL SECURITY;

CREATE POLICY student_highlights_select ON student_highlights FOR SELECT
    USING (
        student_id = app_user_id()
        OR marked_by = app_user_id()
        OR is_admin()
    );

CREATE POLICY student_highlights_insert ON student_highlights FOR INSERT
    WITH CHECK (is_admin() OR marked_by = app_user_id());

CREATE POLICY student_highlights_update ON student_highlights FOR UPDATE
    USING (is_admin())
    WITH CHECK (is_admin());

CREATE POLICY student_highlights_delete ON student_highlights FOR DELETE
    USING (is_admin());

-- ── certificates ───────────────────────────────────────────────────────────
ALTER TABLE certificates ENABLE ROW LEVEL SECURITY;
ALTER TABLE certificates FORCE ROW LEVEL SECURITY;

CREATE POLICY certificates_select ON certificates FOR SELECT
    USING (student_id = app_user_id() OR is_admin());

CREATE POLICY certificates_insert ON certificates FOR INSERT
    WITH CHECK (is_admin());

CREATE POLICY certificates_update ON certificates FOR UPDATE
    USING (is_admin())
    WITH CHECK (is_admin());

CREATE POLICY certificates_delete ON certificates FOR DELETE
    USING (is_admin());

-- ── reviews ────────────────────────────────────────────────────────────────
ALTER TABLE reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE reviews FORCE ROW LEVEL SECURITY;

CREATE POLICY reviews_select ON reviews FOR SELECT
    USING (is_visible = true OR student_id = app_user_id() OR is_admin());

CREATE POLICY reviews_insert ON reviews FOR INSERT
    WITH CHECK (student_id = app_user_id());

CREATE POLICY reviews_update ON reviews FOR UPDATE
    USING (student_id = app_user_id() OR is_admin())
    WITH CHECK (student_id = app_user_id() OR is_admin());

CREATE POLICY reviews_delete ON reviews FOR DELETE
    USING (student_id = app_user_id() OR is_admin());


-- ============================================================================
-- TIER 5 — COMMUNICATION & SYSTEM
-- ============================================================================

-- ── notifications ──────────────────────────────────────────────────────────
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications FORCE ROW LEVEL SECURITY;

CREATE POLICY notifications_select ON notifications FOR SELECT
    USING (user_id = app_user_id() OR is_admin());

CREATE POLICY notifications_insert ON notifications FOR INSERT
    WITH CHECK (is_admin() OR app_user_role() = 'system');

CREATE POLICY notifications_update ON notifications FOR UPDATE
    USING (user_id = app_user_id() OR is_admin())
    WITH CHECK (user_id = app_user_id() OR is_admin());

CREATE POLICY notifications_delete ON notifications FOR DELETE
    USING (user_id = app_user_id() OR is_admin());

-- ── suggestions ────────────────────────────────────────────────────────────
ALTER TABLE suggestions ENABLE ROW LEVEL SECURITY;
ALTER TABLE suggestions FORCE ROW LEVEL SECURITY;

CREATE POLICY suggestions_select ON suggestions FOR SELECT
    USING (user_id = app_user_id() OR is_admin());

CREATE POLICY suggestions_insert ON suggestions FOR INSERT
    WITH CHECK (user_id = app_user_id());

CREATE POLICY suggestions_update ON suggestions FOR UPDATE
    USING (is_admin())
    WITH CHECK (is_admin());

CREATE POLICY suggestions_delete ON suggestions FOR DELETE
    USING (is_admin());

-- ── audit_logs ─────────────────────────────────────────────────────────────
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs FORCE ROW LEVEL SECURITY;

CREATE POLICY audit_logs_select ON audit_logs FOR SELECT
    USING (is_admin());

CREATE POLICY audit_logs_insert ON audit_logs FOR INSERT
    WITH CHECK (true);  -- any authenticated action can create audit entries

-- No UPDATE/DELETE policies — audit logs are immutable.

-- ── system_settings ────────────────────────────────────────────────────────
ALTER TABLE system_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_settings FORCE ROW LEVEL SECURITY;

CREATE POLICY system_settings_select ON system_settings FOR SELECT
    USING (is_public = true OR is_admin());

CREATE POLICY system_settings_insert ON system_settings FOR INSERT
    WITH CHECK (is_admin());

CREATE POLICY system_settings_update ON system_settings FOR UPDATE
    USING (is_admin())
    WITH CHECK (is_admin());

CREATE POLICY system_settings_delete ON system_settings FOR DELETE
    USING (is_admin());

-- ── feature_flags ──────────────────────────────────────────────────────────
ALTER TABLE feature_flags ENABLE ROW LEVEL SECURITY;
ALTER TABLE feature_flags FORCE ROW LEVEL SECURITY;

CREATE POLICY feature_flags_select ON feature_flags FOR SELECT
    USING (true);  -- flags are read by the app for feature gating

CREATE POLICY feature_flags_insert ON feature_flags FOR INSERT
    WITH CHECK (is_admin());

CREATE POLICY feature_flags_update ON feature_flags FOR UPDATE
    USING (is_admin())
    WITH CHECK (is_admin());

CREATE POLICY feature_flags_delete ON feature_flags FOR DELETE
    USING (is_admin());

-- ── content_versions ───────────────────────────────────────────────────────
ALTER TABLE content_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_versions FORCE ROW LEVEL SECURITY;

CREATE POLICY content_versions_select ON content_versions FOR SELECT
    USING (changed_by = app_user_id() OR is_admin());

CREATE POLICY content_versions_insert ON content_versions FOR INSERT
    WITH CHECK (changed_by = app_user_id() OR is_admin());

-- No UPDATE/DELETE — versions are immutable.

-- ── email_queue ────────────────────────────────────────────────────────────
ALTER TABLE email_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_queue FORCE ROW LEVEL SECURITY;

CREATE POLICY email_queue_select ON email_queue FOR SELECT
    USING (is_admin() OR app_user_role() = 'system');

CREATE POLICY email_queue_insert ON email_queue FOR INSERT
    WITH CHECK (true);  -- any service can enqueue emails

CREATE POLICY email_queue_update ON email_queue FOR UPDATE
    USING (is_admin() OR app_user_role() = 'system');

CREATE POLICY email_queue_delete ON email_queue FOR DELETE
    USING (is_admin());

-- ── background_jobs ────────────────────────────────────────────────────────
ALTER TABLE background_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE background_jobs FORCE ROW LEVEL SECURITY;

CREATE POLICY background_jobs_select ON background_jobs FOR SELECT
    USING (is_admin() OR app_user_role() = 'system');

CREATE POLICY background_jobs_insert ON background_jobs FOR INSERT
    WITH CHECK (true);  -- any service can create jobs

CREATE POLICY background_jobs_update ON background_jobs FOR UPDATE
    USING (is_admin() OR app_user_role() = 'system');

CREATE POLICY background_jobs_delete ON background_jobs FOR DELETE
    USING (is_admin());

-- ── file_uploads ───────────────────────────────────────────────────────────
ALTER TABLE file_uploads ENABLE ROW LEVEL SECURITY;
ALTER TABLE file_uploads FORCE ROW LEVEL SECURITY;

CREATE POLICY file_uploads_select ON file_uploads FOR SELECT
    USING (
        is_public = true
        OR uploaded_by = app_user_id()
        OR is_admin()
    );

CREATE POLICY file_uploads_insert ON file_uploads FOR INSERT
    WITH CHECK (uploaded_by = app_user_id() OR is_admin());

CREATE POLICY file_uploads_update ON file_uploads FOR UPDATE
    USING (uploaded_by = app_user_id() OR is_admin())
    WITH CHECK (uploaded_by = app_user_id() OR is_admin());

CREATE POLICY file_uploads_delete ON file_uploads FOR DELETE
    USING (uploaded_by = app_user_id() OR is_admin());


-- ============================================================================
-- VERIFICATION: List all tables with RLS enabled
-- ============================================================================
DO $$
DECLARE
    r RECORD;
    cnt INTEGER := 0;
BEGIN
    FOR r IN
        SELECT relname FROM pg_class
        WHERE relrowsecurity = true AND relnamespace = 'public'::regnamespace
        ORDER BY relname
    LOOP
        RAISE NOTICE 'RLS enabled on: %', r.relname;
        cnt := cnt + 1;
    END LOOP;
    RAISE NOTICE 'Total tables with RLS: %', cnt;
END $$;
