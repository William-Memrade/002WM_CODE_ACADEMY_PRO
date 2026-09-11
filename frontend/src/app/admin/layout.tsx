"use client";
import DashboardLayout from "@/components/layout/DashboardLayout";
import ProtectedRoute from "@/components/ui/ProtectedRoute";

const ADMIN_NAV = [
  { label: "Dashboard", href: "/admin/dashboard", icon: "📊" },
  { label: "Usuarios", href: "/admin/users", icon: "👤" },
  { label: "Cursos", href: "/admin/courses", icon: "📚" },
  { label: "Clases", href: "/admin/classes", icon: "🏫" },
  { label: "Docentes", href: "/admin/teachers", icon: "👨‍🏫" },
  { label: "Alumnos", href: "/admin/students", icon: "👥" },
  { label: "Pagos", href: "/admin/payments", icon: "💳" },
  { label: "Certificados", href: "/admin/certificates", icon: "📜" },
  { label: "Categorías", href: "/admin/categories", icon: "🏷️" },
  { label: "Feedback", href: "/admin/feedback", icon: "💬" },
  { label: "Auditoría", href: "/admin/audit", icon: "🔍" },
  { label: "Feature Flags", href: "/admin/feature-flags", icon: "🚩" },
  { label: "Configuración", href: "/admin/settings", icon: "⚙️" },
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <ProtectedRoute allowedRoles={["admin"]}>
      <DashboardLayout title="Panel Admin" subtitle="Administración" items={ADMIN_NAV}>
        {children}
      </DashboardLayout>
    </ProtectedRoute>
  );
}
