"use client";

import { useState, useEffect, useCallback } from "react";
import Modal from "@/components/ui/Modal";
import Captcha, { isCaptchaEnabled, resetCaptcha } from "@/components/ui/Captcha";
import { api } from "@/lib/api";
import { toast } from "@/components/ui/Toast";

interface AdminUser {
  id: string;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  status: string;
  is_blocked: boolean;
  email_verified: boolean;
  force_change_password: boolean;
  roles: string[];
  created_at: string;
}

interface Paginated<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

export default function AdminUsersPage() {
  const [data, setData] = useState<Paginated<AdminUser> | null>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [page, setPage] = useState(1);
  const [confirmAction, setConfirmAction] = useState<{
    id: string;
    name: string;
    action: "block" | "unblock";
  } | null>(null);
  const [saving, setSaving] = useState(false);

  // ── Create user modal state ───────────────────────────────────────────
  const [createOpen, setCreateOpen] = useState(false);
  const [form, setForm] = useState({ first_name: "", last_name: "", email: "", role: "teacher" });
  const [captchaToken, setCaptchaToken] = useState("");
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState("");
  const captchaEnabled = isCaptchaEnabled();

  const fetchUsers = useCallback(async (p = page, q = search, st = statusFilter) => {
    try {
      setLoading(true);
      const params = new URLSearchParams({ page: String(p), per_page: "20" });
      if (q) params.set("search", q);
      // If status filter is set, we filter by role or status
      const res = await api.get<Paginated<AdminUser>>(`/users/admin/users?${params}`);
      
      // Client-side status filter
      if (st !== "all") {
        res.items = res.items.filter(u => u.status === st);
        res.total = res.items.length;
      }
      
      setData(res);
    } catch {
      toast.error("Error al cargar usuarios");
    } finally {
      setLoading(false);
    }
  }, [page, search, statusFilter]);

  useEffect(() => { fetchUsers(); }, [fetchUsers]);

  useEffect(() => {
    const t = setTimeout(() => { setPage(1); fetchUsers(1, search, statusFilter); }, 400);
    return () => clearTimeout(t);
  }, [search, statusFilter]);

  const handleAction = async () => {
    if (!confirmAction) return;
    setSaving(true);
    try {
      if (confirmAction.action === "block") {
        await api.patch(`/users/admin/users/${confirmAction.id}/block`);
        toast.success("Usuario bloqueado");
      } else if (confirmAction.action === "unblock") {
        await api.patch(`/users/admin/users/${confirmAction.id}/unblock`);
        toast.success("Usuario desbloqueado");
      }
      setConfirmAction(null);
      fetchUsers();
    } catch {
      toast.error("Error al realizar la acción");
    } finally {
      setSaving(false);
    }
  };

  const openCreateModal = () => {
    setForm({ first_name: "", last_name: "", email: "", role: "teacher" });
    setCaptchaToken("");
    setCreateError("");
    setCreateOpen(true);
  };

  const closeCreateModal = () => {
    setCreateOpen(false);
    resetCaptcha();
  };

  const handleCreateUser = async () => {
    setCreateError("");
    if (!form.first_name.trim() || form.first_name.trim().length < 2) {
      setCreateError("El nombre es obligatorio (mínimo 2 caracteres)");
      return;
    }
    if (!form.email.trim()) {
      setCreateError("El email es obligatorio");
      return;
    }
    if (captchaEnabled && !captchaToken) {
      setCreateError("Por favor completa el captcha");
      return;
    }
    setCreating(true);
    try {
      await api.post("/users/admin/users", {
        email: form.email.trim(),
        first_name: form.first_name.trim(),
        last_name: form.last_name.trim(),
        role: form.role,
        captcha_token: captchaEnabled ? captchaToken : null,
      });
      toast.success("Usuario creado. Se envió un correo con la contraseña temporal.");
      closeCreateModal();
      fetchUsers();
    } catch (err: any) {
      const detail = err?.message;
      if (err?.status === 409) setCreateError("El correo electrónico ya está registrado");
      else if (err?.status === 400) setCreateError(detail || "Validación captcha fallida o datos inválidos");
      else setCreateError(detail || "Error al crear el usuario");
      resetCaptcha();
      setCaptchaToken("");
    } finally {
      setCreating(false);
    }
  };

  const users = data?.items ?? [];

  const statusBadge = (u: AdminUser) => {
    if (u.is_blocked) return <span className="badge badge-error">Bloqueado</span>;
    if (u.status === "pending") return <span className="badge badge-warning">Pendiente</span>;
    if (u.status === "active") return <span className="badge badge-success">Activo</span>;
    return <span className="badge">{u.status}</span>;
  };

  return (
    <>
      <div className="page-header">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "12px", flexWrap: "wrap" }}>
          <div>
            <h1>Usuarios</h1>
            <p>Gestión de todos los usuarios registrados ({data?.total ?? "…"} total).</p>
          </div>
          <button className="btn btn-primary" onClick={openCreateModal} style={{ alignSelf: "center" }}>
            + Crear usuario
          </button>
        </div>
      </div>

      <div style={{ display: "flex", gap: "12px", marginBottom: "24px", alignItems: "center", flexWrap: "wrap" }}>
        <input
          className="input"
          placeholder="🔍 Buscar por nombre, email o username…"
          style={{ maxWidth: "400px" }}
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <div style={{ display: "flex", gap: "6px" }}>
          {["all", "pending", "active", "inactive"].map(st => (
            <button
              key={st}
              className={`btn btn-sm ${statusFilter === st ? "btn-primary" : "btn-secondary"}`}
              onClick={() => { setStatusFilter(st); setPage(1); }}
            >
              {st === "all" ? "Todos" : st === "pending" ? "⏳ Pendientes" : st === "active" ? "✅ Activos" : "⛔ Inactivos"}
            </button>
          ))}
        </div>
        {search && (
          <button className="btn btn-secondary btn-sm" onClick={() => setSearch("")}>✕ Limpiar</button>
        )}
      </div>

      {loading ? (
        <div className="card" style={{ textAlign: "center", padding: "40px", color: "var(--color-text-muted)" }}>Cargando usuarios…</div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Nombre</th><th>Email</th><th>Roles</th>
                <th>Estado</th><th>Registro</th><th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {users.length === 0 && (
                <tr><td colSpan={6} style={{ textAlign: "center", color: "var(--color-text-muted)", padding: "32px" }}>
                  {search ? "No se encontraron resultados." : "No hay usuarios."}
                </td></tr>
              )}
              {users.map(u => (
                <tr key={u.id}>
                  <td style={{ fontWeight: 500 }}>{u.first_name} {u.last_name}</td>
                  <td style={{ fontSize: "0.875rem" }}>{u.email}</td>
                  <td>
                    <div style={{ display: "flex", gap: "4px", flexWrap: "wrap" }}>
                      {u.roles.map(r => (
                        <span key={r} className="badge" style={{
                          fontSize: "0.75rem",
                          background: r === "admin" ? "rgba(239,68,68,0.12)" : r === "teacher" ? "rgba(16,185,129,0.12)" : r === "student" ? "rgba(99,102,241,0.12)" : "rgba(156,163,175,0.12)",
                          color: r === "admin" ? "#ef4444" : r === "teacher" ? "#10b981" : r === "student" ? "#6366f1" : "#9ca3af",
                        }}>
                          {r === "admin" ? "👑 Admin" : r === "teacher" ? "👩‍🏫 Docente" : r === "student" ? "🎓 Alumno" : `👤 ${r}`}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td>
                    <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                      {statusBadge(u)}
                      {u.force_change_password && (
                        <span className="badge badge-info" style={{ fontSize: "0.7rem" }}>🔐 Cambio pendiente</span>
                      )}
                    </div>
                  </td>
                  <td style={{ fontSize: "0.8125rem" }}>
                    {u.created_at ? new Date(u.created_at).toLocaleDateString("es-MX") : "—"}
                  </td>
                  <td>
                    <div style={{ display: "flex", gap: "6px" }}>
                      <button
                        className={`btn btn-sm ${u.is_blocked ? "btn-secondary" : "btn-danger"}`}
                        onClick={() => setConfirmAction({
                          id: u.id,
                          name: `${u.first_name} ${u.last_name}`,
                          action: u.is_blocked ? "unblock" : "block",
                        })}
                      >
                        {u.is_blocked ? "Desbloquear" : "Bloquear"}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination */}
      {data && data.pages > 1 && (
        <div style={{ display: "flex", gap: "8px", justifyContent: "center", marginTop: "24px" }}>
          <button className="btn btn-secondary btn-sm" disabled={page <= 1} onClick={() => setPage(p => p - 1)}>← Anterior</button>
          <span style={{ display: "flex", alignItems: "center", fontSize: "0.875rem", color: "var(--color-text-muted)" }}>
            Página {page} de {data.pages}
          </span>
          <button className="btn btn-secondary btn-sm" disabled={page >= data.pages} onClick={() => setPage(p => p + 1)}>Siguiente →</button>
        </div>
      )}

      {/* Confirm Action Modal */}
      <Modal
        open={!!confirmAction}
        onClose={() => setConfirmAction(null)}
        title={
          confirmAction?.action === "block" ? "Bloquear usuario" : "Desbloquear usuario"
        }
        width="420px"
      >
        {confirmAction && (
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: "3rem", marginBottom: "16px" }}>
              {confirmAction.action === "block" ? "🔒" : "🔓"}
            </div>
            <p style={{ marginBottom: "24px" }}>
              ¿{confirmAction.action === "block" ? "Bloquear" : "Desbloquear"} a <strong>{confirmAction.name}</strong>?
            </p>
            <div style={{ display: "flex", gap: "12px", justifyContent: "center" }}>
              <button className="btn btn-secondary" onClick={() => setConfirmAction(null)}>Cancelar</button>
              <button
                className={`btn ${confirmAction.action === "block" ? "btn-danger" : "btn-primary"}`}
                onClick={handleAction}
                disabled={saving}
              >
                {saving ? "Procesando…" : "Confirmar"}
              </button>
            </div>
          </div>
        )}
      </Modal>

      {/* Create User Modal */}
      <Modal
        open={createOpen}
        onClose={closeCreateModal}
        title="Crear nuevo usuario"
        width="520px"
      >
        <div>
          {createError && (
            <div
              style={{
                background: "rgba(239,68,68,0.1)",
                border: "1px solid rgba(239,68,68,0.3)",
                color: "#ef4444",
                padding: "12px 16px",
                borderRadius: "8px",
                fontSize: "0.875rem",
                marginBottom: "20px",
              }}
            >
              {createError}
            </div>
          )}

          <div className="form-group">
            <label className="label" htmlFor="cu_first_name">Nombre *</label>
            <input
              className="input"
              id="cu_first_name"
              placeholder="Nombre del usuario"
              value={form.first_name}
              onChange={(e) => setForm(f => ({ ...f, first_name: e.target.value }))}
            />
          </div>

          <div className="form-group">
            <label className="label" htmlFor="cu_last_name">Apellido (opcional)</label>
            <input
              className="input"
              id="cu_last_name"
              placeholder="Apellido del usuario"
              value={form.last_name}
              onChange={(e) => setForm(f => ({ ...f, last_name: e.target.value }))}
            />
          </div>

          <div className="form-group">
            <label className="label" htmlFor="cu_email">Email *</label>
            <input
              className="input"
              id="cu_email"
              type="email"
              placeholder="usuario@email.com"
              value={form.email}
              onChange={(e) => setForm(f => ({ ...f, email: e.target.value }))}
            />
          </div>

          <div className="form-group">
            <label className="label">Rol *</label>
            <div style={{ display: "flex", gap: "8px" }}>
              <button
                type="button"
                className={`btn btn-sm ${form.role === "teacher" ? "btn-primary" : "btn-secondary"}`}
                onClick={() => setForm(f => ({ ...f, role: "teacher" }))}
              >
                👩‍🏫 Docente
              </button>
              <button
                type="button"
                className={`btn btn-sm ${form.role === "admin" ? "btn-primary" : "btn-secondary"}`}
                onClick={() => setForm(f => ({ ...f, role: "admin" }))}
              >
                👑 Admin
              </button>
            </div>
          </div>

          <p style={{ fontSize: "0.8rem", color: "var(--color-text-muted)", marginBottom: "16px" }}>
            Se generará una contraseña temporal y se enviará por correo electrónico a {form.email || "el usuario"}.
            El nuevo usuario deberá cambiarla al primer inicio de sesión.
          </p>

          <div className="form-group">
            <Captcha onVerify={setCaptchaToken} onExpire={() => setCaptchaToken("")} />
          </div>

          <div style={{ display: "flex", gap: "12px", justifyContent: "flex-end", marginTop: "8px" }}>
            <button className="btn btn-secondary" onClick={closeCreateModal} disabled={creating}>Cancelar</button>
            <button
              className="btn btn-primary"
              onClick={handleCreateUser}
              disabled={creating || (captchaEnabled && !captchaToken)}
            >
              {creating ? "Creando…" : "Crear usuario"}
            </button>
          </div>
        </div>
      </Modal>
    </>
  );
}
