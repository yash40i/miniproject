"use client";

import React, { useState } from "react";
import { ChevronDown } from "lucide-react";

export interface UserProfile {
  experience_level: "beginner" | "intermediate" | "advanced";
  learning_style: "visual" | "hands-on" | "theory" | "mixed";
  availability_hours_per_week: number;
  preferred_resource_types: string[];
  budget: "free" | "limited" | "flexible";
}

interface UserProfileFormProps {
  onSubmit: (profile: UserProfile) => void;
  isLoading?: boolean;
  initialData?: Partial<UserProfile>;
}

const EXPERIENCE_LEVELS = [
  { value: "beginner", label: "Beginner", description: "Just starting out" },
  {
    value: "intermediate",
    label: "Intermediate",
    description: "Some experience, ready to grow",
  },
  {
    value: "advanced",
    label: "Advanced",
    description: "Expert-level knowledge",
  },
];

const LEARNING_STYLES = [
  { value: "visual", label: "Visual", description: "Videos, diagrams, visuals" },
  { value: "hands-on", label: "Hands-On", description: "Learning by doing" },
  { value: "theory", label: "Theory", description: "Deep concept understanding" },
  { value: "mixed", label: "Mixed", description: "Combination of all" },
];

const RESOURCE_TYPES = [
  "Official Docs",
  "Tutorial",
  "Course",
  "Practice",
  "Project",
  "Hands-on Lab",
  "Article",
];

const BUDGET_OPTIONS = [
  {
    value: "free",
    label: "Free Only",
    description: "Only free resources",
  },
  {
    value: "limited",
    label: "Limited Budget",
    description: "Some paid resources OK",
  },
  {
    value: "flexible",
    label: "Flexible Budget",
    description: "Any quality resources",
  },
];

export default function UserProfileForm({
  onSubmit,
  isLoading = false,
  initialData = {},
}: UserProfileFormProps) {
  const [profile, setProfile] = useState<UserProfile>({
    experience_level: initialData.experience_level || "intermediate",
    learning_style: initialData.learning_style || "hands-on",
    availability_hours_per_week: initialData.availability_hours_per_week || 15,
    preferred_resource_types:
      initialData.preferred_resource_types || ["Course", "Tutorial"],
    budget: initialData.budget || "free",
  });

  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleResourceTypeToggle = (type: string) => {
    setProfile((prev) => ({
      ...prev,
      preferred_resource_types: prev.preferred_resource_types.includes(type)
        ? prev.preferred_resource_types.filter((t) => t !== type)
        : [...prev.preferred_resource_types, type],
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(profile);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-slate-800 rounded-lg border border-slate-700 p-6 space-y-6"
    >
      <div>
        <h3 className="text-xl font-semibold text-white mb-4">
          🎯 Learning Profile
        </h3>
        <p className="text-slate-400 text-sm mb-6">
          Tell us about your learning preferences so we can personalize your
          learning path
        </p>
      </div>

      {/* Experience Level */}
      <div>
        <label className="block text-sm font-medium text-slate-300 mb-3">
          Your Experience Level
        </label>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {EXPERIENCE_LEVELS.map((level) => (
            <button
              key={level.value}
              type="button"
              onClick={() =>
                setProfile((prev) => ({
                  ...prev,
                  experience_level: level.value as UserProfile["experience_level"],
                }))
              }
              className={`p-4 rounded-lg border-2 transition-all ${
                profile.experience_level === level.value
                  ? "border-blue-500 bg-blue-500/10"
                  : "border-slate-600 bg-slate-700/50 hover:border-slate-500"
              }`}
            >
              <div className="text-left">
                <div className="font-medium text-white">{level.label}</div>
                <div className="text-xs text-slate-400">{level.description}</div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Learning Style */}
      <div>
        <label className="block text-sm font-medium text-slate-300 mb-3">
          Preferred Learning Style
        </label>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          {LEARNING_STYLES.map((style) => (
            <button
              key={style.value}
              type="button"
              onClick={() =>
                setProfile((prev) => ({
                  ...prev,
                  learning_style: style.value as UserProfile["learning_style"],
                }))
              }
              className={`p-4 rounded-lg border-2 transition-all ${
                profile.learning_style === style.value
                  ? "border-purple-500 bg-purple-500/10"
                  : "border-slate-600 bg-slate-700/50 hover:border-slate-500"
              }`}
            >
              <div className="text-left">
                <div className="font-medium text-white text-sm">
                  {style.label}
                </div>
                <div className="text-xs text-slate-400">
                  {style.description}
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Budget */}
      <div>
        <label className="block text-sm font-medium text-slate-300 mb-3">
          Budget for Learning
        </label>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {BUDGET_OPTIONS.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() =>
                setProfile((prev) => ({
                  ...prev,
                  budget: option.value as UserProfile["budget"],
                }))
              }
              className={`p-4 rounded-lg border-2 transition-all ${
                profile.budget === option.value
                  ? "border-green-500 bg-green-500/10"
                  : "border-slate-600 bg-slate-700/50 hover:border-slate-500"
              }`}
            >
              <div className="text-left">
                <div className="font-medium text-white">{option.label}</div>
                <div className="text-xs text-slate-400">
                  {option.description}
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Time Availability */}
      <div>
        <label className="block text-sm font-medium text-slate-300 mb-3">
          Weekly Time Availability
        </label>
        <div className="flex items-center gap-4">
          <input
            type="range"
            min="5"
            max="50"
            step="5"
            value={profile.availability_hours_per_week}
            onChange={(e) =>
              setProfile((prev) => ({
                ...prev,
                availability_hours_per_week: parseInt(e.target.value),
              }))
            }
            className="flex-1"
          />
          <div className="text-right">
            <span className="text-lg font-semibold text-blue-400">
              {profile.availability_hours_per_week}
            </span>
            <span className="text-sm text-slate-400 ml-1">hours/week</span>
          </div>
        </div>
        <p className="text-xs text-slate-400 mt-2">
          This helps us create a realistic learning timeline
        </p>
      </div>

      {/* Advanced Options */}
      <div>
        <button
          type="button"
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="flex items-center gap-2 text-slate-300 hover:text-white transition-colors"
        >
          <ChevronDown
            size={18}
            className={`transition-transform ${showAdvanced ? "rotate-180" : ""}`}
          />
          <span className="text-sm font-medium">Preferred Resource Types</span>
        </button>

        {showAdvanced && (
          <div className="mt-4 p-4 bg-slate-700/50 rounded-lg">
            <p className="text-xs text-slate-400 mb-3">
              Select the types of resources you prefer
            </p>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
              {RESOURCE_TYPES.map((type) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => handleResourceTypeToggle(type)}
                  className={`px-3 py-2 rounded text-xs font-medium transition-all ${
                    profile.preferred_resource_types.includes(type)
                      ? "bg-blue-600 text-white"
                      : "bg-slate-600 text-slate-300 hover:bg-slate-500"
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Summary */}
      <div className="bg-slate-700/50 rounded-lg p-4">
        <h4 className="text-sm font-semibold text-white mb-2">📋 Summary</h4>
        <ul className="text-xs text-slate-400 space-y-1">
          <li>
            • Level: <span className="text-slate-300">{profile.experience_level}</span>
          </li>
          <li>
            • Style:{" "}
            <span className="text-slate-300">{profile.learning_style}</span>
          </li>
          <li>
            • Time: <span className="text-slate-300">{profile.availability_hours_per_week} hours/week</span>
          </li>
          <li>
            • Budget: <span className="text-slate-300">{profile.budget}</span>
          </li>
          <li>
            • Resources:{" "}
            <span className="text-slate-300">
              {profile.preferred_resource_types.join(", ")}
            </span>
          </li>
        </ul>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-lg transition-all"
      >
        {isLoading ? (
          <span className="flex items-center justify-center gap-2">
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            Generating Personalized Path...
          </span>
        ) : (
          "Generate Personalized Learning Path →"
        )}
      </button>

      <p className="text-xs text-slate-400 text-center">
        We'll create an adaptive learning roadmap based on your preferences
      </p>
    </form>
  );
}
