-- ============================================================================
-- CodeAcademy Pro — Settings & Feature Flags Seed
-- Idempotent migration for general settings and feature flags.
-- Run after 014_audit_logs_enhancement.sql
-- ============================================================================

-- ── General Settings ─────────────────────────────────────────────────────────
INSERT INTO system_settings (id, key, value, description, is_public) VALUES
    (gen_random_uuid(), 'global_max_students_per_course', '100', 'Global maximum students per course', FALSE)
ON CONFLICT (key) DO NOTHING;

-- Ensure app_name exists (seeded in 003 but safe to re-insert)
INSERT INTO system_settings (id, key, value, description, is_public) VALUES
    (gen_random_uuid(), 'app_name', 'CodeAcademy Pro', 'Platform name', TRUE)
ON CONFLICT (key) DO NOTHING;

INSERT INTO system_settings (id, key, value, description, is_public) VALUES
    (gen_random_uuid(), 'default_currency', 'USD', 'Default currency', TRUE)
ON CONFLICT (key) DO NOTHING;

-- ── Feature Flags ─────────────────────────────────────────────────────────────
-- Only seed if key does not exist (preserves any existing flags)
INSERT INTO feature_flags (id, key, enabled, description, flag_metadata)
SELECT gen_random_uuid(), 'manual_payments', TRUE, 'Enable manual bank transfer payments', '{}'
WHERE NOT EXISTS (SELECT 1 FROM feature_flags WHERE key = 'manual_payments');

INSERT INTO feature_flags (id, key, enabled, description, flag_metadata)
SELECT gen_random_uuid(), 'live_classes', TRUE, 'Enable live class scheduling', '{}'
WHERE NOT EXISTS (SELECT 1 FROM feature_flags WHERE key = 'live_classes');

INSERT INTO feature_flags (id, key, enabled, description, flag_metadata)
SELECT gen_random_uuid(), 'certificates', TRUE, 'Enable certificate issuance', '{}'
WHERE NOT EXISTS (SELECT 1 FROM feature_flags WHERE key = 'certificates');

INSERT INTO feature_flags (id, key, enabled, description, flag_metadata)
SELECT gen_random_uuid(), 'student_highlights', TRUE, 'Enable student highlight/reputation system', '{}'
WHERE NOT EXISTS (SELECT 1 FROM feature_flags WHERE key = 'student_highlights');

INSERT INTO feature_flags (id, key, enabled, description, flag_metadata)
SELECT gen_random_uuid(), 'email_notifications', TRUE, 'Enable transactional email notifications', '{}'
WHERE NOT EXISTS (SELECT 1 FROM feature_flags WHERE key = 'email_notifications');

INSERT INTO feature_flags (id, key, enabled, description, flag_metadata)
SELECT gen_random_uuid(), 'content_versioning', TRUE, 'Enable content version history', '{}'
WHERE NOT EXISTS (SELECT 1 FROM feature_flags WHERE key = 'content_versioning');

INSERT INTO feature_flags (id, key, enabled, description, flag_metadata)
SELECT gen_random_uuid(), 'online_payments', FALSE, 'Enable online payment gateway (Stripe/PayPal)', '{}'
WHERE NOT EXISTS (SELECT 1 FROM feature_flags WHERE key = 'online_payments');

INSERT INTO feature_flags (id, key, enabled, description, flag_metadata)
SELECT gen_random_uuid(), 'student_ratings', TRUE, 'Enable student rating system', '{}'
WHERE NOT EXISTS (SELECT 1 FROM feature_flags WHERE key = 'student_ratings');

INSERT INTO feature_flags (id, key, enabled, description, flag_metadata)
SELECT gen_random_uuid(), 'advanced_analytics', FALSE, 'Enable advanced analytics dashboard', '{}'
WHERE NOT EXISTS (SELECT 1 FROM feature_flags WHERE key = 'advanced_analytics');

INSERT INTO feature_flags (id, key, enabled, description, flag_metadata)
SELECT gen_random_uuid(), 'ai_tutor', FALSE, 'Enable AI tutor (future feature)', '{}'
WHERE NOT EXISTS (SELECT 1 FROM feature_flags WHERE key = 'ai_tutor');

INSERT INTO feature_flags (id, key, enabled, description, flag_metadata)
SELECT gen_random_uuid(), 'job_board', FALSE, 'Enable job board (future feature)', '{}'
WHERE NOT EXISTS (SELECT 1 FROM feature_flags WHERE key = 'job_board');

INSERT INTO feature_flags (id, key, enabled, description, flag_metadata)
SELECT gen_random_uuid(), 'mobile_app_api', FALSE, 'Enable mobile app API (future feature)', '{}'
WHERE NOT EXISTS (SELECT 1 FROM feature_flags WHERE key = 'mobile_app_api');

INSERT INTO feature_flags (id, key, enabled, description, flag_metadata)
SELECT gen_random_uuid(), 'payment_proof_upload', TRUE, 'Enable payment proof upload', '{}'
WHERE NOT EXISTS (SELECT 1 FROM feature_flags WHERE key = 'payment_proof_upload');
