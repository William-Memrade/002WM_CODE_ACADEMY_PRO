"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { usePlatformSettings } from "@/hooks/usePlatformSettings";

export default function LoginPage() {
  const router = useRouter();
  const { settings } = usePlatformSettings();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await fetch("/api/v1/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Error al iniciar sesión");
      }

      const data = await res.json();

      // Save tokens and user info
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      localStorage.setItem("user", JSON.stringify(data.user));

      // New users created by an admin (temp password) must change it first.
      if (data.user?.force_change_password) {
        router.push("/change-password");
        return;
      }

      // Check if user was trying to enroll in a course before login
      const pendingCourse = sessionStorage.getItem("enroll_after_login");
      if (pendingCourse) {
        sessionStorage.removeItem("enroll_after_login");
        router.push(`/courses/${pendingCourse}`);
        return;
      }

      // Redirect based on role
      const roles: string[] = data.user.roles || [];
      if (roles.includes("admin")) {
        router.push("/admin/dashboard");
      } else if (roles.includes("teacher")) {
        router.push("/teacher/dashboard");
      } else if (roles.includes("student")) {
        router.push("/student/dashboard");
      } else {
        // Pending users or users with only "user" role → browse courses
        router.push("/courses");
      }
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
            Inicia sesión en tu cuenta
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

            <div className="form-group">
              <label className="label" htmlFor="email">Correo electrónico</label>
              <input
                className="input"
                id="email"
                type="email"
                placeholder="tu@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoFocus
              />
            </div>

            <div className="form-group">
              <label className="label" htmlFor="password">Contraseña</label>
              <input
                className="input"
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={8}
              />
            </div>

            <button
              className="btn btn-primary"
              type="submit"
              disabled={loading}
              style={{ width: "100%", marginTop: "8px" }}
            >
              {loading ? "Iniciando sesión..." : "Iniciar sesión"}
            </button>
          </form>

          <div style={{ textAlign: "center", marginTop: "24px", fontSize: "0.875rem" }}>
            <span style={{ color: "var(--color-text-muted)" }}>¿No tienes cuenta? </span>
            <Link href="/register" style={{ color: "var(--color-primary)", fontWeight: 500 }}>
              Regístrate
            </Link>
          </div>
        </div>

        {/* Demo credentials hint */}
        <div
          style={{
            marginTop: "20px",
            padding: "16px",
            borderRadius: "8px",
            background: "rgba(99,102,241,0.08)",
            border: "1px solid rgba(99,102,241,0.2)",
            fontSize: "0.8rem",
            color: "var(--color-text-muted)",
          }}
        >
          <p style={{ fontWeight: 600, color: "var(--color-primary)", marginBottom: "8px" }}>
            Cuentas de demostración:
          </p>
          <p>👑 Admin: <code>admin@codeacademypro.com</code> / <code>Admin123!</code></p>
          <p>👩‍🏫 Docente: <code>ana.garcia@codeacademypro.com</code> / <code>Teacher123!</code></p>
          <p>🎓 Estudiante: <code>estudiante@codeacademypro.com</code> / <code>Student123!</code></p>
        </div>
      </div>
    </div>
  );
}
