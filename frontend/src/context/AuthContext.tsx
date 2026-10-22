"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { authService } from "@/services/auth.service";
import { User, LoginRequest, RegisterRequest } from "@/types";
import { ROUTES } from "@/lib/routes";
interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginRequest, redirectTo?: string) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const router = useRouter();

  // Restore authenticated session on initial mount via HttpOnly cookie
  useEffect(() => {
    const restoreSession = async () => {
      try {
        // Browser automatically attaches HttpOnly cookie to this fetch
        const currentUser = await authService.getCurrentUser();
        setUser(currentUser);
      } catch {
        // If cookie is missing or invalid, API returns 401
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    restoreSession();
  }, []);

  const login = async (
    credentials: LoginRequest,
    redirectTo = ROUTES.DASHBOARD.HOME,
  ) => {
    setIsLoading(true);
    try {
      // 1. API endpoint sets HttpOnly access_token & csrf_token cookies
      const currentUser = await authService.login(credentials);
      // 2. Update client user state
      setUser(currentUser);
      // 3. Refresh App Router cache so middleware & server components see new cookies
      router.refresh();
      router.push(redirectTo);
    } catch (error) {
      setUser(null);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (data: RegisterRequest) => {
    setIsLoading(true);
    try {
      const currentUser = await authService.register(data);
      // 2. Update client user state
      setUser(currentUser);
      // 3. Refresh App Router cache so middleware & server components see new cookies
      router.refresh();
      router.push(ROUTES.DASHBOARD.HOME);
    } catch (error) {
      setIsLoading(false);
      throw error;
    }
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      // 1. Instruct server to expire/clear HttpOnly cookies via HTTP headers
      await authService.logout();
    } catch {
      // Clear state even if network call fails
    } finally {
      setUser(null);
      router.refresh();
      router.push("/login");
      setIsLoading(false);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
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
