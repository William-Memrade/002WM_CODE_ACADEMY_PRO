"use client";

import { useState, useEffect, ChangeEvent } from "react";
import { api } from "@/lib/api";
import { toast } from "@/components/ui/Toast";

interface PaymentSettings {
  id: string | null;
  bank_name: string;
  account_number: string;
  account_holder: string;
  payment_instructions: string | null;
  qr_image_url: string | null;
  created_at: string | null;
  updated_at: string | null;
}

interface GeneralSettings {
  platform_name: string;
  default_currency: string;
  global_max_students_per_class: number;
}

export default function AdminSettingsPage() {
  const [paymentSettings, setPaymentSettings] = useState<PaymentSettings>({
    id: null,
    bank_name: "",
    account_number: "",
    account_holder: "",
    payment_instructions: null,
    qr_image_url: null,
    created_at: null,
    updated_at: null,
  });

  const [generalSettings, setGeneralSettings] = useState<GeneralSettings>({
    platform_name: "",
    default_currency: "USD",
    global_max_students_per_class: 100,
  });

  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [savingPayment, setSavingPayment] = useState(false);
  const [savingGeneral, setSavingGeneral] = useState(false);
  const [uploadingQr, setUploadingQr] = useState(false);

  useEffect(() => {
    loadAllSettings();
  }, []);

  const loadAllSettings = async () => {
    try {
      setLoading(true);
      setLoadError(null);
      const [paymentData, generalData] = await Promise.all([
        api.get<PaymentSettings>("/payments/settings"),
        api.get<GeneralSettings>("/settings"),
      ]);
      setPaymentSettings(paymentData);
      setGeneralSettings(generalData);
    } catch (error) {
      console.error("Error loading settings:", error);
      setLoadError("Error al cargar la configuración. Intenta recargar la página.");
      toast.error("Error al cargar configuración");
    } finally {
      setLoading(false);
    }
  };

  const handleSavePaymentSettings = async () => {
    if (!paymentSettings.bank_name.trim() || !paymentSettings.account_number.trim() || !paymentSettings.account_holder.trim()) {
      toast.error("Banco, número de cuenta y titular son obligatorios");
      return;
    }

    if (paymentSettings.bank_name.length > 255 || paymentSettings.account_holder.length > 255) {
      toast.error("El banco y el titular no pueden exceder 255 caracteres");
      return;
    }

    if (paymentSettings.account_number.length > 100) {
      toast.error("El número de cuenta no puede exceder 100 caracteres");
      return;
    }

    if (paymentSettings.payment_instructions && paymentSettings.payment_instructions.length > 2000) {
      toast.error("Las instrucciones de pago no pueden exceder 2000 caracteres");
      return;
    }

    try {
      setSavingPayment(true);
      const payload = {
        bank_name: paymentSettings.bank_name,
        account_number: paymentSettings.account_number,
        account_holder: paymentSettings.account_holder,
        payment_instructions: paymentSettings.payment_instructions,
      };
      const result = await api.post<PaymentSettings>("/payments/settings", payload);
      setPaymentSettings(result);
      toast.success("Configuración de pagos guardada correctamente");
    } catch (error: any) {
      console.error("Error saving payment settings:", error);
      const message = error?.message || "Error al guardar configuración de pagos";
      toast.error(message);
    } finally {
      setSavingPayment(false);
    }
  };

  const handleSaveGeneralSettings = async () => {
    if (!generalSettings.platform_name.trim()) {
      toast.error("El nombre de la plataforma es obligatorio");
      return;
    }

    if (generalSettings.global_max_students_per_class < 1 || generalSettings.global_max_students_per_class > 1000) {
      toast.error("El máximo de alumnos debe estar entre 1 y 1000");
      return;
    }

    try {
      setSavingGeneral(true);
      const result = await api.put<GeneralSettings>("/settings", generalSettings);
      setGeneralSettings(result);
      // Invalidate public settings cache so all clients pick up the new value
      localStorage.removeItem("platform_settings");
      toast.success("Configuración general guardada correctamente");
    } catch (error: any) {
      console.error("Error saving general settings:", error);
      const message = error?.message || "Error al guardar configuración general";
      toast.error(message);
    } finally {
      setSavingGeneral(false);
    }
  };

  const handleQrUpload = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      toast.error("Solo se permiten archivos de imagen");
      return;
    }

    if (file.size > 2 * 1024 * 1024) {
      toast.error("El archivo no puede superar 2MB");
      return;
    }

    try {
      setUploadingQr(true);
      const result = await api.upload<PaymentSettings>("/payments/settings/qr-upload", file);
      setPaymentSettings(result);
      toast.success("Imagen QR subida correctamente");
    } catch (error) {
      console.error("Error uploading QR:", error);
      toast.error("Error al subir imagen QR");
    } finally {
      setUploadingQr(false);
      event.target.value = "";
    }
  };

  const handlePaymentInputChange = (field: keyof PaymentSettings, value: string) => {
    setPaymentSettings(prev => ({ ...prev, [field]: value }));
  };

  const handleGeneralInputChange = (field: keyof GeneralSettings, value: string | number) => {
    setGeneralSettings(prev => ({ ...prev, [field]: value }));
  };

  if (loading) {
    return (
      <>
        <div className="page-header">
          <h1>Configuración</h1>
          <p>Ajustes generales de la plataforma.</p>
        </div>
        <div style={{ maxWidth: "600px" }}>
          <div className="card">
            <div style={{ textAlign: "center", padding: "40px" }}>
              Cargando configuración...
            </div>
          </div>
        </div>
      </>
    );
  }

  if (loadError) {
    return (
      <>
        <div className="page-header">
          <h1>Configuración</h1>
          <p>Ajustes generales de la plataforma.</p>
        </div>
        <div style={{ maxWidth: "600px" }}>
          <div className="card" style={{ textAlign: "center", padding: "40px", color: "var(--color-text-muted)" }}>
            <p>{loadError}</p>
            <button className="btn btn-primary" onClick={loadAllSettings} style={{ marginTop: "16px" }}>
              Reintentar
            </button>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <div className="page-header">
        <h1>Configuración</h1>
        <p>Ajustes generales de la plataforma.</p>
      </div>

      <div style={{ maxWidth: "600px" }}>
        {/* ── General Settings ───────────────────────────────────────────── */}
        <div className="card" style={{ marginBottom: "24px" }}>
          <h3 style={{ fontWeight: 600, marginBottom: "16px" }}>General</h3>
          <div className="form-group">
            <label className="label">Nombre de la plataforma</label>
            <input
              className="input"
              value={generalSettings.platform_name}
              onChange={(e) => handleGeneralInputChange("platform_name", e.target.value)}
              placeholder="Mi Plataforma"
            />
          </div>
          <div className="form-group">
            <label className="label">Moneda predeterminada</label>
            <select
              className="input"
              value={generalSettings.default_currency}
              onChange={(e) => handleGeneralInputChange("default_currency", e.target.value)}
            >
              <option value="USD">USD — US$</option>
              <option value="EUR">EUR — €</option>
              <option value="MXN">MXN — MX$</option>
              <option value="COP">COP — COP$</option>
              <option value="GTQ">GTQ — Q</option>
              <option value="HNL">HNL — L</option>
              <option value="NIO">NIO — C$</option>
              <option value="CRC">CRC — ₡</option>
              <option value="SVC">SVC — $</option>
            </select>
          </div>
          <div className="form-group">
            <label className="label">Máximo alumnos por clase (global)</label>
            <input
              className="input"
              type="number"
              min={1}
              max={1000}
              value={generalSettings.global_max_students_per_class}
              onChange={(e) => handleGeneralInputChange("global_max_students_per_class", parseInt(e.target.value) || 1)}
            />
          </div>
          <button
            className="btn btn-primary"
            onClick={handleSaveGeneralSettings}
            disabled={savingGeneral}
          >
            {savingGeneral ? "Guardando..." : "Guardar"}
          </button>
        </div>

        {/* ── Bank Details ───────────────────────────────────────────────── */}
        <div className="card" style={{ marginBottom: "24px" }}>
          <h3 style={{ fontWeight: 600, marginBottom: "16px" }}>Datos Bancarios (para comprobantes)</h3>

          <div className="form-group">
            <label className="label">Banco</label>
            <input
              className="input"
              value={paymentSettings.bank_name}
              onChange={(e) => handlePaymentInputChange("bank_name", e.target.value)}
              placeholder="Nombre del banco"
            />
          </div>

          <div className="form-group">
            <label className="label">Número de cuenta</label>
            <input
              className="input"
              value={paymentSettings.account_number}
              onChange={(e) => handlePaymentInputChange("account_number", e.target.value)}
              placeholder="Número de cuenta bancaria"
            />
          </div>

          <div className="form-group">
            <label className="label">Titular</label>
            <input
              className="input"
              value={paymentSettings.account_holder}
              onChange={(e) => handlePaymentInputChange("account_holder", e.target.value)}
              placeholder="Nombre del titular de la cuenta"
            />
          </div>

          <div className="form-group">
            <label className="label">Instrucciones de pago</label>
            <input
              className="input"
              value={paymentSettings.payment_instructions || ""}
              onChange={(e) => handlePaymentInputChange("payment_instructions", e.target.value)}
              placeholder="Instrucciones adicionales para el pago"
            />
          </div>

          <div className="form-group">
            <label className="label">Código QR</label>
            <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
              <input
                type="file"
                accept=".jpg,.jpeg,.png,.svg"
                onChange={handleQrUpload}
                disabled={uploadingQr}
                style={{ flex: 1 }}
              />
              {uploadingQr && <span>Subiendo...</span>}
            </div>
            {paymentSettings.qr_image_url && (
              <div style={{ marginTop: "8px" }}>
                <img
                  src={paymentSettings.qr_image_url}
                  alt="Código QR"
                  style={{ maxWidth: "150px", maxHeight: "150px", border: "1px solid #ddd" }}
                />
              </div>
            )}
          </div>

          <button
            className="btn btn-primary"
            onClick={handleSavePaymentSettings}
            disabled={savingPayment}
          >
            {savingPayment ? "Guardando..." : "Guardar Configuración"}
          </button>
        </div>

        {/* ── SMTP / Email (read-only informational) ────────────────────── */}
        <div className="card">
          <h3 style={{ fontWeight: 600, marginBottom: "16px" }}>SMTP / Email</h3>
          <div style={{
            background: "rgba(59,130,246,0.06)",
            border: "1px solid rgba(59,130,246,0.15)",
            padding: "16px",
            borderRadius: "8px",
            fontSize: "0.875rem",
            color: "var(--color-text-muted)",
          }}>
            <p style={{ margin: "0 0 8px", fontWeight: 500, color: "var(--color-text)" }}>
              Configuración gestionada por variables de entorno
            </p>
            <p style={{ margin: 0 }}>
              La configuración SMTP se gestiona por variables de entorno por seguridad.
              No se permite editar credenciales sensibles desde el panel admin.
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
