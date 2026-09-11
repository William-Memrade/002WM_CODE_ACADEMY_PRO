// HomeNav — updated 2026-05-04
"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { isAuthenticated, getUser, logout } from "@/lib/auth";

export default function HomeNav() {
  const [authed, setAuthed] = useState(false);
  const [user, setUser] = useState<{ first_name: string; roles: string[] } | null>(null);

  useEffect(() => {
    setAuthed(isAuthenticated());
    setUser(getUser());
  }, []);

  return (
    <nav style={{ display: "flex", gap: "32px", alignItems: "center" }}>
      <Link href="/courses" style={{ color: "#94a3b8", fontSize: "0.9375rem" }}>Cursos</Link>
      {authed ? (
        <>
          <span style={{ color: "#94a3b8", fontSize: "0.9375rem" }}>
            Hola, <strong style={{ color: "#e2e8f0" }}>{user?.first_name}</strong>
          </span>
          <button
            className="btn btn-secondary btn-sm"
            onClick={() => logout()}
            style={{ cursor: "pointer", color: "#94a3b8", borderColor: "rgba(255,255,255,0.2)" }}
          >
            Cerrar sesión
          </button>
        </>
      ) : (
        <>
          <Link href="/login" className="btn btn-secondary btn-sm">Iniciar sesión</Link>
          <Link href="/register" className="btn btn-primary btn-sm">Registrarse</Link>
        </>
      )}
    </nav>
  );
}
