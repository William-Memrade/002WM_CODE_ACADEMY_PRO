"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { toast } from "@/components/ui/Toast";
import { CourseClass } from "@/types";
import Link from "next/link";

interface FlatClass extends CourseClass {
  course_title: string;
}

export default function CoordinatorDashboard() {
  const [loading, setLoading] = useState(true);
  const [totalClasses, setTotalClasses] = useState(0);
  const [totalStudents, setTotalStudents] = useState(0);
  const [pendingPayments, setPendingPayments] = useState(0);
  const [recentClasses, setRecentClasses] = useState<FlatClass[]>([]);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const coursesRes = await api.get<{ items: Array<{ id: string; title: string }> }>("/courses?per_page=100");
        const courses = coursesRes.items;

        const classesByCourse = await Promise.all(
          courses.map(async (c) => {
            try {
              const list = await api.get<CourseClass[]>(`/courses/${c.id}/classes`);
              return list.map((cls) => ({ ...cls, course_title: c.title }));
            } catch {
              return [] as FlatClass[];
            }
          })
        );

        const allClasses = classesByCourse.flat();
        setTotalClasses(allClasses.length);
        setTotalStudents(allClasses.reduce((sum, c) => sum + (c.enrolled_count ?? 0), 0));
        setRecentClasses(
          allClasses
            .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
            .slice(0, 5)
        );

        const paymentsRes = await api.get<{ total: number }>(
          "/payments/admin/list?status=approved_pending_class&per_page=1"
        );
        setPendingPayments(paymentsRes.total);
      } catch {
        toast.error("Error al cargar el dashboard");
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  const stats = [
    { icon: "📚", label: "Clases gestionadas", value: totalClasses, bg: "#eef2ff", color: "#6366f1" },
    { icon: "👥", label: "Alumnos en clases", value: totalStudents, bg: "#ecfdf5", color: "#10b981" },
    { icon: "💳", label: "Pagos por asignar", value: pendingPayments, bg: "#fee2e2", color: "#ef4444" },
  ];

  return (
    <>
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Resumen de clases y pagos pendientes de asignación.</p>
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
          <h2 style={{ fontSize: "1.25rem", fontWeight: 600, marginBottom: "16px" }}>Clases recientes</h2>
          <div className="card">
            {loading ? (
              <p style={{ color: "var(--color-text-muted)", fontSize: "0.9rem" }}>Cargando clases…</p>
            ) : recentClasses.length === 0 ? (
              <p style={{ color: "var(--color-text-muted)", fontSize: "0.9rem" }}>No hay clases registradas.</p>
            ) : (
              recentClasses.map((c, i) => (
                <div
                  key={c.id}
                  style={{
                    padding: "12px 0",
                    display: "flex",
                    justifyContent: "space-between",
                    borderBottom: i < recentClasses.length - 1 ? "1px solid var(--color-border)" : "none",
                  }}
                >
                  <div>
                    <span style={{ fontSize: "0.9375rem", fontWeight: 500 }}>{c.name}</span>
                    <span style={{ fontSize: "0.8rem", color: "var(--color-text-muted)", marginLeft: "8px" }}>
                      {c.course_title}
                    </span>
                  </div>
                  <span style={{ fontSize: "0.8125rem", color: "var(--color-text-muted)" }}>
                    {c.schedule_info ?? "Sin horario"}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        <div>
          <h2 style={{ fontSize: "1.25rem", fontWeight: 600, marginBottom: "16px" }}>Pagos pendientes</h2>
          <div className="card">
            {loading ? (
              <p style={{ color: "var(--color-text-muted)", fontSize: "0.9rem" }}>Cargando pagos…</p>
            ) : (
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <div>
                  <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "var(--color-primary)" }}>
                    {pendingPayments}
                  </div>
                  <div style={{ fontSize: "0.875rem", color: "var(--color-text-muted)" }}>
                    pagos aprobados sin clase asignada
                  </div>
                </div>
                <Link href="/coordinator/payments" className="btn btn-primary btn-sm">
                  Ver pagos
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
