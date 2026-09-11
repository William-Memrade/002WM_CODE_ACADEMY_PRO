// CoursesPage — updated 2026-05-04
"use client";
import { useEffect, useState, useCallback, useRef } from "react";
import Link from "next/link";
import { isAuthenticated, getUser, logout } from "@/lib/auth";
import { formatCurrency } from "@/lib/currency";
import { usePlatformSettings } from "@/hooks/usePlatformSettings";

interface CourseItem {
  id: string;
  title: string;
  slug: string;
  short_description: string | null;
  thumbnail_url: string | null;
  price: number;
  currency: string;
  level: string;
  duration_hours: number | null;
  is_featured: boolean;
  teacher: { first_name: string; last_name: string } | null;
  category: { name: string; slug: string } | null;
  duration_months: number | null;
  monthly_price?: number;
  full_payment_price?: number;
  full_payment_discount_pct?: number;
  has_available_classes?: boolean;
}

const LEVEL_LABELS: Record<string, string> = {
  beginner: "Principiante",
  intermediate: "Intermedio",
  advanced: "Avanzado",
};

const LEVEL_COLORS: Record<string, string> = {
  beginner: "#22c55e",
  intermediate: "#f59e0b",
  advanced: "#ef4444",
};

export default function CoursesPage() {
  const [courses, setCourses] = useState<CourseItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState("");
  const [level, setLevel] = useState("");
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [categories, setCategories] = useState<{ name: string; slug: string }[]>([]);
  const abortRef = useRef<AbortController | null>(null);

  // Auth state
  const [authed, setAuthed] = useState(false);
  const [user, setUser] = useState<{ first_name: string; roles: string[] } | null>(null);
  const { settings } = usePlatformSettings();

  useEffect(() => {
    setAuthed(isAuthenticated());
    setUser(getUser());
  }, []);

  // Fetch categories once
  useEffect(() => {
    fetch("/api/v1/courses/categories")
      .then((r) => r.json())
      .then(setCategories)
      .catch(() => {});
  }, []);

  // Debounce search input — 400ms delay
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearch(search), 400);
    return () => clearTimeout(timer);
  }, [search]);

  // Fetch courses when filters change (using debounced search)
  const fetchCourses = useCallback(async () => {
    // Cancel previous in-flight request
    if (abortRef.current) abortRef.current.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setLoading(true);
    const params = new URLSearchParams();
    if (category) params.set("category", category);
    if (level) params.set("level", level);
    if (debouncedSearch) params.set("search", debouncedSearch);

    try {
      const res = await fetch(`/api/v1/courses?${params.toString()}`, {
        signal: controller.signal,
      });
      const data = await res.json();
      setCourses(data.items || []);
    } catch (err: any) {
      if (err.name !== "AbortError") setCourses([]);
    } finally {
      setLoading(false);
    }
  }, [category, level, debouncedSearch]);

  useEffect(() => {
    fetchCourses();
  }, [fetchCourses]);

  return (
    <div style={{ minHeight: "100vh", background: "var(--color-bg)" }}>
      {/* Header — auth-aware */}
      <nav style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "16px 32px", borderBottom: "1px solid var(--color-border)" }}>
        <Link href="/" style={{ fontWeight: 700, fontSize: "1.125rem", textDecoration: "none", color: "var(--color-text)" }}>🎓 {settings.platform_name}</Link>
        <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
          {authed ? (
            <>
              <span style={{ fontSize: "0.875rem", color: "var(--color-text-muted)" }}>
                Hola, <strong>{user?.first_name}</strong>
              </span>
              <button
                className="btn btn-secondary btn-sm"
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

      <div style={{ maxWidth: "1200px", margin: "0 auto", padding: "32px 24px" }}>
        <h1 style={{ fontSize: "2rem", fontWeight: 700, marginBottom: "8px" }}>Catálogo de Cursos</h1>
        <p style={{ color: "var(--color-text-muted)", marginBottom: "32px" }}>
          Explora nuestros cursos de programación y tecnología.
        </p>

        {/* Filters */}
        <div style={{ display: "flex", gap: "12px", marginBottom: "32px", flexWrap: "wrap" }}>
          <input
            className="input"
            placeholder="Buscar cursos..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ maxWidth: "300px" }}
          />
          <select className="input" value={category} onChange={(e) => setCategory(e.target.value)} style={{ maxWidth: "200px" }}>
            <option value="">Todas las categorías</option>
            {categories.map((c) => (
              <option key={c.slug} value={c.slug}>{c.name}</option>
            ))}
          </select>
          <select className="input" value={level} onChange={(e) => setLevel(e.target.value)} style={{ maxWidth: "180px" }}>
            <option value="">Todos los niveles</option>
            <option value="beginner">Principiante</option>
            <option value="intermediate">Intermedio</option>
            <option value="advanced">Avanzado</option>
          </select>
        </div>

        {/* Course Grid */}
        {loading ? (
          <div style={{ textAlign: "center", padding: "60px", color: "var(--color-text-muted)" }}>
            Cargando cursos...
          </div>
        ) : courses.length === 0 ? (
          <div style={{ textAlign: "center", padding: "60px", color: "var(--color-text-muted)" }}>
            No se encontraron cursos.
          </div>
        ) : (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: "24px" }}>
            {courses.map((course) => (
              <Link key={course.id} href={`/courses/${course.slug}`} style={{ textDecoration: "none" }}>
                <div
                  className="card"
                  style={{
                    height: "100%",
                    transition: "transform 0.2s, box-shadow 0.2s",
                    cursor: "pointer",
                  }}
                  onMouseEnter={(e) => {
                    (e.currentTarget as HTMLDivElement).style.transform = "translateY(-4px)";
                    (e.currentTarget as HTMLDivElement).style.boxShadow = "0 8px 30px rgba(0,0,0,0.12)";
                  }}
                  onMouseLeave={(e) => {
                    (e.currentTarget as HTMLDivElement).style.transform = "translateY(0)";
                    (e.currentTarget as HTMLDivElement).style.boxShadow = "";
                  }}
                >
                  {/* Gradient placeholder for thumbnail */}
                  <div
                    style={{
                      height: "140px",
                      borderRadius: "8px 8px 0 0",
                      background: `linear-gradient(135deg, ${
                        course.level === "advanced" ? "#7c3aed, #ec4899" :
                        course.level === "intermediate" ? "#2563eb, #06b6d4" :
                        "#10b981, #3b82f6"
                      })`,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      marginBottom: "16px",
                    }}
                  >
                    {course.is_featured && (
                      <span style={{ background: "rgba(255,255,255,0.2)", padding: "4px 12px", borderRadius: "20px", color: "#fff", fontSize: "0.75rem", fontWeight: 600 }}>
                        ⭐ Destacado
                      </span>
                    )}
                  </div>

                  <div style={{ padding: "0 16px 16px" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                      <span style={{
                        fontSize: "0.7rem",
                        fontWeight: 600,
                        padding: "2px 8px",
                        borderRadius: "4px",
                        background: `${LEVEL_COLORS[course.level]}22`,
                        color: LEVEL_COLORS[course.level],
                      }}>
                        {LEVEL_LABELS[course.level] || course.level}
                      </span>
                      {course.category && (
                        <span style={{ fontSize: "0.7rem", color: "var(--color-text-muted)" }}>
                          {course.category.name}
                        </span>
                      )}
                    </div>

                    <h3 style={{ fontSize: "1.125rem", fontWeight: 600, marginBottom: "8px", color: "var(--color-text)" }}>
                      {course.title}
                    </h3>
                    <p style={{ fontSize: "0.85rem", color: "var(--color-text-muted)", marginBottom: "16px", lineHeight: 1.5 }}>
                      {course.short_description}
                    </p>

                    <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <span style={{ fontSize: "1.25rem", fontWeight: 700, color: "var(--color-primary)" }}>
                          {formatCurrency(course.price, course.currency)}
                        </span>
                        {course.duration_hours && (
                          <span style={{ fontSize: "0.8rem", color: "var(--color-text-muted)" }}>
                            {course.duration_hours}h
                          </span>
                        )}
                      </div>

                      {course.monthly_price != null && course.duration_months != null && (
                        <span style={{ fontSize: "0.8rem", color: "var(--color-text-muted)" }}>
                          Desde {formatCurrency(course.monthly_price, course.currency)}/mes · {course.duration_months} meses
                        </span>
                      )}

                      {course.full_payment_price != null && course.full_payment_discount_pct != null && course.full_payment_discount_pct > 0 && (
                        <span style={{ fontSize: "0.8rem", color: "#22c55e", fontWeight: 500 }}>
                          {formatCurrency(course.full_payment_price, course.currency)} pago completo ({course.full_payment_discount_pct}% desc.)
                        </span>
                      )}

                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "4px" }}>
                        {course.has_available_classes === true && (
                          <span style={{ fontSize: "0.75rem", color: "#22c55e", fontWeight: 600 }}>
                            ✅ Cupos disponibles
                          </span>
                        )}
                        {course.has_available_classes === false && (
                          <span style={{ fontSize: "0.75rem", color: "#ef4444", fontWeight: 600 }}>
                            ⛔ Sin cupos
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
