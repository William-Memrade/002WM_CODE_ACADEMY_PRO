-- ============================================================================
-- CodeAcademy Pro — Audit Logs Enhancement Migration
-- Adds missing columns, converts ip_address to VARCHAR, and adds indexes.
-- Idempotent: can be safely re-run.
-- ============================================================================

-- ── Convert ip_address from INET to VARCHAR(45) if needed ──────────────────
-- The ORM maps this column as String(45). PostgreSQL INET requires valid IP
-- strings; VARCHAR is safer for arbitrary client-provided values and avoids
-- insert failures when X-Forwarded-For contains non-IP content.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'audit_logs' AND column_name = 'ip_address'
          AND data_type = 'inet'
    ) THEN
        ALTER TABLE audit_logs ALTER COLUMN ip_address TYPE VARCHAR(45);
    END IF;
END $$;

-- ── Add missing columns if not present ─────────────────────────────────────
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'audit_logs' AND column_name = 'actor_email'
    ) THEN
        ALTER TABLE audit_logs ADD COLUMN actor_email VARCHAR(255);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'audit_logs' AND column_name = 'entity_label'
    ) THEN
        ALTER TABLE audit_logs ADD COLUMN entity_label VARCHAR(255);
    END IF;
END $$;

-- ── Create indexes if not present ───────────────────────────────────────────
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE indexname = 'ix_audit_logs_created_at'
    ) THEN
        CREATE INDEX ix_audit_logs_created_at ON audit_logs(created_at DESC);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE indexname = 'ix_audit_logs_user_id'
    ) THEN
        CREATE INDEX ix_audit_logs_user_id ON audit_logs(user_id);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE indexname = 'ix_audit_logs_action'
    ) THEN
        CREATE INDEX ix_audit_logs_action ON audit_logs(action);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE indexname = 'ix_audit_logs_entity_type'
    ) THEN
        CREATE INDEX ix_audit_logs_entity_type ON audit_logs(entity_type);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE indexname = 'ix_audit_logs_entity_id'
    ) THEN
        CREATE INDEX ix_audit_logs_entity_id ON audit_logs(entity_id);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE indexname = 'ix_audit_logs_actor_email'
    ) THEN
        CREATE INDEX ix_audit_logs_actor_email ON audit_logs(actor_email);
    END IF;
END $$;
