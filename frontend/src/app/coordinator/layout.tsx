"use client";

import DashboardLayout from "@/components/layout/DashboardLayout";
import ProtectedRoute from "@/components/ui/ProtectedRoute";

const COORDINATOR_NAV = [
  { label: "Dashboard", href: "/coordinator/dashboard", icon: "📊" },
  { label: "Clases", href: "/coordinator/classes", icon: "📚" },
  { label: "Pagos pendientes", href: "/coordinator/payments", icon: "💳" },
];

export default function CoordinatorLayout({ children }: { children: React.ReactNode }) {
  return (
    <ProtectedRoute allowedRoles={["coordinator"]}>
      <DashboardLayout title="Panel Coordinador" subtitle="Coordinación" items={COORDINATOR_NAV}>
        {children}
      </DashboardLayout>
    </ProtectedRoute>
  );
}
