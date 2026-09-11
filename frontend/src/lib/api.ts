/**
 * CodeAcademy Pro — API Client
 * Centralized fetch wrapper for backend communication.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api/v1";

interface ApiOptions extends RequestInit {
  token?: string;
}

class ApiClient {
  private readonly baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private getToken(): string | null {
    if (globalThis.window === undefined) return null;
    return localStorage.getItem("access_token");
  }

  private async request<T>(endpoint: string, options: ApiOptions = {}): Promise<T> {
    const { token, ...fetchOptions } = options;
    const accessToken = token || this.getToken();

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };

    if (accessToken) {
      headers["Authorization"] = `Bearer ${accessToken}`;
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...fetchOptions,
      headers,
    });

    if (response.status === 401) {
      // Token expired → try refresh
      const refreshed = await this.refreshToken();
      if (refreshed) {
        headers["Authorization"] = `Bearer ${this.getToken()}`;
        const retryResponse = await fetch(`${this.baseUrl}${endpoint}`, {
          ...fetchOptions,
          headers,
        });
        if (!retryResponse.ok) throw new ApiError(retryResponse);
        const retryText = await retryResponse.text();
        if (!retryText) return undefined as unknown as T;
        return JSON.parse(retryText);
      }
      // Refresh failed → redirect to login
      if (globalThis.window !== undefined) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        globalThis.window.location.href = "/login";
      }
    }

    if (!response.ok) {
      throw new ApiError(response);
    }

    const text = await response.text();
    if (!text) return undefined as unknown as T;
    return JSON.parse(text);
  }

  private async refreshToken(): Promise<boolean> {
    const refreshToken = localStorage.getItem("refresh_token");
    if (!refreshToken) return false;

    try {
      const res = await fetch(`${this.baseUrl}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!res.ok) return false;

      const data = await res.json();
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      return true;
    } catch {
      return false;
    }
  }

  // ── Convenience Methods ──────────────────────────────────────────────

  get<T>(endpoint: string, options?: ApiOptions) {
    return this.request<T>(endpoint, { ...options, method: "GET" });
  }

  post<T>(endpoint: string, body?: unknown, options?: ApiOptions) {
    return this.request<T>(endpoint, {
      ...options,
      method: "POST",
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  put<T>(endpoint: string, body?: unknown, options?: ApiOptions) {
    return this.request<T>(endpoint, {
      ...options,
      method: "PUT",
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  patch<T>(endpoint: string, body?: unknown, options?: ApiOptions) {
    return this.request<T>(endpoint, {
      ...options,
      method: "PATCH",
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  delete<T>(endpoint: string, options?: ApiOptions) {
    return this.request<T>(endpoint, { ...options, method: "DELETE" });
  }

  async upload<T>(
    endpoint: string,
    file: File,
    fieldName = "file",
    extraFields?: Record<string, string>
  ): Promise<T> {
    const formData = new FormData();
    formData.append(fieldName, file);

    if (extraFields) {
      for (const [key, value] of Object.entries(extraFields)) {
        formData.append(key, value);
      }
    }

    const accessToken = this.getToken();
    const headers: Record<string, string> = {};
    if (accessToken) headers["Authorization"] = `Bearer ${accessToken}`;

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: "POST",
      headers,
      body: formData,
    });

    if (!response.ok) throw new ApiError(response);
    return response.json();
  }
}

class ApiError extends Error {
  status: number;
  constructor(response: Response) {
    super(`API Error: ${response.status} ${response.statusText}`);
    this.status = response.status;
  }
}

export const api = new ApiClient(API_BASE);
export { ApiError };
