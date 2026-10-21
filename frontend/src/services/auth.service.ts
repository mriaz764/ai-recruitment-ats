import { apiClient } from "@/lib/api";
import { User, AuthToken, LoginRequest, RegisterRequest } from "@/types/api";

export const authService = {
  async login(credentials: LoginRequest): Promise<AuthToken> {
    const formData = new URLSearchParams();
    formData.append("username", credentials.username);
    formData.append("password", credentials.password);

    return apiClient.post<AuthToken>("/auth/token", formData);
  },

  async register(data: RegisterRequest): Promise<User> {
    return apiClient.post<User>("/auth/register", data);
  },

  async getCurrentUser(): Promise<User> {
    return apiClient.get<User>("/auth/me");
  },
};