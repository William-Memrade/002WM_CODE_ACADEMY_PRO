export default function AdminFeedbackPage() {
  return (
    <>
      <div className="page-header"><h1>Feedback</h1><p>Reseñas y valoraciones de los cursos.</p></div>
      <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
        {[
          { student: "Juan Pérez", course: "Python desde Cero", rating: 5, comment: "Excelente curso, muy bien explicado. La docente tiene mucha paciencia.", date: "2026-04-03" },
          { student: "María López", course: "React Avanzado", rating: 4, comment: "Buen contenido, me gustaría más ejercicios prácticos.", date: "2026-04-01" },
          { student: "Carlos Díaz", course: "Docker y DevOps", rating: 5, comment: "Increíble. Aprendí a desplegar mi app en producción.", date: "2026-03-28" },
        ].map((r, i) => (
          <div key={i} className="card">
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
              <div>
                <span style={{ fontWeight: 600 }}>{r.student}</span>
                <span style={{ color: "var(--color-text-muted)", margin: "0 8px" }}>en</span>
                <span style={{ fontWeight: 500 }}>{r.course}</span>
              </div>
              <span style={{ fontSize: "0.8125rem", color: "var(--color-text-muted)" }}>{r.date}</span>
            </div>
            <div style={{ marginBottom: "8px" }}>{"⭐".repeat(r.rating)}</div>
            <p style={{ color: "var(--color-text-secondary)", fontSize: "0.9375rem" }}>{r.comment}</p>
          </div>
        ))}
      </div>
    </>
  );
}
