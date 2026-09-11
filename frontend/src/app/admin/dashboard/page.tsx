"use client";

import { useAdminMetrics } from "@/hooks/useAdminData";
import { useEffect, useState, useCallback } from "react";
import { api } from "@/lib/api";
import { formatCurrency } from "@/lib/currency";
import { usePlatformSettings } from "@/hooks/usePlatformSettings";

interface TopCourse { title: string; total_students: number; is_active: boolean; }

export default function AdminDashboard() {
  const { data: metrics, loading } = useAdminMetrics();
  const { settings } = usePlatformSettings();
  const [courses, setCourses] = useState<TopCourse[]>([]);

  // Fetch top courses alongside metrics (both are triggered on mount)
  const fetchTopCourses = useCallback(async () => {
    try {
      const res = await api.get<{ items: TopCourse[] }>("/courses/admin/all?per_page=5");
      setCourses(res.items.slice(0, 5));
    } catch { /* silent */ }
  }, []);

  useEffect(() => { fetchTopCourses(); }, [fetchTopCourses]);

  const stats = [
    { icon: "👥", label: "Total alumnos",    value: metrics?.total_students ?? "—",  bg: "#eef2ff", color: "#6366f1" },
    { icon: "👨‍🏫", label: "Total docentes",   value: metrics?.total_teachers ?? "—",  bg: "#ecfdf5", color: "#10b981" },
    { icon: "📚", label: "Cursos activos",   value: metrics?.active_courses ?? "—",   bg: "#fef3c7", color: "#f59e0b" },
    { icon: "💰", label: "Ingresos totales", value: metrics ? formatCurrency(metrics.total_revenue, settings.default_currency) : "—", bg: "#dcfce7", color: "#16a34a" },
    { icon: "⏳", label: "Pagos pendientes", value: metrics?.pending_payments ?? "—", bg: "#fee2e2", color: "#ef4444" },
    { icon: "👤", label: "Usuarios pendientes", value: metrics?.pending_users ?? "—", bg: "#fef9c3", color: "#ca8a04" },
    { icon: "🎓", label: "Total cursos",     value: metrics?.total_courses ?? "—",    bg: "#fce7f3", color: "#ec4899" },
  ];

  return (
    <>
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Métricas generales de la plataforma en tiempo real.</p>
      </div>

      <div className="grid-stats">
        {stats.map((s, i) => (
          <div key={i} className="stats-card">
            <div className="stats-icon" style={{ background: s.bg, color: s.color }}>{s.icon}</div>
            <div>
              <div className="stats-value">
                {loading ? <span style={{ opacity: 0.4 }}>…</span> : s.value}
              </div>
              <div className="stats-label">{s.label}</div>
            </div>
          </div>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px" }}>
        <div>
          <h2 style={{ fontSize: "1.25rem", fontWeight: 600, marginBottom: "16px" }}>Cursos de la plataforma</h2>
          <div className="card">
            {courses.length === 0 && (
              <p style={{ color: "var(--color-text-muted)", fontSize: "0.9rem" }}>Cargando cursos…</p>
            )}
            {courses.map((c, i) => (
              <div key={i} style={{
                padding: "12px 0", display: "flex", justifyContent: "space-between",
                borderBottom: i < courses.length - 1 ? "1px solid var(--color-border)" : "none",
              }}>
                <span style={{ fontSize: "0.9375rem", fontWeight: 500 }}>{c.title}</span>
                <span style={{ fontSize: "0.8125rem", color: "var(--color-text-muted)" }}>
                  {(c as any).is_active ? "✅ Activo" : "⏸ Inactivo"}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h2 style={{ fontSize: "1.25rem", fontWeight: 600, marginBottom: "16px" }}>Resumen rápido</h2>
          <div className="card">
            {[
              { label: "Ingresos aprobados", value: metrics ? formatCurrency(metrics.total_revenue, settings.default_currency) : "…" },
              { label: "Pagos pendientes de revisión", value: metrics?.pending_payments ?? "…" },
              { label: "Alumnos registrados", value: metrics?.total_students ?? "…" },
              { label: "Docentes activos", value: metrics?.total_teachers ?? "…" },
            ].map((item, i) => (
              <div key={i} style={{
                padding: "12px 0", display: "flex", justifyContent: "space-between",
                borderBottom: i < 3 ? "1px solid var(--color-border)" : "none",
              }}>
                <span style={{ fontSize: "0.9375rem" }}>{item.label}</span>
                <strong style={{ fontSize: "0.9375rem" }}>{item.value}</strong>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}
