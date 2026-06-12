"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/useAuth";
import { apiClient } from "@/lib/api";
import {
  User,
  Mail,
  Calendar,
  Lock,
  Edit2,
  Save,
  X,
  Loader,
  Check,
} from "lucide-react";
import { motion } from "framer-motion";
import { toast } from "react-toastify";

interface ProfileData {
  id: number;
  email: string;
  full_name: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export default function ProfilePage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState({
    full_name: "",
    email: "",
  });
  const [isSaving, setIsSaving] = useState(false);

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/login?from=/profile");
    }
  }, [isAuthenticated, authLoading, router]);

  // Load profile data
  useEffect(() => {
    if (isAuthenticated && !authLoading) {
      loadProfile();
    }
  }, [isAuthenticated, authLoading]);

  const loadProfile = async () => {
    try {
      setIsLoading(true);
      const profileData = await apiClient.getProfile();
      setProfile(profileData);
      setEditData({
        full_name: profileData.full_name || "",
        email: profileData.email,
      });
    } catch (error) {
      toast.error("Failed to load profile");
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveProfile = async () => {
    try {
      setIsSaving(true);
      await apiClient.updateProfile(editData);
      await loadProfile();
      setIsEditing(false);
      toast.success("Profile updated successfully!");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to update profile");
    } finally {
      setIsSaving(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  if (authLoading || isLoading || !profile) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-white mb-2">My Profile</h1>
          <p className="text-slate-400">Manage your account information and settings</p>
        </motion.div>

        {/* Main Profile Card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-slate-800/50 border border-slate-700 rounded-xl p-8 mb-6 backdrop-blur-sm"
        >
          <div className="flex items-center gap-6 mb-8">
            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-blue-400 to-purple-600 flex items-center justify-center">
              <User className="w-10 h-10 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">
                {profile.full_name || "User"}
              </h2>
              <p className="text-slate-400">{profile.email}</p>
              <div className="flex items-center gap-2 mt-2">
                <Check className="w-4 h-4 text-green-500" />
                <span className="text-sm text-green-500">Account Active</span>
              </div>
            </div>
          </div>

          {/* Profile Information */}
          <div className="space-y-4">
            {!isEditing ? (
              <>
                {/* Display Mode */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-slate-700/30 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Mail className="w-4 h-4 text-blue-400" />
                      <label className="text-sm font-medium text-slate-300">
                        Email Address
                      </label>
                    </div>
                    <p className="text-white font-mono text-sm">{profile.email}</p>
                  </div>

                  <div className="bg-slate-700/30 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <User className="w-4 h-4 text-blue-400" />
                      <label className="text-sm font-medium text-slate-300">
                        Full Name
                      </label>
                    </div>
                    <p className="text-white">
                      {profile.full_name || "Not specified"}
                    </p>
                  </div>

                  <div className="bg-slate-700/30 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Calendar className="w-4 h-4 text-blue-400" />
                      <label className="text-sm font-medium text-slate-300">
                        Member Since
                      </label>
                    </div>
                    <p className="text-white">{formatDate(profile.created_at)}</p>
                  </div>

                  <div className="bg-slate-700/30 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Calendar className="w-4 h-4 text-blue-400" />
                      <label className="text-sm font-medium text-slate-300">
                        Last Updated
                      </label>
                    </div>
                    <p className="text-white">{formatDate(profile.updated_at)}</p>
                  </div>
                </div>

                <button
                  onClick={() => setIsEditing(true)}
                  className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all mt-6"
                >
                  <Edit2 className="w-4 h-4" />
                  Edit Profile
                </button>
              </>
            ) : (
              <>
                {/* Edit Mode */}
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Full Name
                    </label>
                    <input
                      type="text"
                      value={editData.full_name}
                      onChange={(e) =>
                        setEditData({ ...editData, full_name: e.target.value })
                      }
                      className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                      placeholder="Enter your full name"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Email Address
                    </label>
                    <input
                      type="email"
                      value={editData.email}
                      onChange={(e) =>
                        setEditData({ ...editData, email: e.target.value })
                      }
                      className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                      placeholder="Enter your email"
                    />
                  </div>
                </div>

                <div className="flex gap-3 pt-4">
                  <button
                    onClick={handleSaveProfile}
                    disabled={isSaving}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white font-semibold rounded-lg hover:from-green-600 hover:to-emerald-700 disabled:opacity-50 transition-all"
                  >
                    {isSaving ? (
                      <>
                        <Loader className="w-4 h-4 animate-spin" />
                        Saving...
                      </>
                    ) : (
                      <>
                        <Save className="w-4 h-4" />
                        Save Changes
                      </>
                    )}
                  </button>
                  <button
                    onClick={() => {
                      setIsEditing(false);
                      setEditData({
                        full_name: profile.full_name || "",
                        email: profile.email,
                      });
                    }}
                    className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-slate-700 text-white font-semibold rounded-lg hover:bg-slate-600 transition-all"
                  >
                    <X className="w-4 h-4" />
                    Cancel
                  </button>
                </div>
              </>
            )}
          </div>
        </motion.div>

        {/* Security Section */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="bg-slate-800/50 border border-slate-700 rounded-xl p-8 backdrop-blur-sm"
        >
          <div className="flex items-center gap-3 mb-6">
            <Lock className="w-5 h-5 text-blue-400" />
            <h3 className="text-lg font-bold text-white">Security</h3>
          </div>

          <p className="text-slate-400 mb-4">
            Manage your password and security settings
          </p>

          <button
            onClick={() => router.push("/settings")}
            className="flex items-center justify-center gap-2 px-4 py-3 bg-slate-700 text-white font-semibold rounded-lg hover:bg-slate-600 transition-all w-full md:w-auto"
          >
            <Lock className="w-4 h-4" />
            Change Password
          </button>
        </motion.div>
      </div>
    </div>
  );
}
