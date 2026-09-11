-- ============================================================================
-- CodeAcademy Pro — 023: columnas que el ORM usa y ninguna migración creaba
-- ============================================================================
-- Contexto del bug (mismo patrón que las tablas students/teachers, ver 004a):
-- la base local se generó con `Base.metadata.create_all()`, así que tenía columnas
-- que la cadena de migraciones nunca creó. En una base nueva, cualquier consulta
-- del ORM sobre ellas falla con `column ... does not exist`, y 004 rompía incluso
-- la propia cadena (indexaba users.status).
--
-- Se puede detectar en segundos con:  python scripts/check_schema_drift.py
--
-- Todo es aditivo (ADD COLUMN / backfill): no borra ni renombra nada, así que es
-- seguro sobre una base que ya tenía estas columnas creadas por el ORM.
-- ============================================================================

-- ── 1. users.status ─────────────────────────────────────────────────────────
-- Usada por el modelo (app/models/user.py:61), por el registro
-- (auth_service.py:56 → status="pending") y por el panel /admin/users.
-- 004_performance_indexes.sql ya intentaba indexarla (ahora va guardado).
ALTER TABLE users ADD COLUMN IF NOT EXISTS status VARCHAR(20);

-- Backfill por NULL: distingue las filas que existían ANTES de la columna de las
-- que el código creó después con status='pending' (registro sin verificar).
UPDATE users
   SET status = CASE
                    WHEN is_active IS FALSE OR is_blocked IS TRUE THEN 'inactive'
                    ELSE 'active'
                END
 WHERE status IS NULL;

ALTER TABLE users ALTER COLUMN status SET DEFAULT 'pending';
ALTER TABLE users ALTER COLUMN status SET NOT NULL;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
         WHERE conname = 'chk_users_status' AND conrelid = 'users'::regclass
    ) THEN
        ALTER TABLE users
            ADD CONSTRAINT chk_users_status
            CHECK (status IN ('pending', 'active', 'inactive'));
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS ix_users_status ON users(status);
CREATE INDEX IF NOT EXISTS ix_users_status_deleted ON users(status, deleted_at);

COMMENT ON COLUMN users.status IS
    'Ciclo de vida de la cuenta: pending (registro sin confirmar) / active / inactive.';

-- ── 2. feature_flags.flag_metadata ──────────────────────────────────────────
-- La crea 014a_add_flag_metadata.sql (tiene que existir antes de 015, que inserta
-- filas con esa columna). No se repite acá.

-- ── 3. payment_proofs.created_at / updated_at ───────────────────────────────
-- PaymentProof hereda BaseModel/TimestampMixin: el ORM los selecciona siempre.
-- La tabla tenía `uploaded_at` en su lugar (el schema Pydantic PaymentProofResponse
-- lo declara, pero no se usa en ningún router y el endpoint arma la respuesta a
-- mano → uploaded_at queda como residuo).
ALTER TABLE payment_proofs ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE payment_proofs ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE;

UPDATE payment_proofs
   SET created_at = COALESCE(uploaded_at, NOW()), updated_at = COALESCE(uploaded_at, NOW())
 WHERE created_at IS NULL
   AND EXISTS (
        SELECT 1 FROM information_schema.columns
         WHERE table_schema = 'public' AND table_name = 'payment_proofs'
           AND column_name = 'uploaded_at'
   );

UPDATE payment_proofs SET created_at = NOW() WHERE created_at IS NULL;
UPDATE payment_proofs SET updated_at = created_at WHERE updated_at IS NULL;

ALTER TABLE payment_proofs ALTER COLUMN created_at SET DEFAULT NOW();
ALTER TABLE payment_proofs ALTER COLUMN updated_at SET DEFAULT NOW();
ALTER TABLE payment_proofs ALTER COLUMN created_at SET NOT NULL;
ALTER TABLE payment_proofs ALTER COLUMN updated_at SET NOT NULL;

-- ── 4. Timestamps que faltaban en tablas del ORM ────────────────────────────
-- (las tres heredan TimestampMixin: created_at/updated_at NOT NULL)
ALTER TABLE roles           ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE system_settings ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE background_jobs ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE email_queue     ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE;

UPDATE roles           SET updated_at = COALESCE(created_at, NOW()) WHERE updated_at IS NULL;
UPDATE system_settings SET created_at = NOW() WHERE created_at IS NULL;
UPDATE background_jobs SET updated_at = COALESCE(created_at, NOW()) WHERE updated_at IS NULL;
UPDATE email_queue     SET updated_at = COALESCE(created_at, NOW()) WHERE updated_at IS NULL;

ALTER TABLE roles           ALTER COLUMN updated_at SET DEFAULT NOW();
ALTER TABLE system_settings ALTER COLUMN created_at SET DEFAULT NOW();
ALTER TABLE background_jobs ALTER COLUMN updated_at SET DEFAULT NOW();
ALTER TABLE email_queue     ALTER COLUMN updated_at SET DEFAULT NOW();

ALTER TABLE roles           ALTER COLUMN updated_at SET NOT NULL;
ALTER TABLE system_settings ALTER COLUMN created_at SET NOT NULL;
ALTER TABLE background_jobs ALTER COLUMN updated_at SET NOT NULL;
ALTER TABLE email_queue     ALTER COLUMN updated_at SET NOT NULL;
