"use client";

import { useState } from "react";
import Modal from "@/components/ui/Modal";
import { useTeacherClasses, CourseClassItem } from "@/hooks/useAdminData";
import { toast } from "@/components/ui/Toast";

const WEEKDAY_LABELS: Record<string, string> = {
  mon: "Lun", tue: "Mar", wed: "Mié", thu: "Jue", fri: "Vie", sat: "Sáb", sun: "Dom",
};

const EN_TO_CODE: Record<string, string> = {
  monday: "mon",
  tuesday: "tue",
  wednesday: "wed",
  thursday: "thu",
  friday: "fri",
  saturday: "sat",
  sunday: "sun",
};

export default function TeacherClassesPage() {
  const { data: classes, loading, refresh, updateMeetingLink } = useTeacherClasses();

  const [meetingModal, setMeetingModal] = useState<CourseClassItem | null>(null);
  const [meetingPlatform, setMeetingPlatform] = useState("");
  const [meetingUrl, setMeetingUrl] = useState("");
  const [saving, setSaving] = useState(false);

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

  const today = new Date().toLocaleDateString("es-MX", { weekday: "long", day: "numeric", month: "long" });

  return (
    <>
      <div className="page-header">
        <div>
          <h1>Mis Clases</h1>
          <p>Clases asignadas a ti. Hoy es {today}.</p>
        </div>
      </div>

      {loading ? (
        <div className="card" style={{ textAlign: "center", padding: "40px", color: "var(--color-text-muted)" }}>
          Cargando clases…
        </div>
      ) : classes.length === 0 ? (
        <div className="card" style={{ textAlign: "center", padding: "48px" }}>
          <div style={{ fontSize: "3rem", marginBottom: "16px" }}>🏫</div>
          <h3 style={{ fontWeight: 600, marginBottom: "8px" }}>Sin clases asignadas</h3>
          <p style={{ color: "var(--color-text-muted)" }}>No tienes clases asignadas actualmente.</p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          {classes.map((cls) => {
            const todayCode = EN_TO_CODE[new Date().toLocaleDateString("en-US", { weekday: "long" }).toLowerCase()];
            const isToday = todayCode ? cls.days_of_week.includes(todayCode) : false;
            return (
              <div key={cls.id} className="card" style={{ position: "relative" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "12px" }}>
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
                      <h3 style={{ fontWeight: 600, fontSize: "1.1rem" }}>{cls.name}</h3>
                      <span className={`badge ${cls.status === "active" ? "badge-success" : "badge-warning"}`}>
                        {cls.status === "active" ? "Activa" : cls.status}
                      </span>
                      {isToday && <span className="badge badge-info">Hoy</span>}
                    </div>
                    <p style={{ color: "var(--color-text-muted)", fontSize: "0.875rem", marginBottom: "8px" }}>
                      {cls.course_title ?? "—"}
                    </p>
                    <div style={{ display: "flex", gap: "12px", flexWrap: "wrap", fontSize: "0.875rem" }}>
                      <span><strong>Horario:</strong> {cls.schedule_info ?? "—"}</span>
                      <span><strong>Días:</strong> {cls.days_of_week.map((d) => WEEKDAY_LABELS[d] ?? d).join(", ")}</span>
                      <span><strong>Alumnos:</strong> {cls.enrolled_count} / {cls.global_max}</span>
                    </div>
                  </div>
                  <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                    {!cls.meeting_url && (
                      <span style={{ color: "#ef4444", fontSize: "0.8rem", display: "flex", alignItems: "center" }}>
                        ⚠ Falta link de clase
                      </span>
                    )}
                    <button className="btn btn-primary btn-sm" onClick={() => openMeeting(cls)}>
                      {cls.meeting_url ? "Editar enlace" : "Asignar enlace"}
                    </button>
                    <a href={`/teacher/classes/${cls.id}/attendance`} className="btn btn-secondary btn-sm">
                      Asistencia
                    </a>
                  </div>
                </div>
                {cls.meeting_url && (
                  <div style={{ marginTop: "12px", paddingTop: "12px", borderTop: "1px solid var(--color-border)", fontSize: "0.875rem" }}>
                    <span style={{ color: "var(--color-text-muted)" }}>Enlace: </span>
                    <a href={cls.meeting_url} target="_blank" rel="noopener noreferrer" style={{ color: "var(--color-primary)" }}>
                      {cls.meeting_url}
                    </a>
                  </div>
                )}
              </div>
            );
          })}
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
    </>
  );
}
