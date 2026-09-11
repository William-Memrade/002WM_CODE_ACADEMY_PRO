/**
 * CodeAcademy Pro — Auth Utilities
 * Client-side authentication helpers.
 */

import { api } from "./api";
import type { TokenResponse, User } from "@/types";

const TOKEN_KEY = "access_token";
const REFRESH_KEY = "refresh_token";
const USER_KEY = "user";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function getUser(): User | null {
  if (typeof window === "undefined") return null;
  const data = localStorage.getItem(USER_KEY);
  return data ? JSON.parse(data) : null;
}

export function saveAuth(data: TokenResponse): void {
  localStorage.setItem(TOKEN_KEY, data.access_token);
  localStorage.setItem(REFRESH_KEY, data.refresh_token);
  localStorage.setItem(USER_KEY, JSON.stringify(data.user));
}

export function clearAuth(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
  localStorage.removeItem(USER_KEY);
}

export function isAuthenticated(): boolean {
  return !!getToken();
}

export function hasRole(role: string): boolean {
  const user = getUser();
  return user?.roles?.includes(role) ?? false;
}

export function redirectByRole(): string {
  if (hasRole("admin")) return "/admin/dashboard";
  if (hasRole("teacher")) return "/teacher/dashboard";
  if (hasRole("student")) return "/student/dashboard";
  return "/courses";
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  const data = await api.post<TokenResponse>("/auth/login", { email, password });
  saveAuth(data);
  return data;
}

export async function register(formData: {
  email: string;
  username: string;
  password: string;
  first_name: string;
  last_name: string;
}) {
  return api.post("/auth/register", formData);
}

export async function logout(): Promise<void> {
  try {
    await api.post("/auth/logout");
  } finally {
    clearAuth();
    window.location.href = "/login";
  }
}
