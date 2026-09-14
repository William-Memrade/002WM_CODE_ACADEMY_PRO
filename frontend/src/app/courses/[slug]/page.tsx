// CourseDetailPage — updated 2026-06-02
"use client";
import { useEffect, useState, useCallback, useRef } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { isAuthenticated, getUser, getToken, logout } from "@/lib/auth";
import { formatCurrency } from "@/lib/currency";
import { api } from "@/lib/api";
import { toast } from "@/components/ui/Toast";
import { usePlatformSettings } from "@/hooks/usePlatformSettings";

interface Lesson {
  id: string;
  title: string;
  duration_minutes: number | null;
  is_free: boolean;
}

interface Module {
  id: string;
  title: string;
  sort_order: number;
  lessons: Lesson[];
}

interface AvailableClass {
  id: string;
  name: string;
  teacher_name?: string;
  schedule_info?: string | null;
  available_slots?: number;
  is_full?: boolean;
  global_max?: number;
}

interface CourseAccess {
  can_view_full_syllabus: boolean;
  enrollment_status: string | null;
  role_for_course: string | null;
}

interface CourseDetail {
  id: string;
  title: string;
  slug: string;
  description: string;
  short_description: string | null;
  price: number;
  currency: string;
  level: string;
  duration_hours: number | null;
  is_featured: boolean;
  category: { name: string; slug: string } | null;
  modules: Module[];
  duration_months: number | null;
  monthly_price?: number;
  full_payment_price?: number;
  full_payment_discount_pct?: number;
  total_classes_count?: number;
  total_available_slots?: number;
  raw_available_slots?: number;
  has_available_classes?: boolean;
  needs_more_classes?: boolean;
  available_classes?: AvailableClass[];
}

interface PaymentInfo {
  id: string | null;
  bank_name: string;
  account_number: string;
  account_holder: string;
  payment_instructions: string | null;
  qr_image_url: string | null;
  account_type?: string;
  holder_type?: string;
  created_at: string | null;
  updated_at: string | null;
}

const LEVEL_LABELS: Record<string, string> = {
  beginner: "Principiante",
  intermediate: "Intermedio",
  advanced: "Avanzado",
};

export default function CourseDetailPage() {
  const params = useParams();
  const router = useRouter();
  const slug = params.slug as string;
  const [course, setCourse] = useState<CourseDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [openModules, setOpenModules] = useState<Set<string>>(new Set());

  // Auth
  const [authed, setAuthed] = useState(false);
  const [user, setUser] = useState<{ first_name: string; roles: string[]; status?: string } | null>(null);
  const [access, setAccess] = useState<CourseAccess | null>(null);
  const { settings } = usePlatformSettings();

  // Payment modals
  const [showPaymentInfo, setShowPaymentInfo] = useState(false);
  const [showUploadProof, setShowUploadProof] = useState(false);
  const [paymentInfo, setPaymentInfo] = useState<PaymentInfo | null>(null);
  const [loadingInfo, setLoadingInfo] = useState(false);
  const [paymentInfoError, setPaymentInfoError] = useState("");

  const PAYMENT_INFO_FALLBACK: PaymentInfo = {
    id: null,
    bank_name: "",
    account_number: "",
    account_holder: "",
    payment_instructions: "",
    qr_image_url: "",
    created_at: null,
    updated_at: null,
  };

  // Payment plan
  const [paymentPlan, setPaymentPlan] = useState<"monthly" | "full">("monthly");

  // Upload state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const dropRef = useRef<HTMLButtonElement>(null);
  const [uploadError, setUploadError] = useState("");

  useEffect(() => {
    setAuthed(isAuthenticated());
    setUser(getUser());
  }, []);

  useEffect(() => {
    fetch(`/api/v1/courses/${slug}`)
      .then((r) => { if (!r.ok) throw new Error("Not found"); return r.json(); })
      .then(setCourse)
      .catch(() => setCourse(null))
      .finally(() => setLoading(false));

    // Fetch access permissions (auth-optional endpoint)
    const token = getToken();
    fetch(`/api/v1/courses/${slug}/access`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (data) setAccess(data);
      })
      .catch(() => setAccess(null));
  }, [slug]);

  const toggleModule = (id: string) => {
    setOpenModules((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  // Determine if user can see full syllabus (server-side access check)
  const canSeeFullSyllabus = access?.can_view_full_syllabus ?? false;

  useEffect(() => {
    // Performance fix: only open Module 1 by default instead of all modules
    if (course && course.modules.length > 0) {
      const sorted = [...course.modules].sort((a, b) => a.sort_order - b.sort_order);
      setOpenModules(new Set([sorted[0].id]));
    }
  }, [course]);

  // Computed amount based on selected plan
  const expectedAmount = useCallback(() => {
    if (!course) return 0;
    if (paymentPlan === "monthly") {
      return course.monthly_price ?? course.price;
    }
    return course.full_payment_price ?? course.price;
  }, [course, paymentPlan]);

  // Fetch payment info
  const handleShowPaymentInfo = async () => {
    setShowPaymentInfo(true);
    if (!paymentInfo || paymentInfoError) {
      setPaymentInfoError("");
      setLoadingInfo(true);
      try {
        const res = await fetch("/api/v1/payments/settings/public");
        if (!res.ok) {
          const data = await res.json().catch(() => ({}));
          setPaymentInfoError(data.detail || "No se pudo cargar la configuración de pago.");
          setPaymentInfo(PAYMENT_INFO_FALLBACK);
          return;
        }

        const data = await res.json();
        setPaymentInfo({
          ...PAYMENT_INFO_FALLBACK,
          bank_name: data.bank_name ?? "",
          account_number: data.account_number ?? "",
          account_holder: data.account_holder ?? "",
          payment_instructions: data.payment_instructions ?? "",
          qr_image_url: data.qr_image_url ?? "",
          id: data.id ?? null,
          created_at: data.created_at ?? null,
          updated_at: data.updated_at ?? null,
        });
      } catch (err: any) {
        console.error("Payment info load error", err);
        setPaymentInfoError("Error al cargar la configuración de pago. Intenta nuevamente.");
        setPaymentInfo(PAYMENT_INFO_FALLBACK);
      } finally {
        setLoadingInfo(false);
      }
    }
  };

  // Handle proof upload
  const handleShowUpload = () => {
    if (!authed) {
      sessionStorage.setItem("enroll_after_login", slug);
      router.push("/login");
      return;
    }
    setShowUploadProof(true);
    setSelectedFile(null);
    setUploadError("");
    setUploadSuccess(false);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Client-side validation
    const ext = file.name.split(".").pop()?.toLowerCase();
    if (!ext || !["jpg", "jpeg", "png"].includes(ext)) {
      setUploadError("Solo se permiten archivos JPG, JPEG o PNG");
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      setUploadError("El archivo no puede superar los 5MB");
      return;
    }
    setUploadError("");
    setSelectedFile(file);
  };

  // Drag & drop handlers
  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    // Only set false if leaving the drop zone (not entering a child)
    if (dropRef.current && !dropRef.current.contains(e.relatedTarget as Node)) {
      setIsDragging(false);
    }
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (!file) return;
    const ext = file.name.split(".").pop()?.toLowerCase();
    if (!ext || !["jpg", "jpeg", "png"].includes(ext)) {
      setUploadError("Solo se permiten archivos JPG, JPEG o PNG");
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      setUploadError("El archivo no puede superar los 5MB");
      return;
    }
    setUploadError("");
    setSelectedFile(file);
  }, []);

  const handleUpload = async () => {
    if (!selectedFile || !course) return;
    setUploading(true);
    setUploadError("");

    try {
      await api.upload(
        `/payments/submit-proof`,
        selectedFile,
        "file",
        {
          course_id: course.id,
          payment_plan: paymentPlan,
        }
      );
      setUploadSuccess(true);
      toast.success("Comprobante enviado correctamente");
    } catch (err: any) {
      const msg = err?.message || "Error al subir comprobante";
      setUploadError(msg);
      toast.error(msg);
    } finally {
      setUploading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "var(--color-bg)" }}>
        <p style={{ color: "var(--color-text-muted)" }}>Cargando curso...</p>
      </div>
    );
  }

  if (!course) {
    return (
      <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "var(--color-bg)", flexDirection: "column", gap: "16px" }}>
        <h2>Curso no encontrado</h2>
        <Link href="/courses" className="btn btn-primary">Ver catálogo</Link>
      </div>
    );
  }

  const totalLessons = course.modules.reduce((sum, m) => sum + m.lessons.length, 0);
  const totalMinutes = course.modules.reduce(
    (sum, m) => sum + m.lessons.reduce((s, l) => s + (l.duration_minutes || 0), 0), 0
  );

  let paymentInfoContent;
  if (loadingInfo) {
    paymentInfoContent = (
      <p style={{ textAlign: "center", color: "var(--color-text-muted)" }}>Cargando...</p>
    );
  } else if (paymentInfo) {
    const hasPaymentData = Boolean(
      paymentInfo.bank_name || paymentInfo.account_number || paymentInfo.account_holder || paymentInfo.payment_instructions || paymentInfo.qr_image_url
    );

    paymentInfoContent = (
      <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
        {paymentInfoError && (
          <div style={{ padding: "12px", borderRadius: "8px", background: "#fef2f2", border: "1px solid #fecaca", color: "#991b1b" }}>
            {paymentInfoError}
          </div>
        )}

        {!hasPaymentData && (
          <div style={{ padding: "12px", borderRadius: "8px", background: "#f0f9ff", border: "1px solid #bae6fd", color: "#0c4a6e" }}>
            No hay configuración de pago disponible en este momento. Contacta al administrador para habilitar los datos bancarios y el QR.
          </div>
        )}

        {/* Payment plan selector inside payment info */}
        <div style={{ background: "var(--color-bg)", padding: "16px", borderRadius: "8px" }}>
          <p style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", textTransform: "uppercase", fontWeight: 600, marginBottom: "12px" }}>
            Plan de pago seleccionado
          </p>
          <div style={{ display: "flex", gap: "12px", marginBottom: "12px" }}>
            <label style={{ flex: 1, cursor: "pointer", display: "flex", alignItems: "center", gap: "8px", padding: "10px", borderRadius: "8px", border: paymentPlan === "monthly" ? "2px solid var(--color-primary)" : "1px solid var(--color-border)", background: paymentPlan === "monthly" ? "rgba(99,102,241,0.08)" : "transparent" }}>
              <input
                type="radio"
                name="payment-plan"
                value="monthly"
                checked={paymentPlan === "monthly"}
                onChange={() => setPaymentPlan("monthly")}
              />
              <span style={{ fontWeight: 500 }}>Mensual</span>
            </label>
            <label style={{ flex: 1, cursor: "pointer", display: "flex", alignItems: "center", gap: "8px", padding: "10px", borderRadius: "8px", border: paymentPlan === "full" ? "2px solid var(--color-primary)" : "1px solid var(--color-border)", background: paymentPlan === "full" ? "rgba(99,102,241,0.08)" : "transparent" }}>
              <input
                type="radio"
                name="payment-plan"
                value="full"
                checked={paymentPlan === "full"}
                onChange={() => setPaymentPlan("full")}
              />
              <span style={{ fontWeight: 500 }}>Completo</span>
            </label>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontSize: "0.875rem", color: "var(--color-text-muted)" }}>
              {paymentPlan === "monthly"
                ? course.duration_months
                  ? `${course.duration_months} meses`
                  : ""
                : course.full_payment_discount_pct && course.full_payment_discount_pct > 0
                ? `Descuento ${course.full_payment_discount_pct}%`
                : ""}
            </span>
            <span style={{ fontWeight: 700, fontSize: "1.25rem", color: "var(--color-primary)" }}>
              {formatCurrency(expectedAmount(), course.currency)}
            </span>
          </div>
        </div>

        <div style={{ background: "var(--color-bg)", padding: "16px", borderRadius: "8px" }}>
          <div style={{ display: "grid", gap: "12px", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))" }}>
            <div>
              <span style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", textTransform: "uppercase", fontWeight: 600 }}>Banco</span>
              <p style={{ fontWeight: 600, fontSize: "1rem", margin: "4px 0 0" }}>{paymentInfo.bank_name || "No configurado"}</p>
            </div>
            <div>
              <span style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", textTransform: "uppercase", fontWeight: 600 }}>Titular</span>
              <p style={{ fontWeight: 600, fontSize: "1rem", margin: "4px 0 0" }}>{paymentInfo.account_holder || "No configurado"}</p>
            </div>
            <div>
              <span style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", textTransform: "uppercase", fontWeight: 600 }}>Número de Cuenta</span>
              <p style={{ fontWeight: 600, fontSize: "1rem", margin: "4px 0 0", fontFamily: "monospace", letterSpacing: "1px" }}>{paymentInfo.account_number || "No configurado"}</p>
            </div>

            {paymentInfo.account_type ? (
              <div>
                <span style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", textTransform: "uppercase", fontWeight: 600 }}>Tipo de Cuenta</span>
                <p style={{ fontWeight: 600, fontSize: "1rem", margin: "4px 0 0" }}>{paymentInfo.account_type}</p>
              </div>
            ) : null}

            {paymentInfo.holder_type ? (
              <div>
                <span style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", textTransform: "uppercase", fontWeight: 600 }}>Tipo</span>
                <p style={{ fontWeight: 600, fontSize: "1rem", margin: "4px 0 0" }}>{paymentInfo.holder_type}</p>
              </div>
            ) : null}
            <div>
              <span style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", textTransform: "uppercase", fontWeight: 600 }}>Monto a pagar</span>
              <p style={{ fontWeight: 700, fontSize: "1.25rem", margin: "4px 0 0", color: "var(--color-primary)" }}>
                {formatCurrency(expectedAmount(), course.currency)}
              </p>
            </div>
          </div>
        </div>

        <div style={{ textAlign: "center", background: "var(--color-bg)", padding: "16px", borderRadius: "8px" }}>
          <span style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", textTransform: "uppercase", fontWeight: 600, display: "block", marginBottom: "12px" }}>Código QR de Pago</span>
          {paymentInfo.qr_image_url ? (
            <>
              <img
                src={paymentInfo.qr_image_url}
                alt="QR de pago"
                style={{ maxWidth: "200px", maxHeight: "200px", margin: "0 auto", borderRadius: "8px", border: "1px solid var(--color-border)" }}
              />
              <p style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", marginTop: "8px" }}>Escanea el código QR para realizar el pago</p>
            </>
          ) : (
            <div style={{
              width: "200px", height: "200px", margin: "0 auto", borderRadius: "8px",
              border: "2px dashed var(--color-border)", display: "flex", alignItems: "center",
              justifyContent: "center", flexDirection: "column", gap: "8px",
            }}>
              <span style={{ fontSize: "2rem", opacity: 0.4 }}>📷</span>
              <p style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", margin: 0 }}>QR no disponible</p>
              <p style={{ fontSize: "0.7rem", color: "var(--color-text-muted)", margin: 0 }}>Realiza la transferencia con los datos bancarios</p>
            </div>
          )}
        </div>

        <div style={{ background: "rgba(99,102,241,0.08)", border: "1px solid rgba(99,102,241,0.2)", padding: "16px", borderRadius: "8px" }}>
          <p style={{ fontWeight: 600, color: "var(--color-primary)", marginBottom: "8px", fontSize: "0.875rem" }}>📋 Instrucciones</p>
          <p style={{ fontSize: "0.875rem", lineHeight: 1.6, color: "var(--color-text-muted)" }}>
            {paymentInfo.payment_instructions || "Realice la transferencia bancaria usando los datos proporcionados arriba."}
          </p>
        </div>

        <button type="button" className="btn btn-primary" style={{ width: "100%" }} onClick={() => { setShowPaymentInfo(false); handleShowUpload(); }}>
          Ya realicé el pago — Subir comprobante
        </button>
      </div>
    );
  } else {
    paymentInfoContent = (
      <p style={{ color: "var(--color-text-muted)" }}>No se pudo cargar la información de pago.</p>
    );
  }

  return (
    <div style={{ minHeight: "100vh", background: "var(--color-bg)" }}>
      {/* Nav */}
      <nav style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "16px 32px", borderBottom: "1px solid var(--color-border)" }}>
        <Link href="/" style={{ fontWeight: 700, fontSize: "1.125rem", textDecoration: "none", color: "var(--color-text)" }}>🎓 {settings.platform_name}</Link>
        <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
          <Link href="/courses" className="btn btn-secondary btn-sm">← Cursos</Link>
          {authed ? (
            <>
              <span style={{ fontSize: "0.875rem", color: "var(--color-text-muted)" }}>
                Hola, <strong>{user?.first_name}</strong>
              </span>
              <button
                className="btn btn-secondary btn-sm"
                type="button"
                onClick={() => logout()}
                style={{ cursor: "pointer" }}
              >Cerrar sesión</button>
            </>
          ) : (
            <>
              <Link href="/login" className="btn btn-secondary btn-sm">Iniciar sesión</Link>
              <Link href="/register" className="btn btn-primary btn-sm">Registrarse</Link>
            </>
          )}
        </div>
      </nav>

      {/* Hero */}
      <div style={{
        background: `linear-gradient(135deg, ${course.level === "advanced" ? "#7c3aed, #ec4899" : course.level === "intermediate" ? "#2563eb, #06b6d4" : "#10b981, #3b82f6"})`,
        padding: "60px 32px", color: "#fff",
      }}>
        <div style={{ maxWidth: "900px", margin: "0 auto" }}>
          <div style={{ display: "flex", gap: "12px", marginBottom: "16px", flexWrap: "wrap" }}>
            {course.category && (
              <span style={{ background: "rgba(255,255,255,0.2)", padding: "4px 12px", borderRadius: "20px", fontSize: "0.8rem" }}>{course.category.name}</span>
            )}
            <span style={{ background: "rgba(255,255,255,0.2)", padding: "4px 12px", borderRadius: "20px", fontSize: "0.8rem" }}>{LEVEL_LABELS[course.level]}</span>
          </div>
          <h1 style={{ fontSize: "2.5rem", fontWeight: 800, marginBottom: "16px" }}>{course.title}</h1>
          <p style={{ fontSize: "1.1rem", opacity: 0.9, lineHeight: 1.6, maxWidth: "600px" }}>
            {course.short_description || course.description.slice(0, 200)}
          </p>
        </div>
      </div>

      <div style={{ maxWidth: "900px", margin: "0 auto", padding: "40px 24px" }}>
        {/* Stats */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "16px", marginBottom: "40px" }}>
          {[
            { label: "Módulos", value: course.modules.length },
            { label: "Lecciones", value: totalLessons },
            { label: "Duración", value: `${Math.round(totalMinutes / 60)}h ${totalMinutes % 60}m` },
            { label: "Precio", value: formatCurrency(course.price, course.currency) },
          ].map((stat) => (
            <div key={stat.label} className="card" style={{ textAlign: "center", padding: "20px" }}>
              <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "var(--color-primary)" }}>{stat.value}</div>
              <div style={{ fontSize: "0.8rem", color: "var(--color-text-muted)", marginTop: "4px" }}>{stat.label}</div>
            </div>
          ))}
        </div>

        {/* Description */}
        <div className="card" style={{ padding: "24px", marginBottom: "32px" }}>
          <h2 style={{ fontSize: "1.25rem", fontWeight: 600, marginBottom: "12px" }}>Descripción</h2>
          <p style={{ color: "var(--color-text-muted)", lineHeight: 1.7 }}>{course.description}</p>
        </div>

        {/* Syllabus */}
        <h2 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "20px" }}>
          📚 Temario ({course.modules.length} módulos, {totalLessons} lecciones)
        </h2>
        <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
          {[...course.modules].sort((a, b) => a.sort_order - b.sort_order).map((mod, mIdx) => {
            const isLocked = !canSeeFullSyllabus && mIdx > 0;
            return (
            <div key={mod.id} className="card" style={{ overflow: "hidden", position: "relative", opacity: isLocked ? 0.6 : 1 }}>
              <button
                id={`module-toggle-${mod.id}`}
                type="button"
                disabled={isLocked}
                aria-expanded={!isLocked && openModules.has(mod.id)}
                aria-controls={`module-panel-${mod.id}`}
                onClick={() => toggleModule(mod.id)}
                style={{
                  width: "100%",
                  padding: "16px 20px",
                  cursor: isLocked ? "default" : "pointer",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  border: "none",
                  background: "transparent",
                  textAlign: "left",
                  borderBottom: openModules.has(mod.id) && !isLocked ? "1px solid var(--color-border)" : "none",
                  userSelect: "none",
                }}
              >
                <span>
                  <span style={{ color: isLocked ? "var(--color-text-muted)" : "var(--color-primary)", fontWeight: 600, marginRight: "8px" }}>Módulo {mIdx + 1}</span>
                  <span style={{ fontWeight: 600 }}>{mod.title}</span>
                  <span style={{ color: "var(--color-text-muted)", fontSize: "0.8rem", marginLeft: "12px" }}>{mod.lessons.length} lecciones</span>
                </span>
                <span style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  {isLocked && <span style={{ fontSize: "1rem" }}>🔒</span>}
                  {!isLocked && <span style={{ fontSize: "1.2rem", transform: openModules.has(mod.id) ? "rotate(180deg)" : "rotate(0)", transition: "transform 0.2s" }}>▼</span>}
                </span>
              </button>
              {!isLocked && openModules.has(mod.id) && (
                <div id={`module-panel-${mod.id}`} role="region" aria-labelledby={`module-toggle-${mod.id}`}>
                  {mod.lessons.map((lesson, lIdx) => (
                    <div key={lesson.id} style={{
                      padding: "12px 20px 12px 40px", display: "flex", justifyContent: "space-between", alignItems: "center",
                      borderBottom: lIdx < mod.lessons.length - 1 ? "1px solid var(--color-border)" : "none", fontSize: "0.9rem",
                    }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                        <span style={{ color: "var(--color-text-muted)", fontSize: "0.8rem" }}>{mIdx + 1}.{lIdx + 1}</span>
                        <span>{lesson.title}</span>
                        {lesson.is_free && <span style={{ background: "#22c55e22", color: "#22c55e", padding: "1px 6px", borderRadius: "4px", fontSize: "0.65rem", fontWeight: 600 }}>GRATIS</span>}
                      </div>
                      <span style={{ color: "var(--color-text-muted)", fontSize: "0.8rem", whiteSpace: "nowrap" }}>
                        {lesson.duration_minutes ? `${lesson.duration_minutes} min` : ""}
                      </span>
                    </div>
                  ))}
                </div>
              )}
              {isLocked && (
                <div style={{
                  padding: "12px 20px", textAlign: "center", fontSize: "0.8rem",
                  color: "var(--color-text-muted)", background: "rgba(99,102,241,0.04)",
                  borderTop: "1px solid var(--color-border)",
                }}>
                  🔒 Inscríbete para ver el contenido completo
                </div>
              )}
            </div>
            );
          })}
        </div>

        {/* ── Pricing Section ─────────────────────────────────────── */}
        <div className="card" style={{ marginTop: "48px", padding: "32px" }}>
          <h2 style={{ fontSize: "1.25rem", fontWeight: 700, marginBottom: "20px" }}>💰 Opciones de pago</h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "16px", marginBottom: "24px" }}>
            {course.monthly_price != null && course.duration_months != null && (
              <div
                onClick={() => setPaymentPlan("monthly")}
                style={{
                  padding: "20px",
                  borderRadius: "12px",
                  border: paymentPlan === "monthly" ? "2px solid var(--color-primary)" : "1px solid var(--color-border)",
                  background: paymentPlan === "monthly" ? "rgba(99,102,241,0.06)" : "var(--color-bg)",
                  cursor: "pointer",
                }}
              >
                <div style={{ fontSize: "0.875rem", color: "var(--color-text-muted)", marginBottom: "8px" }}>Pago mensual</div>
                <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "var(--color-primary)", marginBottom: "4px" }}>
                  {formatCurrency(course.monthly_price, course.currency)}
                </div>
                <div style={{ fontSize: "0.8rem", color: "var(--color-text-muted)" }}>
                  por mes · {course.duration_months} meses
                </div>
              </div>
            )}
            {course.full_payment_price != null && (
              <div
                onClick={() => setPaymentPlan("full")}
                style={{
                  padding: "20px",
                  borderRadius: "12px",
                  border: paymentPlan === "full" ? "2px solid var(--color-primary)" : "1px solid var(--color-border)",
                  background: paymentPlan === "full" ? "rgba(99,102,241,0.06)" : "var(--color-bg)",
                  cursor: "pointer",
                }}
              >
                <div style={{ fontSize: "0.875rem", color: "var(--color-text-muted)", marginBottom: "8px" }}>Pago completo</div>
                <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "var(--color-primary)", marginBottom: "4px" }}>
                  {formatCurrency(course.full_payment_price, course.currency)}
                </div>
                {course.full_payment_discount_pct != null && course.full_payment_discount_pct > 0 && (
                  <div style={{ fontSize: "0.8rem", color: "#22c55e", fontWeight: 600 }}>
                    Ahorra {course.full_payment_discount_pct}%
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Available classes */}
          {course.available_classes && course.available_classes.length > 0 && (
            <div style={{ marginBottom: "24px" }}>
              <h3 style={{ fontSize: "1rem", fontWeight: 600, marginBottom: "12px" }}>Clases disponibles</h3>
              <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                {course.available_classes.map((cls) => (
                  <div key={cls.id} style={{ padding: "12px 16px", borderRadius: "8px", border: "1px solid var(--color-border)", background: "var(--color-bg)" }}>
                    <div style={{ fontWeight: 600, marginBottom: "4px" }}>{cls.name}</div>
                    {cls.teacher_name && <div style={{ fontSize: "0.8rem", color: "var(--color-text-muted)" }}>Profesor: {cls.teacher_name}</div>}
                    {cls.schedule_info && <div style={{ fontSize: "0.8rem", color: "var(--color-text-muted)" }}>Horario: {cls.schedule_info}</div>}
                    {cls.is_full ? (
                      <div style={{ fontSize: "0.75rem", color: "#f59e0b", marginTop: "4px" }}>
                        ⏳ Clase llena — nueva clase próxima
                      </div>
                    ) : cls.available_slots != null ? (
                      <div style={{ fontSize: "0.75rem", color: "#22c55e", marginTop: "4px" }}>
                        {cls.available_slots} cupos disponibles
                      </div>
                    ) : null}
                  </div>
                ))}
              </div>
            </div>
          )}

          {course.needs_more_classes && (
            <div style={{ padding: "12px", borderRadius: "8px", background: "#fffbeb", border: "1px solid #fde68a", color: "#92400e", marginBottom: "24px" }}>
              {course.total_classes_count === 0 ? (
                <>
                  ⏳ Todavía no hay clases abiertas para este curso. Podés inscribirte y subir tu
                  comprobante: al confirmarse el pago tu inscripción queda <strong>en espera de
                  asignación de clase</strong> y te avisamos en cuanto haya una.
                </>
              ) : (
                <>
                  ⏳ Las clases actuales están completas. Estamos preparando una nueva clase próximamente.
                  Podés inscribirte y tu pago quedará en espera de asignación.
                </>
              )}
            </div>
          )}
        </div>

        {/* ── Purchase Section ─────────────────────────────────────── */}
        <div style={{ marginTop: "48px", padding: "40px", background: "var(--color-surface)", borderRadius: "12px" }}>
          <h3 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "8px", textAlign: "center" }}>
            Inscríbete en este curso
          </h3>
          <p style={{ color: "var(--color-text-muted)", marginBottom: "24px", textAlign: "center" }}>
            Plan seleccionado: <strong style={{ fontSize: "1.25rem", color: "var(--color-primary)" }}>
              {paymentPlan === "monthly" ? "Mensual" : "Completo"}
            </strong>
            <br />
            <span style={{ fontSize: "0.9rem" }}>
              Monto esperado: {course ? formatCurrency(expectedAmount(), course.currency) : "—"}
            </span>
          </p>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", maxWidth: "500px", margin: "0 auto" }}>
            {/* Button 1: Payment Info */}
            <button
              className="btn btn-secondary"
              type="button"
              style={{ padding: "16px", fontSize: "0.95rem", display: "flex", flexDirection: "column", alignItems: "center", gap: "8px" }}
              onClick={handleShowPaymentInfo}
            >
              <span style={{ fontSize: "1.5rem" }}>🏦</span>
              Realizar Pago
            </button>

            {/* Button 2: Upload Proof */}
            <button
              className="btn btn-primary"
              type="button"
              style={{ padding: "16px", fontSize: "0.95rem", display: "flex", flexDirection: "column", alignItems: "center", gap: "8px" }}
              onClick={handleShowUpload}
            >
              <span style={{ fontSize: "1.5rem" }}>📤</span>
              Subir Comprobante
            </button>
          </div>

          {!authed && (
            <p style={{ color: "var(--color-text-muted)", fontSize: "0.8125rem", marginTop: "16px", textAlign: "center" }}>
              Debes <Link href="/login" style={{ color: "var(--color-primary)", fontWeight: 500 }}>iniciar sesión</Link> para subir tu comprobante.{" "}
              <Link href="/register" style={{ color: "var(--color-primary)", fontWeight: 500 }}>Regístrate gratis</Link>
            </p>
          )}
        </div>
      </div>

      {/* ── Modal: Payment Info ──────────────────────────────────── */}
      {showPaymentInfo && (
        <div style={{
          position: "fixed", inset: 0, display: "flex",
          alignItems: "center", justifyContent: "center", zIndex: 1000, padding: "20px",
        }}>
          <button
            type="button"
            aria-label="Cerrar información de pago"
            onClick={() => setShowPaymentInfo(false)}
            style={{
              position: "absolute",
              inset: 0,
              background: "rgba(0,0,0,0.6)",
              border: "none",
              padding: 0,
              margin: 0,
              cursor: "pointer",
            }}
          />
          <div
            className="card"
            style={{
              maxWidth: "480px",
              width: "100%",
              padding: "24px",
              maxHeight: "calc(100vh - 40px)",
              overflowY: "auto",
              position: "relative",
              zIndex: 1,
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
              <h3 style={{ fontSize: "1.25rem", fontWeight: 700 }}>🏦 Información de Pago</h3>
              <button type="button" onClick={() => setShowPaymentInfo(false)} style={{ background: "none", border: "none", fontSize: "1.5rem", cursor: "pointer", color: "var(--color-text-muted)" }}>×</button>
            </div>
            {paymentInfoContent}
          </div>
        </div>
      )}

      {/* ── Modal: Upload Proof ──────────────────────────────────── */}
      {showUploadProof && (
        <div style={{
          position: "fixed", inset: 0, display: "flex",
          alignItems: "center", justifyContent: "center", zIndex: 1000, padding: "20px",
        }}>
          <button
            type="button"
            aria-label="Cerrar subir comprobante"
            disabled={uploading}
            onClick={() => setShowUploadProof(false)}
            style={{
              position: "absolute",
              inset: 0,
              background: "rgba(0,0,0,0.6)",
              border: "none",
              padding: 0,
              margin: 0,
              cursor: uploading ? "not-allowed" : "pointer",
            }}
          />
          <div className="card" style={{ maxWidth: "480px", width: "100%", padding: "32px", position: "relative", zIndex: 1 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
              <h3 style={{ fontSize: "1.25rem", fontWeight: 700 }}>📤 Subir Comprobante</h3>
              <button type="button" onClick={() => !uploading && setShowUploadProof(false)} style={{ background: "none", border: "none", fontSize: "1.5rem", cursor: "pointer", color: "var(--color-text-muted)" }}>×</button>
            </div>

            {uploadSuccess ? (
              <div style={{ textAlign: "center" }}>
                <div style={{ fontSize: "3rem", marginBottom: "16px" }}>✅</div>
                <h4 style={{ fontWeight: 600, marginBottom: "8px" }}>¡Comprobante enviado!</h4>
                <p style={{ color: "var(--color-text-muted)", marginBottom: "24px", fontSize: "0.875rem" }}>
                  Tu pago será revisado por un administrador. Te notificaremos cuando sea aprobado.
                </p>
                <button type="button" className="btn btn-primary" style={{ width: "100%" }} onClick={() => setShowUploadProof(false)}>
                  Cerrar
                </button>
              </div>
            ) : (
              <div>
                {/* Plan selector */}
                <div style={{ marginBottom: "16px" }}>
                  <p style={{ fontSize: "0.875rem", fontWeight: 600, marginBottom: "8px" }}>Plan de pago</p>
                  <div style={{ display: "flex", gap: "12px" }}>
                    <label style={{ flex: 1, cursor: "pointer", display: "flex", alignItems: "center", gap: "8px", padding: "10px", borderRadius: "8px", border: paymentPlan === "monthly" ? "2px solid var(--color-primary)" : "1px solid var(--color-border)", background: paymentPlan === "monthly" ? "rgba(99,102,241,0.08)" : "transparent" }}>
                      <input
                        type="radio"
                        name="upload-plan"
                        value="monthly"
                        checked={paymentPlan === "monthly"}
                        onChange={() => setPaymentPlan("monthly")}
                      />
                      <span style={{ fontWeight: 500 }}>Mensual</span>
                    </label>
                    <label style={{ flex: 1, cursor: "pointer", display: "flex", alignItems: "center", gap: "8px", padding: "10px", borderRadius: "8px", border: paymentPlan === "full" ? "2px solid var(--color-primary)" : "1px solid var(--color-border)", background: paymentPlan === "full" ? "rgba(99,102,241,0.08)" : "transparent" }}>
                      <input
                        type="radio"
                        name="upload-plan"
                        value="full"
                        checked={paymentPlan === "full"}
                        onChange={() => setPaymentPlan("full")}
                      />
                      <span style={{ fontWeight: 500 }}>Completo</span>
                    </label>
                  </div>
                  <p style={{ fontSize: "0.875rem", color: "var(--color-text-muted)", marginTop: "8px" }}>
                    Monto esperado: <strong>{course ? formatCurrency(expectedAmount(), course.currency) : "—"}</strong>
                  </p>
                </div>

                <p style={{ fontSize: "0.875rem", color: "var(--color-text-muted)", marginBottom: "16px" }}>
                  Sube una imagen de tu comprobante de pago para <strong>{course.title}</strong>.
                </p>

                <input
                  id="proof-file-input"
                  type="file"
                  accept=".jpg,.jpeg,.png"
                  style={{ display: "none" }}
                  onChange={handleFileChange}
                />

                <button
                  type="button"
                  ref={dropRef}
                  style={{
                    border: `2px dashed ${isDragging ? "var(--color-primary)" : "var(--color-border)"}`,
                    borderRadius: "12px",
                    padding: "32px",
                    textAlign: "center",
                    marginBottom: "16px",
                    cursor: "pointer",
                    width: "100%",
                    appearance: "none",
                    background: isDragging ? "rgba(99,102,241,0.1)" : selectedFile ? "rgba(99,102,241,0.05)" : "transparent",
                    transition: "background 0.2s, border-color 0.2s",
                  }}
                  onClick={() => document.getElementById("proof-file-input")?.click()}
                  onDragEnter={handleDragEnter}
                  onDragLeave={handleDragLeave}
                  onDragOver={handleDragOver}
                  onDrop={handleDrop}
                >
                  {isDragging ? (
                    <>
                      <span style={{ display: "block", fontSize: "2rem", marginBottom: "8px" }}>📥</span>
                      <span style={{ display: "block", fontWeight: 600, color: "var(--color-primary)" }}>Suelta el archivo aquí</span>
                    </>
                  ) : selectedFile ? (
                    <>
                      <span style={{ display: "block", fontSize: "2rem", marginBottom: "8px" }}>📎</span>
                      <span style={{ display: "block", fontWeight: 600 }}>{selectedFile.name}</span>
                      <span style={{ display: "block", fontSize: "0.8rem", color: "var(--color-text-muted)" }}>
                        {(selectedFile.size / 1024).toFixed(0)} KB — Clic o arrastra para cambiar
                      </span>
                    </>
                  ) : (
                    <>
                      <span style={{ display: "block", fontSize: "2rem", marginBottom: "8px" }}>📁</span>
                      <span style={{ display: "block", fontWeight: 500 }}>Arrastra tu archivo aquí o haz clic para seleccionar</span>
                      <span style={{ display: "block", fontSize: "0.8rem", color: "var(--color-text-muted)" }}>JPG, JPEG o PNG — Máximo 5MB</span>
                    </>
                  )}
                </button>

                {uploadError && (
                  <div style={{
                    background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)",
                    color: "#ef4444", padding: "10px 16px", borderRadius: "8px",
                    fontSize: "0.875rem", marginBottom: "16px",
                  }}>
                    {uploadError}
                  </div>
                )}

                <button
                  className="btn btn-primary"
                  type="button"
                  style={{ width: "100%" }}
                  disabled={!selectedFile || uploading}
                  onClick={handleUpload}
                >
                  {uploading ? "Enviando..." : "Enviar comprobante"}
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
