"use client";

import { useAuditLogs } from "@/hooks/useAdminData";

export default function AdminAuditPage() {
  const {
    data,
    loading,
    error,
    actionFilter,
    setActionFilter,
    emailFilter,
    setEmailFilter,
    dateFrom,
    setDateFrom,
    dateTo,
    setDateTo,
    page,
    setPage,
  } = useAuditLogs();

  const formatDate = (iso: string | null) => {
    if (!iso) return "—";
    const d = new Date(iso);
    return d.toLocaleString("es-ES", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <>
      <div className="page-header">
        <h1>Auditoría</h1>
        <p>Registro de acciones del sistema.</p>
      </div>

      <div style={{ display: "flex", gap: "12px", marginBottom: "24px", flexWrap: "wrap" }}>
        <select
          className="input"
          style={{ maxWidth: "200px" }}
          value={actionFilter}
          onChange={(e) => setActionFilter(e.target.value)}
        >
          <option value="">Todas las acciones</option>
          <option value="login_success">login_success</option>
          <option value="login_failed">login_failed</option>
          <option value="logout">logout</option>
          <option value="user_created">user_created</option>
          <option value="user_updated">user_updated</option>
          <option value="user_blocked">user_blocked</option>
          <option value="user_unblocked">user_unblocked</option>
          <option value="user_activated">user_activated</option>
          <option value="course_created">course_created</option>
          <option value="course_updated">course_updated</option>
          <option value="course_deleted">course_deleted</option>
          <option value="course_published">course_published</option>
          <option value="course_unpublished">course_unpublished</option>
          <option value="teacher_assigned">teacher_assigned</option>
          <option value="teacher_removed">teacher_removed</option>
          <option value="payment_approved">payment_approved</option>
          <option value="payment_rejected">payment_rejected</option>
          <option value="enrollment_created">enrollment_created</option>
        </select>
        <input
          className="input"
          placeholder="Filtrar por email..."
          style={{ maxWidth: "300px" }}
          value={emailFilter}
          onChange={(e) => setEmailFilter(e.target.value)}
        />
        <input
          className="input"
          type="date"
          placeholder="Desde"
          value={dateFrom}
          onChange={(e) => setDateFrom(e.target.value)}
        />
        <input
          className="input"
          type="date"
          placeholder="Hasta"
          value={dateTo}
          onChange={(e) => setDateTo(e.target.value)}
        />
      </div>

      {loading && <p>Cargando auditoría...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      {!loading && !error && (!data || data.items.length === 0) && (
        <p>No hay registros de auditoría</p>
      )}

      {!loading && !error && data && data.items.length > 0 && (
        <>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Usuario</th>
                  <th>Acción</th>
                  <th>Entidad</th>
                  <th>IP</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((l) => (
                  <tr key={l.id}>
                    <td style={{ fontSize: "0.8125rem", fontFamily: "monospace" }}>
                      {formatDate(l.created_at)}
                    </td>
                    <td>{l.actor_email || "system"}</td>
                    <td>
                      <span className="badge badge-info">{l.action}</span>
                    </td>
                    <td>{l.entity_label || "—"}</td>
                    <td style={{ fontFamily: "monospace", fontSize: "0.8125rem" }}>
                      {l.ip_address || "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {data.pages > 1 && (
            <div style={{ display: "flex", gap: "8px", justifyContent: "center", marginTop: "16px" }}>
              <button
                className="btn"
                disabled={page <= 1}
                onClick={() => setPage(page - 1)}
              >
                ← Anterior
              </button>
              <span style={{ lineHeight: "36px" }}>
                Página {page} de {data.pages}
              </span>
              <button
                className="btn"
                disabled={page >= data.pages}
                onClick={() => setPage(page + 1)}
              >
                Siguiente →
              </button>
            </div>
          )}
        </>
      )}
    </>
  );
}
