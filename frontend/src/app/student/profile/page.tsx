export default function StudentProfilePage() {
  return (
    <>
      <div className="page-header"><h1>Mi Perfil</h1><p>Edita tu información personal.</p></div>
      <div className="card" style={{ maxWidth: "600px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "16px", marginBottom: "24px" }}>
          <div style={{ width: "72px", height: "72px", borderRadius: "50%", background: "var(--color-primary)", color: "white", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "1.75rem", fontWeight: 700 }}>JP</div>
          <div>
            <h3 style={{ fontWeight: 600 }}>Juan Pérez</h3>
            <p style={{ color: "var(--color-text-muted)", fontSize: "0.875rem" }}>@juanperez • Alumno</p>
            <div style={{ display: "flex", gap: "8px", marginTop: "4px" }}><span className="badge badge-info">⭐ 12 estrellas</span><span className="badge badge-success">Destacado</span></div>
          </div>
        </div>
        <form>
          <div className="form-row">
            <div className="form-group"><label className="label">Nombre</label><input className="input" defaultValue="Juan" /></div>
            <div className="form-group"><label className="label">Apellido</label><input className="input" defaultValue="Pérez" /></div>
          </div>
          <div className="form-group"><label className="label">Email</label><input className="input" type="email" defaultValue="juan@email.com" disabled /></div>
          <div className="form-group"><label className="label">Teléfono</label><input className="input" type="tel" placeholder="+1 234 567 8900" /></div>
          <button type="submit" className="btn btn-primary">Guardar cambios</button>
        </form>
      </div>
    </>
  );
}
