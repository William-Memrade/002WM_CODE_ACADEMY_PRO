-- ============================================================================
-- CodeAcademy Pro — Seed Data
-- Run after 001_initial_schema.sql and 002_indexes.sql
-- ============================================================================

-- ============================================================================
-- ROLES — System roles
-- ============================================================================
INSERT INTO roles (name, description) VALUES
    ('admin',   'Platform administrator with full access'),
    ('teacher', 'Course instructor with course management access'),
    ('student', 'Enrolled student with learning access');

-- ============================================================================
-- SYSTEM_SETTINGS — Default configuration
-- ============================================================================
INSERT INTO system_settings (key, value, description, is_public) VALUES
    ('app_name',                'CodeAcademy Pro',          'Platform name',                    TRUE),
    ('app_description',         'Academia virtual de programación', 'Platform description',     TRUE),
    ('support_email',           'soporte@codeacademypro.com', 'Support email',                  TRUE),
    ('max_upload_mb',           '10',                       'Maximum upload size in MB',         FALSE),
    ('max_video_upload_mb',     '500',                      'Maximum video upload size in MB',   FALSE),
    ('payment_bank_name',       'Banco Nacional',           'Bank name for transfers',           TRUE),
    ('payment_bank_account',    '0000-0000-0000-0000',      'Bank account number',              TRUE),
    ('payment_bank_holder',     'CodeAcademy Pro S.A.',     'Account holder name',               TRUE),
    ('payment_instructions',    'Realiza la transferencia al número de cuenta indicado y sube tu comprobante de pago en formato JPG o PNG. Tu inscripción será activada una vez verificado el pago por un administrador.', 'Payment instructions', TRUE),
    ('payment_qr_url',          '',                         'QR code URL for payment',           TRUE),
    ('default_currency',        'USD',                      'Default currency',                  TRUE),
    ('content_version_limit',   '50',                       'Max content versions per entity',   FALSE),
    ('pagination_default',      '20',                       'Default pagination size',           FALSE),
    ('pagination_max',          '100',                      'Maximum pagination size',           FALSE);

-- ============================================================================
-- FEATURE_FLAGS — Initial flags
-- ============================================================================
INSERT INTO feature_flags (key, enabled, description) VALUES
    ('manual_payments',     TRUE,  'Enable manual bank transfer payments'),
    ('live_classes',        TRUE,  'Enable live class scheduling'),
    ('certificates',        TRUE,  'Enable certificate issuance'),
    ('student_highlights',  TRUE,  'Enable student highlight/reputation system'),
    ('email_notifications', TRUE,  'Enable transactional email notifications'),
    ('content_versioning',  TRUE,  'Enable content version history'),
    ('online_payments',     FALSE, 'Enable online payment gateway (Stripe/PayPal)'),
    ('ai_tutor',            FALSE, 'Enable AI tutor chatbot'),
    ('job_board',           FALSE, 'Enable job board feature'),
    ('mobile_api',          FALSE, 'Enable mobile-specific API endpoints'),
    ('advanced_analytics',  FALSE, 'Enable advanced analytics dashboard');

-- ============================================================================
-- CATEGORIES — Default categories
-- ============================================================================
INSERT INTO categories (name, slug, description, is_active, sort_order) VALUES
    ('Backend',      'backend',      'Desarrollo backend y APIs',           TRUE, 1),
    ('Frontend',     'frontend',     'Desarrollo frontend y UI/UX',         TRUE, 2),
    ('Full Stack',   'full-stack',   'Desarrollo completo web',             TRUE, 3),
    ('DevOps',       'devops',       'Infraestructura y deployment',        TRUE, 4),
    ('Mobile',       'mobile',       'Desarrollo de aplicaciones móviles',  TRUE, 5),
    ('Data Science', 'data-science', 'Ciencia de datos y machine learning', TRUE, 6),
    ('Bases de Datos', 'bases-de-datos', 'SQL, NoSQL y diseño de BD',       TRUE, 7),
    ('Seguridad',    'seguridad',    'Ciberseguridad y pentesting',         TRUE, 8);
