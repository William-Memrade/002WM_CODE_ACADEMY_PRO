"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Modal from "@/components/ui/Modal";
import { useAdminCourseClasses, CourseClassItem } from "@/hooks/useAdminData";
import { api } from "@/lib/api";
import { toast } from "@/components/ui/Toast";

interface TeacherOption {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
}

interface CourseDetail {
  id: string;
  title: string;
  slug: string;
}

interface ClassFormState {
  name: string;
  days_of_week: string[];
  start_time: string;
  end_time: string;
  status?: string;
}

const WEEKDAY_OPTIONS = [
  { value: "mon", label: "Lun" },
  { value: "tue", label: "Mar" },
  { value: "wed", label: "Mié" },
  { value: "thu", label: "Jue" },
  { value: "fri", label: "Vie" },
  { value: "sat", label: "Sáb" },
  { value: "sun", label: "Dom" },
];

export default function CourseClassesPage() {
  const params = useParams();
  const courseId = params.id as string;
  const { data: classes, loading, refresh, createClass, updateClass, assignTeacher, getCapacity } = useAdminCourseClasses(courseId);
  const [course, setCourse] = useState<CourseDetail | null>(null);
  const [courseLoading, setCourseLoading] = useState(true);
  const [teachers, setTeachers] = useState<TeacherOption[]>([]);

  const [showCreate, setShowCreate] = useState(false);
  const [editing, setEditing] = useState<CourseClassItem | null>(null);
  const [assigning, setAssigning] = useState<CourseClassItem | null>(null);
  const [viewingCapacity, setViewingCapacity] = useState<CourseClassItem | null>(null);
  const [capacity, setCapacity] = useState<{ enrolled_count: number; global_max: number; available_slots: number } | null>(null);
  const [saving, setSaving] = useState(false);

  const [createForm, setCreateForm] = useState<ClassFormState>({
    name: "",
    days_of_week: [],
    start_time: "",
    end_time: "",
  });

  const [editForm, setEditForm] = useState<ClassFormState>({
    name: "",
    days_of_week: [],
    start_time: "",
    end_time: "",
    status: "active",
  });

  const [selectedTeacherId, setSelectedTeacherId] = useState("");

  useEffect(() => {
    api.get<CourseDetail>(`/courses/${courseId}`)
      .then(setCourse)
      .catch(() => toast.error("Error al cargar curso"))
      .finally(() => setCourseLoading(false));
  }, [courseId]);

  useEffect(() => {
    api.get<{ items: TeacherOption[] }>("/teachers/")
      .then((res) => setTeachers(res.items ?? []))
      .catch(() => toast.error("Error al cargar docentes"));
  }, []);

  const openCreate = () => {
    setCreateForm({ name: "", days_of_week: [], start_time: "", end_time: "" });
    setShowCreate(true);
  };

  const openEdit = (cls: CourseClassItem) => {
    setEditForm({
      name: cls.name,
      days_of_week: cls.days_of_week ?? [],
      start_time: cls.start_time ?? "",
      end_time: cls.end_time ?? "",
      status: cls.status,
    });
    setEditing(cls);
  };

  const openAssign = (cls: CourseClassItem) => {
    setAssigning(cls);
    setSelectedTeacherId(cls.teacher_id ?? "");
  };

  const openCapacity = async (cls: CourseClassItem) => {
    setViewingCapacity(cls);
    try {
      const res = await getCapacity(cls.id);
      setCapacity(res);
    } catch {
      toast.error("Error al cargar cupo");
      setCapacity(null);
    }
  };

  const toggleDay = (day: string, form: "create" | "edit") => {
    const setter = form === "create" ? setCreateForm : setEditForm;
    setter((f) => {
      const has = f.days_of_week.includes(day);
      const next = has ? f.days_of_week.filter((d) => d !== day) : [...f.days_of_week, day];
      return { ...f, days_of_week: next };
    });
  };

  const validateTimeRange = (start: string, end: string) => {
    if (start && end) {
      if (start >= end) {
        toast.error("La hora de fin debe ser posterior a la hora de inicio");
        return false;
      }
    }
    return true;
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateTimeRange(createForm.start_time, createForm.end_time)) return;
    setSaving(true);
    try {
      await createClass({
        name: createForm.name,
        days_of_week: createForm.days_of_week,
        start_time: createForm.start_time || null,
        end_time: createForm.end_time || null,
      });
      setShowCreate(false);
    } catch {
      toast.error("Error al crear la clase");
    } finally {
      setSaving(false);
    }
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editing) return;
    if (!validateTimeRange(editForm.start_time, editForm.end_time)) return;
    setSaving(true);
    try {
      const payload: any = {
        name: editForm.name,
        days_of_week: editForm.days_of_week,
        start_time: editForm.start_time || null,
        end_time: editForm.end_time || null,
        status: editForm.status,
      };
      await updateClass(editing.id, payload);
      setEditing(null);
    } catch {
      toast.error("Error al actualizar la clase");
    } finally {
      setSaving(false);
    }
  };

  const handleAssign = async () => {
    if (!assigning || !selectedTeacherId) return;
    setSaving(true);
    try {
      await assignTeacher(assigning.id, selectedTeacherId);
      setAssigning(null);
    } catch {
      toast.error("Error al asignar docente");
    } finally {
      setSaving(false);
    }
  };

  const statusBadge = (status: string) => {
    const cls =
      status === "active" ? "badge-success" :
      status === "inactive" ? "badge-warning" :
      status === "cancelled" ? "badge-error" :
      status === "deleted" ? "badge-neutral" : "badge-neutral";
    const label =
      status === "active" ? "Activa" :
      status === "inactive" ? "Inactiva" :
      status === "cancelled" ? "Cancelada" :
      status === "deleted" ? "Eliminada" : status;
    return <span className={`badge ${cls}`}>{label}</span>;
  };

  return (
    <>
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h1>Clases — {course?.title ?? "Curso"}</h1>
          <p>Gestión de clases para este curso ({classes.length ?? "…"} clases).</p>
        </div>
        <button className="btn btn-primary" onClick={openCreate}>+ Crear clase</button>
      </div>

      {loading || courseLoading ? (
        <div className="card" style={{ textAlign: "center", padding: "40px", color: "var(--color-text-muted)" }}>Cargando…</div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Nombre</th><th>Horario</th><th>Estado</th><th>Cupo</th><th>Docente</th><th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {classes.length === 0 && (
                <tr><td colSpan={6} style={{ textAlign: "center", color: "var(--color-text-muted)", padding: "32px" }}>No hay clases registradas.</td></tr>
              )}
              {classes.map((cls) => (
                <tr key={cls.id}>
                  <td style={{ fontWeight: 500, maxWidth: "220px" }}>{cls.name}</td>
                  <td style={{ fontSize: "0.875rem" }}>{cls.schedule_info ?? "—"}</td>
                  <td>{statusBadge(cls.status)}</td>
                  <td style={{ fontSize: "0.875rem" }}>
                    {cls.enrolled_count} / {cls.global_max}
                  </td>
                  <td style={{ fontSize: "0.875rem" }}>
                    {teachers.find(t => t.id === cls.teacher_id)
                      ? `${teachers.find(t => t.id === cls.teacher_id)!.first_name} ${teachers.find(t => t.id === cls.teacher_id)!.last_name}`
                      : "Sin asignar"}
                  </td>
                  <td style={{ display: "flex", gap: "4px", flexWrap: "wrap" }}>
                    <button className="btn btn-secondary btn-sm" onClick={() => openEdit(cls)}>Editar</button>
                    <button className="btn btn-secondary btn-sm" onClick={() => openAssign(cls)}>Asignar docente</button>
                    <button className="btn btn-secondary btn-sm" onClick={() => openCapacity(cls)}>Ver cupo</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Create Modal */}
      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="Crear nueva clase" width="640px">
        <form onSubmit={handleCreate} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <div>
            <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>Nombre *</label>
            <input className="input" required value={createForm.name} onChange={e => setCreateForm(f => ({ ...f, name: e.target.value }))} placeholder="Ej: Grupo A - Lunes y Miércoles" />
          </div>
          <div>
            <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>Días de la semana</label>
            <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
              {WEEKDAY_OPTIONS.map((d) => (
                <button
                  key={d.value}
                  type="button"
                  className={`btn btn-sm ${createForm.days_of_week.includes(d.value) ? "btn-primary" : "btn-secondary"}`}
                  onClick={() => toggleDay(d.value, "create")}
                >
                  {d.label}
                </button>
              ))}
            </div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
            <div>
              <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>Hora inicio</label>
              <input className="input" type="time" value={createForm.start_time} onChange={e => setCreateForm(f => ({ ...f, start_time: e.target.value }))} />
            </div>
            <div>
              <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>Hora fin</label>
              <input className="input" type="time" value={createForm.end_time} onChange={e => setCreateForm(f => ({ ...f, end_time: e.target.value }))} />
            </div>
          </div>
          <div style={{ display: "flex", gap: "12px", justifyContent: "flex-end", marginTop: "8px" }}>
            <button type="button" className="btn btn-secondary" onClick={() => setShowCreate(false)}>Cancelar</button>
            <button type="submit" className="btn btn-primary" disabled={saving}>{saving ? "Creando…" : "Crear clase"}</button>
          </div>
        </form>
      </Modal>

      {/* Edit Modal */}
      <Modal open={!!editing} onClose={() => setEditing(null)} title="Editar clase" width="640px">
        {editing && (
          <form onSubmit={handleUpdate} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <div>
              <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>Nombre</label>
              <input className="input" required value={editForm.name} onChange={e => setEditForm(f => ({ ...f, name: e.target.value }))} />
            </div>
            <div>
              <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>Días de la semana</label>
              <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
                {WEEKDAY_OPTIONS.map((d) => (
                  <button
                    key={d.value}
                    type="button"
                    className={`btn btn-sm ${editForm.days_of_week.includes(d.value) ? "btn-primary" : "btn-secondary"}`}
                    onClick={() => toggleDay(d.value, "edit")}
                  >
                    {d.label}
                  </button>
                ))}
              </div>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
              <div>
                <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>Hora inicio</label>
                <input className="input" type="time" value={editForm.start_time} onChange={e => setEditForm(f => ({ ...f, start_time: e.target.value }))} />
              </div>
              <div>
                <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>Hora fin</label>
                <input className="input" type="time" value={editForm.end_time} onChange={e => setEditForm(f => ({ ...f, end_time: e.target.value }))} />
              </div>
            </div>
            <div>
              <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>Estado</label>
              <select className="input" value={editForm.status} onChange={e => setEditForm(f => ({ ...f, status: e.target.value }))}>
                <option value="active">Activa</option>
                <option value="inactive">Inactiva</option>
                <option value="cancelled">Cancelada</option>
              </select>
            </div>
            <div style={{ display: "flex", gap: "12px", justifyContent: "flex-end", marginTop: "8px" }}>
              <button type="button" className="btn btn-secondary" onClick={() => setEditing(null)}>Cancelar</button>
              <button type="submit" className="btn btn-primary" disabled={saving}>{saving ? "Guardando…" : "Guardar cambios"}</button>
            </div>
          </form>
        )}
      </Modal>

      {/* Assign Teacher Modal */}
      <Modal open={!!assigning} onClose={() => setAssigning(null)} title="Asignar docente" width="500px">
        {assigning && (
          <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <div>
              <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>Docente</label>
              <select
                className="input"
                value={selectedTeacherId}
                onChange={e => setSelectedTeacherId(e.target.value)}
                required
              >
                <option value="">— Seleccionar docente —</option>
                {teachers.map(t => (
                  <option key={t.id} value={t.id}>{t.first_name} {t.last_name} ({t.email})</option>
                ))}
              </select>
              {teachers.length === 0 && (
                <p style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", marginTop: "4px" }}>
                  No hay docentes disponibles.
                </p>
              )}
            </div>
            <div style={{ display: "flex", gap: "12px", justifyContent: "flex-end" }}>
              <button className="btn btn-secondary" onClick={() => setAssigning(null)}>Cancelar</button>
              <button
                className="btn btn-primary"
                onClick={handleAssign}
                disabled={saving || !selectedTeacherId}
              >
                {saving ? "Asignando…" : "Confirmar asignación"}
              </button>
            </div>
          </div>
        )}
      </Modal>

      {/* Capacity Modal */}
      <Modal open={!!viewingCapacity} onClose={() => { setViewingCapacity(null); setCapacity(null); }} title="Cupo de clase" width="420px">
        {viewingCapacity && (
          <div style={{ textAlign: "center" }}>
            <p style={{ fontWeight: 500, marginBottom: "16px" }}>{viewingCapacity.name}</p>
            {capacity ? (
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "12px", marginBottom: "24px" }}>
                <div className="card" style={{ padding: "16px" }}>
                  <div style={{ fontSize: "1.25rem", fontWeight: 700 }}>{capacity.enrolled_count}</div>
                  <div style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", marginTop: "4px" }}>Inscritos</div>
                </div>
                <div className="card" style={{ padding: "16px" }}>
                  <div style={{ fontSize: "1.25rem", fontWeight: 700 }}>{capacity.global_max}</div>
                  <div style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", marginTop: "4px" }}>Cupo total</div>
                </div>
                <div className="card" style={{ padding: "16px" }}>
                  <div style={{ fontSize: "1.25rem", fontWeight: 700, color: capacity.available_slots <= 0 ? "var(--color-error)" : "var(--color-success)" }}>
                    {capacity.available_slots}
                  </div>
                  <div style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", marginTop: "4px" }}>Disponibles</div>
                </div>
              </div>
            ) : (
              <p style={{ color: "var(--color-text-muted)" }}>Cargando…</p>
            )}
            <button className="btn btn-secondary" onClick={() => { setViewingCapacity(null); setCapacity(null); }}>Cerrar</button>
          </div>
        )}
      </Modal>
    </>
  );
}
