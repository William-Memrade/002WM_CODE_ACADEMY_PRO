"use client";
import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { toast } from "@/components/ui/Toast";

interface FeatureFlag {
  id: string;
  key: string;
  enabled: boolean;
  description: string | null;
}

export default function AdminFeatureFlagsPage() {
  const [flags, setFlags] = useState<FeatureFlag[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [togglingKey, setTogglingKey] = useState<string | null>(null);

  useEffect(() => {
    loadFlags();
  }, []);

  const loadFlags = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.get<FeatureFlag[]>("/admin/feature-flags");
      setFlags(data);
    } catch (err) {
      console.error("Error loading feature flags:", err);
      setError("Error al cargar feature flags. Intenta recargar la página.");
      toast.error("Error al cargar feature flags");
    } finally {
      setLoading(false);
    }
  };

  const toggle = async (key: string, currentEnabled: boolean) => {
    try {
      setTogglingKey(key);
      await api.patch(`/admin/feature-flags/${key}`, { enabled: !currentEnabled });
      setFlags((prev) =>
        prev.map((f) => (f.key === key ? { ...f, enabled: !currentEnabled } : f))
      );
      toast.success(`Feature flag "${key}" actualizado`);
    } catch (err) {
      console.error("Error toggling feature flag:", err);
      toast.error("Error al actualizar feature flag");
    } finally {
      setTogglingKey(null);
    }
  };

  if (loading) {
    return (
      <>
        <div className="page-header">
          <h1>Feature Flags</h1>
          <p>Activa o desactiva funcionalidades sin desplegar.</p>
        </div>
        <div style={{ textAlign: "center", padding: "40px", color: "var(--color-text-muted)" }}>
          Cargando feature flags…
        </div>
      </>
    );
  }

  if (error) {
    return (
      <>
        <div className="page-header">
          <h1>Feature Flags</h1>
          <p>Activa o desactiva funcionalidades sin desplegar.</p>
        </div>
        <div className="card" style={{ textAlign: "center", padding: "40px", color: "var(--color-text-muted)" }}>
          <p>{error}</p>
          <button className="btn btn-primary" onClick={loadFlags} style={{ marginTop: "16px" }}>
            Reintentar
          </button>
        </div>
      </>
    );
  }

  if (flags.length === 0) {
    return (
      <>
        <div className="page-header">
          <h1>Feature Flags</h1>
          <p>Activa o desactiva funcionalidades sin desplegar.</p>
        </div>
        <div className="card" style={{ textAlign: "center", padding: "40px", color: "var(--color-text-muted)" }}>
          No hay feature flags configurados.
        </div>
      </>
    );
  }

  return (
    <>
      <div className="page-header">
        <h1>Feature Flags</h1>
        <p>Activa o desactiva funcionalidades sin desplegar.</p>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: "8px", maxWidth: "700px" }}>
        {flags.map((flag) => (
          <div
            key={flag.key}
            className="card"
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              padding: "16px 24px",
            }}
          >
            <div>
              <div style={{ fontWeight: 600, fontSize: "0.9375rem" }}>
                {flag.description || flag.key}
              </div>
              <code style={{ fontSize: "0.75rem", color: "var(--color-text-muted)" }}>
                {flag.key}
              </code>
            </div>
            <button
              className={`btn btn-sm ${flag.enabled ? "btn-primary" : "btn-secondary"}`}
              onClick={() => toggle(flag.key, flag.enabled)}
              disabled={togglingKey === flag.key}
              style={{ minWidth: "100px" }}
            >
              {togglingKey === flag.key
                ? "..."
                : flag.enabled
                ? "✓ Activo"
                : "Inactivo"}
            </button>
          </div>
        ))}
      </div>
    </>
  );
}
