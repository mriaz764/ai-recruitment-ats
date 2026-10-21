import { env } from "@/lib/config/env";

export interface RequestOptions extends Omit<RequestInit, "body"> {
  body?: any;
  params?: Record<string, string | number | boolean | undefined | null>;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
    const { params, body, headers: customHeaders, ...customConfig } = options;

    let url = `${this.baseUrl}${endpoint}`;

    // Parse and serialize query parameters if present
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

    const headers: HeadersInit = {
      "Content-Type": "application/json",
      ...customHeaders,
    };

    const config: RequestInit = {
      ...customConfig,
      headers,
    };

    if (body) {
      if (body instanceof URLSearchParams || body instanceof FormData) {
        config.body = body;
        if (body instanceof FormData) {
          delete (headers as Record<string, string>)["Content-Type"];
        }
      } else {
        config.body = JSON.stringify(body);
      }
    }

    const response = await fetch(url, config);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.detail || errorData.message || `HTTP error! status: ${response.status}`
      );
    }

    if (response.status === 204) {
      return {} as T;
    }

    return response.json();
  }

  public get<T>(endpoint: string, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: "GET" });
  }

  public post<T>(endpoint: string, body?: any, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: "POST", body });
  }

  public put<T>(endpoint: string, body?: any, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: "PUT", body });
  }

  public patch<T>(endpoint: string, body?: any, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: "PATCH", body });
  }

  public delete<T>(endpoint: string, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: "DELETE" });
  }
}

export const apiClient = new ApiClient(env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1");