"use client";

import { ReactNode, useEffect, useMemo } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";

interface ProtectedRouteProps {
  children: ReactNode;
  allowedRoles: string[];
}

export default function ProtectedRoute({ children, allowedRoles }: ProtectedRouteProps) {
  const router = useRouter();
  const { loading, isAuthenticated, hasRole } = useAuth();

  const isAuthorized = useMemo(() => {
    if (allowedRoles.length === 0) return true;
    return allowedRoles.some((role) => hasRole(role));
  }, [allowedRoles, hasRole]);

  useEffect(() => {
    if (loading) return;

    if (!isAuthenticated) {
      router.replace("/login");
      return;
    }

    if (!isAuthorized) {
      router.replace("/unauthorized");
    }
  }, [loading, isAuthenticated, isAuthorized, router]);

  if (loading || !isAuthenticated || !isAuthorized) {
    return null;
  }

  return <>{children}</>;
}
