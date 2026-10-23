"use client";

import React, {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";
import { useRouter } from "next/navigation";
import { authService } from "@/services/auth.service";
import { User, LoginRequest, RegisterRequest } from "@/types";
import { ROUTES } from "@/lib/routes";
interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
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
  // Ref updates synchronously to block Strict Mode duplicate calls
  const initialized = useRef(false);
  // Restore authenticated session on initial mount via HttpOnly cookie
  useEffect(() => {
    // 1. Synchronously prevent double execution in React Strict Mode
    if (initialized.current) return;
    initialized.current = true;
    // If user state is already populated, do not refetch
    if (user) return;
    const restoreSession = async () => {
      getCurrentUser();
    };

    restoreSession();
  }, []); // Empty dependency array guarantees this runs ONLY once on app mount
  const getCurrentUser = async () => {
    try {
      const currentUser = await authService.getCurrentUser();
      setUser(currentUser);
    } catch (error) {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (credentials: LoginRequest) => {
    setIsLoading(true);
    try {
      // 1. API endpoint sets HttpOnly access_token & csrf_token cookies
      const currentUser = await authService.login(credentials);
      // 2. Update client user state
      setUser(currentUser);
      // 3. Refresh App Router cache so middleware & server components see new cookies
      router.refresh();
      router.push(ROUTES.DASHBOARD.HOME);
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
    } catch (error) {
      // Clear state even if network call fails
      console.error("Logout failed on server:", error);
    } finally {
      // 2. Reset local state
      initialized.current = false;
      setUser(null);
      setIsLoading(false);
      window.location.href = ROUTES.AUTH.LOGIN;
      //router.refresh();
      //router.replace(ROUTES.AUTH.LOGIN);
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
