"use client";

import { useState } from "react";
import Modal from "@/components/ui/Modal";
import { useAdminUsers } from "@/hooks/useAdminData";
import { toast } from "@/components/ui/Toast";

export default function AdminStudentsPage() {
  const { data, loading, search, setSearch, blockUser, unblockUser, page, setPage } = useAdminUsers("student");
  const [confirmBlock, setConfirmBlock] = useState<{ id: string; name: string; blocked: boolean } | null>(null);
  const [saving, setSaving] = useState(false);

  const handleBlockToggle = async () => {
    if (!confirmBlock) return;
    setSaving(true);
    try {
      if (confirmBlock.blocked) await unblockUser(confirmBlock.id);
      else await blockUser(confirmBlock.id);
      setConfirmBlock(null);
    } catch { toast.error("Error al cambiar estado del usuario"); }
    finally { setSaving(false); }
  };

  const students = data?.items ?? [];

  return (
    <>
      <div className="page-header">
        <h1>Alumnos</h1>
        <p>Gestión de alumnos registrados ({data?.total ?? "…"} total).</p>
      </div>

      <div style={{ display: "flex", gap: "12px", marginBottom: "24px", alignItems: "center" }}>
        <input
          className="input"
          placeholder="🔍 Buscar por nombre, email o username…"
          style={{ maxWidth: "400px" }}
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        {search && (
          <button className="btn btn-secondary btn-sm" onClick={() => setSearch("")}>✕ Limpiar</button>
        )}
      </div>

      {loading ? (
        <div className="card" style={{ textAlign: "center", padding: "40px", color: "var(--color-text-muted)" }}>Cargando alumnos…</div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Alumno</th><th>Email</th><th>Username</th>
                <th>Verificado</th><th>Registro</th><th>Estado</th><th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {students.length === 0 && (
                <tr><td colSpan={7} style={{ textAlign: "center", color: "var(--color-text-muted)", padding: "32px" }}>
                  {search ? "No se encontraron resultados." : "No hay alumnos registrados."}
                </td></tr>
              )}
              {students.map((s) => (
                <tr key={s.id}>
                  <td style={{ fontWeight: 500 }}>{s.first_name} {s.last_name}</td>
                  <td style={{ fontSize: "0.875rem" }}>{s.email}</td>
                  <td style={{ fontSize: "0.875rem", color: "var(--color-text-muted)" }}>@{s.username}</td>
                  <td>
                    <span className={`badge ${s.email_verified ? "badge-success" : "badge-warning"}`}>
                      {s.email_verified ? "Verificado" : "Pendiente"}
                    </span>
                  </td>
                  <td style={{ fontSize: "0.8125rem" }}>
                    {s.created_at ? new Date(s.created_at).toLocaleDateString("es-MX") : "—"}
                  </td>
                  <td>
                    <span className={`badge ${s.is_blocked ? "badge-error" : "badge-success"}`}>
                      {s.is_blocked ? "Bloqueado" : "Activo"}
                    </span>
                  </td>
                  <td>
                    <button
                      className={`btn btn-sm ${s.is_blocked ? "btn-primary" : "btn-danger"}`}
                      onClick={() => setConfirmBlock({ id: s.id, name: `${s.first_name} ${s.last_name}`, blocked: s.is_blocked })}
                    >
                      {s.is_blocked ? "Desbloquear" : "Bloquear"}
                    </button>
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

      {/* Block/Unblock Confirm */}
      <Modal open={!!confirmBlock} onClose={() => setConfirmBlock(null)} title={confirmBlock?.blocked ? "Desbloquear alumno" : "Bloquear alumno"} width="400px">
        {confirmBlock && (
          <div style={{ textAlign: "center" }}>
            <div style={{ fontSize: "3rem", marginBottom: "16px" }}>{confirmBlock.blocked ? "🔓" : "🔒"}</div>
            <p style={{ marginBottom: "24px" }}>
              ¿{confirmBlock.blocked ? "Desbloquear" : "Bloquear"} a <strong>{confirmBlock.name}</strong>?
            </p>
            <div style={{ display: "flex", gap: "12px", justifyContent: "center" }}>
              <button className="btn btn-secondary" onClick={() => setConfirmBlock(null)}>Cancelar</button>
              <button
                className={`btn ${confirmBlock.blocked ? "btn-primary" : "btn-danger"}`}
                onClick={handleBlockToggle}
                disabled={saving}
              >
                {saving ? "Procesando…" : confirmBlock.blocked ? "Sí, desbloquear" : "Sí, bloquear"}
              </button>
            </div>
          </div>
        )}
      </Modal>
    </>
  );
}
