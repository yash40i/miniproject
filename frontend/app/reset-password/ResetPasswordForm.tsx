"use client";

import React, { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/useAuth";
import {
  validateResetPasswordForm,
  validatePassword,
  getFieldError,
  getPasswordStrengthColor,
} from "@/lib/validation";
import { Lock, Loader, Eye, EyeOff, Check, X, ArrowRight } from "lucide-react";
import { motion } from "framer-motion";

export default function ResetPasswordForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { resetPassword, verifyResetToken, isLoading } = useAuth();

  const token = searchParams.get("token");

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [errors, setErrors] = useState<any[]>([]);
  const [apiError, setApiError] = useState("");
  const [success, setSuccess] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [tokenEmail, setTokenEmail] = useState<string | null>(null);
  const [isVerifying, setIsVerifying] = useState(true);
  const [isTokenValid, setIsTokenValid] = useState(false);

  const passwordValidation = validatePassword(password);

  // Verify token on mount
  useEffect(() => {
    const verifyToken = async () => {
      if (!token) {
        setApiError("No reset token provided. Please use the link from your email.");
        setIsVerifying(false);
        return;
      }

      try {
        const result = await verifyResetToken(token);
        if (result.valid) {
          setIsTokenValid(true);
          setTokenEmail(result.email || null);
        } else {
          setApiError("This reset link is invalid or has expired. Please request a new one.");
        }
      } catch (err) {
        setApiError("Failed to verify reset token. Please try again.");
      } finally {
        setIsVerifying(false);
      }
    };

    verifyToken();
  }, [token, verifyResetToken]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setApiError("");
    setErrors([]);

    if (!token) {
      setApiError("No reset token provided");
      return;
    }

    // Validate form
    const validation = validateResetPasswordForm(password, confirmPassword);
    if (!validation.isValid) {
      setErrors(validation.errors);
      return;
    }

    try {
      await resetPassword(token, password, confirmPassword);
      setSuccess(true);
    } catch (err) {
      setApiError(
        err instanceof Error ? err.message : "Failed to reset password"
      );
    }
  };

  if (isVerifying) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        <div className="flex flex-col items-center gap-4">
          <Loader className="w-8 h-8 animate-spin text-blue-400" />
          <p className="text-slate-400">Verifying reset link...</p>
        </div>
      </div>
    );
  }

  if (!isTokenValid) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-md relative bg-gradient-to-b from-slate-800/80 to-slate-900/80 backdrop-blur-xl rounded-2xl shadow-2xl p-8 border border-slate-700/50"
        >
          <div className="text-center">
            <div className="w-16 h-16 rounded-full bg-red-500/20 border border-red-500/50 flex items-center justify-center mx-auto mb-4">
              <X className="w-8 h-8 text-red-400" />
            </div>
            <h1 className="text-2xl font-bold text-white mb-2">Invalid Link</h1>
            <p className="text-slate-400 mb-6">{apiError}</p>
            <Link
              href="/forgot-password"
              className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold rounded-lg transition-all"
            >
              Request New Link
            </Link>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 px-4 py-8">
      <div className="w-full max-w-md">
        {/* Background decoration */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-20 right-10 w-72 h-72 bg-purple-500/10 rounded-full blur-3xl"></div>
          <div className="absolute bottom-20 left-10 w-72 h-72 bg-pink-500/10 rounded-full blur-3xl"></div>
        </div>

        {/* Main card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="relative bg-gradient-to-b from-slate-800/80 to-slate-900/80 backdrop-blur-xl rounded-2xl shadow-2xl p-8 border border-slate-700/50"
        >
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">Create New Password</h1>
            <p className="text-slate-400 text-sm">
              {tokenEmail && (
                <>
                  Resetting password for <span className="font-medium text-slate-300">{tokenEmail}</span>
                </>
              )}
              {!tokenEmail && "Enter your new password below"}
            </p>
          </div>

          {!success ? (
            <>
              {/* API Error */}
              {apiError && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  className="mb-6 p-4 bg-red-500/10 border border-red-500/50 rounded-lg backdrop-blur-sm"
                >
                  <p className="text-red-400 text-sm font-medium">{apiError}</p>
                </motion.div>
              )}

              {/* Form */}
              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Password Field */}
                <div>
                  <label className="block text-sm font-medium text-slate-200 mb-2">
                    New Password
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                    <input
                      type={showPassword ? "text" : "password"}
                      value={password}
                      onChange={(e) => {
                        setPassword(e.target.value);
                        setErrors(errors.filter((e) => e.field !== "password"));
                      }}
                      placeholder="••••••••"
                      className={`w-full pl-10 pr-12 py-3 bg-slate-700/50 border rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 transition-all ${
                        getFieldError(errors, "password")
                          ? "border-red-500/50 focus:ring-red-500/50"
                          : "border-slate-600 focus:ring-purple-500/50"
                      }`}
                      disabled={isLoading}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-300 transition-colors"
                      disabled={isLoading}
                    >
                      {showPassword ? (
                        <EyeOff className="w-5 h-5" />
                      ) : (
                        <Eye className="w-5 h-5" />
                      )}
                    </button>
                  </div>

                  {/* Password Strength Indicator */}
                  {password && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      className="mt-3 p-3 rounded-lg bg-slate-700/50 border border-slate-600"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-medium text-slate-300">
                          Password Strength
                        </span>
                        <span
                          className={`text-xs font-semibold ${getPasswordStrengthColor(
                            passwordValidation.strength
                          )}`}
                        >
                          {passwordValidation.strength.charAt(0).toUpperCase() +
                            passwordValidation.strength.slice(1)}
                        </span>
                      </div>
                      <div className="w-full h-2 bg-slate-600 rounded-full overflow-hidden mb-2">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{
                            width: {
                              weak: "25%",
                              fair: "50%",
                              good: "75%",
                              strong: "100%",
                            }[passwordValidation.strength],
                          }}
                          className={`h-full transition-all ${
                            {
                              weak: "bg-red-500",
                              fair: "bg-orange-500",
                              good: "bg-yellow-500",
                              strong: "bg-green-500",
                            }[passwordValidation.strength]
                          }`}
                        ></motion.div>
                      </div>
                    </motion.div>
                  )}

                  {getFieldError(errors, "password") && (
                    <p className="text-red-400 text-xs mt-1">
                      {getFieldError(errors, "password")}
                    </p>
                  )}
                </div>

                {/* Confirm Password Field */}
                <div>
                  <label className="block text-sm font-medium text-slate-200 mb-2">
                    Confirm Password
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                    <input
                      type={showConfirmPassword ? "text" : "password"}
                      value={confirmPassword}
                      onChange={(e) => {
                        setConfirmPassword(e.target.value);
                        setErrors(errors.filter((e) => e.field !== "confirmPassword"));
                      }}
                      placeholder="••••••••"
                      className={`w-full pl-10 pr-12 py-3 bg-slate-700/50 border rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 transition-all ${
                        getFieldError(errors, "confirmPassword")
                          ? "border-red-500/50 focus:ring-red-500/50"
                          : "border-slate-600 focus:ring-purple-500/50"
                      }`}
                      disabled={isLoading}
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-300 transition-colors"
                      disabled={isLoading}
                    >
                      {showConfirmPassword ? (
                        <EyeOff className="w-5 h-5" />
                      ) : (
                        <Eye className="w-5 h-5" />
                      )}
                    </button>
                  </div>
                  {password && confirmPassword && password === confirmPassword && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="flex items-center gap-2 text-green-400 text-xs mt-1"
                    >
                      <Check className="w-3 h-3" />
                      Passwords match
                    </motion.div>
                  )}
                  {getFieldError(errors, "confirmPassword") && (
                    <p className="text-red-400 text-xs mt-1">
                      {getFieldError(errors, "confirmPassword")}
                    </p>
                  )}
                </div>

                {/* Submit Button */}
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  type="submit"
                  disabled={isLoading}
                  className="w-full mt-6 py-3 px-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold rounded-lg flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-purple-500/20"
                  onMouseEnter={() => setIsHovered(true)}
                  onMouseLeave={() => setIsHovered(false)}
                >
                  {isLoading && <Loader className="w-5 h-5 animate-spin" />}
                  {isLoading ? "Resetting..." : "Reset Password"}
                  {!isLoading && (
                    <motion.div
                      animate={{ x: isHovered ? 4 : 0 }}
                      transition={{ type: "spring", stiffness: 400, damping: 10 }}
                    >
                      <ArrowRight className="w-4 h-4" />
                    </motion.div>
                  )}
                </motion.button>
              </form>
            </>
          ) : (
            // Success State
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-center py-8"
            >
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, type: "spring" }}
                className="w-16 h-16 rounded-full bg-green-500/20 border border-green-500/50 flex items-center justify-center mx-auto mb-4"
              >
                <Check className="w-8 h-8 text-green-400" />
              </motion.div>

              <h2 className="text-xl font-bold text-white mb-2">Password Reset Successful</h2>
              <p className="text-slate-400 mb-6">
                Your password has been successfully reset. You can now log in with your new password.
              </p>

              <Link
                href="/login"
                className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-semibold rounded-lg transition-all"
              >
                Go to Login
              </Link>
            </motion.div>
          )}
        </motion.div>
      </div>
    </div>
  );
}
