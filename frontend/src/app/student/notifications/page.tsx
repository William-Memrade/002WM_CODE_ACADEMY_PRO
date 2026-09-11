"use client";

export default function StudentNotificationsPage() {
  return (
    <>
      <div className="page-header">
        <h1>Notificaciones</h1>
        <p>Tus notificaciones recientes.</p>
      </div>

      <div className="card" style={{ textAlign: "center", padding: "48px" }}>
        <div style={{ fontSize: "3rem", marginBottom: "16px" }}>🔔</div>
        <h3 style={{ fontWeight: 600, marginBottom: "8px" }}>Sin notificaciones</h3>
        <p style={{ color: "var(--color-text-muted)" }}>
          No tienes notificaciones por el momento.
        </p>
      </div>
    </>
  );
}
