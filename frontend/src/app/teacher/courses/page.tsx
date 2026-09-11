/**
 * CodeAcademy Pro — Panel docente: Mis Cursos
 * Cursos que imparte el docente (titular o con alguna clase asignada) con los
 * conteos reales del temario y de sus alumnos. Enlaza al editor de temario y al
 * listado de alumnos filtrado por curso.
 */
"use client";

import { useTeacherCourses } from "@/hooks/useTeacherData";

export default function TeacherCoursesPage() {
  const { data: courses, loading } = useTeacherCourses();

  return (
    <>
      <div className="page-header">
        <div>
          <h1>Mis Cursos</h1>
          <p>Cursos que impartes. Revisa el temario y sigue a tus alumnos.</p>
        </div>
      </div>

      {loading ? (
        <div className="card" style={{ textAlign: "center", padding: "40px", color: "var(--color-text-muted)" }}>
          Cargando cursos…
        </div>
      ) : courses.length === 0 ? (
        <div className="card" style={{ textAlign: "center", padding: "48px" }}>
          <div style={{ fontSize: "3rem", marginBottom: "16px" }}>📚</div>
          <h3 style={{ fontWeight: 600, marginBottom: "8px" }}>Sin cursos asignados</h3>
          <p style={{ color: "var(--color-text-muted)" }}>
            Todavía no eres docente de ningún curso ni tienes clases asignadas.
          </p>
        </div>
      ) : (
        <div className="grid-cards">
          {courses.map((course) => (
            <div key={course.id} className="card">
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "8px" }}>
                <h3 style={{ fontSize: "1rem", fontWeight: 600 }}>{course.title}</h3>
                <span className={`badge ${course.is_active ? "badge-success" : "badge-neutral"}`}>
                  {course.is_active ? "Activo" : "Inactivo"}
                </span>
              </div>
              <p style={{ fontSize: "0.8125rem", color: "var(--color-text-muted)", marginTop: "4px" }}>
                Nivel {course.level} ·{" "}
                {course.is_teacher_owner ? "Docente titular" : "Docente de una clase"}
              </p>

              <div
                style={{
                  display: "flex",
                  gap: "12px",
                  flexWrap: "wrap",
                  fontSize: "0.875rem",
                  color: "var(--color-text-secondary)",
                  margin: "14px 0",
                }}
              >
                <span>📦 {course.modules_count} módulos</span>
                <span>📄 {course.lessons_count} lecciones</span>
                <span>🏫 {course.classes_count} clases</span>
                <span>👥 {course.students_count} alumnos</span>
              </div>

              <div style={{ marginBottom: "16px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.8125rem", marginBottom: "4px" }}>
                  <span style={{ color: "var(--color-text-muted)" }}>Progreso medio</span>
                  <span>{course.avg_progress}%</span>
                </div>
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: `${course.avg_progress}%` }} />
                </div>
              </div>

              <div style={{ display: "flex", gap: "8px" }}>
                <a
                  href={`/teacher/courses/${course.id}/curriculum`}
                  className="btn btn-primary btn-sm"
                  style={{ flex: 1, textAlign: "center" }}
                >
                  Editar temario
                </a>
                <a
                  href={`/teacher/students?course=${course.id}`}
                  className="btn btn-secondary btn-sm"
                  style={{ flex: 1, textAlign: "center" }}
                >
                  Ver alumnos
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  );
}
