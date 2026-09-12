/**
 * CodeAcademy Pro — Admin Data Hooks
 * Custom hooks for all admin CRUD operations.
 */
"use client";

import { useState, useEffect, useCallback } from "react";
import { api } from "@/lib/api";
import { toast } from "@/components/ui/Toast";

// ── Types ─────────────────────────────────────────────────────────────────────

export interface AdminCourse {
  id: string; title: string; slug: string; description?: string; short_description?: string | null;
  price: number; currency: string;
  level: string; is_active: boolean; is_featured: boolean; duration_hours: number | null;
  teacher?: { id: string; first_name: string; last_name: string } | null;
  category: { id: string; name: string; slug: string } | null;
  duration_months?: number | null;
  full_payment_discount_pct?: number;
}

export interface AdminUser {
  id: string; email: string; username: string; first_name: string; last_name: string;
  status: string; is_blocked: boolean; email_verified: boolean;
  roles: string[]; created_at: string;
}

export interface AdminPayment {
  id: string; enrollment_id: string | null; course_id: string; amount: number; currency: string;
  payment_method: string; status: string; reference_number: string | null;
  reviewed_at: string | null; review_notes: string | null; created_at: string;
  student: { id: string; full_name: string; email: string } | null;
  course: { id: string; title: string; slug: string } | null;
  proofs: { id: string; file_url: string; file_name: string }[];
  payment_plan?: string;
  expected_amount?: number;
  monthly_amount?: number;
  full_amount?: number;
  duration_months?: number;
  course_class_id?: string | null;
}

export interface AdminCategory {
  id: string; name: string; slug: string; description: string | null;
  sort_order: number; is_active: boolean;
}

export interface CourseClassItem {
  id: string;
  course_id: string;
  teacher_id: string | null;
  name: string;
  slug: string;
  schedule_info: string | null;
  days_of_week: string[];
  start_time: string | null;
  end_time: string | null;
  status: string;
  meeting_platform: string | null;
  meeting_url: string | null;
  created_at: string | null;
  updated_at: string | null;
  deleted_at: string | null;
  enrolled_count: number;
  available_slots: number;
  global_max: number;
  teacher_name?: string | null;
  course_title?: string | null;
  has_meeting_link?: boolean;
  recording_platform?: string | null;
  recording_url?: string | null;
  recording_updated_at?: string | null;
  has_recording?: boolean;
}

export interface CourseClassCapacity {
  course_class_id: string;
  global_max: number;
  enrolled_count: number;
  available_slots: number;
  is_full: boolean;
}

export interface AdminMetrics {
  total_students: number; total_teachers: number; total_courses: number;
  active_courses: number; pending_payments: number; total_revenue: number;
  pending_users: number;
}

interface Paginated<T> { items: T[]; total: number; page: number; per_page: number; pages: number; }

// ── useAdminMetrics ───────────────────────────────────────────────────────────

export function useAdminMetrics() {
  const [data, setData] = useState<AdminMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  const fetch_ = useCallback(async () => {
    try {
      setLoading(true);
      const res = await api.get<AdminMetrics>("/users/admin/metrics");
      setData(res);
    } catch { toast.error("Error al cargar métricas"); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { fetch_(); }, [fetch_]);
  return { data, loading, refresh: fetch_ };
}

// ── useAdminCourses ───────────────────────────────────────────────────────────

export function useAdminCourses() {
  const [data, setData] = useState<Paginated<AdminCourse> | null>(null);
  const [loading, setLoading] = useState(true);

  const fetch_ = useCallback(async (page = 1) => {
    try {
      setLoading(true);
      const res = await api.get<Paginated<AdminCourse>>(`/courses/admin/all?page=${page}&per_page=50`);
      setData(res);
    } catch { toast.error("Error al cargar cursos"); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { fetch_(); }, [fetch_]);

  const createCourse = async (payload: object) => {
    const res = await api.post<{ id: string; title: string }>("/courses/", payload);
    toast.success(`Curso "${(res as any).title}" creado`);
    fetch_();
    return res;
  };

  const updateCourse = async (id: string, payload: object) => {
    await api.put(`/courses/${id}`, payload);
    toast.success("Curso actualizado");
    fetch_();
  };

  const toggleActive = async (id: string, active: boolean) => {
    await api.patch(`/courses/${id}/${active ? "activate" : "deactivate"}`);
    toast.success(active ? "Curso activado" : "Curso desactivado");
    fetch_();
  };

  const deleteCourse = async (id: string) => {
    await api.delete(`/courses/${id}`);
    toast.success("Curso eliminado");
    fetch_();
  };

  return { data, loading, refresh: fetch_, createCourse, updateCourse, toggleActive, deleteCourse };
}

// ── useAdminUsers ─────────────────────────────────────────────────────────────

export function useAdminUsers(role?: "student" | "teacher" | "admin") {
  const [data, setData] = useState<Paginated<AdminUser> | null>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);

  const fetch_ = useCallback(async (p = page, q = search) => {
    try {
      setLoading(true);
      const params = new URLSearchParams({ page: String(p), per_page: "20" });
      if (role) params.set("role", role);
      if (q) params.set("search", q);
      const res = await api.get<Paginated<AdminUser>>(`/users/admin/users?${params}`);
      setData(res);
    } catch { toast.error("Error al cargar usuarios"); }
    finally { setLoading(false); }
  }, [role, page, search]);

  useEffect(() => { fetch_(); }, [fetch_]);

  // Debounce search
  useEffect(() => {
    const t = setTimeout(() => { setPage(1); fetch_(1, search); }, 400);
    return () => clearTimeout(t);
  }, [search]);

  const blockUser = async (id: string) => {
    await api.patch(`/users/admin/users/${id}/block`);
    toast.success("Usuario bloqueado");
    fetch_();
  };

  const unblockUser = async (id: string) => {
    await api.patch(`/users/admin/users/${id}/unblock`);
    toast.success("Usuario desbloqueado");
    fetch_();
  };

  const createUser = async (payload: object) => {
    const res = await api.post<{ id: string; email: string }>("/users/admin/users", payload);
    toast.success("Usuario creado correctamente");
    fetch_();
    return res;
  };

  return {
    data, loading, search, setSearch, page, setPage,
    blockUser, unblockUser, createUser, refresh: fetch_,
  };
}

// ── useAdminPayments ──────────────────────────────────────────────────────────

export function useAdminPayments() {
  const [data, setData] = useState<Paginated<AdminPayment> | null>(null);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState<string>("pending");

  const fetch_ = useCallback(async (st = status) => {
    try {
      setLoading(true);
      const params = new URLSearchParams({ per_page: "50" });
      if (st !== "all") params.set("status", st);
      const res = await api.get<Paginated<AdminPayment>>(`/payments/admin/list?${params}`);
      setData(res);
    } catch { toast.error("Error al cargar pagos"); }
    finally { setLoading(false); }
  }, [status]);

  useEffect(() => { fetch_(); }, [fetch_]);

  const approvePayment = async (id: string, notes?: string) => {
    const res = await api.post(`/payments/${id}/approve`, { notes });
    fetch_();
    return res;
  };

  const rejectPayment = async (id: string, notes?: string) => {
    await api.post(`/payments/${id}/reject`, { notes });
    toast.success("Pago rechazado");
    fetch_();
  };

  return { data, loading, status, setStatus, approvePayment, rejectPayment, refresh: fetch_ };
}

// ── useAdminCategories ────────────────────────────────────────────────────────

export function useAdminCategories() {
  const [data, setData] = useState<AdminCategory[]>([]);
  const [loading, setLoading] = useState(true);

  const fetch_ = useCallback(async () => {
    try {
      setLoading(true);
      const res = await api.get<AdminCategory[]>("/courses/categories");
      setData(res);
    } catch { toast.error("Error al cargar categorías"); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { fetch_(); }, [fetch_]);

  const createCategory = async (payload: object) => {
    const res = await api.post<AdminCategory>("/courses/categories", payload);
    toast.success(`Categoría "${(res as any).name}" creada`);
    fetch_();
    return res;
  };

  const updateCategory = async (id: string, payload: object) => {
    await api.put(`/courses/categories/${id}`, payload);
    toast.success("Categoría actualizada");
    fetch_();
  };

  const deleteCategory = async (id: string) => {
    await api.delete(`/courses/categories/${id}`);
    toast.success("Categoría eliminada");
    fetch_();
  };

  return { data, loading, createCategory, updateCategory, deleteCategory, refresh: fetch_ };
}

// ── useAdminCourseClasses ───────────────────────────────────────────────────

export function useAdminCourseClasses(courseId: string) {
  const [data, setData] = useState<CourseClassItem[]>([]);
  const [loading, setLoading] = useState(true);

  const fetch_ = useCallback(async () => {
    try {
      setLoading(true);
      const res = await api.get<{ items: CourseClassItem[] }>(`/courses/${courseId}/classes`);
      setData(res.items ?? []);
    } catch { toast.error("Error al cargar clases"); }
    finally { setLoading(false); }
  }, [courseId]);

  useEffect(() => { fetch_(); }, [fetch_]);

  const createClass = async (payload: object) => {
    const res = await api.post<CourseClassItem>(`/courses/${courseId}/classes`, payload);
    toast.success(`Clase "${res.name}" creada`);
    fetch_();
    return res;
  };

  const updateClass = async (classId: string, payload: object) => {
    const res = await api.patch<CourseClassItem>(`/course-classes/${classId}`, payload);
    toast.success("Clase actualizada");
    fetch_();
    return res;
  };

  const assignTeacher = async (classId: string, teacherId: string) => {
    const res = await api.patch<CourseClassItem>(`/course-classes/${classId}/assign-teacher`, { teacher_id: teacherId });
    toast.success("Docente asignado");
    fetch_();
    return res;
  };

  const getCapacity = async (classId: string) => {
    const res = await api.get<CourseClassCapacity>(`/course-classes/${classId}/capacity`);
    return res;
  };

  return { data, loading, refresh: fetch_, createClass, updateClass, assignTeacher, getCapacity };
}

// ── useAdminTeachers (perfiles de docente: `teachers.id`, no el id de usuario) ─

export interface TeacherOption {
  id: string;
  user_id: string;
  first_name: string;
  last_name: string;
  email: string;
}

/**
 * Docentes activos para asignarlos a un curso o a una clase.
 *
 * Ojo: `id` es el id del PERFIL docente (`teachers.id`), que es lo que esperan
 * `courses.teacher_id` y `course_classes.teacher_id`; el id de usuario no sirve.
 */
export function useAdminTeachers() {
  const [data, setData] = useState<TeacherOption[]>([]);
  const [loading, setLoading] = useState(true);

  const fetch_ = useCallback(async () => {
    try {
      setLoading(true);
      const res = await api.get<{ items: TeacherOption[] }>("/teachers");
      setData(res.items ?? []);
    } catch { toast.error("Error al cargar docentes"); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { fetch_(); }, [fetch_]);
  return { data, loading, refresh: fetch_ };
}

/** Nombre para mostrar de un docente ("Sin asignar" cuando no hay). */
export function teacherLabel(teacher?: { first_name: string; last_name: string } | null) {
  if (!teacher) return "Sin asignar";
  return `${teacher.first_name} ${teacher.last_name}`.trim();
}

// ── useCreateClass (alta de clase para un curso cualquiera) ──────────────────

/**
 * Crea una clase en un curso y, si se indica, le asigna el docente.
 *
 * `POST /courses/{course_id}/classes` no acepta `teacher_id`, así que la asignación va
 * en un segundo paso con `PATCH /course-classes/{id}/assign-teacher`.
 */
export function useCreateClass() {
  const [saving, setSaving] = useState(false);

  const createClassInCourse = async (
    courseId: string,
    payload: object,
    teacherId?: string
  ): Promise<CourseClassItem> => {
    setSaving(true);
    try {
      const created = await api.post<CourseClassItem>(`/courses/${courseId}/classes`, payload);
      if (teacherId) {
        await api.patch(`/course-classes/${created.id}/assign-teacher`, { teacher_id: teacherId });
      }
      toast.success(`Clase "${created.name}" creada`);
      return created;
    } finally {
      setSaving(false);
    }
  };

  return { createClassInCourse, saving };
}

// ── useClasses (general class listing for admin/coordinator) ────────────────

export type ClassFilter = "today" | "all" | "without_teacher" | "available_slots" | "missing_link" | "inactive" | "cancelled" | "deleted";

export function useClasses(filter?: ClassFilter) {
  const [data, setData] = useState<CourseClassItem[]>([]);
  const [loading, setLoading] = useState(true);

  const fetch_ = useCallback(async () => {
    try {
      setLoading(true);
      let endpoint = "/course-classes";
      if (filter === "today") {
        endpoint = "/course-classes/today";
      } else {
        const params = new URLSearchParams();
        if (filter === "without_teacher") params.set("without_teacher", "true");
        if (filter === "available_slots") params.set("available_slots", "true");
        if (filter === "missing_link") params.set("missing_link", "true");
        if (filter === "inactive") params.set("status", "inactive");
        if (filter === "cancelled") params.set("status", "cancelled");
        if (filter === "deleted") {
          params.set("include_deleted", "true");
          params.set("status", "deleted");
        }
        endpoint = `/course-classes?${params.toString()}`;
      }
      const res = await api.get<{ items: CourseClassItem[] }>(endpoint);
      setData(res.items ?? []);
    } catch { toast.error("Error al cargar clases"); }
    finally { setLoading(false); }
  }, [filter]);

  useEffect(() => { fetch_(); }, [fetch_]);

  const updateStatus = async (classId: string, status: string) => {
    await api.patch(`/course-classes/${classId}/status`, { status });
    toast.success(`Estado actualizado a ${status}`);
    fetch_();
  };

  const deleteClass = async (classId: string) => {
    await api.delete(`/course-classes/${classId}`);
    toast.success("Clase eliminada");
    fetch_();
  };

  const updateMeetingLink = async (classId: string, platform: string, url: string) => {
    await api.patch(`/course-classes/${classId}/meeting-link`, { meeting_platform: platform, meeting_url: url });
    toast.success("Enlace actualizado");
    fetch_();
  };

  /** Publica (o quita) la grabación de la clase: URL vacía = retirarla. */
  const updateRecordingLink = async (classId: string, platform: string, url: string) => {
    await api.patch(`/course-classes/${classId}/recording-link`, {
      recording_platform: platform || null,
      recording_url: url || null,
    });
    toast.success(url ? "Grabación publicada" : "Grabación retirada");
    fetch_();
  };

  return { data, loading, refresh: fetch_, updateStatus, deleteClass, updateMeetingLink, updateRecordingLink };
}

// ── useTeacherClasses ─────────────────────────────────────────────────────────

export function useTeacherClasses() {
  const [data, setData] = useState<CourseClassItem[]>([]);
  const [loading, setLoading] = useState(true);

  const fetch_ = useCallback(async () => {
    try {
      setLoading(true);
      const res = await api.get<{ items: CourseClassItem[] }>("/teachers/me/classes");
      setData(res.items ?? []);
    } catch { toast.error("Error al cargar clases"); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { fetch_(); }, [fetch_]);

  const updateMeetingLink = async (classId: string, platform: string, url: string) => {
    await api.patch(`/course-classes/${classId}/meeting-link`, { meeting_platform: platform, meeting_url: url });
    toast.success("Enlace actualizado");
    fetch_();
  };

  /**
   * Publica (o quita) la grabación de la clase.
   *
   * URL vacía = borrar la grabación publicada.
   */
  const updateRecordingLink = async (classId: string, platform: string, url: string) => {
    await api.patch(`/course-classes/${classId}/recording-link`, {
      recording_platform: platform || null,
      recording_url: url || null,
    });
    toast.success(url ? "Grabación publicada" : "Grabación retirada");
    fetch_();
  };

  return { data, loading, refresh: fetch_, updateMeetingLink, updateRecordingLink };
}

// ── useAuditLogs ────────────────────────────────────────────────────────────

import { AuditLog } from "@/types";

export function useAuditLogs() {
  const [data, setData] = useState<Paginated<AuditLog> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionFilter, setActionFilter] = useState("");
  const [emailFilter, setEmailFilter] = useState("");
  const [debouncedEmail, setDebouncedEmail] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [page, setPage] = useState(1);

  const fetch_ = useCallback(async (p = page) => {
    try {
      setLoading(true);
      setError(null);
      const params = new URLSearchParams({ page: String(p), per_page: "50" });
      if (actionFilter) params.set("action", actionFilter);
      if (debouncedEmail) params.set("actor_email", debouncedEmail);
      if (dateFrom) params.set("date_from", new Date(dateFrom).toISOString());
      if (dateTo) params.set("date_to", new Date(dateTo).toISOString());
      const res = await api.get<Paginated<AuditLog>>(`/audit-logs?${params}`);
      setData(res);
    } catch {
      setError("Error al cargar auditoría");
      toast.error("Error al cargar auditoría");
    } finally {
      setLoading(false);
    }
  }, [actionFilter, debouncedEmail, dateFrom, dateTo, page]);

  useEffect(() => { fetch_(); }, [fetch_]);

  // Debounce email filter (400ms)
  useEffect(() => {
    const t = setTimeout(() => { setPage(1); setDebouncedEmail(emailFilter); }, 400);
    return () => clearTimeout(t);
  }, [emailFilter]);

  // Reset to page 1 when non-email filters change
  useEffect(() => {
    setPage(1);
  }, [actionFilter, dateFrom, dateTo]);

  return {
    data,
    loading,
    error,
    actionFilter,
    setActionFilter,
    emailFilter,
    setEmailFilter,
    dateFrom,
    setDateFrom,
    dateTo,
    setDateTo,
    page,
    setPage,
    refresh: fetch_,
  };
}
