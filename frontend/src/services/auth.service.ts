import { apiClient } from "@/lib/api";
import { User, LoginRequest, RegisterRequest } from "@/types";

export const authService = {
  async login(credentials: LoginRequest): Promise<User> {
    return apiClient.post<User>("/auth/login", credentials);
  },

  async register(data: RegisterRequest): Promise<User> {
    return apiClient.post<User>("/auth/register", data);
  },

  async getCurrentUser(): Promise<User> {
    return apiClient.get<User>("/auth/me");
  },
  async logout(): Promise<void> {
    return apiClient.post("/auth/logout");
  },
};