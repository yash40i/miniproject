"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/useAuth";
import {
  validateSignupForm,
  validatePassword,
  getFieldError,
  getPasswordStrengthColor,
  getPasswordStrengthBgColor,
} from "@/lib/validation";
import { Mail, Lock, User, Loader, Eye, EyeOff, Chrome, Check, X, ArrowRight } from "lucide-react";
import { motion } from "framer-motion";
import { GoogleOAuthProvider, GoogleLogin } from "@react-oauth/google";

export default function SignupForm() {
  const router = useRouter();
  const { signup, isLoading } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [errors, setErrors] = useState<any[]>([]);
  const [apiError, setApiError] = useState("");
  const [isHovered, setIsHovered] = useState(false);
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);

  const passwordValidation = validatePassword(password);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setApiError("");
    setErrors([]);

    // Validate form
    const validation = validateSignupForm(email, password, confirmPassword, fullName);
    if (!validation.isValid) {
      setErrors(validation.errors);
      return;
    }

    try {
      await signup(email, password, fullName || undefined);
      router.push("/");
    } catch (err) {
      setApiError(
        err instanceof Error ? err.message : "Signup failed. Please try again."
      );
    }
  };

  const handleGoogleSuccess = async (credentialResponse: any) => {
    try {
      setIsGoogleLoading(true);
      setApiError("");

      // Decode JWT token to get user info
      const token = credentialResponse.credential;
      const parts = token.split(".");
      const payload = JSON.parse(atob(parts[1]));

      // Send to backend
      const response = await fetch("/api/auth/google", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          token,
          email: payload.email,
          name: payload.name,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Google authentication failed");
      }

      const data = await response.json();
      // Store token
      if (typeof window !== "undefined") {
        localStorage.setItem("auth_token", data.access_token);
      }
      
      router.push("/");
    } catch (err) {
      setApiError(
        err instanceof Error ? err.message : "Google signup failed. Please try again."
      );
    } finally {
      setIsGoogleLoading(false);
    }
  };

  const handleGoogleError = () => {
    setApiError("Google signup failed. Please try again.");
  };

  const googleClientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 px-4 py-8">
      <div className="w-full max-w-md">
        {/* Background decoration */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-20 right-10 w-72 h-72 bg-green-500/10 rounded-full blur-3xl"></div>
          <div className="absolute bottom-20 left-10 w-72 h-72 bg-purple-500/10 rounded-full blur-3xl"></div>
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
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center">
                <span className="text-white font-bold text-lg">RI</span>
              </div>
              <h1 className="text-2xl font-bold text-white">Get Started</h1>
            </div>
            <p className="text-slate-400 text-sm">
              Create an account to use Resume-Insight AI
            </p>
          </div>

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

          {/* Google Sign Up */}
          {googleClientId && (
            <GoogleOAuthProvider clientId={googleClientId}>
              <div className="mb-6">
                <GoogleLogin
                  onSuccess={handleGoogleSuccess}
                  onError={handleGoogleError}
                  theme="dark"
                  size="large"
                  width="100%"
                />
              </div>
            </GoogleOAuthProvider>
          )}

          {/* Divider */}
          <div className="relative mb-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-700"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-gradient-to-b from-slate-800/80 to-slate-900/80 text-slate-400">
                Or sign up with email
              </span>
            </div>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Full Name Field */}
            <div>
              <label className="block text-sm font-medium text-slate-200 mb-2">
                Full Name (Optional)
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => {
                    setFullName(e.target.value);
                    setErrors(errors.filter((e) => e.field !== "fullName"));
                  }}
                  placeholder="John Doe"
                  className={`w-full pl-10 pr-4 py-3 bg-slate-700/50 border rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 transition-all ${
                    getFieldError(errors, "fullName")
                      ? "border-red-500/50 focus:ring-red-500/50"
                      : "border-slate-600 focus:ring-green-500/50"
                  }`}
                  disabled={isLoading}
                />
              </div>
              {getFieldError(errors, "fullName") && (
                <p className="text-red-400 text-xs mt-1">
                  {getFieldError(errors, "fullName")}
                </p>
              )}
            </div>

            {/* Email Field */}
            <div>
              <label className="block text-sm font-medium text-slate-200 mb-2">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value);
                    setErrors(errors.filter((e) => e.field !== "email"));
                  }}
                  placeholder="you@example.com"
                  className={`w-full pl-10 pr-4 py-3 bg-slate-700/50 border rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 transition-all ${
                    getFieldError(errors, "email")
                      ? "border-red-500/50 focus:ring-red-500/50"
                      : "border-slate-600 focus:ring-green-500/50"
                  }`}
                  disabled={isLoading}
                />
              </div>
              {getFieldError(errors, "email") && (
                <p className="text-red-400 text-xs mt-1">
                  {getFieldError(errors, "email")}
                </p>
              )}
            </div>

            {/* Password Field */}
            <div>
              <label className="block text-sm font-medium text-slate-200 mb-2">
                Password
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
                      : "border-slate-600 focus:ring-green-500/50"
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
                  {passwordValidation.feedback.length > 0 && (
                    <ul className="space-y-1">
                      {passwordValidation.feedback.map((tip, idx) => (
                        <li
                          key={idx}
                          className="flex items-center gap-2 text-xs text-slate-400"
                        >
                          <X className="w-3 h-3 text-red-500 flex-shrink-0" />
                          {tip}
                        </li>
                      ))}
                    </ul>
                  )}
                  {passwordValidation.feedback.length === 0 && (
                    <div className="flex items-center gap-2 text-xs text-green-400">
                      <Check className="w-3 h-3 flex-shrink-0" />
                      Strong password!
                    </div>
                  )}
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
                      : "border-slate-600 focus:ring-green-500/50"
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
              className="w-full mt-6 py-3 px-4 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-semibold rounded-lg flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-green-500/20"
              onMouseEnter={() => setIsHovered(true)}
              onMouseLeave={() => setIsHovered(false)}
            >
              {isLoading && <Loader className="w-5 h-5 animate-spin" />}
              {isLoading ? "Creating account..." : "Create Account"}
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

          {/* Footer */}
          <div className="mt-8 pt-6 border-t border-slate-700">
            <p className="text-center text-slate-400 text-sm">
              Already have an account?{" "}
              <Link
                href="/login"
                className="text-green-400 hover:text-green-300 font-semibold transition-colors"
              >
                Sign in
              </Link>
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
