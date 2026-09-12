"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Modal from "@/components/ui/Modal";
import { useAdminCourses, useAdminCategories, useAdminTeachers, teacherLabel, AdminCourse } from "@/hooks/useAdminData";
import { toast } from "@/components/ui/Toast";
import { formatCurrency } from "@/lib/currency";
import { usePlatformSettings } from "@/hooks/usePlatformSettings";

const LEVELS = [
  { value: "beginner", label: "Principiante" },
  { value: "intermediate", label: "Intermedio" },
  { value: "advanced", label: "Avanzado" },
];

function computedMonthly(priceStr: string, monthsStr: string): number | null {
  const price = parseFloat(priceStr);
  const months = parseInt(monthsStr);
  if (!isNaN(price) && !isNaN(months) && months > 0) {
    return price / months;
  }
  return null;
}

function computedFullPayment(priceStr: string, discountStr: string): number | null {
  const price = parseFloat(priceStr);
  const discount = parseFloat(discountStr);
  if (!isNaN(price) && !isNaN(discount)) {
    return price * (1 - discount / 100);
  }
  return null;
}

export default function AdminCoursesPage() {
  const router = useRouter();
  const { data, loading, createCourse, updateCourse, toggleActive, deleteCourse } = useAdminCourses();
  const { data: categoriesData } = useAdminCategories();
  const { data: teachers } = useAdminTeachers();

  const [showCreate, setShowCreate] = useState(false);
  const [editing, setEditing] = useState<AdminCourse | null>(null);
  const [confirmDelete, setConfirmDelete] = useState<AdminCourse | null>(null);
  const [saving, setSaving] = useState(false);

  const [form, setForm] = useState({
    title: "",
    description: "",
    short_description: "",
    price: "",
    level: "beginner",
    duration_hours: "",
    duration_months: "",
    full_payment_discount_pct: "",
    category_id: "",
    is_featured: false,
    teacher_id: "",
  });

  const openCreate = () => {
    setForm({
      title: "",
      description: "",
      short_description: "",
      price: "",
      level: "beginner",
      duration_hours: "",
      duration_months: "",
      full_payment_discount_pct: "",
      category_id: "",
      is_featured: false,
      teacher_id: "",
    });
    setShowCreate(true);
  };

  const openEdit = (c: AdminCourse) => {
    setForm({
      title: c.title,
      description: c.description ?? "",
      short_description: c.short_description ?? "",
      price: String(c.price),
      level: c.level,
      duration_hours: String(c.duration_hours ?? ""),
      duration_months: String(c.duration_months ?? ""),
      full_payment_discount_pct: String(c.full_payment_discount_pct ?? ""),
      category_id: c.category?.id ?? "",
      is_featured: c.is_featured ?? false,
      teacher_id: c.teacher?.id ?? "",
    });
    setEditing(c);
  };

  const buildPayloadFromForm = (forCreate: boolean) => {
    const payload: any = {
      title: form.title,
      price: form.price || undefined,
      level: form.level,
      duration_hours: form.duration_hours ? parseInt(form.duration_hours) : null,
      duration_months: form.duration_months ? parseInt(form.duration_months) : null,
      full_payment_discount_pct: form.full_payment_discount_pct ? parseFloat(form.full_payment_discount_pct) : 0,
      category_id: form.category_id || null,
      is_featured: form.is_featured,
      // `teacher_id` es el id del PERFIL docente (teachers.id), no el de usuario.
      // Cadena vacía = quitar la asignación.
      teacher_id: form.teacher_id || null,
    };

    if (forCreate) {
      payload.description = form.description;
      payload.short_description = form.short_description || null;
    } else {
      if (form.description) payload.description = form.description;
      if (form.short_description !== "") payload.short_description = form.short_description || null;
      if (form.duration_months !== "") payload.duration_months = form.duration_months ? parseInt(form.duration_months) : null;
      if (form.full_payment_discount_pct !== "") payload.full_payment_discount_pct = parseFloat(form.full_payment_discount_pct);
    }

    return payload;
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await createCourse(buildPayloadFromForm(true));
      setShowCreate(false);
    } catch (err: any) {
      toast.error("Error al crear el curso");
    } finally {
      setSaving(false);
    }
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editing) return;
    setSaving(true);
    try {
      await updateCourse(editing.id, buildPayloadFromForm(false));
      setEditing(null);
    } catch {
      toast.error("Error al actualizar el curso");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!confirmDelete) return;
    setSaving(true);
    try {
      await deleteCourse(confirmDelete.id);
      setConfirmDelete(null);
    } catch {
      toast.error("Error al eliminar el curso");
    } finally {
      setSaving(false);
    }
  };

  const courses = data?.items ?? [];
  const { settings } = usePlatformSettings();

  const monthlyPrice = computedMonthly(form.price, form.duration_months);
  const fullPaymentPrice = computedFullPayment(form.price, form.full_payment_discount_pct);

  return (
    <>
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div><h1>Cursos</h1><p>Gestión de cursos de la plataforma ({data?.total ?? "…"} total).</p></div>
        <button className="btn btn-primary" onClick={openCreate}>+ Crear curso</button>
      </div>

      {loading ? (
        <div className="card" style={{ textAlign: "center", padding: "40px", color: "var(--color-text-muted)" }}>Cargando cursos…</div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Curso</th><th>Categoría</th><th>Docente</th>
                <th>Precio total</th><th>Nivel</th><th>Estado</th><th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {courses.length === 0 && (
                <tr><td colSpan={7} style={{ textAlign: "center", color: "var(--color-text-muted)", padding: "32px" }}>No hay cursos registrados.</td></tr>
              )}
              {courses.map((c) => (
                <tr key={c.id}>
                  <td style={{ fontWeight: 500, maxWidth: "220px" }}>{c.title}</td>
                  <td>{c.category ? <span className="badge badge-neutral">{c.category.name}</span> : "—"}</td>
                  <td>
                    {c.teacher ? teacherLabel(c.teacher) : (
                      <span className="badge badge-warning">Sin asignar</span>
                    )}
                  </td>
                  <td>{formatCurrency(c.price, c.currency)}</td>
                  <td><span className="badge badge-neutral">{c.level}</span></td>
                  <td>
                    <span className={`badge ${c.is_active ? "badge-success" : "badge-warning"}`}>
                      {c.is_active ? "Activo" : "Inactivo"}
                    </span>
                  </td>
                  <td style={{ display: "flex", gap: "4px", flexWrap: "wrap" }}>
                    <button className="btn btn-secondary btn-sm" onClick={() => openEdit(c)}>Editar</button>
                    <button className="btn btn-secondary btn-sm" onClick={() => router.push(`/admin/courses/${c.id}/curriculum`)}>Temario</button>
                    <button className="btn btn-secondary btn-sm" onClick={() => router.push(`/admin/courses/${c.id}/classes`)}>Clases</button>
                    <button
                      className={`btn btn-sm ${c.is_active ? "btn-secondary" : "btn-primary"}`}
                      onClick={() => toggleActive(c.id, !c.is_active)}
                    >{c.is_active ? "Desactivar" : "Activar"}</button>
                    <button className="btn btn-danger btn-sm" onClick={() => setConfirmDelete(c)}>Eliminar</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Create Modal */}
      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="Crear nuevo curso" width="640px">
        <form onSubmit={handleCreate} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <div>
            <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>Título *</label>
            <input className="input" required value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} placeholder="Ej: Python desde Cero" />
          </div>
          <div>
            <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>Descripción *</label>
            <textarea className="input" required rows={3} value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} placeholder="Descripción detallada del curso…" style={{ resize: "vertical" }} />
          </div>
          <div>
            <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>Descripción corta</label>
            <input className="input" value={form.short_description} onChange={e => setForm(f => ({ ...f, short_description: e.target.value }))} placeholder="Resumen breve para la tarjeta del curso" />
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
            <div>
              <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>Precio ({settings.default_currency}) *</label>
              <input className="input" required type="number" min="0" step="0.01" value={form.price} onChange={e => setForm(f => ({ ...f, price: e.target.value }))} placeholder="49.99" />
            </div>
            <div>
              <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>Nivel *</label>
              <select className="input" value={form.level} onChange={e => setForm(f => ({ ...f, level: e.target.value }))}>
                {LEVELS.map(l => <option key={l.value} value={l.value}>{l.label}</option>)}
              </select>
            </div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
            <div>
              <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>Horas de duración</label>
              <input className="input" type="number" min="0" value={form.duration_hours} onChange={e => setForm(f => ({ ...f, duration_hours: e.target.value }))} placeholder="40" />
            </div>
            <div>
              <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>Duración en meses</label>
              <input className="input" type="number" min="1" value={form.duration_months} onChange={e => setForm(f => ({ ...f, duration_months: e.target.value }))} placeholder="3" />
            </div>
          </div>
          <div>
            <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>Descuento por pago completo (%)</label>
            <input className="input" type="number" min="0" max="100" step="0.01" value={form.full_payment_discount_pct} onChange={e => setForm(f => ({ ...f, full_payment_discount_pct: e.target.value }))} placeholder="10" />
          </div>
          {monthlyPrice !== null && (
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
              <div style={{ padding: "10px 12px", background: "var(--color-surface-elevated)", borderRadius: "8px", border: "1px solid var(--color-border)" }}>
                <div style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", marginBottom: "2px" }}>Pago mensual estimado</div>
                <div style={{ fontWeight: 600 }}>{formatCurrency(monthlyPrice, settings.default_currency)}</div>
              </div>
              <div style={{ padding: "10px 12px", background: "var(--color-surface-elevated)", borderRadius: "8px", border: "1px solid var(--color-border)" }}>
                <div style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", marginBottom: "2px" }}>Pago completo con descuento</div>
                <div style={{ fontWeight: 600 }}>{formatCurrency(fullPaymentPrice ?? 0, settings.default_currency)}</div>
              </div>
            </div>
          )}
          <div>
            <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>Categoría</label>
            <select className="input" value={form.category_id} onChange={e => setForm(f => ({ ...f, category_id: e.target.value }))}>
              <option value="">— Sin categoría —</option>
              {(categoriesData ?? []).map((c: any) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>Docente asignado</label>
            <select className="input" value={form.teacher_id} onChange={e => setForm(f => ({ ...f, teacher_id: e.target.value }))}>
              <option value="">— Sin asignar —</option>
              {teachers.map((t) => (
                <option key={t.id} value={t.id}>{t.first_name} {t.last_name} ({t.email})</option>
              ))}
            </select>
            <p style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", marginTop: "4px" }}>
              El docente verá el curso en «Mis cursos» y podrá editar su temario, sus clases y el progreso.
            </p>
          </div>
          <div>
            <label style={{ display: "flex", alignItems: "center", gap: "8px", fontWeight: 500, fontSize: "0.875rem", cursor: "pointer" }}>
              <input type="checkbox" checked={form.is_featured} onChange={e => setForm(f => ({ ...f, is_featured: e.target.checked }))} />
              Curso destacado
            </label>
          </div>
          <div style={{ display: "flex", gap: "12px", justifyContent: "flex-end", marginTop: "8px" }}>
            <button type="button" className="btn btn-secondary" onClick={() => setShowCreate(false)}>Cancelar</button>
            <button type="submit" className="btn btn-primary" disabled={saving}>{saving ? "Creando…" : "Crear curso"}</button>
          </div>
        </form>
      </Modal>

      {/* Edit Modal */}
      <Modal open={!!editing} onClose={() => setEditing(null)} title="Editar curso" width="640px">
        {editing && (
          <form onSubmit={handleUpdate} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <div>
              <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>Título</label>
              <input className="input" value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} />
            </div>
            <div>
              <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>Descripción</label>
              <textarea className="input" rows={3} value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} placeholder="Descripción detallada del curso…" style={{ resize: "vertical" }} />
            </div>
            <div>
              <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>Descripción corta</label>
              <input className="input" value={form.short_description} onChange={e => setForm(f => ({ ...f, short_description: e.target.value }))} placeholder="Resumen breve para la tarjeta del curso" />
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
              <div>
                <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>Precio ({settings.default_currency})</label>
                <input className="input" type="number" min="0" step="0.01" value={form.price} onChange={e => setForm(f => ({ ...f, price: e.target.value }))} />
              </div>
              <div>
                <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>Nivel</label>
                <select className="input" value={form.level} onChange={e => setForm(f => ({ ...f, level: e.target.value }))}>
                  {LEVELS.map(l => <option key={l.value} value={l.value}>{l.label}</option>)}
                </select>
              </div>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
              <div>
                <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>Horas de duración</label>
                <input className="input" type="number" min="0" value={form.duration_hours} onChange={e => setForm(f => ({ ...f, duration_hours: e.target.value }))} />
              </div>
              <div>
                <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>Duración en meses</label>
                <input className="input" type="number" min="1" value={form.duration_months} onChange={e => setForm(f => ({ ...f, duration_months: e.target.value }))} />
              </div>
            </div>
            <div>
              <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>Descuento por pago completo (%)</label>
              <input className="input" type="number" min="0" max="100" step="0.01" value={form.full_payment_discount_pct} onChange={e => setForm(f => ({ ...f, full_payment_discount_pct: e.target.value }))} />
            </div>
            {monthlyPrice !== null && (
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
                <div style={{ padding: "10px 12px", background: "var(--color-surface-elevated)", borderRadius: "8px", border: "1px solid var(--color-border)" }}>
                  <div style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", marginBottom: "2px" }}>Pago mensual estimado</div>
                  <div style={{ fontWeight: 600 }}>{formatCurrency(monthlyPrice, settings.default_currency)}</div>
                </div>
                <div style={{ padding: "10px 12px", background: "var(--color-surface-elevated)", borderRadius: "8px", border: "1px solid var(--color-border)" }}>
                  <div style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", marginBottom: "2px" }}>Pago completo con descuento</div>
                  <div style={{ fontWeight: 600 }}>{formatCurrency(fullPaymentPrice ?? 0, settings.default_currency)}</div>
                </div>
              </div>
            )}
            <div>
              <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>Categoría</label>
              <select className="input" value={form.category_id} onChange={e => setForm(f => ({ ...f, category_id: e.target.value }))}>
                <option value="">— Sin categoría —</option>
                {(categoriesData ?? []).map((c: any) => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>Docente asignado</label>
              <select className="input" value={form.teacher_id} onChange={e => setForm(f => ({ ...f, teacher_id: e.target.value }))}>
                <option value="">— Sin asignar —</option>
                {teachers.map((t) => (
                  <option key={t.id} value={t.id}>{t.first_name} {t.last_name} ({t.email})</option>
                ))}
              </select>
            </div>
            <div>
              <label style={{ display: "flex", alignItems: "center", gap: "8px", fontWeight: 500, fontSize: "0.875rem", cursor: "pointer" }}>
                <input type="checkbox" checked={form.is_featured} onChange={e => setForm(f => ({ ...f, is_featured: e.target.checked }))} />
                Curso destacado
              </label>
            </div>
            <div style={{ display: "flex", gap: "12px", justifyContent: "flex-end", marginTop: "8px" }}>
              <button type="button" className="btn btn-secondary" onClick={() => setEditing(null)}>Cancelar</button>
              <button type="submit" className="btn btn-primary" disabled={saving}>{saving ? "Guardando…" : "Guardar cambios"}</button>
            </div>
          </form>
        )}
      </Modal>

      {/* Delete Confirm */}
      <Modal open={!!confirmDelete} onClose={() => setConfirmDelete(null)} title="Confirmar eliminación" width="420px">
        {confirmDelete && (
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: "3rem", marginBottom: "16px" }}>🗑️</div>
            <p style={{ marginBottom: "8px" }}>¿Eliminar el curso <strong>"{confirmDelete.title}"</strong>?</p>
            <p style={{ fontSize: "0.875rem", color: "var(--color-text-muted)", marginBottom: "24px" }}>Esta acción es reversible (soft delete).</p>
            <div style={{ display: "flex", gap: "12px", justifyContent: "center" }}>
              <button className="btn btn-secondary" onClick={() => setConfirmDelete(null)}>Cancelar</button>
              <button className="btn btn-danger" onClick={handleDelete} disabled={saving}>{saving ? "Eliminando…" : "Sí, eliminar"}</button>
            </div>
          </div>
        )}
      </Modal>
    </>
  );
}
