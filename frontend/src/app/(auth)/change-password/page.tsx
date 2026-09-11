"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { toast } from "@/components/ui/Toast";
import Captcha, { isCaptchaEnabled, resetCaptcha } from "@/components/ui/Captcha";

// Mirror of backend password policy for inline UX feedback.
const PASSWORD_RULES = [
  { label: "Mínimo 8 caracteres", test: (p: string) => p.length >= 8 },
  { label: "Una mayúscula", test: (p: string) => /[A-Z]/.test(p) },
  { label: "Un número", test: (p: string) => /\d/.test(p) },
  { label: "Un carácter especial (_ ! ? *)", test: (p: string) => /[_!?*]/.test(p) },
];

export default function ChangePasswordPage() {
  const router = useRouter();
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [captchaToken, setCaptchaToken] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const captchaEnabled = isCaptchaEnabled();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (newPassword !== confirmPassword) {
      setError("Las contraseñas no coinciden");
      return;
    }
    if (captchaEnabled && !captchaToken) {
      setError("Por favor completa el captcha");
      return;
    }

    setLoading(true);
    try {
      await api.post("/users/me/change-temp-password", {
        new_password: newPassword,
        confirm_password: confirmPassword,
        captcha_token: captchaEnabled ? captchaToken : null,
      });
      toast.success("Contraseña actualizada");

      // Update cached user info so the force-change flag is cleared.
      try {
        const stored = localStorage.getItem("user");
        if (stored) {
          const u = JSON.parse(stored);
          u.force_change_password = false;
          localStorage.setItem("user", JSON.stringify(u));
        }
      } catch { /* ignore parse errors */ }

      // Redirect by role now that the temp password is replaced.
      const stored = localStorage.getItem("user");
      const roles: string[] = stored ? JSON.parse(stored).roles || [] : [];
      if (roles.includes("admin")) router.push("/admin/dashboard");
      else if (roles.includes("teacher")) router.push("/teacher/dashboard");
      else if (roles.includes("student")) router.push("/student/dashboard");
      else router.push("/courses");
    } catch (err: any) {
      const status = err?.status;
      if (status === 403) {
        setError("No se requiere cambio de contraseña temporal para este usuario.");
      } else if (status === 400) {
        setError("Validación captcha fallida o contraseña inválida.");
      } else {
        setError(err?.message || "Error al actualizar la contraseña");
      }
      resetCaptcha();
      setCaptchaToken("");
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
      <div style={{ width: "100%", maxWidth: "480px" }}>
        <div style={{ textAlign: "center", marginBottom: "24px" }}>
          <h1 style={{ fontSize: "1.5rem", fontWeight: 700, color: "var(--color-text)" }}>
            🔑 Cambio de contraseña temporal
          </h1>
          <p style={{ color: "var(--color-text-muted)", marginTop: "8px" }}>
            Por seguridad, define una nueva contraseña para continuar.
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
              <label className="label" htmlFor="new_password">Nueva contraseña</label>
              <input
                className="input"
                id="new_password"
                type="password"
                placeholder="••••••••"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
                minLength={8}
                autoFocus
              />
            </div>

            <div className="form-group">
              <label className="label" htmlFor="confirm_password">Confirmar contraseña</label>
              <input
                className="input"
                id="confirm_password"
                type="password"
                placeholder="••••••••"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                minLength={8}
              />
            </div>

            <ul style={{ listStyle: "none", padding: 0, margin: "4px 0 20px", display: "flex", flexWrap: "wrap", gap: "8px" }}>
              {PASSWORD_RULES.map((r) => {
                const ok = r.test(newPassword);
                return (
                  <li
                    key={r.label}
                    style={{
                      fontSize: "0.75rem",
                      padding: "3px 8px",
                      borderRadius: "999px",
                      background: ok ? "rgba(16,185,129,0.12)" : "rgba(156,163,175,0.12)",
                      color: ok ? "#10b981" : "var(--color-text-muted)",
                    }}
                  >
                    {ok ? "✓ " : "• "}{r.label}
                  </li>
                );
              })}
            </ul>

            <div className="form-group">
              <Captcha onVerify={setCaptchaToken} onExpire={() => setCaptchaToken("")} />
            </div>

            <button
              className="btn btn-primary"
              type="submit"
              disabled={loading || (captchaEnabled && !captchaToken)}
              style={{ width: "100%", marginTop: "8px" }}
            >
              {loading ? "Actualizando..." : "Actualizar contraseña"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}