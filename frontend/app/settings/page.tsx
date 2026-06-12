"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/useAuth";
import { apiClient } from "@/lib/api";
import {
  Lock,
  Eye,
  EyeOff,
  Save,
  Loader,
  CheckCircle,
  AlertCircle,
} from "lucide-react";
import { motion } from "framer-motion";
import { toast } from "react-toastify";

interface PasswordData {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

interface PasswordStrength {
  score: number;
  label: string;
  color: string;
}

export default function SettingsPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const [passwords, setPasswords] = useState<PasswordData>({
    current_password: "",
    new_password: "",
    confirm_password: "",
  });
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false,
  });
  const [isSaving, setIsSaving] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState<PasswordStrength>({
    score: 0,
    label: "Very Weak",
    color: "bg-red-500",
  });

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/login?from=/settings");
    }
  }, [isAuthenticated, authLoading, router]);

  // Calculate password strength
  useEffect(() => {
    const password = passwords.new_password;
    let score = 0;

    if (password.length >= 8) score++;
    if (password.length >= 12) score++;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++;
    if (/\d/.test(password)) score++;
    if (/[^a-zA-Z\d]/.test(password)) score++;

    const strengths: PasswordStrength[] = [
      {
        score: 0,
        label: "Very Weak",
        color: "bg-red-500",
      },
      {
        score: 1,
        label: "Weak",
        color: "bg-orange-500",
      },
      {
        score: 2,
        label: "Fair",
        color: "bg-yellow-500",
      },
      {
        score: 3,
        label: "Good",
        color: "bg-blue-500",
      },
      {
        score: 4,
        label: "Strong",
        color: "bg-green-500",
      },
      {
        score: 5,
        label: "Very Strong",
        color: "bg-green-600",
      },
    ];

    setPasswordStrength(strengths[score] || strengths[0]);
  }, [passwords.new_password]);

  const validatePasswords = (): boolean => {
    if (!passwords.current_password.trim()) {
      toast.error("Current password is required");
      return false;
    }

    if (passwords.new_password.length < 8) {
      toast.error("New password must be at least 8 characters");
      return false;
    }

    if (passwords.new_password !== passwords.confirm_password) {
      toast.error("New passwords do not match");
      return false;
    }

    if (passwords.current_password === passwords.new_password) {
      toast.error("New password must be different from current password");
      return false;
    }

    return true;
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validatePasswords()) return;

    try {
      setIsSaving(true);
      await apiClient.changePassword({
        current_password: passwords.current_password,
        new_password: passwords.new_password,
        confirm_password: passwords.confirm_password,
      });

      toast.success("Password changed successfully!");
      setPasswords({
        current_password: "",
        new_password: "",
        confirm_password: "",
      });

      // Redirect to profile after 2 seconds
      setTimeout(() => {
        router.push("/profile");
      }, 2000);
    } catch (error) {
      toast.error(
        error instanceof Error ? error.message : "Failed to change password"
      );
    } finally {
      setIsSaving(false);
    }
  };

  if (authLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 py-8 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-white mb-2">Security Settings</h1>
          <p className="text-slate-400">Change your password and manage security</p>
        </motion.div>

        {/* Change Password Card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-slate-800/50 border border-slate-700 rounded-xl p-8 backdrop-blur-sm"
        >
          <div className="flex items-center gap-3 mb-6">
            <Lock className="w-5 h-5 text-blue-400" />
            <h2 className="text-xl font-bold text-white">Change Password</h2>
          </div>

          <form onSubmit={handleChangePassword} className="space-y-6">
            {/* Current Password */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Current Password *
              </label>
              <div className="relative">
                <input
                  type={showPasswords.current ? "text" : "password"}
                  value={passwords.current_password}
                  onChange={(e) =>
                    setPasswords({
                      ...passwords,
                      current_password: e.target.value,
                    })
                  }
                  className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all pr-10"
                  placeholder="Enter your current password"
                />
                <button
                  type="button"
                  onClick={() =>
                    setShowPasswords({
                      ...showPasswords,
                      current: !showPasswords.current,
                    })
                  }
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 hover:text-slate-300"
                >
                  {showPasswords.current ? (
                    <EyeOff className="w-5 h-5" />
                  ) : (
                    <Eye className="w-5 h-5" />
                  )}
                </button>
              </div>
            </div>

            {/* New Password */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                New Password *
              </label>
              <div className="relative">
                <input
                  type={showPasswords.new ? "text" : "password"}
                  value={passwords.new_password}
                  onChange={(e) =>
                    setPasswords({
                      ...passwords,
                      new_password: e.target.value,
                    })
                  }
                  className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all pr-10"
                  placeholder="Enter your new password"
                />
                <button
                  type="button"
                  onClick={() =>
                    setShowPasswords({
                      ...showPasswords,
                      new: !showPasswords.new,
                    })
                  }
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 hover:text-slate-300"
                >
                  {showPasswords.new ? (
                    <EyeOff className="w-5 h-5" />
                  ) : (
                    <Eye className="w-5 h-5" />
                  )}
                </button>
              </div>

              {/* Password Strength Indicator */}
              {passwords.new_password && (
                <div className="mt-3 space-y-2">
                  <div className="flex gap-1">
                    {[...Array(5)].map((_, i) => (
                      <div
                        key={i}
                        className={`h-2 flex-1 rounded-full ${
                          i < passwordStrength.score
                            ? passwordStrength.color
                            : "bg-slate-700"
                        } transition-all`}
                      />
                    ))}
                  </div>
                  <p className={`text-sm font-medium ${
                    passwordStrength.score <= 1 ? "text-red-400" :
                    passwordStrength.score === 2 ? "text-yellow-400" :
                    passwordStrength.score === 3 ? "text-blue-400" :
                    "text-green-400"
                  }`}>
                    Password Strength: {passwordStrength.label}
                  </p>
                </div>
              )}

              <div className="mt-3 space-y-1 text-sm text-slate-400">
                <div className="flex items-center gap-2">
                  {passwords.new_password.length >= 8 ? (
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  ) : (
                    <AlertCircle className="w-4 h-4 text-slate-500" />
                  )}
                  <span>At least 8 characters</span>
                </div>
                <div className="flex items-center gap-2">
                  {/[a-z]/.test(passwords.new_password) &&
                  /[A-Z]/.test(passwords.new_password) ? (
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  ) : (
                    <AlertCircle className="w-4 h-4 text-slate-500" />
                  )}
                  <span>Mix of uppercase and lowercase letters</span>
                </div>
                <div className="flex items-center gap-2">
                  {/\d/.test(passwords.new_password) ? (
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  ) : (
                    <AlertCircle className="w-4 h-4 text-slate-500" />
                  )}
                  <span>At least one number</span>
                </div>
                <div className="flex items-center gap-2">
                  {/[^a-zA-Z\d]/.test(passwords.new_password) ? (
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  ) : (
                    <AlertCircle className="w-4 h-4 text-slate-500" />
                  )}
                  <span>At least one special character</span>
                </div>
              </div>
            </div>

            {/* Confirm Password */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Confirm New Password *
              </label>
              <div className="relative">
                <input
                  type={showPasswords.confirm ? "text" : "password"}
                  value={passwords.confirm_password}
                  onChange={(e) =>
                    setPasswords({
                      ...passwords,
                      confirm_password: e.target.value,
                    })
                  }
                  className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all pr-10"
                  placeholder="Confirm your new password"
                />
                <button
                  type="button"
                  onClick={() =>
                    setShowPasswords({
                      ...showPasswords,
                      confirm: !showPasswords.confirm,
                    })
                  }
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 hover:text-slate-300"
                >
                  {showPasswords.confirm ? (
                    <EyeOff className="w-5 h-5" />
                  ) : (
                    <Eye className="w-5 h-5" />
                  )}
                </button>
              </div>

              {passwords.new_password && passwords.confirm_password && (
                <div className="mt-2">
                  {passwords.new_password === passwords.confirm_password ? (
                    <div className="flex items-center gap-2 text-green-400 text-sm">
                      <CheckCircle className="w-4 h-4" />
                      Passwords match
                    </div>
                  ) : (
                    <div className="flex items-center gap-2 text-red-400 text-sm">
                      <AlertCircle className="w-4 h-4" />
                      Passwords do not match
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Submit Buttons */}
            <div className="flex gap-3 pt-6">
              <button
                type="submit"
                disabled={isSaving}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold rounded-lg hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 transition-all"
              >
                {isSaving ? (
                  <>
                    <Loader className="w-4 h-4 animate-spin" />
                    Changing...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4" />
                    Change Password
                  </>
                )}
              </button>
              <button
                type="button"
                onClick={() => router.push("/profile")}
                className="flex-1 px-4 py-3 bg-slate-700 text-white font-semibold rounded-lg hover:bg-slate-600 transition-all"
              >
                Cancel
              </button>
            </div>
          </form>
        </motion.div>

        {/* Security Tips */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="mt-6 bg-blue-900/20 border border-blue-700/30 rounded-xl p-6 backdrop-blur-sm"
        >
          <h3 className="text-lg font-semibold text-blue-300 mb-4 flex items-center gap-2">
            <AlertCircle className="w-5 h-5" />
            Security Tips
          </h3>
          <ul className="space-y-2 text-sm text-slate-300">
            <li>✓ Use a strong password with mixed case letters, numbers, and symbols</li>
            <li>✓ Avoid using personal information like names or birthdates</li>
            <li>✓ Don't reuse passwords from other accounts</li>
            <li>✓ Change your password regularly for maximum security</li>
          </ul>
        </motion.div>
      </div>
    </div>
  );
}
