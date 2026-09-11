// HomePage — updated 2026-05-04
"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import HomeNav from "./HomeNav";
import { isAuthenticated } from "@/lib/auth";
import { usePlatformSettings } from "@/hooks/usePlatformSettings";

export default function HomePage() {
  const [authed, setAuthed] = useState(false);
  const { settings } = usePlatformSettings();

  useEffect(() => {
    setAuthed(isAuthenticated());
  }, []);

  return (
    <>
      {/* ── Header ──────────────────────────────────────────────────────── */}
      <header style={{ position: "fixed", top: 0, left: 0, right: 0, zIndex: 100, background: "rgba(15,23,42,0.95)", backdropFilter: "blur(12px)", borderBottom: "1px solid rgba(255,255,255,0.06)" }}>
        <div className="container" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", height: "64px" }}>
          <Link href="/" style={{ color: "white", fontSize: "1.25rem", fontWeight: 700 }}>
            🎓 {settings.platform_name}
          </Link>
          <HomeNav />
        </div>
      </header>

      {/* ── Hero ────────────────────────────────────────────────────────── */}
      <section className="hero">
        <div className="container">
          <h1>
            Aprende a programar con
            <br />
            <span>clases en vivo</span> y a tu ritmo
          </h1>
          <p>
            Cursos de programación con docentes expertos, clases en vivo interactivas,
            contenido pregrabado y certificados de finalización.
          </p>
          <div className="hero-buttons">
            <Link href="/courses" className="btn btn-primary btn-lg">
              Ver cursos
            </Link>
            {!authed && (
              <Link href="/register" className="btn btn-secondary btn-lg" style={{ background: "rgba(255,255,255,0.1)", color: "white", border: "1px solid rgba(255,255,255,0.2)" }}>
                Crear cuenta gratis
              </Link>
            )}
          </div>
        </div>
      </section>

      {/* ── Features ────────────────────────────────────────────────────── */}
      <section className="features-section">
        <div className="container" style={{ textAlign: "center", marginBottom: "48px" }}>
          <h2 style={{ fontSize: "2rem", fontWeight: 700 }}>¿Por qué {settings.platform_name}?</h2>
          <p style={{ color: "var(--color-text-secondary)", marginTop: "8px", fontSize: "1.0625rem" }}>
            Todo lo que necesitas para convertirte en un programador profesional.
          </p>
        </div>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon" style={{ background: "#eef2ff", color: "#6366f1" }}>🎥</div>
            <h3>Clases en Vivo</h3>
            <p>Sesiones interactivas con docentes expertos. Haz preguntas en tiempo real.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon" style={{ background: "#ecfdf5", color: "#10b981" }}>📹</div>
            <h3>Clases Pregrabadas</h3>
            <p>Accede al contenido cuando quieras, a tu propio ritmo, desde cualquier dispositivo.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon" style={{ background: "#fef3c7", color: "#f59e0b" }}>📜</div>
            <h3>Certificados</h3>
            <p>Obtén certificados verificables al completar cada curso exitosamente.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon" style={{ background: "#fce7f3", color: "#ec4899" }}>⭐</div>
            <h3>Sistema de Reputación</h3>
            <p>Gana estrellas, destácate y demuestra tu nivel ante potenciales empleadores.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon" style={{ background: "#dbeafe", color: "#3b82f6" }}>📊</div>
            <h3>Progreso en Tiempo Real</h3>
            <p>Visualiza tu avance en cada curso con métricas claras y detalladas.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon" style={{ background: "#f3e8ff", color: "#8b5cf6" }}>👨‍🏫</div>
            <h3>Docentes Expertos</h3>
            <p>Profesionales de la industria con años de experiencia práctica.</p>
          </div>
        </div>
      </section>

      {/* ── CTA ─────────────────────────────────────────────────────────── */}
      <section style={{ padding: "80px 24px", background: "linear-gradient(135deg, #6366f1, #8b5cf6)", textAlign: "center", color: "white" }}>
        <div className="container">
          <h2 style={{ fontSize: "2rem", fontWeight: 700, marginBottom: "16px" }}>
            ¿Listo para empezar?
          </h2>
          <p style={{ fontSize: "1.125rem", opacity: 0.9, marginBottom: "32px", maxWidth: "500px", margin: "0 auto 32px" }}>
            Únete a nuestra comunidad de estudiantes y da el primer paso hacia tu carrera en tecnología.
          </p>
          {authed ? (
            <Link href="/courses" className="btn btn-lg" style={{ background: "white", color: "#6366f1", fontWeight: 600 }}>
              Ver cursos
            </Link>
          ) : (
            <Link href="/register" className="btn btn-lg" style={{ background: "white", color: "#6366f1", fontWeight: 600 }}>
              Crear cuenta gratis
            </Link>
          )}
        </div>
      </section>

      {/* ── Footer ──────────────────────────────────────────────────────── */}
      <footer style={{ background: "#0f172a", color: "#94a3b8", padding: "48px 24px 24px" }}>
        <div className="container" style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: "32px" }}>
          <div>
            <h3 style={{ color: "white", fontSize: "1.125rem", marginBottom: "12px" }}>🎓 {settings.platform_name}</h3>
            <p style={{ fontSize: "0.875rem", maxWidth: "300px" }}>Academia virtual de programación con clases en vivo y pregrabadas.</p>
          </div>
          <div>
            <h4 style={{ color: "white", fontSize: "0.875rem", fontWeight: 600, marginBottom: "12px" }}>Plataforma</h4>
            <div style={{ display: "flex", flexDirection: "column", gap: "8px", fontSize: "0.875rem" }}>
              <Link href="/courses">Cursos</Link>
              {!authed && <Link href="/register">Registrarse</Link>}
              {!authed && <Link href="/login">Iniciar sesión</Link>}
            </div>
          </div>
        </div>
        <div className="container" style={{ borderTop: "1px solid rgba(255,255,255,0.08)", marginTop: "32px", paddingTop: "24px", textAlign: "center", fontSize: "0.8125rem" }}>
          © 2026 {settings.platform_name}. Todos los derechos reservados.
        </div>
      </footer>
    </>
  );
}
