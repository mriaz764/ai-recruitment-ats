import { env } from "@/lib/config/env";

type RequestOptions = RequestInit & {
  auth?: boolean;
};

export const apiClient = {
  async request<T>(
    path: string,
    options: RequestOptions = {},
  ): Promise<T> {
    const { headers, body, ...requestOptions } = options;

    const requestHeaders = new Headers(headers);

    // Auto-set Content-Type to JSON unless sending FormData or URLSearchParams
    if (
      !requestHeaders.has("Content-Type") && 
      !(body instanceof FormData) && 
      !(body instanceof URLSearchParams)
    ) {
      requestHeaders.set("Content-Type", "application/json");
    }

    const url = `${env.NEXT_PUBLIC_API_URL}${path}`;

    const response = await fetch(url, {
      ...requestOptions,
      body: body as BodyInit | null | undefined,
      headers: requestHeaders,
      credentials: "include",
    });

    if (!response.ok) {
      let message = `HTTP ${response.status}: An unexpected error occurred`;

      try {
        const errorBody = await response.json();

        if (errorBody?.detail) {
          if (typeof errorBody.detail === "string") {
            message = errorBody.detail;
          } else if (Array.isArray(errorBody.detail) && errorBody.detail.length > 0) {
            message = errorBody.detail.map((err: { msg: string }) => err.msg).join(", ");
          }
        } else if (typeof errorBody?.message === "string") {
          message = errorBody.message;
        }
      } catch {
        // Keep default status message if body is unparseable
      }

      throw new Error(message);
    }

    if (response.status === 204) {
      return undefined as T;
    }

    return response.json() as Promise<T>;
  },

  get<T>(path: string, options?: RequestOptions) {
    return apiClient.request<T>(path, {
      ...options,
      method: "GET",
    });
  },

  post<T>(path: string, body?: unknown, options?: RequestOptions) {
    const isRawBody = body instanceof FormData || body instanceof URLSearchParams;
    return apiClient.request<T>(path, {
      ...options,
      method: "POST",
      body: isRawBody ? (body as BodyInit) : body !== undefined ? JSON.stringify(body) : undefined,
    });
  },

  put<T>(path: string, body?: unknown, options?: RequestOptions) {
    const isRawBody = body instanceof FormData || body instanceof URLSearchParams;
    return apiClient.request<T>(path, {
      ...options,
      method: "PUT",
      body: isRawBody ? (body as BodyInit) : body !== undefined ? JSON.stringify(body) : undefined,
    });
  },

  delete<T>(path: string, options?: RequestOptions) {
    return apiClient.request<T>(path, {
      ...options,
      method: "DELETE",
    });
  },
};