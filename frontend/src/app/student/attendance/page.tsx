"use client";

import { useEffect, useState, useMemo } from "react";
import { api } from "@/lib/api";
import { toast } from "@/components/ui/Toast";

interface AttendanceItem {
  id: string;
  course_class_name: string;
  session_date: string;
  status: string;
  notes: string | null;
}

function statusBadge(status: string) {
  switch (status) {
    case "present":
      return { cls: "badge-success", label: "Presente" };
    case "absent":
      return { cls: "badge-error", label: "Ausente" };
    case "late":
      return { cls: "badge-warning", label: "Tarde" };
    case "excused":
      return { cls: "badge-info", label: "Justificado" };
    default:
      return { cls: "badge-secondary", label: status };
  }
}

export default function StudentAttendancePage() {
  const [records, setRecords] = useState<AttendanceItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get<{ items: AttendanceItem[] }>("/students/me/attendance")
      .then((data) => setRecords(data.items || []))
      .catch(() => {
        toast.error("No se pudo cargar la asistencia");
        setRecords([]);
      })
      .finally(() => setLoading(false));
  }, []);

  const stats = useMemo(() => {
    const total = records.length;
    const present = records.filter((r) => r.status === "present").length;
    const late = records.filter((r) => r.status === "late").length;
    const rate = total > 0 ? Math.round(((present + late) / total) * 100) : 0;
    return { total, present, late, rate };
  }, [records]);

  return (
    <>
      <div className="page-header">
        <h1>Mi Asistencia</h1>
        <p>Registro de asistencia a tus clases.</p>
      </div>

      {loading ? (
        <div className="card" style={{ textAlign: "center", padding: "40px", color: "var(--color-text-muted)" }}>
          Cargando asistencia...
        </div>
      ) : records.length === 0 ? (
        <div className="card" style={{ textAlign: "center", padding: "48px" }}>
          <div style={{ fontSize: "3rem", marginBottom: "16px" }}>📋</div>
          <h3 style={{ fontWeight: 600, marginBottom: "8px" }}>Sin registros</h3>
          <p style={{ color: "var(--color-text-muted)" }}>
            Aún no hay registros de asistencia para mostrar.
          </p>
        </div>
      ) : (
        <>
          <div
            className="card"
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
              gap: "16px",
              marginBottom: "24px",
            }}
          >
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "var(--color-primary)" }}>
                {stats.total}
              </div>
              <div style={{ fontSize: "0.8rem", color: "var(--color-text-muted)" }}>Sesiones</div>
            </div>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "var(--color-primary)" }}>
                {stats.present}
              </div>
              <div style={{ fontSize: "0.8rem", color: "var(--color-text-muted)" }}>Presentes</div>
            </div>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "var(--color-primary)" }}>
                {stats.rate}%
              </div>
              <div style={{ fontSize: "0.8rem", color: "var(--color-text-muted)" }}>Asistencia</div>
            </div>
          </div>

          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Clase</th>
                  <th>Fecha</th>
                  <th>Estado</th>
                  <th>Notas</th>
                </tr>
              </thead>
              <tbody>
                {records.map((r) => {
                  const badge = statusBadge(r.status);
                  return (
                    <tr key={r.id}>
                      <td style={{ fontWeight: 500 }}>{r.course_class_name}</td>
                      <td style={{ fontSize: "0.8125rem" }}>
                        {new Date(r.session_date).toLocaleDateString("es-MX", {
                          year: "numeric",
                          month: "short",
                          day: "numeric",
                        })}
                      </td>
                      <td>
                        <span className={`badge ${badge.cls}`}>{badge.label}</span>
                      </td>
                      <td style={{ fontSize: "0.8125rem", color: "var(--color-text-muted)", maxWidth: "240px" }}>
                        {r.notes || "—"}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </>
      )}
    </>
  );
}
