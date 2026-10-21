"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import Cookies from "js-cookie";
import { useRouter } from "next/navigation";
import { authService } from "@/services/auth.service";
import { User, LoginRequest, RegisterRequest } from "@/types";

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const router = useRouter();

  // Restore authenticated session on initial mount
  useEffect(() => {
    const restoreSession = async () => {
      const storedToken = Cookies.get("access_token");
      if (!storedToken) {
        setIsLoading(false);
        return;
      }

      setToken(storedToken);
      try {
        const currentUser = await authService.getCurrentUser();
        setUser(currentUser);
      } catch {
        // Clear invalid token if session restoration fails
        Cookies.remove("access_token");
        setToken(null);
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    restoreSession();
  }, []);

  const login = async (credentials: LoginRequest) => {
    setIsLoading(true);
    try {
      const tokenData = await authService.login(credentials);

      // Store JWT in cookies (7 days expiry, accessible by Next.js Edge Middleware)
      Cookies.set("access_token", tokenData.access_token, {
        expires: 7,
        sameSite: "lax",
      });
      setToken(tokenData.access_token);

      // Fetch user profile & tenant ID
      const currentUser = await authService.getCurrentUser();
      setUser(currentUser);

      router.push("/dashboard");
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (data: RegisterRequest) => {
    setIsLoading(true);
    try {
      await authService.register(data);
      // Auto-login following successful registration
      await login({ username: data.email, password: data.password });
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    Cookies.remove("access_token");
    setToken(null);
    setUser(null);
    router.push("/login");
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
