"use client";

import { useState, useEffect, useCallback } from "react";
import Modal from "@/components/ui/Modal";
import { useAdminUsers } from "@/hooks/useAdminData";
import { api } from "@/lib/api";
import { toast } from "@/components/ui/Toast";

interface EligibleUser {
  id: string;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  status: string;
}

export default function AdminTeachersPage() {
  const { data, loading, search, setSearch } = useAdminUsers("teacher");
  const [showCreate, setShowCreate] = useState(false);
  const [saving, setSaving] = useState(false);

  // Eligible users state
  const [eligibleUsers, setEligibleUsers] = useState<EligibleUser[]>([]);
  const [eligibleLoading, setEligibleLoading] = useState(false);
  const [eligibleSearch, setEligibleSearch] = useState("");
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null);

  const fetchEligible = useCallback(async (q = "") => {
    setEligibleLoading(true);
    try {
      const params = new URLSearchParams();
      if (q) params.set("search", q);
      const res = await api.get<{ items: EligibleUser[] }>(`/teachers/eligible-users?${params}`);
      setEligibleUsers(res.items);
    } catch {
      toast.error("Error al cargar usuarios disponibles");
    } finally {
      setEligibleLoading(false);
    }
  }, []);

  // Load eligible users when modal opens
  useEffect(() => {
    if (showCreate) {
      fetchEligible();
      setSelectedUserId(null);
      setEligibleSearch("");
    }
  }, [showCreate, fetchEligible]);

  // Debounce search for eligible users
  useEffect(() => {
    if (!showCreate) return;
    const t = setTimeout(() => fetchEligible(eligibleSearch), 300);
    return () => clearTimeout(t);
  }, [eligibleSearch, showCreate, fetchEligible]);

  const handleAssignTeacher = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedUserId) {
      toast.error("Selecciona un usuario primero");
      return;
    }
    setSaving(true);
    try {
      await api.post(`/teachers/${selectedUserId}`);
      toast.success("Docente asignado correctamente ✅");
      setShowCreate(false);
      // Refresh teacher list
      window.location.reload();
    } catch (err: any) {
      toast.error("Error al asignar docente. Verifica que no sea ya docente.");
    } finally {
      setSaving(false);
    }
  };

  const teachers = data?.items ?? [];
  const selectedUser = eligibleUsers.find(u => u.id === selectedUserId);

  return (
    <>
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div><h1>Docentes</h1><p>Equipo docente de la plataforma ({data?.total ?? "…"} total).</p></div>
        <button className="btn btn-primary" onClick={() => setShowCreate(true)}>+ Asignar docente</button>
      </div>

      <div style={{ display: "flex", gap: "12px", marginBottom: "24px" }}>
        <input
          className="input" placeholder="🔍 Buscar docente…" style={{ maxWidth: "360px" }}
          value={search} onChange={e => setSearch(e.target.value)}
        />
      </div>

      {loading ? (
        <div className="card" style={{ textAlign: "center", padding: "40px", color: "var(--color-text-muted)" }}>Cargando docentes…</div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr><th>Nombre</th><th>Email</th><th>Username</th><th>Estado</th><th>Registro</th></tr>
            </thead>
            <tbody>
              {teachers.length === 0 && (
                <tr><td colSpan={5} style={{ textAlign: "center", color: "var(--color-text-muted)", padding: "32px" }}>
                  {search ? "Sin resultados." : "No hay docentes registrados."}
                </td></tr>
              )}
              {teachers.map((t) => (
                <tr key={t.id}>
                  <td style={{ fontWeight: 500 }}>{t.first_name} {t.last_name}</td>
                  <td>{t.email}</td>
                  <td style={{ fontSize: "0.875rem", color: "var(--color-text-muted)" }}>@{t.username}</td>
                  <td>
                    <span className={`badge ${t.is_blocked ? "badge-error" : t.status === "pending" ? "badge-warning" : "badge-success"}`}>
                      {t.is_blocked ? "Bloqueado" : t.status === "pending" ? "Pendiente" : "Activo"}
                    </span>
                  </td>
                  <td style={{ fontSize: "0.8125rem" }}>
                    {t.created_at ? new Date(t.created_at).toLocaleDateString("es-MX") : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Assign Teacher Modal — User Selector */}
      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="Asignar nuevo docente" width="600px">
        <form onSubmit={handleAssignTeacher} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <div>
            <p style={{ fontSize: "0.9rem", color: "var(--color-text-muted)", marginBottom: "12px" }}>
              Selecciona un usuario existente para convertirlo en docente. Solo se muestran usuarios que aún no tienen perfil de docente.
            </p>
          </div>
          
          <div>
            <label style={{ display: "block", marginBottom: "6px", fontWeight: 500, fontSize: "0.875rem" }}>Buscar usuario</label>
            <input
              className="input"
              placeholder="🔍 Buscar por nombre, email o username…"
              value={eligibleSearch}
              onChange={e => setEligibleSearch(e.target.value)}
            />
          </div>

          <div style={{
            border: "1px solid var(--color-border)",
            borderRadius: "8px",
            maxHeight: "280px",
            overflowY: "auto",
          }}>
            {eligibleLoading ? (
              <div style={{ padding: "24px", textAlign: "center", color: "var(--color-text-muted)" }}>Buscando usuarios…</div>
            ) : eligibleUsers.length === 0 ? (
              <div style={{ padding: "24px", textAlign: "center", color: "var(--color-text-muted)" }}>
                {eligibleSearch ? "No se encontraron usuarios." : "No hay usuarios disponibles."}
              </div>
            ) : (
              eligibleUsers.map(u => (
                <div
                  key={u.id}
                  onClick={() => setSelectedUserId(u.id)}
                  style={{
                    padding: "12px 16px",
                    cursor: "pointer",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    borderBottom: "1px solid var(--color-border)",
                    background: selectedUserId === u.id ? "rgba(99,102,241,0.12)" : "transparent",
                    transition: "background 0.15s",
                  }}
                >
                  <div>
                    <div style={{ fontWeight: 500, fontSize: "0.9375rem" }}>{u.first_name} {u.last_name}</div>
                    <div style={{ fontSize: "0.8125rem", color: "var(--color-text-muted)" }}>{u.email} · @{u.username}</div>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <span className={`badge ${u.status === "pending" ? "badge-warning" : "badge-success"}`} style={{ fontSize: "0.75rem" }}>
                      {u.status === "pending" ? "Pendiente" : "Activo"}
                    </span>
                    {selectedUserId === u.id && (
                      <span style={{ color: "var(--color-primary)", fontSize: "1.25rem" }}>✓</span>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>

          {selectedUser && (
            <div style={{
              padding: "12px 16px",
              background: "rgba(99,102,241,0.08)",
              border: "1px solid rgba(99,102,241,0.2)",
              borderRadius: "8px",
              fontSize: "0.875rem",
            }}>
              <strong>Seleccionado:</strong> {selectedUser.first_name} {selectedUser.last_name} ({selectedUser.email})
              <br />
              <span style={{ color: "var(--color-text-muted)", fontSize: "0.8125rem" }}>
                Al asignar como docente, su estado será actualizado a <strong>activo</strong> automáticamente.
              </span>
            </div>
          )}

          <div style={{ display: "flex", gap: "12px", justifyContent: "flex-end", marginTop: "8px" }}>
            <button type="button" className="btn btn-secondary" onClick={() => setShowCreate(false)}>Cancelar</button>
            <button type="submit" className="btn btn-primary" disabled={saving || !selectedUserId}>
              {saving ? "Asignando…" : "Asignar como docente"}
            </button>
          </div>
        </form>
      </Modal>
    </>
  );
}
