"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import { toast } from "@/components/ui/Toast";
import type { CourseClass } from "@/types";

interface AttendanceItem {
  id: string;
  course_class_id: string;
  student_id: string;
  session_date: string;
  status: string;
  notes: string | null;
  student_name?: string;
}

interface EnrolledStudent {
  enrollment_id: string;
  student_id: string;
  student_name: string;
  student_email: string;
  status: string;
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
      return { cls: "badge-neutral", label: status };
  }
}

export default function TeacherClassAttendancePage() {
  const params = useParams();
  const classId = params.id as string;

  const [classDetail, setClassDetail] = useState<CourseClass | null>(null);
  const [records, setRecords] = useState<AttendanceItem[]>([]);
  const [students, setStudents] = useState<EnrolledStudent[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const [studentId, setStudentId] = useState("");
  const [sessionDate, setSessionDate] = useState("");
  const [status, setStatus] = useState("present");
  const [notes, setNotes] = useState("");

  const fetchAttendance = async () => {
    try {
      const data = await api.get<{ items: AttendanceItem[] }>(`/course-classes/${classId}/attendance`);
      setRecords(data.items || []);
    } catch {
      toast.error("No se pudo cargar la asistencia");
      setRecords([]);
    }
  };

  const fetchStudents = async () => {
    try {
      const data = await api.get<{ items: EnrolledStudent[] }>(`/course-classes/${classId}/students`);
      setStudents(data.items || []);
    } catch {
      toast.error("No se pudo cargar la lista de estudiantes");
      setStudents([]);
    }
  };

  useEffect(() => {
    if (!classId) return;
    setLoading(true);

    api
      .get<CourseClass>(`/course-classes/${classId}`)
      .then((data) => setClassDetail(data))
      .catch(() => toast.error("No se pudo cargar el detalle de la clase"));

    Promise.all([fetchStudents(), fetchAttendance()]).finally(() => setLoading(false));
  }, [classId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!studentId || !sessionDate) {
      toast.error("Completa todos los campos obligatorios");
      return;
    }
    setSubmitting(true);
    try {
      await api.post(`/course-classes/${classId}/attendance`, {
        student_id: studentId,
        session_date: sessionDate,
        status,
        notes: notes || null,
      });
      toast.success("Asistencia registrada");
      setStudentId("");
      setSessionDate("");
      setStatus("present");
      setNotes("");
      await fetchAttendance();
    } catch {
      toast.error("Error al registrar asistencia");
    } finally {
      setSubmitting(false);
    }
  };

  // Students already marked for the selected date
  const alreadyMarkedForDate = new Set(
    records
      .filter((r) => r.session_date === sessionDate)
      .map((r) => r.student_id)
  );

  const availableStudents = students.filter(
    (s) => !alreadyMarkedForDate.has(s.student_id)
  );

  return (
    <>
      <div className="page-header">
        <h1>Asistencia</h1>
        <p>{classDetail ? `Clase: ${classDetail.name}` : "Cargando clase..."}</p>
      </div>

      <div className="card" style={{ marginBottom: "24px" }}>
        <h3 style={{ fontSize: "1rem", fontWeight: 600, marginBottom: "16px" }}>Registrar asistencia</h3>
        {students.length === 0 && !loading ? (
          <div style={{ padding: "16px", background: "#fef2f2", border: "1px solid #fecaca", borderRadius: "8px", color: "#991b1b" }}>
            No hay estudiantes inscritos en esta clase.
          </div>
        ) : (
          <form onSubmit={handleSubmit} style={{ display: "grid", gap: "16px" }}>
            <div className="form-row">
              <div>
                <label className="label">Estudiante</label>
                <select
                  className="input"
                  value={studentId}
                  onChange={(e) => setStudentId(e.target.value)}
                  required
                >
                  <option value="">Selecciona un estudiante</option>
                  {availableStudents.map((s) => (
                    <option key={s.student_id} value={s.student_id}>
                      {s.student_name}
                    </option>
                  ))}
                </select>
                {availableStudents.length === 0 && students.length > 0 && sessionDate && (
                  <p style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", marginTop: "4px" }}>
                    Todos los estudiantes ya tienen asistencia registrada para esta fecha.
                  </p>
                )}
              </div>
              <div>
                <label className="label">Fecha de sesión</label>
                <input
                  type="date"
                  className="input"
                  value={sessionDate}
                  onChange={(e) => setSessionDate(e.target.value)}
                  required
                />
              </div>
            </div>
            <div className="form-row">
              <div>
                <label className="label">Estado</label>
                <select className="input" value={status} onChange={(e) => setStatus(e.target.value)}>
                  <option value="present">Presente</option>
                  <option value="absent">Ausente</option>
                  <option value="late">Tarde</option>
                  <option value="excused">Justificado</option>
                </select>
              </div>
              <div>
                <label className="label">Notas</label>
                <input
                  type="text"
                  className="input"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Opcional"
                />
              </div>
            </div>
            <div style={{ display: "flex", justifyContent: "flex-end" }}>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={submitting || !studentId || students.length === 0}
              >
                {submitting ? "Guardando..." : "Registrar asistencia"}
              </button>
            </div>
          </form>
        )}
      </div>

      <h2 style={{ fontSize: "1.25rem", fontWeight: 600, marginBottom: "16px" }}>Registros de asistencia</h2>

      {loading ? (
        <div className="card" style={{ textAlign: "center", padding: "40px", color: "var(--color-text-muted)" }}>
          Cargando asistencia...
        </div>
      ) : records.length === 0 ? (
        <div className="card" style={{ textAlign: "center", padding: "48px" }}>
          <div style={{ fontSize: "3rem", marginBottom: "16px" }}>📋</div>
          <h3 style={{ fontWeight: 600, marginBottom: "8px" }}>Sin registros</h3>
          <p style={{ color: "var(--color-text-muted)" }}>Aún no hay registros de asistencia para esta clase.</p>
        </div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Estudiante</th>
                <th>Estado</th>
                <th>Notas</th>
              </tr>
            </thead>
            <tbody>
              {records.map((r) => {
                const badge = statusBadge(r.status);
                return (
                  <tr key={r.id}>
                    <td style={{ fontSize: "0.8125rem" }}>
                      {new Date(r.session_date).toLocaleDateString("es-MX", {
                        year: "numeric",
                        month: "short",
                        day: "numeric",
                      })}
                    </td>
                    <td style={{ fontWeight: 500 }}>{r.student_name || r.student_id.slice(0, 8) + "..." || "—"}</td>
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
      )}
    </>
  );
}
