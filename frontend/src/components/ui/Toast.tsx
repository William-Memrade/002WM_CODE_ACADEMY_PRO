/**
 * CodeAcademy Pro — Toast Notification System
 * useToast hook + ToastContainer component.
 */
"use client";

import { useState, useCallback, useEffect } from "react";

export type ToastType = "success" | "error" | "info" | "warning";

interface Toast {
  id: string;
  message: string;
  type: ToastType;
}

const ICONS: Record<ToastType, string> = {
  success: "✅",
  error: "❌",
  warning: "⚠️",
  info: "ℹ️",
};

const COLORS: Record<ToastType, { bg: string; border: string; color: string }> = {
  success: { bg: "#ecfdf5", border: "#10b981", color: "#065f46" },
  error:   { bg: "#fef2f2", border: "#ef4444", color: "#991b1b" },
  warning: { bg: "#fffbeb", border: "#f59e0b", color: "#92400e" },
  info:    { bg: "#eff6ff", border: "#3b82f6", color: "#1e40af" },
};

// Singleton event system for cross-component toasts
type ToastListener = (toast: Toast) => void;
const listeners: ToastListener[] = [];

export function toast(message: string, type: ToastType = "info") {
  const t: Toast = { id: Math.random().toString(36).slice(2), message, type };
  listeners.forEach((l) => l(t));
}
toast.success = (msg: string) => toast(msg, "success");
toast.error = (msg: string) => toast(msg, "error");
toast.warning = (msg: string) => toast(msg, "warning");

export function useToast() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  useEffect(() => {
    const handler: ToastListener = (t) => {
      setToasts((prev) => [...prev, t]);
      setTimeout(() => setToasts((prev) => prev.filter((x) => x.id !== t.id)), 3500);
    };
    listeners.push(handler);
    return () => {
      const idx = listeners.indexOf(handler);
      if (idx >= 0) listeners.splice(idx, 1);
    };
  }, []);

  const dismiss = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return { toasts, dismiss };
}

export function ToastContainer() {
  const { toasts, dismiss } = useToast();

  return (
    <div style={{
      position: "fixed", bottom: "24px", right: "24px",
      zIndex: 2000, display: "flex", flexDirection: "column", gap: "10px",
      maxWidth: "380px",
    }}>
      {toasts.map((t) => {
        const c = COLORS[t.type];
        return (
          <div
            key={t.id}
            style={{
              display: "flex", alignItems: "flex-start", gap: "10px",
              padding: "14px 16px", borderRadius: "12px",
              background: c.bg, border: `1px solid ${c.border}`, color: c.color,
              boxShadow: "0 4px 20px rgba(0,0,0,0.12)",
              animation: "slideInRight 0.25s ease",
              cursor: "pointer",
              fontSize: "0.9rem", fontWeight: 500,
            }}
            onClick={() => dismiss(t.id)}
          >
            <span>{ICONS[t.type]}</span>
            <span style={{ flex: 1 }}>{t.message}</span>
          </div>
        );
      })}
      <style>{`
        @keyframes slideInRight {
          from { transform: translateX(120%); opacity: 0 }
          to   { transform: translateX(0);   opacity: 1 }
        }
      `}</style>
    </div>
  );
}
