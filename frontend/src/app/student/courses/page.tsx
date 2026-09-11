"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { formatCurrency } from "@/lib/currency";
import { toast } from "@/components/ui/Toast";

interface PaymentItem {
  id: string;
  course_title: string;
  course_id: string;
  amount: number;
  currency: string;
  status: string;
  created_at: string | null;
  payment_plan?: string;
  expected_amount?: number;
}

interface EnrolledClass {
  id: string;
  course_id: string;
  name: string;
  teacher_name?: string | null;
  schedule_info?: string | null;
  meeting_url?: string | null;
  meeting_platform?: string | null;
}

function getStatusBadge(status: string) {
  switch (status) {
    case "approved":
      return { cls: "badge-success", label: "Activo" };
    case "approved_pending_class":
      return { cls: "badge-info", label: "Aprobado, sin clase" };
    case "pending":
      return { cls: "badge-warning", label: "En revisión" };
    case "rejected":
      return { cls: "badge-error", label: "Rechazado" };
    default:
      return { cls: "badge-secondary", label: status };
  }
}

export default function StudentCoursesPage() {
  const [payments, setPayments] = useState<PaymentItem[]>([]);
  const [classes, setClasses] = useState<Record<string, EnrolledClass>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [paymentsData, classesData] = await Promise.all([
          api.get<{ items: PaymentItem[] }>("/payments/my-payments"),
          api.get<{ items: EnrolledClass[] }>("/students/me/classes"),
        ]);
        setPayments(paymentsData.items || []);
        const classMap: Record<string, EnrolledClass> = {};
        (classesData.items || []).forEach((c) => {
          classMap[c.course_id] = c;
        });
        setClasses(classMap);
      } catch {
        toast.error("No se pudieron cargar los cursos");
        setPayments([]);
        setClasses({});
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  const active = payments.filter(
    (p) => p.status === "approved" && classes[p.course_id]
  );
  const pendingClass = payments.filter(
    (p) => p.status === "approved_pending_class"
  );
  const inReview = payments.filter((p) => p.status === "pending");

  return (
    <>
      <div className="page-header">
        <h1>Mis Cursos</h1>
        <p>Cursos en los que estás inscrito.</p>
      </div>

      {loading ? (
        <div className="card" style={{ textAlign: "center", padding: "40px", color: "var(--color-text-muted)" }}>
          Cargando cursos...
        </div>
      ) : active.length === 0 && pendingClass.length === 0 && inReview.length === 0 ? (
        <div className="card" style={{ textAlign: "center", padding: "48px" }}>
          <div style={{ fontSize: "3rem", marginBottom: "16px" }}>📭</div>
          <h3 style={{ fontWeight: 600, marginBottom: "8px" }}>Sin cursos aún</h3>
          <p style={{ color: "var(--color-text-muted)", marginBottom: "24px" }}>
            No tienes cursos inscritos. Explora el catálogo y encuentra tu próximo curso.
          </p>
          <a href="/courses" className="btn btn-primary">Ver catálogo</a>
        </div>
      ) : (
        <div className="grid-cards">
          {active.map((c) => {
            const badge = getStatusBadge("approved");
            const cls = classes[c.course_id];
            return (
              <div key={c.id} className="card">
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "12px" }}>
                  <span style={{ fontSize: "1.5rem" }}>📚</span>
                  <span className={`badge ${badge.cls}`}>{badge.label}</span>
                </div>
                <h3 style={{ fontSize: "1rem", fontWeight: 600, marginBottom: "8px" }}>{c.course_title}</h3>
                <div style={{ fontSize: "0.8125rem", color: "var(--color-text-muted)", marginBottom: "12px" }}>
                  {cls && (
                    <>
                      <p style={{ marginBottom: "4px" }}>
                        <strong>Clase:</strong> {cls.name}
                      </p>
                      {cls.teacher_name && (
                        <p style={{ marginBottom: "4px" }}>
                          <strong>Profesor:</strong> {cls.teacher_name}
                        </p>
                      )}
                      {cls.schedule_info && (
                        <p style={{ marginBottom: "4px" }}>
                          <strong>Horario:</strong> {cls.schedule_info}
                        </p>
                      )}
                      {cls.meeting_url && (
                        <p>
                          <a href={cls.meeting_url} target="_blank" rel="noopener noreferrer" style={{ color: "var(--color-primary)" }}>
                            Enlace de clase →
                          </a>
                        </p>
                      )}
                    </>
                  )}
                </div>
                <p style={{ fontSize: "0.8125rem", color: "var(--color-text-muted)" }}>
                  Inscrito el {c.created_at ? new Date(c.created_at).toLocaleDateString("es-MX") : "—"}
                </p>
              </div>
            );
          })}
          {pendingClass.map((c) => {
            const badge = getStatusBadge("approved_pending_class");
            return (
              <div key={c.id} className="card">
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "12px" }}>
                  <span style={{ fontSize: "1.5rem" }}>⏳</span>
                  <span className={`badge ${badge.cls}`}>{badge.label}</span>
                </div>
                <h3 style={{ fontSize: "1rem", fontWeight: 600, marginBottom: "8px" }}>{c.course_title}</h3>
                <p style={{ fontSize: "0.8125rem", color: "var(--color-text-muted)", marginBottom: "12px" }}>
                  Pago aprobado, pendiente de asignación de clase.
                </p>
                <p style={{ fontSize: "0.8125rem", color: "var(--color-text-muted)" }}>
                  Inscrito el {c.created_at ? new Date(c.created_at).toLocaleDateString("es-MX") : "—"}
                </p>
              </div>
            );
          })}
          {inReview.map((c) => (
            <div key={c.id} className="card">
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "12px" }}>
                <span style={{ fontSize: "1.5rem" }}>🕐</span>
                <span className="badge badge-warning">En revisión</span>
              </div>
              <h3 style={{ fontSize: "1rem", fontWeight: 600, marginBottom: "8px" }}>{c.course_title}</h3>
              <p style={{ fontSize: "0.8125rem", color: "var(--color-text-muted)" }}>
                Comprobante en revisión
              </p>
            </div>
          ))}
        </div>
      )}
    </>
  );
}
