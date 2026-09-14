-- 026_access_control_capacity_notifications.sql
--
-- Cierra tres huecos del slice de control de acceso, cupos y notificaciones:
--
--   1. El límite global de alumnos por clase pasa de 100 a 20.
--   2. Se asegura que la tabla notifications tenga RLS y políticas mínimas.
--   3. Se amplía el CHECK de notifications.type para admitir alertas administrativas.

-- ── 1. Cupo global por clase = 20 ────────────────────────────────────────────

INSERT INTO system_settings (key, value, description, is_public)
VALUES (
    'global_max_students_per_class',
    '20',
    'Máximo global de alumnos por clase',
    false
)
ON CONFLICT (key) DO UPDATE SET
    value = EXCLUDED.value,
    updated_at = NOW();

-- ── 2. RLS sobre notifications (idempotente) ─────────────────────────────────

ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS notifications_select ON notifications;
DROP POLICY IF EXISTS notifications_insert ON notifications;
DROP POLICY IF EXISTS notifications_update ON notifications;
DROP POLICY IF EXISTS notifications_delete ON notifications;

CREATE POLICY notifications_select ON notifications FOR SELECT
    USING (user_id = app_user_id() OR is_admin());

CREATE POLICY notifications_insert ON notifications FOR INSERT
    WITH CHECK (is_admin() OR app_user_role() = 'system');

CREATE POLICY notifications_update ON notifications FOR UPDATE
    USING (user_id = app_user_id() OR is_admin())
    WITH CHECK (user_id = app_user_id() OR is_admin());

CREATE POLICY notifications_delete ON notifications FOR DELETE
    USING (user_id = app_user_id() OR is_admin());

-- ── 3. Ampliar tipos de notificación para alertas de admin ───────────────────

ALTER TABLE notifications DROP CONSTRAINT IF EXISTS chk_notification_type;

ALTER TABLE notifications
    ADD CONSTRAINT chk_notification_type CHECK (
        type IN (
            'payment',
            'enrollment',
            'class',
            'certificate',
            'system',
            'highlight',
            'review',
            'admin_alert'
        )
    );
