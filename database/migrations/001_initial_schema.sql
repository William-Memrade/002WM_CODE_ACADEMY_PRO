-- ============================================================================
-- CodeAcademy Pro — Initial Database Schema
-- Supabase PostgreSQL
-- 26 tables, UUID PKs, timestamps, soft delete
-- ============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- 1. ROLES — System roles (admin, teacher, student)
-- ============================================================================
CREATE TABLE roles (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(50) UNIQUE NOT NULL,               -- admin, teacher, student
    description VARCHAR(255),
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE roles IS 'System roles for RBAC';

-- ============================================================================
-- 2. USERS — All platform users
-- ============================================================================
CREATE TABLE users (
    id                       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email                    VARCHAR(255) UNIQUE NOT NULL,
    username                 VARCHAR(30) UNIQUE NOT NULL,
    password_hash            VARCHAR(255) NOT NULL,
    first_name               VARCHAR(120) NOT NULL,
    last_name                VARCHAR(120) NOT NULL,
    avatar_url               VARCHAR(500),
    phone                    VARCHAR(20),
    bio                      TEXT,
    is_active                BOOLEAN DEFAULT TRUE,
    is_blocked               BOOLEAN DEFAULT FALSE,
    email_verified           BOOLEAN DEFAULT FALSE,
    email_verification_token VARCHAR(255),
    last_login_at            TIMESTAMP WITH TIME ZONE,
    created_at               TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at               TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at               TIMESTAMP WITH TIME ZONE,      -- soft delete

    CONSTRAINT chk_users_email CHECK (email ~* '^[^\s@]+@[^\s@]+\.[^\s@]+$'),
    CONSTRAINT chk_users_username CHECK (username ~* '^[a-zA-Z0-9_]{3,30}$')
);

COMMENT ON TABLE users IS 'All platform users (admins, teachers, students)';
COMMENT ON COLUMN users.deleted_at IS 'Soft delete timestamp - NULL means active';

-- ============================================================================
-- 3. USER_ROLES — Many-to-many users <=> roles
-- ============================================================================
CREATE TABLE user_roles (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    role_id     UUID NOT NULL REFERENCES roles(id) ON DELETE RESTRICT,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT uq_user_roles UNIQUE (user_id, role_id)
);

COMMENT ON TABLE user_roles IS 'User role assignments (many-to-many)';

-- ============================================================================
-- 4. CATEGORIES — Course categories
-- ============================================================================
CREATE TABLE categories (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(100) UNIQUE NOT NULL,
    slug        VARCHAR(120) UNIQUE NOT NULL,
    description TEXT,
    is_active   BOOLEAN DEFAULT TRUE,
    sort_order  INTEGER DEFAULT 0,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT chk_categories_slug CHECK (slug ~* '^[a-z0-9-]{3,120}$')
);

COMMENT ON TABLE categories IS 'Course categories (e.g., Backend, Frontend, DevOps)';

-- ============================================================================
-- 5. COURSES — Platform courses
-- ============================================================================
CREATE TABLE courses (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title             VARCHAR(255) NOT NULL,
    slug              VARCHAR(120) UNIQUE NOT NULL,
    description       TEXT NOT NULL,
    short_description VARCHAR(500),
    thumbnail_url     VARCHAR(500),
    category_id       UUID REFERENCES categories(id) ON DELETE SET NULL,
    teacher_id        UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    price             DECIMAL(10,2) NOT NULL,
    currency          VARCHAR(3) DEFAULT 'USD',
    level             VARCHAR(20) DEFAULT 'beginner',
    duration_hours    INTEGER,
    is_active         BOOLEAN DEFAULT FALSE,
    is_featured       BOOLEAN DEFAULT FALSE,
    max_students      INTEGER,                              -- NULL = unlimited
    starts_at         TIMESTAMP WITH TIME ZONE,
    ends_at           TIMESTAMP WITH TIME ZONE,
    created_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at        TIMESTAMP WITH TIME ZONE,

    CONSTRAINT chk_courses_price CHECK (price >= 0),
    CONSTRAINT chk_courses_level CHECK (level IN ('beginner', 'intermediate', 'advanced')),
    CONSTRAINT chk_courses_slug CHECK (slug ~* '^[a-z0-9-]{3,120}$'),
    CONSTRAINT chk_courses_dates CHECK (ends_at IS NULL OR ends_at > starts_at)
);

COMMENT ON TABLE courses IS 'Platform courses with teacher assignment';
COMMENT ON COLUMN courses.max_students IS 'NULL means unlimited enrollment';

-- ============================================================================
-- 6. MODULES — Course modules (sections)
-- ============================================================================
CREATE TABLE modules (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id    UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    title        VARCHAR(255) NOT NULL,
    description  TEXT,
    sort_order   INTEGER NOT NULL DEFAULT 0,
    is_published BOOLEAN DEFAULT FALSE,
    created_at   TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at   TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE modules IS 'Course modules/sections containing lessons';

-- ============================================================================
-- 7. LESSONS — Module lessons
-- ============================================================================
CREATE TABLE lessons (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    module_id        UUID NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    title            VARCHAR(255) NOT NULL,
    description      TEXT,
    content          TEXT,                                   -- markdown content
    sort_order       INTEGER NOT NULL DEFAULT 0,
    duration_minutes INTEGER,
    is_free          BOOLEAN DEFAULT FALSE,                  -- free preview
    is_published     BOOLEAN DEFAULT FALSE,
    created_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE lessons IS 'Individual lessons within a module';
COMMENT ON COLUMN lessons.is_free IS 'If true, lesson is available as free preview';

-- ============================================================================
-- 8. LIVE_CLASSES — Scheduled live sessions
-- ============================================================================
CREATE TABLE live_classes (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id        UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    title            VARCHAR(255) NOT NULL,
    description      TEXT,
    meeting_url      VARCHAR(500) NOT NULL,
    meeting_platform VARCHAR(50),                            -- zoom, meet, teams
    scheduled_at     TIMESTAMP WITH TIME ZONE NOT NULL,
    duration_minutes INTEGER DEFAULT 60,
    is_recorded      BOOLEAN DEFAULT FALSE,
    recording_url    VARCHAR(500),
    status           VARCHAR(20) DEFAULT 'scheduled',

    created_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT chk_live_classes_status CHECK (
        status IN ('scheduled', 'live', 'completed', 'cancelled')
    )
);

COMMENT ON TABLE live_classes IS 'Scheduled live class sessions with meeting links';

-- ============================================================================
-- 9. RECORDED_CLASSES — Pre-recorded video lessons
-- ============================================================================
CREATE TABLE recorded_classes (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lesson_id      UUID NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    title          VARCHAR(255) NOT NULL,
    video_url      VARCHAR(500) NOT NULL,
    video_provider VARCHAR(50) DEFAULT 'storage',            -- storage, youtube, vimeo
    duration_minutes INTEGER,
    thumbnail_url  VARCHAR(500),
    sort_order     INTEGER DEFAULT 0,
    is_published   BOOLEAN DEFAULT TRUE,
    created_at     TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at     TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE recorded_classes IS 'Pre-recorded video content for lessons';

-- ============================================================================
-- 10. ENROLLMENTS — Student course enrollments
-- ============================================================================
CREATE TABLE enrollments (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id           UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    course_id            UUID NOT NULL REFERENCES courses(id) ON DELETE RESTRICT,
    status               VARCHAR(30) NOT NULL DEFAULT 'pending_payment',
    enrolled_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    approved_at          TIMESTAMP WITH TIME ZONE,
    cancelled_at         TIMESTAMP WITH TIME ZONE,
    cancellation_reason  TEXT,
    completed_at         TIMESTAMP WITH TIME ZONE,
    progress_percentage  DECIMAL(5,2) DEFAULT 0.00,
    created_at           TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at           TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT uq_enrollments UNIQUE (student_id, course_id),
    CONSTRAINT chk_enrollments_status CHECK (
        status IN ('pending_payment', 'payment_pending_review', 'payment_approved',
                   'payment_rejected', 'active', 'cancelled', 'completed', 'expired')
    ),
    CONSTRAINT chk_enrollments_progress CHECK (
        progress_percentage >= 0 AND progress_percentage <= 100
    )
);

COMMENT ON TABLE enrollments IS 'Student course enrollments with payment and progress tracking';

-- ============================================================================
-- 11. PAYMENTS — Payment records
-- ============================================================================
CREATE TABLE payments (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    enrollment_id    UUID NOT NULL REFERENCES enrollments(id) ON DELETE RESTRICT,
    student_id       UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    amount           DECIMAL(10,2) NOT NULL,
    currency         VARCHAR(3) DEFAULT 'USD',
    payment_method   VARCHAR(50) DEFAULT 'bank_transfer',
    status           VARCHAR(30) NOT NULL DEFAULT 'pending',
    reference_number VARCHAR(100),
    reviewed_by      UUID REFERENCES users(id) ON DELETE SET NULL,
    reviewed_at      TIMESTAMP WITH TIME ZONE,
    review_notes     TEXT,
    created_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT chk_payments_amount CHECK (amount > 0),
    CONSTRAINT chk_payments_status CHECK (
        status IN ('pending', 'pending_review', 'approved', 'rejected')
    )
);

COMMENT ON TABLE payments IS 'Payment records linked to enrollments';

-- ============================================================================
-- 12. PAYMENT_PROOFS — Uploaded payment proof files
-- ============================================================================
CREATE TABLE payment_proofs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_id  UUID NOT NULL REFERENCES payments(id) ON DELETE CASCADE,
    file_url    VARCHAR(500) NOT NULL,
    file_name   VARCHAR(255) NOT NULL,
    file_size   INTEGER NOT NULL,
    mime_type   VARCHAR(100) NOT NULL,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE payment_proofs IS 'Uploaded payment proof images/PDFs';

-- ============================================================================
-- 13. REVIEWS — Course reviews by students
-- ============================================================================
CREATE TABLE reviews (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id  UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id   UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    rating      INTEGER NOT NULL,
    comment     TEXT,
    is_visible  BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT uq_reviews UNIQUE (student_id, course_id),
    CONSTRAINT chk_reviews_rating CHECK (rating >= 1 AND rating <= 5)
);

COMMENT ON TABLE reviews IS 'Course reviews and ratings by students';

-- ============================================================================
-- 14. SUGGESTIONS — User suggestions to admin
-- ============================================================================
CREATE TABLE suggestions (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject     VARCHAR(255) NOT NULL,
    message     TEXT NOT NULL,
    status      VARCHAR(20) DEFAULT 'pending',
    admin_notes TEXT,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT chk_suggestions_status CHECK (
        status IN ('pending', 'reviewed', 'archived')
    )
);

COMMENT ON TABLE suggestions IS 'User suggestions and feedback';

-- ============================================================================
-- 15. CERTIFICATES — Issued certificates
-- ============================================================================
CREATE TABLE certificates (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id       UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    course_id        UUID NOT NULL REFERENCES courses(id) ON DELETE RESTRICT,
    certificate_code VARCHAR(50) UNIQUE NOT NULL,
    file_url         VARCHAR(500),
    issued_by        UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    issued_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata         JSONB DEFAULT '{}',
    created_at       TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT uq_certificates UNIQUE (student_id, course_id)
);

COMMENT ON TABLE certificates IS 'Issued course completion certificates';

-- ============================================================================
-- 16. STUDENT_PROGRESS — Per-lesson progress tracking
-- ============================================================================
CREATE TABLE student_progress (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id            UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    lesson_id             UUID NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    enrollment_id         UUID NOT NULL REFERENCES enrollments(id) ON DELETE CASCADE,
    status                VARCHAR(20) DEFAULT 'not_started',
    completed_at          TIMESTAMP WITH TIME ZONE,
    time_spent_seconds    INTEGER DEFAULT 0,
    last_position_seconds INTEGER DEFAULT 0,
    created_at            TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at            TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT uq_student_progress UNIQUE (student_id, lesson_id),
    CONSTRAINT chk_progress_status CHECK (
        status IN ('not_started', 'in_progress', 'completed')
    )
);

COMMENT ON TABLE student_progress IS 'Per-lesson progress tracking for students';

-- ============================================================================
-- 17. STUDENT_RATINGS — Teacher ratings of students
-- ============================================================================
CREATE TABLE student_ratings (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id  UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id   UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    teacher_id  UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    score       DECIMAL(5,2),
    stars       INTEGER DEFAULT 0,
    feedback    TEXT,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT uq_student_ratings UNIQUE (student_id, course_id),
    CONSTRAINT chk_ratings_score CHECK (score IS NULL OR (score >= 0 AND score <= 100)),
    CONSTRAINT chk_ratings_stars CHECK (stars >= 0 AND stars <= 5)
);

COMMENT ON TABLE student_ratings IS 'Teacher evaluations and ratings of students';

-- ============================================================================
-- 18. STUDENT_HIGHLIGHTS — Outstanding students marking
-- ============================================================================
CREATE TABLE student_highlights (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id      UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    highlight_type VARCHAR(30) NOT NULL,
    marked_by      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    notes          TEXT,
    created_at     TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT uq_student_highlights UNIQUE (student_id, course_id, highlight_type),
    CONSTRAINT chk_highlight_type CHECK (
        highlight_type IN ('outstanding', 'ready_for_evaluation')
    )
);

COMMENT ON TABLE student_highlights IS 'Marks students as outstanding or ready for external evaluation';

-- ============================================================================
-- 19. NOTIFICATIONS — In-app notifications
-- ============================================================================
CREATE TABLE notifications (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id        UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title          VARCHAR(255) NOT NULL,
    message        TEXT NOT NULL,
    type           VARCHAR(50) NOT NULL,
    reference_type VARCHAR(50),
    reference_id   UUID,
    is_read        BOOLEAN DEFAULT FALSE,
    read_at        TIMESTAMP WITH TIME ZONE,
    created_at     TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT chk_notification_type CHECK (
        type IN ('payment', 'enrollment', 'class', 'certificate', 'system', 'highlight', 'review')
    )
);

COMMENT ON TABLE notifications IS 'In-app notifications for all users';

-- ============================================================================
-- 20. AUDIT_LOGS — System audit trail
-- ============================================================================
CREATE TABLE audit_logs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID REFERENCES users(id) ON DELETE SET NULL,
    action      VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id   UUID,
    details     JSONB DEFAULT '{}',
    ip_address  INET,
    user_agent  VARCHAR(500),
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE audit_logs IS 'Audit trail for security-critical actions';

-- ============================================================================
-- 21. FILE_UPLOADS — File upload registry
-- ============================================================================
CREATE TABLE file_uploads (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    uploaded_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    file_name   VARCHAR(255) NOT NULL,
    file_path   VARCHAR(500) NOT NULL,
    file_size   INTEGER NOT NULL,
    mime_type   VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id   UUID,
    is_public   BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at  TIMESTAMP WITH TIME ZONE
);

COMMENT ON TABLE file_uploads IS 'Registry of all uploaded files with metadata';

-- ============================================================================
-- 22. SYSTEM_SETTINGS — Key-value system configuration
-- ============================================================================
CREATE TABLE system_settings (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key         VARCHAR(100) UNIQUE NOT NULL,
    value       TEXT NOT NULL,
    description VARCHAR(255),
    is_public   BOOLEAN DEFAULT FALSE,
    updated_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE system_settings IS 'Key-value system configuration accessible via admin panel';

-- ============================================================================
-- 23. CONTENT_VERSIONS — Content version history
-- ============================================================================
CREATE TABLE content_versions (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type    VARCHAR(50) NOT NULL,
    entity_id      UUID NOT NULL,
    version_number INTEGER NOT NULL,
    snapshot       JSONB NOT NULL,
    changed_by     UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    change_summary VARCHAR(500),
    created_at     TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT uq_content_versions UNIQUE (entity_type, entity_id, version_number),
    CONSTRAINT chk_content_entity_type CHECK (
        entity_type IN ('course', 'module', 'lesson')
    )
);

COMMENT ON TABLE content_versions IS 'Version history for educational content (courses, modules, lessons)';

-- ============================================================================
-- 24. EMAIL_QUEUE — Transactional email queue
-- ============================================================================
CREATE TABLE email_queue (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    to_email      VARCHAR(255) NOT NULL,
    to_user_id    UUID REFERENCES users(id) ON DELETE SET NULL,
    subject       VARCHAR(255) NOT NULL,
    template      VARCHAR(100) NOT NULL,
    template_data JSONB DEFAULT '{}',
    status        VARCHAR(20) DEFAULT 'pending',
    attempts      INTEGER DEFAULT 0,
    max_attempts  INTEGER DEFAULT 3,
    last_error    TEXT,
    sent_at       TIMESTAMP WITH TIME ZONE,
    scheduled_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at    TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT chk_email_status CHECK (
        status IN ('pending', 'processing', 'sent', 'failed')
    )
);

COMMENT ON TABLE email_queue IS 'Queue for transactional emails processed by background worker';

-- ============================================================================
-- 25. FEATURE_FLAGS — Feature toggle system
-- ============================================================================
CREATE TABLE feature_flags (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key         VARCHAR(100) UNIQUE NOT NULL,
    enabled     BOOLEAN DEFAULT FALSE,
    description VARCHAR(500),
    metadata    JSONB DEFAULT '{}',
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE feature_flags IS 'Feature flags for toggling features without deployment';

-- ============================================================================
-- 26. BACKGROUND_JOBS — Job execution tracking
-- ============================================================================
CREATE TABLE background_jobs (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_type     VARCHAR(100) NOT NULL,
    payload      JSONB DEFAULT '{}',
    status       VARCHAR(20) DEFAULT 'pending',
    result       JSONB,
    error        TEXT,
    attempts     INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    scheduled_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at   TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at   TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT chk_job_status CHECK (
        status IN ('pending', 'processing', 'completed', 'failed')
    )
);

COMMENT ON TABLE background_jobs IS 'Tracking table for async background job execution';

-- ============================================================================
-- AUTO-UPDATE updated_at TRIGGER
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all tables that have updated_at
DO $$
DECLARE
    t TEXT;
BEGIN
    FOR t IN
        SELECT table_name FROM information_schema.columns
        WHERE column_name = 'updated_at'
        AND table_schema = 'public'
    LOOP
        EXECUTE format(
            'CREATE TRIGGER trg_%s_updated_at
             BEFORE UPDATE ON %I
             FOR EACH ROW
             EXECUTE FUNCTION update_updated_at_column()',
            t, t
        );
    END LOOP;
END;
$$;
