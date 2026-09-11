"use client";

import { useState, useEffect, useCallback } from "react";
import Modal from "@/components/ui/Modal";
import { useAdminPayments, AdminPayment, CourseClassItem } from "@/hooks/useAdminData";
import { toast } from "@/components/ui/Toast";
import { getToken } from "@/lib/auth";
import { api } from "@/lib/api";
import { formatCurrency } from "@/lib/currency";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api/v1";

const TABS = [
  { key: "pending",  label: "Pendientes", badge: "badge-warning" },
  { key: "approved", label: "Aprobados",  badge: "badge-success" },
  { key: "approved_pending_class", label: "Aprobados sin clase", badge: "badge-success" },
  { key: "rejected", label: "Rechazados", badge: "badge-error"   },
  { key: "all",      label: "Todos",      badge: "badge-neutral"  },
];

const STATUS_LABELS: Record<string, string> = {
  pending: "Pendiente",
  approved: "Aprobado",
  approved_pending_class: "Aprobado, sin clase",
  rejected: "Rechazado",
  pending_proof: "Sin comprobante",
};

/** Fetch a proof image with Authorization header and return a blob URL. */
function useProofImage(proofUrl: string | null) {
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!proofUrl) {
      setImageUrl(null);
      return;
    }

    let revoked = false;
    let objectUrl: string | null = null;
    setLoading(true);

    const token = getToken();
    fetch(`${API_BASE}${proofUrl}`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to load proof");
        return res.blob();
      })
      .then((blob) => {
        if (!revoked) {
          objectUrl = URL.createObjectURL(blob);
          setImageUrl(objectUrl);
        }
      })
      .catch(() => {
        if (!revoked) setImageUrl(null);
      })
      .finally(() => {
        if (!revoked) setLoading(false);
      });

    return () => {
      revoked = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [proofUrl]);

  return { imageUrl, loading };
}

export default function AdminPaymentsPage() {
  const { data, loading, status, setStatus, approvePayment, rejectPayment, refresh } = useAdminPayments();
  const [selected, setSelected] = useState<AdminPayment | null>(null);
  const [action, setAction] = useState<"approve" | "reject" | null>(null);
  const [notes, setNotes] = useState("");
  const [saving, setSaving] = useState(false);
  const [viewingProof, setViewingProof] = useState<string | null>(null);
  const [assigning, setAssigning] = useState<AdminPayment | null>(null);
  const [availableClasses, setAvailableClasses] = useState<CourseClassItem[]>([]);
  const [selectedClassId, setSelectedClassId] = useState("");
  const [assignSaving, setAssignSaving] = useState(false);

  const proofImage = useProofImage(
    selected && action && selected.proofs.length > 0
      ? selected.proofs[0].file_url
      : null
  );

  const viewerImage = useProofImage(viewingProof);

  const openAction = (payment: AdminPayment, act: "approve" | "reject") => {
    setSelected(payment);
    setAction(act);
    setNotes("");
  };

  const openAssign = async (payment: AdminPayment) => {
    setAssigning(payment);
    setSelectedClassId("");
    try {
      const res = await api.get<{ items: CourseClassItem[] }>(`/courses/${payment.course_id}/classes`);
      setAvailableClasses(res.items ?? []);
    } catch {
      toast.error("Error al cargar clases");
      setAvailableClasses([]);
    }
  };

  const handleAssign = async () => {
    if (!assigning || !selectedClassId) return;
    setAssignSaving(true);
    try {
      await api.post(`/payments/${assigning.id}/assign-class`, { course_class_id: selectedClassId });
      toast.success("Clase asignada correctamente");
      setAssigning(null);
      refresh();
    } catch {
      toast.error("Error al asignar clase");
    } finally {
      setAssignSaving(false);
    }
  };

  const handleAction = async () => {
    if (!selected || !action) return;
    setSaving(true);
    try {
      if (action === "approve") {
        const res = await approvePayment(selected.id, notes || undefined);
        if ((res as any)?.status === "approved_pending_class") {
          toast.success("Pago aprobado, pendiente de asignación de clase.");
        } else {
          toast.success("Pago aprobado ✅");
        }
      } else {
        await rejectPayment(selected.id, notes || undefined);
      }
      setSelected(null); setAction(null);
    } catch { toast.error("Error al procesar el pago"); }
    finally { setSaving(false); }
  };

  const payments = data?.items ?? [];

  return (
    <>
      <div className="page-header">
        <h1>Pagos</h1>
        <p>Revisión y gestión de pagos de la plataforma ({data?.total ?? "…"} registros).</p>
      </div>

      {/* Status Tabs */}
      <div style={{ display: "flex", gap: "8px", marginBottom: "24px", flexWrap: "wrap" }}>
        {TABS.map(t => (
          <button
            key={t.key}
            className={`btn btn-sm ${status === t.key ? "btn-primary" : "btn-secondary"}`}
            onClick={() => setStatus(t.key)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="card" style={{ textAlign: "center", padding: "40px", color: "var(--color-text-muted)" }}>Cargando pagos…</div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Usuario</th><th>Curso</th><th>Plan</th><th>Monto</th>
                <th>Comprobante</th><th>Fecha</th><th>Estado</th><th>Acciones</th>
              </tr>
            </thead>
            <tbody>
                {payments.length === 0 && (
                <tr><td colSpan={8} style={{ textAlign: "center", color: "var(--color-text-muted)", padding: "40px" }}>
                  No hay pagos {status !== "all" ? `con estado "${STATUS_LABELS[status] || status}"` : ""}.
                </td></tr>
              )}
              {payments.map((p) => (
                <tr key={p.id}>
                  <td style={{ fontWeight: 500 }}>
                    {p.student?.full_name ?? "—"}<br/>
                    <span style={{ fontSize: "0.75rem", color: "var(--color-text-muted)" }}>{p.student?.email}</span>
                  </td>
                  <td style={{ fontSize: "0.875rem" }}>{p.course?.title ?? "—"}</td>
                  <td style={{ fontSize: "0.875rem" }}>
                    {p.payment_plan === "monthly" ? "Mensual" : p.payment_plan === "full" ? "Completo" : "—"}
                  </td>
                  <td style={{ fontWeight: 600 }}>
                    {formatCurrency(p.expected_amount ?? p.amount, p.currency)}
                  </td>
                  <td>
                    {p.proofs.length > 0 ? (
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => setViewingProof(p.proofs[0].file_url)}
                      >
                        📎 Ver comprobante
                      </button>
                    ) : (
                      <span style={{ fontSize: "0.8rem", color: "var(--color-text-muted)" }}>Sin comprobante</span>
                    )}
                  </td>
                  <td style={{ fontSize: "0.8125rem" }}>
                    {p.created_at ? new Date(p.created_at).toLocaleDateString("es-MX") : "—"}
                  </td>
                  <td>
                    <span className={`badge ${
                      p.status === "approved" || p.status === "approved_pending_class" ? "badge-success" :
                      p.status === "rejected" ? "badge-error" : "badge-warning"
                    }`}>
                      {STATUS_LABELS[p.status] || p.status}
                    </span>
                  </td>
                  <td>
                    <div style={{ display: "flex", gap: "4px" }}>
                      {p.status === "pending" && (
                        <>
                          <button className="btn btn-primary btn-sm" onClick={() => openAction(p, "approve")}>✓ Aprobar</button>
                          <button className="btn btn-danger btn-sm" onClick={() => openAction(p, "reject")}>✗ Rechazar</button>
                        </>
                      )}
                      {p.status === "approved_pending_class" && (
                        <button className="btn btn-primary btn-sm" onClick={() => openAssign(p)}>Asignar a clase</button>
                      )}
                      {p.status !== "pending" && p.review_notes && (
                        <button
                          className="btn btn-secondary btn-sm"
                          title={p.review_notes}
                          onClick={() => { setSelected(p); setAction(null); }}
                        >
                          💬 Notas
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Approve / Reject Modal */}
      <Modal
        open={!!selected && !!action}
        onClose={() => { setSelected(null); setAction(null); }}
        title={action === "approve" ? "✅ Aprobar pago" : "❌ Rechazar pago"}
        width="500px"
      >
        {selected && action && (
          <div>
            {/* Student & Course Info */}
            <div className="card" style={{ marginBottom: "16px", background: "var(--color-bg)" }}>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
                <div>
                  <span style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", textTransform: "uppercase", fontWeight: 600 }}>Usuario</span>
                  <p style={{ fontWeight: 500, margin: "4px 0 0" }}>{selected.student?.full_name}</p>
                  <p style={{ fontSize: "0.8rem", color: "var(--color-text-muted)", margin: 0 }}>{selected.student?.email}</p>
                </div>
                <div>
                  <span style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", textTransform: "uppercase", fontWeight: 600 }}>Curso</span>
                  <p style={{ fontWeight: 500, margin: "4px 0 0" }}>{selected.course?.title}</p>
                  <p style={{ fontWeight: 700, color: "var(--color-primary)", margin: 0 }}>{formatCurrency(selected.amount, selected.currency)}</p>
                </div>
              </div>
            </div>

            {/* Proof preview — fetched securely, no token in URL */}
            {selected.proofs.length > 0 && (
              <div style={{ marginBottom: "16px" }}>
                <span style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", textTransform: "uppercase", fontWeight: 600, display: "block", marginBottom: "8px" }}>
                  Comprobante adjunto
                </span>
                <div style={{ border: "1px solid var(--color-border)", borderRadius: "8px", overflow: "hidden", maxHeight: "200px" }}>
                  {proofImage.loading ? (
                    <div style={{ textAlign: "center", padding: "20px", color: "var(--color-text-muted)" }}>Cargando…</div>
                  ) : proofImage.imageUrl ? (
                    /* eslint-disable-next-line @next/next/no-img-element */
                    <img
                      src={proofImage.imageUrl}
                      alt="Comprobante"
                      style={{ width: "100%", objectFit: "contain", maxHeight: "200px", cursor: "pointer" }}
                      onClick={() => setViewingProof(selected.proofs[0].file_url)}
                    />
                  ) : (
                    <div style={{ textAlign: "center", padding: "20px", color: "var(--color-text-muted)" }}>Error al cargar comprobante</div>
                  )}
                </div>
              </div>
            )}

            {/* Notes */}
            <div style={{ marginBottom: "16px" }}>
              <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>
                {action === "approve" ? "Notas de aprobación (opcional)" : "Motivo del rechazo"}
              </label>
              <textarea
                className="input" rows={3}
                value={notes} onChange={e => setNotes(e.target.value)}
                placeholder={action === "approve" ? "Pago verificado correctamente…" : "Razón del rechazo…"}
                style={{ resize: "vertical" }}
                required={action === "reject"}
              />
            </div>

            {action === "approve" && (
              <div style={{
                background: "rgba(34,197,94,0.08)", border: "1px solid rgba(34,197,94,0.2)",
                padding: "12px", borderRadius: "8px", marginBottom: "16px", fontSize: "0.8125rem",
              }}>
                <strong>Al aprobar:</strong> Se creará la inscripción del alumno, se activará su acceso al curso
                y se le asignará el rol de estudiante automáticamente.
              </div>
            )}

            <div style={{ display: "flex", gap: "12px", justifyContent: "flex-end" }}>
              <button className="btn btn-secondary" onClick={() => { setSelected(null); setAction(null); }}>Cancelar</button>
              <button
                className={`btn ${action === "approve" ? "btn-primary" : "btn-danger"}`}
                onClick={handleAction} disabled={saving}
              >
                {saving ? "Procesando…" : action === "approve" ? "Confirmar aprobación" : "Confirmar rechazo"}
              </button>
            </div>
          </div>
        )}
      </Modal>

      {/* Review Notes Modal */}
      <Modal
        open={!!selected && !action && !viewingProof}
        onClose={() => setSelected(null)}
        title="Notas de revisión"
        width="420px"
      >
        {selected && (
          <div>
            <p style={{ marginBottom: "8px", fontWeight: 500 }}>{selected.student?.full_name} — {selected.course?.title}</p>
            <p style={{ fontSize: "0.875rem", color: "var(--color-text-muted)", background: "var(--color-bg)", padding: "16px", borderRadius: "8px" }}>
              {selected.review_notes || "Sin notas."}
            </p>
            {selected.reviewed_at && (
              <p style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", marginTop: "8px" }}>
                Revisado: {new Date(selected.reviewed_at).toLocaleString("es-MX")}
              </p>
            )}
          </div>
        )}
      </Modal>

      {/* Full-screen Proof Viewer */}
      {viewingProof && (
        <div
          style={{
            position: "fixed", inset: 0, background: "rgba(0,0,0,0.85)", display: "flex",
            alignItems: "center", justifyContent: "center", zIndex: 2000, cursor: "pointer",
          }}
          onClick={() => setViewingProof(null)}
        >
          <div style={{ position: "relative", maxWidth: "90vw", maxHeight: "90vh" }}>
            <button
              onClick={() => setViewingProof(null)}
              style={{
                position: "absolute", top: "-40px", right: 0, background: "none",
                border: "none", color: "#fff", fontSize: "2rem", cursor: "pointer",
              }}
            >×</button>
            {viewerImage.loading ? (
              <div style={{ color: "#fff", fontSize: "1rem" }}>Cargando…</div>
            ) : viewerImage.imageUrl ? (
              /* eslint-disable-next-line @next/next/no-img-element */
              <img
                src={viewerImage.imageUrl}
                alt="Comprobante de pago"
                style={{ maxWidth: "90vw", maxHeight: "85vh", objectFit: "contain", borderRadius: "8px" }}
              />
            ) : (
              <div style={{ color: "#fff" }}>Error al cargar comprobante</div>
            )}
          </div>
        </div>
      )}

      {/* Assign Class Modal */}
      <Modal
        open={!!assigning}
        onClose={() => setAssigning(null)}
        title="Asignar a clase"
        width="500px"
      >
        {assigning && (
          <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <div>
              <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>
                Clase disponible para {assigning.course?.title}
              </label>
              <select
                className="input"
                value={selectedClassId}
                onChange={e => setSelectedClassId(e.target.value)}
                required
              >
                <option value="">— Seleccionar clase —</option>
                {availableClasses.map(cls => (
                  <option key={cls.id} value={cls.id}>{cls.name} — {cls.schedule_info || "Sin horario"}</option>
                ))}
              </select>
              {availableClasses.length === 0 && (
                <p style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", marginTop: "4px" }}>
                  No hay clases activas para este curso.
                </p>
              )}
            </div>
            <div style={{ display: "flex", gap: "12px", justifyContent: "flex-end" }}>
              <button className="btn btn-secondary" onClick={() => setAssigning(null)}>Cancelar</button>
              <button
                className="btn btn-primary"
                onClick={handleAssign}
                disabled={assignSaving || !selectedClassId}
              >
                {assignSaving ? "Asignando…" : "Confirmar asignación"}
              </button>
            </div>
          </div>
        )}
      </Modal>
    </>
  );
}
