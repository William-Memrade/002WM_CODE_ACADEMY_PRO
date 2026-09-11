"use client";

export default function StudentCertificatesPage() {
  return (
    <>
      <div className="page-header">
        <h1>Certificados</h1>
        <p>Tus certificados de finalización de cursos.</p>
      </div>

      <div className="card" style={{ textAlign: "center", padding: "48px" }}>
        <div style={{ fontSize: "3rem", marginBottom: "16px" }}>📜</div>
        <h3 style={{ fontWeight: 600, marginBottom: "8px" }}>Sin certificados aún</h3>
        <p style={{ color: "var(--color-text-muted)", marginBottom: "24px" }}>
          Completa tus cursos para obtener certificados de finalización.
        </p>
        <a href="/courses" className="btn btn-primary">Ver cursos</a>
      </div>
    </>
  );
}
