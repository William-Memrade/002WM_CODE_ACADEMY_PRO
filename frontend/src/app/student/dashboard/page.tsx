"use client";

import { useEffect, useState } from "react";
import { getToken, getUser } from "@/lib/auth";

interface PaymentItem {
  id: string;
  course_title: string;
  amount: number;
  currency: string;
  status: string;
  created_at: string | null;
  review_notes: string | null;
}

export default function StudentDashboard() {
  const [payments, setPayments] = useState<PaymentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const user = getUser();

  useEffect(() => {
    const token = getToken();
    if (!token) return;

    fetch("/api/v1/payments/my-payments", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => (r.ok ? r.json() : { items: [] }))
      .then((data) => setPayments(data.items || []))
      .catch(() => setPayments([]))
      .finally(() => setLoading(false));
  }, []);

  const approved = payments.filter((p) => p.status === "approved");
  const pending = payments.filter((p) => p.status === "pending");

  return (
    <>
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Bienvenido, {user?.first_name || "Estudiante"} 👋</p>
      </div>

      {/* Stats */}
      <div className="grid-stats">
        <div className="stats-card">
          <div className="stats-icon" style={{ background: "#eef2ff", color: "#6366f1" }}>📚</div>
          <div>
            <div className="stats-value">{approved.length}</div>
            <div className="stats-label">Cursos activos</div>
          </div>
        </div>
        <div className="stats-card">
          <div className="stats-icon" style={{ background: "#fef3c7", color: "#f59e0b" }}>⏳</div>
          <div>
            <div className="stats-value">{pending.length}</div>
            <div className="stats-label">Pagos pendientes</div>
          </div>
        </div>
        <div className="stats-card">
          <div className="stats-icon" style={{ background: "#ecfdf5", color: "#10b981" }}>💳</div>
          <div>
            <div className="stats-value">{payments.length}</div>
            <div className="stats-label">Total pagos</div>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="card" style={{ textAlign: "center", padding: "40px", color: "var(--color-text-muted)" }}>
          Cargando...
        </div>
      ) : payments.length === 0 ? (
        <div className="card" style={{ textAlign: "center", padding: "48px" }}>
          <div style={{ fontSize: "3rem", marginBottom: "16px" }}>📭</div>
          <h3 style={{ fontWeight: 600, marginBottom: "8px" }}>Sin actividad aún</h3>
          <p style={{ color: "var(--color-text-muted)", marginBottom: "24px" }}>
            Aún no has realizado ningún pago. Explora nuestros cursos y comienza tu aprendizaje.
          </p>
          <a href="/courses" className="btn btn-primary">Ver catálogo de cursos</a>
        </div>
      ) : (
        <>
          {/* Active Courses */}
          {approved.length > 0 && (
            <>
              <h2 style={{ fontSize: "1.25rem", fontWeight: 600, marginBottom: "16px" }}>Cursos Activos</h2>
              <div className="grid-cards" style={{ marginBottom: "32px" }}>
                {approved.map((p) => (
                  <div key={p.id} className="card">
                    <div style={{ display: "flex", gap: "12px", alignItems: "center", marginBottom: "12px" }}>
                      <span style={{ fontSize: "1.5rem" }}>📚</span>
                      <h3 style={{ fontSize: "1rem", fontWeight: 600 }}>{p.course_title}</h3>
                    </div>
                    <span className="badge badge-success">Activo</span>
                  </div>
                ))}
              </div>
            </>
          )}

          {/* Pending Payments */}
          {pending.length > 0 && (
            <>
              <h2 style={{ fontSize: "1.25rem", fontWeight: 600, marginBottom: "16px" }}>Pagos Pendientes</h2>
              <div className="grid-cards">
                {pending.map((p) => (
                  <div key={p.id} className="card">
                    <div style={{ display: "flex", gap: "12px", alignItems: "center", marginBottom: "12px" }}>
                      <span style={{ fontSize: "1.5rem" }}>⏳</span>
                      <h3 style={{ fontSize: "1rem", fontWeight: 600 }}>{p.course_title}</h3>
                    </div>
                    <span className="badge badge-warning">En revisión</span>
                    <p style={{ fontSize: "0.8125rem", color: "var(--color-text-muted)", marginTop: "8px" }}>
                      Tu comprobante está siendo revisado por un administrador.
                    </p>
                  </div>
                ))}
              </div>
            </>
          )}
        </>
      )}
    </>
  );
}
