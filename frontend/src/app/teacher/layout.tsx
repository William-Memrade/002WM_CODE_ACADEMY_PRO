"use client";
import DashboardLayout from "@/components/layout/DashboardLayout";

const TEACHER_NAV = [
  { label: "Dashboard", href: "/teacher/dashboard", icon: "📊" },
  { label: "Mis Clases", href: "/teacher/classes", icon: "🏫" },
  { label: "Mis Cursos", href: "/teacher/courses", icon: "📚" },
  { label: "Alumnos", href: "/teacher/students", icon: "👥" },
];

export default function TeacherLayout({ children }: { children: React.ReactNode }) {
  return <DashboardLayout title="Panel Docente" subtitle="Panel Docente" items={TEACHER_NAV}>{children}</DashboardLayout>;
}
