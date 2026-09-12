"use client";

/**
 * CodeAcademy Pro — Alumno: Mis Cursos
 *
 * La tarjeta sale de la INSCRIPCIÓN (`/students/me/progress`), que guarda el estado del
 * ciclo de pago (aprobado sin clase → con clase), no del pago suelto. Los pagos se usan
 * sólo para lo que aún NO tiene inscripción: comprobante en revisión o rechazado.
 *
 * Estados que ve el alumno:
 *   en_revision   → subió el comprobante, pendiente de confirmación de pago
 *   espera_clase  → pago confirmado, en espera de asignación de clase
 *   activo        → clase asignada: horario, enlace de clase y grabación
 *   rechazado / completado / cancelado
 */

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { formatCurrency } from "@/lib/currency";
import { toast } from "@/components/ui/Toast";
import { useStudentProgress, StudentProgressRow } from "@/hooks/useStudentProgress";

interface PaymentItem {
  id: string;
  course_title: string;
  course_id: string;
  amount: number;
  currency: string;
  status: string;
  created_at: string | null;
  review_notes?: string | null;
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
  recording_url?: string | null;
  recording_platform?: string | null;
}

type Estado = "activo" | "espera_clase" | "en_revision" | "rechazado" | "completado" | "cancelado";

const ESTADOS: Record<Estado, { icon: string; badge: string; label: string; note: string }> = {
  activo: { icon: "📚", badge: "badge-success", label: "Activo", note: "" },
  espera_clase: {
    icon: "⏳",
    badge: "badge-info",
    label: "En espera de asignación de clase",
    note: "Tu pago está confirmado. En cuanto administración te asigne una clase verás aquí el horario, el enlace de la clase en vivo y la grabación.",
  },
  en_revision: {
    icon: "🕐",
    badge: "badge-warning",
    label: "Pendiente de confirmación",
    note: "Recibimos tu comprobante. Administración lo revisará y te habilitará el curso.",
  },
  rechazado: {
    icon: "⛔",
    badge: "badge-error",
    label: "Pago rechazado",
    note: "Tu comprobante no fue validado. Puedes volver a subirlo desde la ficha del curso.",
  },
  completado: { icon: "🎓", badge: "badge-success", label: "Completado", note: "" },
  cancelado: { icon: "🚫", badge: "badge-secondary", label: "Cancelado", note: "" },
};

/** Traduce el estado de la inscripción (o del pago, si aún no hay inscripción). */
function estadoDeInscripcion(row: StudentProgressRow): Estado {
  switch (row.status) {
    case "active":
      return row.course_class_id ? "activo" : "espera_clase";
    case "payment_approved":
      return "espera_clase";
    case "payment_rejected":
      return "rechazado";
    case "completed":
      return "completado";
    case "cancelled":
      return "cancelado";
    default:
      return "en_revision";
  }
}

function estadoDePago(status: string): Estado {
  if (status === "rejected") return "rechazado";
  return "en_revision";
}

interface Tarjeta {
  key: string;
  courseId: string;
  title: string;
  estado: Estado;
  date: string | null;
  clase?: EnrolledClass;
  enrollment?: StudentProgressRow;
  pago?: PaymentItem;
}

export default function StudentCoursesPage() {
  const [payments, setPayments] = useState<PaymentItem[]>([]);
  const [classes, setClasses] = useState<Record<string, EnrolledClass>>({});
  const [loading, setLoading] = useState(true);
  // El progreso (y el estado de la inscripción) lo escribe el docente/administración:
  // aquí sólo se lee.
  const { data: enrollments, loading: loadingEnrollments } = useStudentProgress();

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

  const enrolledCourseIds = new Set(enrollments.map((e) => e.course_id));

  const tarjetas: Tarjeta[] = [
    ...enrollments.map<Tarjeta>((e) => ({
      key: `enrollment-${e.enrollment_id}`,
      courseId: e.course_id,
      title: e.course_title || "Curso",
      estado: estadoDeInscripcion(e),
      date: e.enrolled_at ?? null,
      clase: classes[e.course_id],
      enrollment: e,
      pago: payments.find((p) => p.course_id === e.course_id),
    })),
    // Pagos sin inscripción todavía: comprobante en revisión o rechazado.
    ...payments
      .filter((p) => !enrolledCourseIds.has(p.course_id))
      .map<Tarjeta>((p) => ({
        key: `payment-${p.id}`,
        courseId: p.course_id,
        title: p.course_title,
        estado: estadoDePago(p.status),
        date: p.created_at,
        pago: p,
      })),
  ];

  const orden: Estado[] = ["activo", "espera_clase", "en_revision", "rechazado", "completado", "cancelado"];
  tarjetas.sort((a, b) => orden.indexOf(a.estado) - orden.indexOf(b.estado));

  return (
    <>
      <div className="page-header">
        <h1>Mis Cursos</h1>
        <p>Cursos en los que estás inscrito y el estado de tu pago.</p>
      </div>

      {loading || loadingEnrollments ? (
        <div className="card" style={{ textAlign: "center", padding: "40px", color: "var(--color-text-muted)" }}>
          Cargando cursos...
        </div>
      ) : tarjetas.length === 0 ? (
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
          {tarjetas.map((t) => {
            const estado = ESTADOS[t.estado];
            const clase = t.clase;
            const progreso = t.enrollment;
            return (
              <div key={t.key} className="card">
                <div style={{ display: "flex", justifyContent: "space-between", gap: "8px", marginBottom: "12px" }}>
                  <span style={{ fontSize: "1.5rem" }}>{estado.icon}</span>
                  <span className={`badge ${estado.badge}`}>{estado.label}</span>
                </div>

                <h3 style={{ fontSize: "1rem", fontWeight: 600, marginBottom: "8px" }}>{t.title}</h3>

                {estado.note && (
                  <p style={{ fontSize: "0.8125rem", color: "var(--color-text-muted)", marginBottom: "12px" }}>
                    {estado.note}
                  </p>
                )}

                {t.estado === "rechazado" && t.pago?.review_notes && (
                  <p style={{ fontSize: "0.8125rem", color: "var(--color-danger, #ef4444)", marginBottom: "12px" }}>
                    <strong>Motivo:</strong> {t.pago.review_notes}
                  </p>
                )}

                {t.estado === "en_revision" && t.pago && (
                  <p style={{ fontSize: "0.8125rem", color: "var(--color-text-muted)", marginBottom: "12px" }}>
                    Monto declarado: {formatCurrency(t.pago.amount, t.pago.currency)}
                  </p>
                )}

                {clase && (t.estado === "activo" || t.estado === "completado") && (
                  <div style={{ fontSize: "0.8125rem", color: "var(--color-text-muted)", marginBottom: "12px" }}>
                    <p style={{ marginBottom: "4px" }}><strong>Clase:</strong> {clase.name}</p>
                    {clase.teacher_name && (
                      <p style={{ marginBottom: "4px" }}><strong>Profesor:</strong> {clase.teacher_name}</p>
                    )}
                    {clase.schedule_info && (
                      <p style={{ marginBottom: "4px" }}><strong>Horario:</strong> {clase.schedule_info}</p>
                    )}
                    {clase.meeting_url && (
                      <p style={{ marginBottom: "4px" }}>
                        <a href={clase.meeting_url} target="_blank" rel="noopener noreferrer" style={{ color: "var(--color-primary)" }}>
                          Enlace de la clase en vivo →
                        </a>
                      </p>
                    )}
                    {clase.recording_url && (
                      <p>
                        <a href={clase.recording_url} target="_blank" rel="noopener noreferrer" style={{ color: "var(--color-primary)" }}>
                          Ver grabación{clase.recording_platform ? ` (${clase.recording_platform})` : ""} →
                        </a>
                      </p>
                    )}
                  </div>
                )}

                {progreso && (t.estado === "activo" || t.estado === "completado") && (
                  <div style={{ marginBottom: "12px" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.8125rem", marginBottom: "4px" }}>
                      <span style={{ color: "var(--color-text-muted)" }}>Tu progreso</span>
                      <span>{progreso.progress_percentage}%</span>
                    </div>
                    <div className="progress-bar">
                      <div className="progress-fill" style={{ width: `${progreso.progress_percentage}%` }} />
                    </div>
                    {progreso.completed_at && (
                      <p style={{ fontSize: "0.8125rem", color: "var(--color-text-muted)", marginTop: "6px" }}>
                        ✅ Curso completado
                      </p>
                    )}
                  </div>
                )}

                <p style={{ fontSize: "0.8125rem", color: "var(--color-text-muted)" }}>
                  {t.date ? `Desde el ${new Date(t.date).toLocaleDateString("es-MX")}` : ""}
                </p>
              </div>
            );
          })}
        </div>
      )}
    </>
  );
}
