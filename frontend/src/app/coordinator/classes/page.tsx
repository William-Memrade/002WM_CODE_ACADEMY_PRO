"use client";

import { useState } from "react";
import Modal from "@/components/ui/Modal";
import { useClasses, ClassFilter, CourseClassItem } from "@/hooks/useAdminData";
import { toast } from "@/components/ui/Toast";

const WEEKDAY_LABELS: Record<string, string> = {
  mon: "Lun", tue: "Mar", wed: "Mié", thu: "Jue", fri: "Vie", sat: "Sáb", sun: "Dom",
};

const STATUS_LABELS: Record<string, string> = {
  active: "Activa", inactive: "Inactiva", cancelled: "Cancelada",
};

const STATUS_BADGE: Record<string, string> = {
  active: "badge-success", inactive: "badge-warning", cancelled: "badge-error",
};

const FILTERS: { key: ClassFilter; label: string }[] = [
  { key: "today", label: "Clases de hoy" },
  { key: "all", label: "Todas" },
  { key: "without_teacher", label: "Sin docente" },
  { key: "available_slots", label: "Cupos disponibles" },
  { key: "missing_link", label: "Sin enlace" },
  { key: "inactive", label: "Inactivas" },
  { key: "cancelled", label: "Canceladas" },
];

export default function CoordinatorClassesPage() {
  const [activeFilter, setActiveFilter] = useState<ClassFilter>("today");
  const { data: classes, loading, refresh, updateStatus, updateMeetingLink } = useClasses(activeFilter);

  const [meetingModal, setMeetingModal] = useState<CourseClassItem | null>(null);
  const [meetingPlatform, setMeetingPlatform] = useState("");
  const [meetingUrl, setMeetingUrl] = useState("");
  const [saving, setSaving] = useState(false);

  const [confirmStatus, setConfirmStatus] = useState<{ cls: CourseClassItem; status: string } | null>(null);

  const openMeeting = (cls: CourseClassItem) => {
    setMeetingModal(cls);
    setMeetingPlatform(cls.meeting_platform || "");
    setMeetingUrl(cls.meeting_url || "");
  };

  const saveMeeting = async () => {
    if (!meetingModal) return;
    setSaving(true);
    try {
      await updateMeetingLink(meetingModal.id, meetingPlatform, meetingUrl);
      setMeetingModal(null);
    } catch {
      toast.error("Error al guardar enlace");
    } finally {
      setSaving(false);
    }
  };

  const handleStatusChange = async () => {
    if (!confirmStatus) return;
    setSaving(true);
    try {
      await updateStatus(confirmStatus.cls.id, confirmStatus.status);
      setConfirmStatus(null);
    } catch {
      toast.error("Error al cambiar estado");
    } finally {
      setSaving(false);
    }
  };

  const renderActions = (cls: CourseClassItem) => {
    return (
      <div style={{ display: "flex", gap: "4px", flexWrap: "wrap" }}>
        <button className="btn btn-secondary btn-sm" onClick={() => openMeeting(cls)}>
          {cls.meeting_url ? "Editar enlace" : "Asignar enlace"}
        </button>
        {cls.status === "active" ? (
          <button className="btn btn-warning btn-sm" onClick={() => setConfirmStatus({ cls, status: "inactive" })}>
            Inactivar
          </button>
        ) : (
          <button className="btn btn-success btn-sm" onClick={() => setConfirmStatus({ cls, status: "active" })}>
            Activar
          </button>
        )}
      </div>
    );
  };

  return (
    <>
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px" }}>
        <div>
          <h1>Clases</h1>
          <p>Gestión operativa de clases.</p>
        </div>
      </div>

      <div style={{ display: "flex", gap: "6px", flexWrap: "wrap", marginBottom: "16px" }}>
        {FILTERS.map((f) => (
          <button
            key={f.key}
            className={`btn btn-sm ${activeFilter === f.key ? "btn-primary" : "btn-secondary"}`}
            onClick={() => setActiveFilter(f.key)}
          >
            {f.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="card" style={{ textAlign: "center", padding: "40px", color: "var(--color-text-muted)" }}>
          Cargando clases…
        </div>
      ) : classes.length === 0 ? (
        <div className="card" style={{ textAlign: "center", padding: "40px", color: "var(--color-text-muted)" }}>
          No hay clases en esta vista.
        </div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Hora</th>
                <th>Curso</th>
                <th>Clase</th>
                <th>Docente</th>
                <th>Días</th>
                <th>Cupo</th>
                <th>Estado</th>
                <th>Enlace</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {classes.map((cls) => (
                <tr key={cls.id}>
                  <td style={{ fontSize: "0.875rem", whiteSpace: "nowrap" }}>
                    {cls.start_time ?? "—"} {cls.end_time ? `– ${cls.end_time}` : ""}
                  </td>
                  <td style={{ fontSize: "0.875rem" }}>{cls.course_title ?? "—"}</td>
                  <td style={{ fontWeight: 500 }}>{cls.name}</td>
                  <td style={{ fontSize: "0.875rem" }}>{cls.teacher_name ?? "Sin asignar"}</td>
                  <td style={{ fontSize: "0.8rem" }}>
                    {cls.days_of_week.map((d) => WEEKDAY_LABELS[d] ?? d).join(", ")}
                  </td>
                  <td style={{ fontSize: "0.875rem" }}>
                    {cls.enrolled_count} / {cls.global_max}
                    {cls.available_slots > 0 && <span style={{ color: "#22c55e", marginLeft: "4px" }}>({cls.available_slots})</span>}
                  </td>
                  <td>
                    <span className={`badge ${STATUS_BADGE[cls.status] ?? "badge-neutral"}`}>
                      {STATUS_LABELS[cls.status] ?? cls.status}
                    </span>
                  </td>
                  <td>
                    {!cls.meeting_url ? (
                      <span style={{ color: "#ef4444", fontSize: "0.8rem" }}>⚠ Falta link</span>
                    ) : (
                      <span style={{ color: "#22c55e", fontSize: "0.8rem" }}>✓ Link asignado</span>
                    )}
                  </td>
                  <td>{renderActions(cls)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Modal open={!!meetingModal} onClose={() => setMeetingModal(null)} title="Enlace de clase" width="480px">
        {meetingModal && (
          <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <div>
              <label className="label">Plataforma</label>
              <input className="input" value={meetingPlatform} onChange={(e) => setMeetingPlatform(e.target.value)} placeholder="Zoom, Google Meet, etc." />
            </div>
            <div>
              <label className="label">URL de la reunión</label>
              <input className="input" type="url" value={meetingUrl} onChange={(e) => setMeetingUrl(e.target.value)} placeholder="https://..." />
            </div>
            <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px" }}>
              <button className="btn btn-secondary" onClick={() => setMeetingModal(null)} disabled={saving}>Cancelar</button>
              <button className="btn btn-primary" onClick={saveMeeting} disabled={saving}>{saving ? "Guardando…" : "Guardar"}</button>
            </div>
          </div>
        )}
      </Modal>

      <Modal open={!!confirmStatus} onClose={() => setConfirmStatus(null)} title="Cambiar estado" width="420px">
        {confirmStatus && (
          <div style={{ textAlign: "center" }}>
            <p style={{ marginBottom: "16px" }}>
              ¿Cambiar estado de <strong>"{confirmStatus.cls.name}"</strong> a <strong>{STATUS_LABELS[confirmStatus.status]}</strong>?
            </p>
            <div style={{ display: "flex", gap: "12px", justifyContent: "center" }}>
              <button className="btn btn-secondary" onClick={() => setConfirmStatus(null)}>Cancelar</button>
              <button className="btn btn-primary" onClick={handleStatusChange} disabled={saving}>
                {saving ? "Guardando…" : "Confirmar"}
              </button>
            </div>
          </div>
        )}
      </Modal>
    </>
  );
}
