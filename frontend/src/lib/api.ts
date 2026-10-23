import { env } from "@/lib/config/env";

export interface RequestOptions extends Omit<RequestInit, "body"> {
  body?: unknown;
  params?: Record<string, string | number | boolean | undefined | null>;
}

// Utility to read non-HttpOnly cookie in client runtime
function getCookie(name: string): string | null {
  if (typeof document === "undefined") return null;
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop()?.split(";").shift() ?? null;
  return null;
}

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
    const { params, body, headers: customHeaders, method = "GET", ...customConfig } = options;

    let url = `${this.baseUrl}${endpoint}`;
    if (params) {
      const searchParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          searchParams.append(key, String(value));
        }
      });
      const queryString = searchParams.toString();
      if (queryString) {
        url += url.includes("?") ? `&${queryString}` : `?${queryString}`;
      }
    }

    const headers = new Headers(customHeaders);

    // Automatically attach CSRF token header for mutation requests
    if (typeof window !== "undefined" && ["POST", "PUT", "PATCH", "DELETE"].includes(method.toUpperCase())) {
      const csrfToken = getCookie("csrf_token");
      if (csrfToken && !headers.has("X-CSRF-Token")) {
        headers.set("X-CSRF-Token", csrfToken);
      }
    }

    let requestBody: BodyInit | undefined;
    if (body !== undefined && body !== null) {
      if (body instanceof FormData || body instanceof URLSearchParams) {
        requestBody = body;
      } else {
        if (!headers.has("Content-Type")) {
          headers.set("Content-Type", "application/json");
        }
        requestBody = JSON.stringify(body);
      }
    }

    const response = await fetch(url, {
      ...customConfig,
      method,
      headers,
      body: requestBody,
      credentials: "include", // Passes HttpOnly auth cookies automatically
    });

    if (!response.ok) {
      let message = `HTTP error! status: ${response.status}`;
      try {
        const errorData = await response.json();
        message = errorData.detail || errorData.message || message;
      } catch {
        // Fallback
      }
      throw new Error(message);
    }

    if (response.status === 204) {
      return undefined as T;
    }

    return response.json() as Promise<T>;
  }

  public get<T>(endpoint: string, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: "GET" });
  }

  public post<T>(endpoint: string, body?: unknown, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: "POST", body });
  }

  public put<T>(endpoint: string, body?: unknown, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: "PUT", body });
  }

  public patch<T>(endpoint: string, body?: unknown, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: "PATCH", body });
  }

  public delete<T>(endpoint: string, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: "DELETE" });
  }
}

export const apiClient = new ApiClient(
  env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"
);