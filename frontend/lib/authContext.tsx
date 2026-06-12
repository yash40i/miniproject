"use client";

import React, { createContext, useEffect, useState } from "react";
import { apiClient, User, AuthToken } from "./api";
import { toast } from "react-toastify";

export interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
  forgotPassword: (email: string) => Promise<void>;
  resetPassword: (token: string, newPassword: string, confirmPassword: string) => Promise<void>;
  verifyResetToken: (token: string) => Promise<{ valid: boolean; email?: string }>;
}

export const AuthContext = createContext<AuthContextType | undefined>(
  undefined
);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check if user is logged in on mount
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      // Check if token exists in localStorage
      if (typeof window !== "undefined") {
        const storedToken = localStorage.getItem("auth_token");
        if (storedToken) {
          setToken(storedToken);
          // Try to get current user
          try {
            const currentUser = await apiClient.getCurrentUser();
            setUser(currentUser);
          } catch (error) {
            // Token is invalid, clear it
            apiClient.clearToken();
            setToken(null);
            setUser(null);
          }
        }
      }
    } catch (error) {
      console.error("Auth check failed:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    try {
      setIsLoading(true);
      const response = await apiClient.login(email, password);
      setToken(response.access_token);

      // Get user info
      const currentUser = await apiClient.getCurrentUser();
      setUser(currentUser);

      toast.success(`Welcome back, ${currentUser.email}!`);
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Login failed";
      toast.error(errorMessage);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const signup = async (
    email: string,
    password: string,
    fullName?: string
  ) => {
    try {
      setIsLoading(true);
      const response = await apiClient.signup(email, password, fullName);
      setToken(response.access_token);

      // Get user info
      const currentUser = await apiClient.getCurrentUser();
      setUser(currentUser);

      toast.success(`Welcome, ${currentUser.email}!`);
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Signup failed";
      toast.error(errorMessage);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    apiClient.logout();
    setUser(null);
    setToken(null);
    toast.info("Logged out successfully");
  };

  const forgotPassword = async (email: string) => {
    try {
      setIsLoading(true);
      const response = await fetch(`/api/auth/forgot-password`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      if (!response.ok) {
        throw new Error("Failed to send reset email");
      }

      toast.success("If an account exists with this email, a password reset link will be sent shortly.");
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Failed to send reset email";
      toast.error(errorMessage);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const verifyResetToken = async (
    token: string
  ): Promise<{ valid: boolean; email?: string }> => {
    try {
      const response = await fetch(
        `/api/auth/verify-reset-token`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ token }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to verify token");
      }

      const data = await response.json();
      return {
        valid: data.valid,
        email: data.email,
      };
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Failed to verify token";
      toast.error(errorMessage);
      throw error;
    }
  };

  const resetPassword = async (
    token: string,
    newPassword: string,
    confirmPassword: string
  ) => {
    try {
      setIsLoading(true);

      if (newPassword !== confirmPassword) {
        throw new Error("Passwords do not match");
      }

      const response = await fetch(
        `/api/auth/reset-password`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            token,
            new_password: newPassword,
            confirm_password: confirmPassword,
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to reset password");
      }

      toast.success("Password has been successfully reset. Please login with your new password.");
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Failed to reset password";
      toast.error(errorMessage);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        isAuthenticated: !!user && !!token,
        login,
        signup,
        logout,
        checkAuth,
        forgotPassword,
        verifyResetToken,
        resetPassword,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
