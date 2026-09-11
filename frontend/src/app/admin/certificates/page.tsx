export default function AdminCertificatesPage() {
  return (
    <>
      <div className="page-header"><h1>Certificados</h1><p>Certificados emitidos en la plataforma.</p></div>
      <div className="table-container">
        <table>
          <thead><tr><th>Alumno</th><th>Curso</th><th>Código</th><th>Fecha</th><th>Acciones</th></tr></thead>
          <tbody>
            {[
              { student: "Juan Pérez", course: "SQL y PostgreSQL", code: "CERT-2026-001", date: "2026-02-20" },
              { student: "Juan Pérez", course: "Git y GitHub", code: "CERT-2026-002", date: "2026-01-10" },
              { student: "Ana Martínez", course: "Python desde Cero", code: "CERT-2026-003", date: "2026-03-15" },
            ].map((c, i) => (
              <tr key={i}>
                <td>{c.student}</td><td>{c.course}</td><td><code style={{ fontSize: "0.8125rem" }}>{c.code}</code></td><td>{c.date}</td>
                <td><button className="btn btn-secondary btn-sm">Ver PDF</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
