-- ============================================================================
-- CodeAcademy Pro — 022: Force Change Password Flag
-- Adds a `force_change_password` boolean column to `users`.
-- When TRUE the user (created by an admin with a temporary password) is forced
-- to set a new password on first login.
-- ============================================================================

BEGIN;

ALTER TABLE users
    ADD COLUMN IF NOT EXISTS force_change_password BOOLEAN NOT NULL DEFAULT FALSE;

COMMIT;