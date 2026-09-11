/**
 * CodeAcademy Pro — Panel docente: Mis Alumnos
 * Alumnos inscritos en las clases del docente, con el progreso de cada uno.
 * El progreso lo escribe el docente (PATCH .../progress); el alumno sólo lo lee.
 */
"use client";

import { useEffect, useMemo, useState } from "react";
import { toast } from "@/components/ui/Toast";
import { TeacherStudentRow, useTeacherStudents } from "@/hooks/useTeacherData";

export default function TeacherStudentsPage() {
  const { data: students, loading, updateProgress } = useTeacherStudents();

  const [search, setSearch] = useState("");
  const [courseFilter, setCourseFilter] = useState("");
  const [classFilter, setClassFilter] = useState("");
  const [draft, setDraft] = useState<Record<string, string>>({});
  const [savingId, setSavingId] = useState<string | null>(null);

  // `/teacher/courses` enlaza aquí con ?course=<id> para ver sólo ese curso.
  useEffect(() => {
    const param = new URLSearchParams(globalThis.location?.search ?? "").get("course");
    if (param) setCourseFilter(param);
  }, []);

  const courses = useMemo(() => {
    const map = new Map<string, string>();
    students.forEach((s) => map.set(s.course_id, s.course_title));
    return [...map.entries()].map(([id, title]) => ({ id, title }));
  }, [students]);

  const classes = useMemo(() => {
    const map = new Map<string, string>();
    students
      .filter((s) => !courseFilter || s.course_id === courseFilter)
      .forEach((s) => {
        if (s.course_class_id) {
          map.set(s.course_class_id, s.course_class_name ?? "Clase sin nombre");
        }
      });
    return [...map.entries()].map(([id, name]) => ({ id, name }));
  }, [students, courseFilter]);

  const visible = students.filter((s) => {
    if (courseFilter && s.course_id !== courseFilter) return false;
    if (classFilter && s.course_class_id !== classFilter) return false;
    if (search) {
      const needle = search.toLowerCase();
      if (
        !s.student_name.toLowerCase().includes(needle) &&
        !s.student_email.toLowerCase().includes(needle)
      ) {
        return false;
      }
    }
    return true;
  });

  const saveProgress = async (row: TeacherStudentRow) => {
    const raw = draft[row.enrollment_id] ?? String(row.progress_percentage);
    const value = Number(raw);
    if (Number.isNaN(value) || value < 0 || value > 100) {
      toast.error("El progreso debe ser un número entre 0 y 100");
      return;
    }
    if (!row.course_class_id) {
      toast.error("El alumno no tiene clase asignada: asígnale una antes de marcar progreso");
      return;
    }
    setSavingId(row.enrollment_id);
    try {
      await updateProgress(row.course_class_id, row.student_id, value);
      toast.success(`Progreso de ${row.student_name} actualizado a ${value}%`);
      setDraft((prev) => {
        const next = { ...prev };
        delete next[row.enrollment_id];
        return next;
      });
    } catch {
      toast.error("No se pudo guardar el progreso");
    } finally {
      setSavingId(null);
    }
  };

  return (
    <>
      <div className="page-header">
        <div>
          <h1>Alumnos</h1>
          <p>Alumnos inscritos en tus clases. Tú marcas el progreso; el alumno lo consulta.</p>
        </div>
      </div>

      <div className="card" style={{ marginBottom: "16px" }}>
        <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
          <div className="form-group" style={{ flex: "1 1 240px", marginBottom: 0 }}>
            <label className="label">Buscar</label>
            <input
              className="input"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Nombre o correo"
            />
          </div>
          <div className="form-group" style={{ flex: "0 1 240px", marginBottom: 0 }}>
            <label className="label">Curso</label>
            <select
              className="input"
              value={courseFilter}
              onChange={(e) => {
                setCourseFilter(e.target.value);
                setClassFilter("");
              }}
            >
              <option value="">Todos mis cursos</option>
              {courses.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.title}
                </option>
              ))}
            </select>
          </div>
          <div className="form-group" style={{ flex: "0 1 240px", marginBottom: 0 }}>
            <label className="label">Clase</label>
            <select className="input" value={classFilter} onChange={(e) => setClassFilter(e.target.value)}>
              <option value="">Todas mis clases</option>
              {classes.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="card" style={{ textAlign: "center", padding: "40px", color: "var(--color-text-muted)" }}>
          Cargando alumnos…
        </div>
      ) : visible.length === 0 ? (
        <div className="card" style={{ textAlign: "center", padding: "48px" }}>
          <div style={{ fontSize: "3rem", marginBottom: "16px" }}>👥</div>
          <h3 style={{ fontWeight: 600, marginBottom: "8px" }}>Sin alumnos que mostrar</h3>
          <p style={{ color: "var(--color-text-muted)" }}>
            {students.length === 0
              ? "Todavía no tienes alumnos inscritos en tus clases."
              : "Ningún alumno coincide con los filtros aplicados."}
          </p>
        </div>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Alumno</th>
                <th>Curso</th>
                <th>Clase</th>
                <th style={{ width: "240px" }}>Progreso</th>
                <th style={{ width: "130px" }}>Estado</th>
                <th style={{ width: "110px" }}>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {visible.map((row) => {
                const value = draft[row.enrollment_id] ?? String(row.progress_percentage);
                const isSaving = savingId === row.enrollment_id;
                return (
                  <tr key={row.enrollment_id}>
                    <td>
                      <div style={{ fontWeight: 500 }}>{row.student_name}</div>
                      <div style={{ fontSize: "0.8125rem", color: "var(--color-text-muted)" }}>
                        {row.student_email}
                      </div>
                    </td>
                    <td>{row.course_title}</td>
                    <td>{row.course_class_name ?? <span style={{ color: "var(--color-text-muted)" }}>Sin clase</span>}</td>
                    <td>
                      <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
                        <div className="progress-bar" style={{ width: "90px" }}>
                          <div className="progress-fill" style={{ width: `${row.progress_percentage}%` }} />
                        </div>
                        <span style={{ fontSize: "0.8125rem" }}>{row.progress_percentage}%</span>
                      </div>
                      <input
                        className="input"
                        type="number"
                        min={0}
                        max={100}
                        step={1}
                        value={value}
                        disabled={!row.course_class_id || isSaving}
                        onChange={(e) => setDraft({ ...draft, [row.enrollment_id]: e.target.value })}
                        style={{ width: "100px" }}
                      />
                    </td>
                    <td>
                      {row.completed_at ? (
                        <span className="badge badge-success">Completado</span>
                      ) : (
                        <span className="badge badge-info">En curso</span>
                      )}
                    </td>
                    <td>
                      <button
                        className="btn btn-primary btn-sm"
                        onClick={() => saveProgress(row)}
                        disabled={!row.course_class_id || isSaving}
                      >
                        {isSaving ? "Guardando…" : "Guardar"}
                      </button>
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
