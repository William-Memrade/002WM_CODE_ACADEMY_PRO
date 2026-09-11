-- ============================================================================
-- CodeAcademy Pro — Payment Info Extra Fields
-- Adds optional payment metadata shown in the "Información de Pago" modal.
-- Run after 003_seed_data.sql
-- ============================================================================

INSERT INTO system_settings (key, value, description, is_public) VALUES
    ('payment_bank_account_type', '', 'Bank account type (e.g., savings/checking)', TRUE),
    ('payment_bank_holder_type',  '', 'Account holder type: natural/juridico',     TRUE);

