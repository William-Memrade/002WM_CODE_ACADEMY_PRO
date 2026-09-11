"use client";

import DashboardLayout from "@/components/layout/DashboardLayout";

const STUDENT_NAV = [
  { label: "Dashboard", href: "/student/dashboard", icon: "📊" },
  { label: "Mis Cursos", href: "/student/courses", icon: "📚" },
  { label: "Asistencia", href: "/student/attendance", icon: "✅" },
  { label: "Pagos", href: "/student/payments", icon: "💳" },
  { label: "Certificados", href: "/student/certificates", icon: "📜" },
  { label: "Notificaciones", href: "/student/notifications", icon: "🔔" },
  { label: "Mi Perfil", href: "/student/profile", icon: "👤" },
];

export default function StudentLayout({ children }: { children: React.ReactNode }) {
  return (
    <DashboardLayout title="Panel Alumno" subtitle="Panel Alumno" items={STUDENT_NAV}>
      {children}
    </DashboardLayout>
  );
}
