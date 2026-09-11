"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { getUser, logout } from "@/lib/auth";
import type { User } from "@/types";
import { ToastContainer } from "@/components/ui/Toast";
import { usePlatformSettings } from "@/hooks/usePlatformSettings";

interface SidebarItem {
  label: string;
  href: string;
  icon: string;
}

interface SidebarProps {
  title: string;
  subtitle: string;
  items: SidebarItem[];
  children: React.ReactNode;
}

export default function DashboardLayout({ title, subtitle, items, children }: SidebarProps) {
  const pathname = usePathname();
  const [user, setUser] = useState<User | null>(null);
  const { settings } = usePlatformSettings();

  useEffect(() => {
    setUser(getUser());
  }, []);

  const initials = user
    ? `${user.first_name?.[0] ?? ""}${user.last_name?.[0] ?? ""}`.toUpperCase() || "U"
    : "…";

  const handleLogout = async (e: React.MouseEvent) => {
    e.preventDefault();
    await logout();
  };

  return (
    <div className="dashboard-layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <Link href="/" style={{ textDecoration: "none" }}>
            <h2>🎓 {settings.platform_name}</h2>
          </Link>
          <span>{subtitle}</span>
        </div>
        <nav className="sidebar-nav">
          {items.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`sidebar-link ${pathname === item.href ? "active" : ""}`}
            >
              <span>{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </nav>
        <div style={{ padding: "16px", borderTop: "1px solid rgba(255,255,255,0.08)" }}>
          <button
            onClick={handleLogout}
            className="sidebar-link"
            style={{ color: "#ef4444", width: "100%", background: "none", border: "none", cursor: "pointer", textAlign: "left" }}
          >
            <span>🚪</span> Cerrar sesión
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="main-content">
        <div className="top-bar">
          <h2 style={{ fontSize: "1.125rem", fontWeight: 600 }}>{title}</h2>
          <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
            {user && (
              <span style={{ fontSize: "0.875rem", color: "var(--color-text-muted)" }}>
                Hola, <strong>{user.first_name}</strong>
              </span>
            )}
            <div
              title={user ? `${user.first_name} ${user.last_name}` : ""}
              style={{
                width: "36px", height: "36px", borderRadius: "50%",
                background: "var(--color-primary)", color: "white",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontWeight: 600, fontSize: "0.875rem", flexShrink: 0, cursor: "default",
              }}
            >
              {initials}
            </div>
          </div>
        </div>
        <main className="main-page">{children}</main>
      </div>

      {/* Global Toast Notifications */}
      <ToastContainer />
    </div>
  );
}
