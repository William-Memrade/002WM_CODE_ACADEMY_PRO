"use client";

import { useState } from "react";
import Modal from "@/components/ui/Modal";
import { useAdminCategories, AdminCategory } from "@/hooks/useAdminData";
import { toast } from "@/components/ui/Toast";

const CATEGORY_EMOJIS: Record<string, string> = {
  python: "🐍", frontend: "🎨", backend: "⚙️", devops: "🐳",
  databases: "🗄️", fundamentals: "📐", mobile: "📱", security: "🔒",
  cloud: "☁️", default: "📚",
};

function getCategoryEmoji(slug: string): string {
  return CATEGORY_EMOJIS[slug] ?? CATEGORY_EMOJIS.default;
}

export default function AdminCategoriesPage() {
  const { data, loading, createCategory, updateCategory, deleteCategory } = useAdminCategories();
  const [showCreate, setShowCreate] = useState(false);
  const [editing, setEditing] = useState<AdminCategory | null>(null);
  const [confirmDelete, setConfirmDelete] = useState<AdminCategory | null>(null);
  const [saving, setSaving] = useState(false);

  const emptyForm = { name: "", description: "", sort_order: "0" };
  const [form, setForm] = useState(emptyForm);

  const openCreate = () => {
    setForm(emptyForm);
    setShowCreate(true);
  };

  const openEdit = (cat: AdminCategory) => {
    setForm({ name: cat.name, description: cat.description ?? "", sort_order: String(cat.sort_order) });
    setEditing(cat);
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await createCategory({ name: form.name, description: form.description || undefined, sort_order: parseInt(form.sort_order) || 0 });
      setShowCreate(false);
    } catch { toast.error("Error al crear categoría (¿ya existe ese nombre?)"); }
    finally { setSaving(false); }
  };

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editing) return;
    setSaving(true);
    try {
      await updateCategory(editing.id, { name: form.name, description: form.description || undefined, sort_order: parseInt(form.sort_order) || 0 });
      setEditing(null);
    } catch { toast.error("Error al actualizar categoría"); }
    finally { setSaving(false); }
  };

  const handleDelete = async () => {
    if (!confirmDelete) return;
    setSaving(true);
    try {
      await deleteCategory(confirmDelete.id);
      setConfirmDelete(null);
    } catch { toast.error("No se puede eliminar: la categoría tiene cursos asignados o hubo un error."); }
    finally { setSaving(false); }
  };

  return (
    <>
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h1>Categorías</h1>
          <p>Organiza el catálogo de cursos por categorías ({data.length} categorías).</p>
        </div>
        <button className="btn btn-primary" onClick={openCreate}>+ Crear categoría</button>
      </div>

      {loading ? (
        <div className="card" style={{ textAlign: "center", padding: "40px", color: "var(--color-text-muted)" }}>Cargando categorías…</div>
      ) : data.length === 0 ? (
        <div className="card" style={{ textAlign: "center", padding: "48px" }}>
          <div style={{ fontSize: "3rem", marginBottom: "16px" }}>🏷️</div>
          <p style={{ color: "var(--color-text-muted)" }}>No hay categorías creadas aún.</p>
          <button className="btn btn-primary" style={{ marginTop: "16px" }} onClick={openCreate}>+ Crear primera categoría</button>
        </div>
      ) : (
        <div className="grid-cards" style={{ gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))" }}>
          {data.map((cat) => (
            <div key={cat.id} className="card" style={{ textAlign: "center", position: "relative" }}>
              {/* Active badge */}
              <span style={{ position: "absolute", top: "12px", right: "12px" }}
                className={`badge ${cat.is_active ? "badge-success" : "badge-warning"}`}>
                {cat.is_active ? "Activa" : "Inactiva"}
              </span>

              <div style={{ fontSize: "2.5rem", marginBottom: "10px" }}>{getCategoryEmoji(cat.slug)}</div>
              <h3 style={{ fontWeight: 600, fontSize: "1rem", marginBottom: "4px" }}>{cat.name}</h3>
              <p style={{ fontSize: "0.8125rem", color: "var(--color-text-muted)", marginBottom: "6px" }}>
                /{cat.slug}
              </p>
              {cat.description && (
                <p style={{ fontSize: "0.8125rem", color: "var(--color-text-muted)", marginBottom: "12px", lineHeight: 1.4 }}>
                  {cat.description}
                </p>
              )}
              <p style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", marginBottom: "14px" }}>
                Orden: {cat.sort_order}
              </p>

              <div style={{ display: "flex", gap: "6px" }}>
                <button className="btn btn-secondary btn-sm" style={{ flex: 1 }} onClick={() => openEdit(cat)}>
                  Editar
                </button>
                <button className="btn btn-danger btn-sm" style={{ flex: 1 }} onClick={() => setConfirmDelete(cat)}>
                  Eliminar
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Modal */}
      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="Nueva categoría" width="460px">
        <form onSubmit={handleCreate} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <div>
            <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>Nombre *</label>
            <input
              className="input" required autoFocus
              value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
              placeholder="Ej: Machine Learning"
            />
            <p style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", marginTop: "4px" }}>
              El slug se genera automáticamente desde el nombre.
            </p>
          </div>
          <div>
            <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>Descripción</label>
            <input
              className="input"
              value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
              placeholder="Breve descripción de la categoría"
            />
          </div>
          <div>
            <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>Orden (menor aparece primero)</label>
            <input
              className="input" type="number" min="0"
              value={form.sort_order} onChange={e => setForm(f => ({ ...f, sort_order: e.target.value }))}
            />
          </div>
          <div style={{ display: "flex", gap: "12px", justifyContent: "flex-end", marginTop: "8px" }}>
            <button type="button" className="btn btn-secondary" onClick={() => setShowCreate(false)}>Cancelar</button>
            <button type="submit" className="btn btn-primary" disabled={saving}>{saving ? "Creando…" : "Crear categoría"}</button>
          </div>
        </form>
      </Modal>

      {/* Edit Modal */}
      <Modal open={!!editing} onClose={() => setEditing(null)} title="Editar categoría" width="460px">
        {editing && (
          <form onSubmit={handleUpdate} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <div>
              <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>Nombre *</label>
              <input
                className="input" required
                value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
              />
            </div>
            <div>
              <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>Descripción</label>
              <input
                className="input"
                value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
                placeholder="Breve descripción"
              />
            </div>
            <div>
              <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>Orden</label>
              <input
                className="input" type="number" min="0"
                value={form.sort_order} onChange={e => setForm(f => ({ ...f, sort_order: e.target.value }))}
              />
            </div>
            <div style={{ display: "flex", gap: "12px", justifyContent: "flex-end", marginTop: "8px" }}>
              <button type="button" className="btn btn-secondary" onClick={() => setEditing(null)}>Cancelar</button>
              <button type="submit" className="btn btn-primary" disabled={saving}>{saving ? "Guardando…" : "Guardar cambios"}</button>
            </div>
          </form>
        )}
      </Modal>

      {/* Delete Confirm */}
      <Modal open={!!confirmDelete} onClose={() => setConfirmDelete(null)} title="Eliminar categoría" width="400px">
        {confirmDelete && (
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: "3rem", marginBottom: "16px" }}>🗑️</div>
            <p style={{ marginBottom: "8px" }}>
              ¿Eliminar <strong>"{confirmDelete.name}"</strong>?
            </p>
            <p style={{ fontSize: "0.875rem", color: "var(--color-text-muted)", marginBottom: "24px" }}>
              Fallará si hay cursos asignados a esta categoría.
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
    </>
  );
}
