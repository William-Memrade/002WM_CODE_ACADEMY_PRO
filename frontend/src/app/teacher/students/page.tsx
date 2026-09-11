export default function TeacherStudentsPage() {
  return (
    <>
      <div className="page-header"><h1>Alumnos</h1><p>Alumnos inscritos en tus cursos.</p></div>
      <div className="table-container">
        <table>
          <thead><tr><th>Alumno</th><th>Curso</th><th>Progreso</th><th>Estrellas</th><th>Estado</th><th>Acciones</th></tr></thead>
          <tbody>
            {[
              { name: "Juan Pérez", course: "Python desde Cero", progress: 85, stars: 5, highlighted: true },
              { name: "María López", course: "Python desde Cero", progress: 72, stars: 4, highlighted: false },
              { name: "Carlos Díaz", course: "Python Avanzado", progress: 45, stars: 3, highlighted: false },
              { name: "Ana Martínez", course: "Django REST", progress: 100, stars: 5, highlighted: true },
            ].map((s, i) => (
              <tr key={i}>
                <td style={{ fontWeight: 500 }}>{s.name}</td>
                <td>{s.course}</td>
                <td>
                  <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <div className="progress-bar" style={{ width: "100px" }}><div className="progress-fill" style={{ width: `${s.progress}%` }} /></div>
                    <span style={{ fontSize: "0.8125rem" }}>{s.progress}%</span>
                  </div>
                </td>
                <td>{"⭐".repeat(s.stars)}</td>
                <td>{s.highlighted && <span className="badge badge-success">Destacado</span>}</td>
                <td><button className="btn btn-secondary btn-sm">Calificar</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
