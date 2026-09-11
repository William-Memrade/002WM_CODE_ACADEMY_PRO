/**
 * CodeAcademy Pro — TypeScript Types
 * Shared types matching backend Pydantic schemas.
 */

// ── Users ─────────────────────────────────────────────────────────────────
export interface User {
  id: string;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  avatar_url: string | null;
  roles: string[];
  status?: string;
  force_change_password?: boolean;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

// ── Courses ───────────────────────────────────────────────────────────────
export interface Course {
  id: string;
  title: string;
  slug: string;
  description: string;
  short_description: string | null;
  thumbnail_url: string | null;
  category: Category | null;
  teacher?: TeacherBrief | null;
  price: number;
  currency: string;
  level: "beginner" | "intermediate" | "advanced";
  duration_hours: number | null;
  is_active: boolean;
  is_featured: boolean;
  max_students?: number | null;
  starts_at?: string | null;
  ends_at?: string | null;
  duration_months: number | null;
  full_payment_discount_pct: number;
  monthly_price?: number;
  full_payment_price?: number;
  total_classes_count?: number;
  total_available_slots?: number;
  has_available_classes?: boolean;
  effective_max_students?: number;
  enrolled_count?: number;
  available_slots?: number;
  created_at: string;
}

export interface CourseListItem {
  id: string;
  title: string;
  slug: string;
  short_description: string | null;
  thumbnail_url: string | null;
  price: number;
  level: string;
  duration_hours: number | null;
  is_featured: boolean;
  avg_rating?: number;
  total_students?: number;
}

export interface Category {
  id: string;
  name: string;
  slug: string;
}

export interface TeacherBrief {
  id: string;
  first_name: string;
  last_name: string;
  avatar_url: string | null;
}

// ── Modules & Lessons ─────────────────────────────────────────────────────
export interface Module {
  id: string;
  title: string;
  description: string | null;
  sort_order: number;
  is_published: boolean;
  lessons: Lesson[];
}

export interface Lesson {
  id: string;
  title: string;
  description: string | null;
  duration_minutes: number | null;
  is_free: boolean;
  is_published: boolean;
}

// ── Enrollments & Payments ────────────────────────────────────────────────
export interface CourseClass {
  id: string;
  course_id: string;
  teacher_id: string | null;
  created_by: string | null;
  name: string;
  slug: string;
  schedule_info: string | null;
  days_of_week: string[];
  start_time: string | null;
  end_time: string | null;
  status: string;
  meeting_platform: string | null;
  meeting_url: string | null;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
  enrolled_count?: number;
  available_slots?: number;
  global_max?: number;
  teacher_name?: string | null;
  course_title?: string | null;
  has_meeting_link?: boolean;
}

export interface AttendanceRecord {
  id: string;
  course_class_id: string;
  student_id: string;
  teacher_id: string;
  session_date: string;
  status: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface Enrollment {
  id: string;
  course_id: string;
  status: string;
  progress_percentage: number;
  enrolled_at: string;
  approved_at: string | null;
  completed_at: string | null;
  course?: CourseListItem;
  course_class_id?: string | null;
}

export interface Payment {
  id: string;
  enrollment_id: string;
  amount: number;
  currency: string;
  status: string;
  reference_number: string | null;
  reviewed_at: string | null;
  created_at: string;
  payment_plan?: string;
  expected_amount?: number;
  monthly_amount?: number;
  full_amount?: number;
  duration_months?: number;
  course_class_id?: string | null;
}

// ── Notifications ─────────────────────────────────────────────────────────
export interface Notification {
  id: string;
  title: string;
  message: string;
  type: string;
  is_read: boolean;
  created_at: string;
}

// ── Dashboard Metrics ─────────────────────────────────────────────────────
export interface AdminMetrics {
  total_students: number;
  total_teachers: number;
  total_courses: number;
  active_courses: number;
  total_revenue: number;
  pending_payments: number;
}

// ── Paginated Response ────────────────────────────────────────────────────
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

// ── Audit Logs ──────────────────────────────────────────────────────────────
export interface AuditLog {
  id: string;
  created_at: string;
  actor_user_id: string | null;
  actor_email: string | null;
  action: string;
  entity_type: string | null;
  entity_id: string | null;
  entity_label: string | null;
  ip_address: string | null;
  user_agent: string | null;
  metadata: Record<string, unknown> | null;
}
