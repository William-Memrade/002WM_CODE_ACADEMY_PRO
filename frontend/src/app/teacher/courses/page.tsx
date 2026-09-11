export default function TeacherCoursesPage() {
  return (
    <>
      <div className="page-header"><h1>Mis Cursos</h1><p>Gestiona el temario de tus cursos asignados.</p></div>
      <div className="grid-cards">
        {[
          { title: "Python desde Cero", modules: 8, lessons: 32, students: 85, emoji: "🐍" },
          { title: "Python Avanzado", modules: 6, lessons: 24, students: 42, emoji: "🔥" },
          { title: "Django REST Framework", modules: 5, lessons: 20, students: 29, emoji: "🌐" },
        ].map((c, i) => (
          <div key={i} className="card">
            <div style={{ display: "flex", gap: "12px", alignItems: "center", marginBottom: "16px" }}>
              <span style={{ fontSize: "2rem" }}>{c.emoji}</span>
              <div><h3 style={{ fontWeight: 600 }}>{c.title}</h3><span style={{ fontSize: "0.8125rem", color: "var(--color-text-muted)" }}>{c.students} alumnos</span></div>
            </div>
            <div style={{ display: "flex", gap: "16px", fontSize: "0.875rem", color: "var(--color-text-secondary)", marginBottom: "16px" }}>
              <span>📦 {c.modules} módulos</span><span>📄 {c.lessons} lecciones</span>
            </div>
            <div style={{ display: "flex", gap: "8px" }}>
              <button className="btn btn-primary btn-sm" style={{ flex: 1 }}>Editar temario</button>
              <button className="btn btn-secondary btn-sm" style={{ flex: 1 }}>Ver alumnos</button>
            </div>
          </div>
        ))}
      </div>
    </>
  );
}
