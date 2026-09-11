"use client";

import { useEffect, useState } from "react";
import Modal from "@/components/ui/Modal";
import { api } from "@/lib/api";
import { toast } from "@/components/ui/Toast";
import { formatCurrency } from "@/lib/currency";
import { AdminPayment } from "@/hooks/useAdminData";
import { CourseClass, PaginatedResponse } from "@/types";

export default function CoordinatorPaymentsPage() {
  const [payments, setPayments] = useState<AdminPayment[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPayment, setSelectedPayment] = useState<AdminPayment | null>(null);
  const [classesForCourse, setClassesForCourse] = useState<CourseClass[]>([]);
  const [selectedClassId, setSelectedClassId] = useState<string>("");
  const [modalOpen, setModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);

  const loadPayments = async () => {
    setLoading(true);
    try {
      const res = await api.get<PaginatedResponse<AdminPayment>>(
        "/payments/admin/list?status=approved_pending_class&per_page=50"
      );
      setPayments(res.items);
    } catch {
      toast.error("Error al cargar pagos");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPayments();
  }, []);

  const openAssign = async (payment: AdminPayment) => {
    setSelectedPayment(payment);
    setSelectedClassId("");
    setClassesForCourse([]);
    setModalOpen(true);
    try {
      const list = await api.get<CourseClass[]>(`/courses/${payment.course!.id}/classes`);
      const available = list.filter(
        (c) => c.status === "active" && (c.available_slots === undefined || c.available_slots > 0)
      );
      setClassesForCourse(available);
      if (available.length > 0) {
        setSelectedClassId(available[0].id);
      }
    } catch {
      toast.error("Error al cargar clases del curso");
      setClassesForCourse([]);
    }
  };

  const handleAssign = async () => {
    if (!selectedPayment || !selectedClassId) return;
    setSaving(true);
    try {
      await api.post(`/payments/${selectedPayment.id}/assign-class`, {
        course_class_id: selectedClassId,
      });
      toast.success("Pago asignado a clase correctamente");
      setModalOpen(false);
      setSelectedPayment(null);
      await loadPayments();
    } catch {
      toast.error("Error al asignar clase al pago");
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <div className="page-header">
        <h1>Pagos pendientes</h1>
        <p>Pagos aprobados que requieren asignación a una clase.</p>
      </div>

      {loading ? (
        <div className="card" style={{ textAlign: "center", padding: "40px", color: "var(--color-text-muted)" }}>
          Cargando pagos…
        </div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Estudiante</th>
                <th>Curso</th>
                <th>Monto</th>
                <th>Plan</th>
                <th>Fecha</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {payments.length === 0 && (
                <tr>
                  <td colSpan={6} style={{ textAlign: "center", color: "var(--color-text-muted)", padding: "40px" }}>
                    No hay pagos pendientes de asignación.
                  </td>
                </tr>
              )}
              {payments.map((p) => (
                <tr key={p.id}>
                  <td style={{ fontWeight: 500 }}>
                    {p.student?.full_name ?? "—"}
                    <br />
                    <span style={{ fontSize: "0.75rem", color: "var(--color-text-muted)" }}>{p.student?.email}</span>
                  </td>
                  <td style={{ fontSize: "0.875rem" }}>{p.course?.title ?? "—"}</td>
                  <td style={{ fontWeight: 600 }}>{formatCurrency(p.amount, p.currency)}</td>
                  <td style={{ fontSize: "0.875rem" }}>{p.payment_plan ?? "—"}</td>
                  <td style={{ fontSize: "0.8125rem" }}>
                    {p.created_at ? new Date(p.created_at).toLocaleDateString("es-MX") : "—"}
                  </td>
                  <td>
                    <button className="btn btn-primary btn-sm" onClick={() => openAssign(p)}>
                      Asignar a clase
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Assign Class Modal */}
      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Asignar a clase" width="520px">
        {selectedPayment && (
          <div>
            <div className="card" style={{ marginBottom: "16px", background: "var(--color-bg)" }}>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
                <div>
                  <span
                    style={{
                      fontSize: "0.75rem",
                      color: "var(--color-text-muted)",
                      textTransform: "uppercase",
                      fontWeight: 600,
                    }}
                  >
                    Estudiante
                  </span>
                  <p style={{ fontWeight: 500, margin: "4px 0 0" }}>{selectedPayment.student?.full_name}</p>
                  <p style={{ fontSize: "0.8rem", color: "var(--color-text-muted)", margin: 0 }}>
                    {selectedPayment.student?.email}
                  </p>
                </div>
                <div>
                  <span
                    style={{
                      fontSize: "0.75rem",
                      color: "var(--color-text-muted)",
                      textTransform: "uppercase",
                      fontWeight: 600,
                    }}
                  >
                    Curso
                  </span>
                  <p style={{ fontWeight: 500, margin: "4px 0 0" }}>{selectedPayment.course?.title}</p>
                  <p style={{ fontWeight: 700, color: "var(--color-primary)", margin: 0 }}>
                    {formatCurrency(selectedPayment.amount, selectedPayment.currency)}
                  </p>
                </div>
              </div>
            </div>

            {classesForCourse.length === 0 ? (
              <div
                style={{
                  background: "rgba(239,68,68,0.08)",
                  border: "1px solid rgba(239,68,68,0.2)",
                  padding: "16px",
                  borderRadius: "8px",
                  fontSize: "0.9375rem",
                  color: "var(--color-text)",
                }}
              >
                No hay clases disponibles con cupo. Cree una nueva clase antes de asignar.
              </div>
            ) : (
              <div style={{ marginBottom: "24px" }}>
                <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>
                  Clase disponible
                </label>
                <select
                  className="input"
                  value={selectedClassId}
                  onChange={(e) => setSelectedClassId(e.target.value)}
                >
                  {classesForCourse.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name} — Cupo: {c.available_slots ?? c.global_max ?? "—"} alumnos
                    </option>
                  ))}
                </select>
              </div>
            )}

            <div style={{ display: "flex", gap: "12px", justifyContent: "flex-end" }}>
              <button className="btn btn-secondary" onClick={() => setModalOpen(false)}>
                Cancelar
              </button>
              <button
                className="btn btn-primary"
                onClick={handleAssign}
                disabled={saving || classesForCourse.length === 0 || !selectedClassId}
              >
                {saving ? "Asignando…" : "Confirmar asignación"}
              </button>
            </div>
          </div>
        )}
      </Modal>
    </>
  );
}
