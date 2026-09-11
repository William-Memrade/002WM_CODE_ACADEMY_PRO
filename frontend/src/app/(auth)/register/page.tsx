"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { usePlatformSettings } from "@/hooks/usePlatformSettings";

export default function RegisterPage() {
  const router = useRouter();
  const { settings } = usePlatformSettings();
  const [form, setForm] = useState({
    email: "",
    username: "",
    password: "",
    first_name: "",
    last_name: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const update = (field: string, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await fetch("/api/v1/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });

      if (!res.ok) {
        const data = await res.json();
        const detail = data.detail;
        if (typeof detail === "string") {
          throw new Error(detail);
        } else if (Array.isArray(detail)) {
          throw new Error(detail.map((d: any) => d.msg).join(", "));
        }
        throw new Error("Error al registrarse");
      }

      const data = await res.json();

      // Auto-login: save tokens and user info
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      localStorage.setItem("user", JSON.stringify(data.user));

      // Check if user was trying to enroll in a course before registering
      const pendingCourse = sessionStorage.getItem("enroll_after_login");
      if (pendingCourse) {
        sessionStorage.removeItem("enroll_after_login");
        router.push(`/courses/${pendingCourse}`);
        return;
      }

      // Redirect — new users go to course catalog
      router.push("/courses");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "var(--color-bg)",
        padding: "20px",
      }}
    >
      <div style={{ width: "100%", maxWidth: "420px" }}>
        <div style={{ textAlign: "center", marginBottom: "32px" }}>
          <Link href="/" style={{ textDecoration: "none" }}>
            <h1 style={{ fontSize: "1.5rem", fontWeight: 700, color: "var(--color-text)" }}>
              🎓 {settings.platform_name}
            </h1>
          </Link>
          <p style={{ color: "var(--color-text-muted)", marginTop: "8px" }}>
            Crea tu cuenta gratuita
          </p>
        </div>

        <div className="card" style={{ padding: "32px" }}>
          <form onSubmit={handleSubmit}>
            {error && (
              <div
                style={{
                  background: "rgba(239,68,68,0.1)",
                  border: "1px solid rgba(239,68,68,0.3)",
                  color: "#ef4444",
                  padding: "12px 16px",
                  borderRadius: "8px",
                  fontSize: "0.875rem",
                  marginBottom: "20px",
                }}
              >
                {error}
              </div>
            )}

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
              <div className="form-group">
                <label className="label" htmlFor="first_name">Nombre</label>
                <input className="input" id="first_name" placeholder="Juan" value={form.first_name} onChange={(e) => update("first_name", e.target.value)} required />
              </div>
              <div className="form-group">
                <label className="label" htmlFor="last_name">Apellido</label>
                <input className="input" id="last_name" placeholder="Pérez" value={form.last_name} onChange={(e) => update("last_name", e.target.value)} required />
              </div>
            </div>

            <div className="form-group">
              <label className="label" htmlFor="username">Usuario</label>
              <input className="input" id="username" placeholder="juanperez" value={form.username} onChange={(e) => update("username", e.target.value)} required minLength={3} maxLength={30} />
            </div>

            <div className="form-group">
              <label className="label" htmlFor="reg-email">Correo electrónico</label>
              <input className="input" id="reg-email" type="email" placeholder="tu@email.com" value={form.email} onChange={(e) => update("email", e.target.value)} required />
            </div>

            <div className="form-group">
              <label className="label" htmlFor="reg-password">Contraseña</label>
              <input className="input" id="reg-password" type="password" placeholder="Mín. 8 caracteres, 1 mayúscula, 1 número" value={form.password} onChange={(e) => update("password", e.target.value)} required minLength={8} />
            </div>

            <button className="btn btn-primary" type="submit" disabled={loading} style={{ width: "100%", marginTop: "8px" }}>
              {loading ? "Creando cuenta..." : "Crear cuenta"}
            </button>
          </form>

          <div style={{ textAlign: "center", marginTop: "24px", fontSize: "0.875rem" }}>
            <span style={{ color: "var(--color-text-muted)" }}>¿Ya tienes cuenta? </span>
            <Link href="/login" style={{ color: "var(--color-primary)", fontWeight: 500 }}>
              Inicia sesión
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
