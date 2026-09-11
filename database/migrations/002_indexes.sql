-- ============================================================================
-- CodeAcademy Pro — Optimized Indexes
-- Run after 001_initial_schema.sql
-- ============================================================================

-- ============================================================================
-- USERS — Search and filter indexes
-- ============================================================================
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_is_active ON users(is_active) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_is_blocked ON users(is_blocked) WHERE is_blocked = TRUE;
CREATE INDEX idx_users_deleted_at ON users(deleted_at) WHERE deleted_at IS NOT NULL;
CREATE INDEX idx_users_created_at ON users(created_at);

-- ============================================================================
-- USER_ROLES — FK indexes + role lookup
-- ============================================================================
CREATE INDEX idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX idx_user_roles_role_id ON user_roles(role_id);

-- ============================================================================
-- CATEGORIES — Lookup indexes
-- ============================================================================
CREATE INDEX idx_categories_slug ON categories(slug);
CREATE INDEX idx_categories_is_active ON categories(is_active) WHERE is_active = TRUE;

-- ============================================================================
-- COURSES — Search, filter, and sort indexes
-- ============================================================================
CREATE INDEX idx_courses_slug ON courses(slug);
CREATE INDEX idx_courses_category_id ON courses(category_id);
CREATE INDEX idx_courses_teacher_id ON courses(teacher_id);
CREATE INDEX idx_courses_is_active ON courses(is_active) WHERE deleted_at IS NULL;
CREATE INDEX idx_courses_level ON courses(level);
CREATE INDEX idx_courses_price ON courses(price);
CREATE INDEX idx_courses_is_featured ON courses(is_featured) WHERE is_featured = TRUE;
CREATE INDEX idx_courses_created_at ON courses(created_at);
CREATE INDEX idx_courses_deleted_at ON courses(deleted_at) WHERE deleted_at IS NOT NULL;
-- Composite: active courses sorted by creation (frequent query for catalog)
CREATE INDEX idx_courses_active_created ON courses(created_at DESC)
    WHERE is_active = TRUE AND deleted_at IS NULL;

-- ============================================================================
-- MODULES — Sort and lookup
-- ============================================================================
CREATE INDEX idx_modules_course_id ON modules(course_id);
CREATE INDEX idx_modules_sort_order ON modules(course_id, sort_order);

-- ============================================================================
-- LESSONS — Sort and lookup
-- ============================================================================
CREATE INDEX idx_lessons_module_id ON lessons(module_id);
CREATE INDEX idx_lessons_sort_order ON lessons(module_id, sort_order);

-- ============================================================================
-- LIVE_CLASSES — Schedule and status lookup
-- ============================================================================
CREATE INDEX idx_live_classes_course_id ON live_classes(course_id);
CREATE INDEX idx_live_classes_scheduled_at ON live_classes(scheduled_at);
CREATE INDEX idx_live_classes_status ON live_classes(status);
-- Composite: upcoming scheduled classes (frequent query)
CREATE INDEX idx_live_classes_upcoming ON live_classes(scheduled_at)
    WHERE status = 'scheduled';

-- ============================================================================
-- RECORDED_CLASSES — Lesson lookup
-- ============================================================================
CREATE INDEX idx_recorded_classes_lesson_id ON recorded_classes(lesson_id);

-- ============================================================================
-- ENROLLMENTS — Critical queries for dashboards
-- ============================================================================
CREATE INDEX idx_enrollments_student_id ON enrollments(student_id);
CREATE INDEX idx_enrollments_course_id ON enrollments(course_id);
CREATE INDEX idx_enrollments_status ON enrollments(status);
-- Composite: active enrollments for a student (frequent query)
CREATE INDEX idx_enrollments_student_active ON enrollments(student_id)
    WHERE status IN ('active', 'payment_approved');
-- Composite: popular courses (count enrollments per course)
CREATE INDEX idx_enrollments_course_count ON enrollments(course_id)
    WHERE status NOT IN ('cancelled', 'expired');

-- ============================================================================
-- PAYMENTS — Admin review workflow
-- ============================================================================
CREATE INDEX idx_payments_enrollment_id ON payments(enrollment_id);
CREATE INDEX idx_payments_student_id ON payments(student_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_reviewed_by ON payments(reviewed_by);
CREATE INDEX idx_payments_created_at ON payments(created_at);
-- Composite: pending payments for admin (frequent query)
CREATE INDEX idx_payments_pending ON payments(created_at DESC)
    WHERE status = 'pending_review';

-- ============================================================================
-- PAYMENT_PROOFS — Payment lookup
-- ============================================================================
CREATE INDEX idx_payment_proofs_payment_id ON payment_proofs(payment_id);

-- ============================================================================
-- REVIEWS — Course reviews listing
-- ============================================================================
CREATE INDEX idx_reviews_course_id ON reviews(course_id);
CREATE INDEX idx_reviews_student_id ON reviews(student_id);
CREATE INDEX idx_reviews_rating ON reviews(rating);

-- ============================================================================
-- SUGGESTIONS — Admin review
-- ============================================================================
CREATE INDEX idx_suggestions_user_id ON suggestions(user_id);
CREATE INDEX idx_suggestions_status ON suggestions(status);

-- ============================================================================
-- CERTIFICATES — Student and course lookup
-- ============================================================================
CREATE INDEX idx_certificates_student_id ON certificates(student_id);
CREATE INDEX idx_certificates_course_id ON certificates(course_id);
CREATE INDEX idx_certificates_code ON certificates(certificate_code);

-- ============================================================================
-- STUDENT_PROGRESS — Progress tracking queries
-- ============================================================================
CREATE INDEX idx_student_progress_student_id ON student_progress(student_id);
CREATE INDEX idx_student_progress_lesson_id ON student_progress(lesson_id);
CREATE INDEX idx_student_progress_enrollment_id ON student_progress(enrollment_id);
CREATE INDEX idx_student_progress_status ON student_progress(status);
-- Composite: completed lessons per enrollment (progress calculation)
CREATE INDEX idx_student_progress_completed ON student_progress(enrollment_id)
    WHERE status = 'completed';

-- ============================================================================
-- STUDENT_RATINGS — Teacher/student lookup
-- ============================================================================
CREATE INDEX idx_student_ratings_student_id ON student_ratings(student_id);
CREATE INDEX idx_student_ratings_course_id ON student_ratings(course_id);
CREATE INDEX idx_student_ratings_teacher_id ON student_ratings(teacher_id);

-- ============================================================================
-- STUDENT_HIGHLIGHTS — Dashboard queries
-- ============================================================================
CREATE INDEX idx_student_highlights_student_id ON student_highlights(student_id);
CREATE INDEX idx_student_highlights_course_id ON student_highlights(course_id);
CREATE INDEX idx_student_highlights_type ON student_highlights(highlight_type);

-- ============================================================================
-- NOTIFICATIONS — User notifications feed
-- ============================================================================
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
CREATE INDEX idx_notifications_created_at ON notifications(created_at);
-- Composite: unread notifications (badge count query)
CREATE INDEX idx_notifications_unread ON notifications(user_id, created_at DESC)
    WHERE is_read = FALSE;

-- ============================================================================
-- AUDIT_LOGS — Admin audit queries
-- ============================================================================
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
-- Composite: recent logs by action (frequent admin query)
CREATE INDEX idx_audit_logs_action_date ON audit_logs(action, created_at DESC);

-- ============================================================================
-- FILE_UPLOADS — Entity lookup
-- ============================================================================
CREATE INDEX idx_file_uploads_uploaded_by ON file_uploads(uploaded_by);
CREATE INDEX idx_file_uploads_entity ON file_uploads(entity_type, entity_id);
CREATE INDEX idx_file_uploads_deleted_at ON file_uploads(deleted_at)
    WHERE deleted_at IS NOT NULL;

-- ============================================================================
-- CONTENT_VERSIONS — Version history lookup
-- ============================================================================
CREATE INDEX idx_content_versions_entity ON content_versions(entity_type, entity_id);
CREATE INDEX idx_content_versions_changed_by ON content_versions(changed_by);
CREATE INDEX idx_content_versions_created_at ON content_versions(created_at);

-- ============================================================================
-- EMAIL_QUEUE — Worker processing
-- ============================================================================
CREATE INDEX idx_email_queue_status ON email_queue(status);
CREATE INDEX idx_email_queue_scheduled ON email_queue(scheduled_at)
    WHERE status = 'pending';
CREATE INDEX idx_email_queue_to_user ON email_queue(to_user_id);

-- ============================================================================
-- FEATURE_FLAGS — Key lookup
-- ============================================================================
CREATE INDEX idx_feature_flags_key ON feature_flags(key);
CREATE INDEX idx_feature_flags_enabled ON feature_flags(enabled)
    WHERE enabled = TRUE;

-- ============================================================================
-- BACKGROUND_JOBS — Worker processing
-- ============================================================================
CREATE INDEX idx_background_jobs_status ON background_jobs(status);
CREATE INDEX idx_background_jobs_type ON background_jobs(job_type);
CREATE INDEX idx_background_jobs_scheduled ON background_jobs(scheduled_at)
    WHERE status = 'pending';
CREATE INDEX idx_background_jobs_created_at ON background_jobs(created_at);
