"use client";

import { useState } from "react";
import Modal from "@/components/ui/Modal";
import {
  ClassFilter,
  CourseClassItem,
  TeacherOption,
  useAdminCourses,
  useAdminTeachers,
  useClasses,
  useCreateClass,
} from "@/hooks/useAdminData";
import { api } from "@/lib/api";
import { toast } from "@/components/ui/Toast";

const WEEKDAY_LABELS: Record<string, string> = {
  mon: "Lun", tue: "Mar", wed: "Mié", thu: "Jue", fri: "Vie", sat: "Sáb", sun: "Dom",
};

const WEEKDAYS = [
  { value: "mon", label: "Lunes" },
  { value: "tue", label: "Martes" },
  { value: "wed", label: "Miércoles" },
  { value: "thu", label: "Jueves" },
  { value: "fri", label: "Viernes" },
  { value: "sat", label: "Sábado" },
  { value: "sun", label: "Domingo" },
];

const PLATFORMS = ["Zoom", "Google Meet", "Microsoft Teams", "Jitsi", "Otra"];

const STATUS_LABELS: Record<string, string> = {
  active: "Activa", inactive: "Inactiva", cancelled: "Cancelada", deleted: "Eliminada",
};

const STATUS_BADGE: Record<string, string> = {
  active: "badge-success", inactive: "badge-warning", cancelled: "badge-error", deleted: "badge-neutral",
};

const FILTERS: { key: ClassFilter; label: string }[] = [
  { key: "today", label: "Clases de hoy" },
  { key: "all", label: "Todas" },
  { key: "without_teacher", label: "Sin docente" },
  { key: "available_slots", label: "Cupos disponibles" },
  { key: "missing_link", label: "Sin enlace" },
  { key: "inactive", label: "Inactivas" },
  { key: "cancelled", label: "Canceladas" },
  { key: "deleted", label: "Eliminadas" },
];

export default function AdminClassesPage() {
  const [activeFilter, setActiveFilter] = useState<ClassFilter>("today");
  const { data: classes, loading, refresh, updateStatus, deleteClass, updateMeetingLink, updateRecordingLink } = useClasses(activeFilter);

  // Alta de clases desde este mismo menú (sólo administración/coordinación).
  const { data: coursesPage } = useAdminCourses();
  const { data: teachers } = useAdminTeachers();
  const { createClassInCourse, saving: creating } = useCreateClass();

  const [showCreate, setShowCreate] = useState(false);
  const [createForm, setCreateForm] = useState({
    course_id: "",
    teacher_id: "",
    name: "",
    days_of_week: [] as string[],
    start_time: "",
    end_time: "",
    meeting_platform: "",
    meeting_url: "",
  });
  const courseOptions = coursesPage?.items ?? [];

  const toggleDay = (day: string) => {
    setCreateForm((f) => ({
      ...f,
      days_of_week: f.days_of_week.includes(day)
        ? f.days_of_week.filter((d) => d !== day)
        : [...f.days_of_week, day],
    }));
  };

  const openCreate = () => {
    setCreateForm({
      course_id: "",
      teacher_id: "",
      name: "",
      days_of_week: [],
      start_time: "",
      end_time: "",
      meeting_platform: "",
      meeting_url: "",
    });
    setShowCreate(true);
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!createForm.course_id) {
      toast.error("Elige el curso de la clase");
      return;
    }
    if (createForm.days_of_week.length === 0) {
      toast.error("Marca al menos un día de la semana");
      return;
    }
    if (!createForm.start_time || !createForm.end_time) {
      toast.error("Indica la hora de inicio y de fin");
      return;
    }
    try {
      await createClassInCourse(
        createForm.course_id,
        {
          name: createForm.name,
          days_of_week: createForm.days_of_week,
          start_time: createForm.start_time,
          end_time: createForm.end_time,
          meeting_platform: createForm.meeting_platform || null,
          meeting_url: createForm.meeting_url || null,
        },
        createForm.teacher_id || undefined
      );
      setShowCreate(false);
      refresh();
    } catch {
      toast.error("No se pudo crear la clase");
    }
  };

  const [meetingModal, setMeetingModal] = useState<CourseClassItem | null>(null);
  const [meetingPlatform, setMeetingPlatform] = useState("");
  const [meetingUrl, setMeetingUrl] = useState("");
  const [recordingPlatform, setRecordingPlatform] = useState("");
  const [recordingUrl, setRecordingUrl] = useState("");
  const [saving, setSaving] = useState(false);

  const [confirmDelete, setConfirmDelete] = useState<CourseClassItem | null>(null);
  const [confirmStatus, setConfirmStatus] = useState<{ cls: CourseClassItem; status: string } | null>(null);

  const openMeeting = (cls: CourseClassItem) => {
    setMeetingModal(cls);
    setMeetingPlatform(cls.meeting_platform || "");
    setMeetingUrl(cls.meeting_url || "");
    setRecordingPlatform(cls.recording_platform || "");
    setRecordingUrl(cls.recording_url || "");
  };

  const saveMeeting = async () => {
    if (!meetingModal) return;
    setSaving(true);
    try {
      await updateMeetingLink(meetingModal.id, meetingPlatform, meetingUrl);
      await updateRecordingLink(meetingModal.id, recordingPlatform, recordingUrl);
      setMeetingModal(null);
    } catch {
      toast.error("Error al guardar");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!confirmDelete) return;
    setSaving(true);
    try {
      await deleteClass(confirmDelete.id);
      setConfirmDelete(null);
    } catch {
      toast.error("Error al eliminar clase");
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
    const isDeleted = cls.status === "deleted";
    return (
      <div style={{ display: "flex", gap: "4px", flexWrap: "wrap" }}>
        <button className="btn btn-secondary btn-sm" onClick={() => openMeeting(cls)}>
          {cls.meeting_url ? "Editar enlace" : "Asignar enlace"}
        </button>
        {!isDeleted && (
          <>
            {cls.status === "active" ? (
              <button className="btn btn-warning btn-sm" onClick={() => setConfirmStatus({ cls, status: "inactive" })}>
                Inactivar
              </button>
            ) : (
              <button className="btn btn-success btn-sm" onClick={() => setConfirmStatus({ cls, status: "active" })}>
                Activar
              </button>
            )}
            <button className="btn btn-error btn-sm" onClick={() => setConfirmDelete(cls)}>
              Eliminar
            </button>
          </>
        )}
      </div>
    );
  };

  return (
    <>
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px" }}>
        <div>
          <h1>Clases</h1>
          <p>Gestión de todas las clases del sistema.</p>
        </div>
        <button className="btn btn-primary" onClick={openCreate}>+ Nueva clase</button>
      </div>

      {/* Filters */}
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

      {/* Create Class Modal */}
      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="Nueva clase" width="620px">
        <form onSubmit={handleCreate} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <div>
            <label className="label">Curso *</label>
            <select
              className="input"
              required
              value={createForm.course_id}
              onChange={(e) => setCreateForm((f) => ({ ...f, course_id: e.target.value }))}
            >
              <option value="">— Elige el curso —</option>
              {courseOptions.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.title}
                  {c.is_active ? "" : " (inactivo)"}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">Docente (opcional)</label>
            <select
              className="input"
              value={createForm.teacher_id}
              onChange={(e) => setCreateForm((f) => ({ ...f, teacher_id: e.target.value }))}
            >
              <option value="">— Sin asignar por ahora —</option>
              {teachers.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.first_name} {t.last_name} ({t.email})
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">Nombre de la clase *</label>
            <input
              className="input"
              required
              value={createForm.name}
              onChange={(e) => setCreateForm((f) => ({ ...f, name: e.target.value }))}
              placeholder="Grupo A — mañanas"
            />
          </div>
          <div>
            <label className="label">Días de la semana *</label>
            <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
              {WEEKDAYS.map((d) => (
                <button
                  type="button"
                  key={d.value}
                  className={`btn btn-sm ${createForm.days_of_week.includes(d.value) ? "btn-primary" : "btn-secondary"}`}
                  onClick={() => toggleDay(d.value)}
                >
                  {d.label}
                </button>
              ))}
            </div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "12px" }}>
            <div>
              <label className="label">Hora de inicio *</label>
              <input
                className="input"
                required
                type="time"
                value={createForm.start_time}
                onChange={(e) => setCreateForm((f) => ({ ...f, start_time: e.target.value }))}
              />
            </div>
            <div>
              <label className="label">Hora de fin *</label>
              <input
                className="input"
                required
                type="time"
                value={createForm.end_time}
                onChange={(e) => setCreateForm((f) => ({ ...f, end_time: e.target.value }))}
              />
            </div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
            <div>
              <label className="label">Plataforma</label>
              <select
                className="input"
                value={createForm.meeting_platform}
                onChange={(e) => setCreateForm((f) => ({ ...f, meeting_platform: e.target.value }))}
              >
                <option value="">— Sin enlace todavía —</option>
                {PLATFORMS.map((p) => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="label">URL de la clase</label>
              <input
                className="input"
                type="url"
                value={createForm.meeting_url}
                onChange={(e) => setCreateForm((f) => ({ ...f, meeting_url: e.target.value }))}
                placeholder="https://…"
              />
            </div>
          </div>
          <p style={{ fontSize: "0.8125rem", color: "var(--color-text-muted)" }}>
            El enlace de la clase y la grabación los puede publicar después el docente desde
            «Mis clases»; administración también puede editarlos aquí.
          </p>
          <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px" }}>
            <button type="button" className="btn btn-secondary" onClick={() => setShowCreate(false)} disabled={creating}>
              Cancelar
            </button>
            <button type="submit" className="btn btn-primary" disabled={creating}>
              {creating ? "Creando…" : "Crear clase"}
            </button>
          </div>
        </form>
      </Modal>

      {/* Meeting Link Modal */}
      <Modal open={!!meetingModal} onClose={() => setMeetingModal(null)} title="Enlaces de la clase" width="480px">
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
            <div style={{ borderTop: "1px solid var(--color-border)", paddingTop: "16px", display: "flex", flexDirection: "column", gap: "12px" }}>
              <p style={{ fontSize: "0.8125rem", color: "var(--color-text-muted)" }}>
                Grabación de la clase (también la puede publicar el docente titular). Vacío = retirarla.
              </p>
              <div>
                <label className="label">Plataforma de la grabación</label>
                <input className="input" value={recordingPlatform} onChange={(e) => setRecordingPlatform(e.target.value)} placeholder="Google Drive, YouTube…" />
              </div>
              <div>
                <label className="label">URL de la grabación</label>
                <input className="input" type="url" value={recordingUrl} onChange={(e) => setRecordingUrl(e.target.value)} placeholder="https://..." />
              </div>
            </div>
            <div style={{ display: "flex", justifyContent: "flex-end", gap: "10px" }}>
              <button className="btn btn-secondary" onClick={() => setMeetingModal(null)} disabled={saving}>Cancelar</button>
              <button className="btn btn-primary" onClick={saveMeeting} disabled={saving}>{saving ? "Guardando…" : "Guardar"}</button>
            </div>
          </div>
        )}
      </Modal>

      {/* Confirm Delete */}
      <Modal open={!!confirmDelete} onClose={() => setConfirmDelete(null)} title="Confirmar eliminación" width="420px">
        {confirmDelete && (
          <div style={{ textAlign: "center" }}>
            <p style={{ marginBottom: "16px" }}>¿Eliminar la clase <strong>"{confirmDelete.name}"</strong>?</p>
            <p style={{ fontSize: "0.875rem", color: "var(--color-text-muted)", marginBottom: "24px" }}>
              Se marcará como eliminada. Los alumnos, asistencias y pagos relacionados se conservan.
            </p>
            <div style={{ display: "flex", gap: "12px", justifyContent: "center" }}>
              <button className="btn btn-secondary" onClick={() => setConfirmDelete(null)}>Cancelar</button>
              <button className="btn btn-danger" onClick={handleDelete} disabled={saving}>
                {saving ? "Eliminando…" : "Sí, eliminar"}
              </button>
            </div>
          </div>
        )}
      </Modal>

      {/* Confirm Status */}
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
