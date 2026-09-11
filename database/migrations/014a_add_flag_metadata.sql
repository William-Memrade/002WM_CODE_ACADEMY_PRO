-- ============================================================================
-- CodeAcademy Pro — 014a: feature_flags.flag_metadata (antes de que 015 la use)
-- ============================================================================
-- Contexto del bug:
--   * 001_initial_schema.sql crea feature_flags con la columna `metadata`.
--   * El ORM no puede mapear un atributo llamado `metadata` (es reservado en
--     declarative), así que el modelo la llama `flag_metadata`
--     (app/models/system.py:55) y el servicio la lee así (feature_flags.py:102).
--   * 015_settings_feature_flags.sql inserta filas usando `flag_metadata` → en una
--     base nueva la cadena moría ahí:
--         column "flag_metadata" of relation "feature_flags" does not exist
--
-- Va justo antes de 015 (orden alfabético: 014_ < 014a_ < 015_) y es aditiva: no
-- renombra `metadata`, solo crea la columna que el ORM espera y copia el contenido
-- de la vieja si existe.
-- ============================================================================

ALTER TABLE feature_flags ADD COLUMN IF NOT EXISTS flag_metadata JSONB;

-- Copia desde la columna vieja `metadata` (bases creadas antes) — el bloque es
-- dinámico porque en una base nueva esa columna sí existe (001) pero en otras
-- podría no estar.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
         WHERE table_schema = 'public' AND table_name = 'feature_flags'
           AND column_name = 'metadata'
    ) THEN
        EXECUTE 'UPDATE feature_flags SET flag_metadata = metadata WHERE flag_metadata IS NULL';
    END IF;
END $$;

UPDATE feature_flags SET flag_metadata = '{}'::jsonb WHERE flag_metadata IS NULL;

COMMENT ON COLUMN feature_flags.flag_metadata IS
    'Configuración extra del flag (el ORM la mapea como flag_metadata porque `metadata` está reservado en SQLAlchemy).';
