"use client";

import { useEffect, useState, useCallback } from "react";
import { getUser, isAuthenticated, clearAuth } from "@/lib/auth";
import type { User } from "@/types";

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isAuthenticated()) {
      setUser(getUser());
    }
    setLoading(false);
  }, []);

  const logout = useCallback(() => {
    clearAuth();
    setUser(null);
    globalThis.location.href = "/login";
  }, []);

  const hasRole = useCallback(
    (role: string) => user?.roles?.includes(role) ?? false,
    [user]
  );

  return {
    user,
    loading,
    isAuthenticated: !!user,
    hasRole,
    isAdmin: hasRole("admin"),
    isTeacher: hasRole("teacher"),
    isStudent: hasRole("student"),
    logout,
  };
}
