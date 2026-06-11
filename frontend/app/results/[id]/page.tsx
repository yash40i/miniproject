"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Loader, CheckCircle2, AlertCircle, BarChart3, Zap, Calendar } from "lucide-react";
import { apiClient, AnalysisResult } from "@/lib/api";
import { useAnalysisStore } from "@/lib/store";
import { useAuth } from "@/lib/useAuth";
import UserMenu from "@/components/UserMenu";
import { toast } from "react-toastify";

export default function ResultsPage() {
  const params = useParams();
  const router = useRouter();
  const analysisId = params.id as string;
  const { isAuthenticated, isLoading: authLoading } = useAuth();

  const { analysisResult, setAnalysisResult, setLoading } = useAnalysisStore();
  const [result, setResult] = useState<AnalysisResult | null>(analysisResult || null);
  const [isLoading, setIsLoading] = useState(!analysisResult);
  const [activeTab, setActiveTab] = useState<"overview" | "skills" | "path">("overview");

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push(`/login?from=/results/${analysisId}`);
    }
  }, [isAuthenticated, authLoading, router, analysisId]);

  if (authLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-900 to-slate-800">
        <div className="text-center">
          <Loader className="w-12 h-12 animate-spin text-blue-400 mx-auto mb-4" />
          <p className="text-white">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  useEffect(() => {
    const fetchResults = async () => {
      try {
        setIsLoading(true);
        const data = await apiClient.getAnalysisResults(analysisId);
        setResult(data);
        setAnalysisResult(data);

        if (data.status === "failed") {
          toast.error(data.error || "Analysis failed");
        } else if (data.status === "processing") {
          // Poll again after 2 seconds
          setTimeout(fetchResults, 2000);
        }
      } catch (error: any) {
        toast.error(error.message);
      } finally {
        setIsLoading(false);
        setLoading(false);
      }
    };

    if (!result || result.status === "processing") {
      fetchResults();
    }
  }, [analysisId, result?.status]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex items-center justify-center">
        <div className="text-center space-y-4">
          <Loader className="w-12 h-12 text-blue-400 animate-spin mx-auto" />
          <p className="text-white text-lg">Analyzing your resume...</p>
          <p className="text-slate-400">This may take a minute</p>
        </div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex items-center justify-center">
        <div className="text-center space-y-4">
          <AlertCircle className="w-12 h-12 text-red-400 mx-auto" />
          <p className="text-white text-lg">Results not found</p>
          <button
            onClick={() => router.push("/")}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  if (result.status === "failed") {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex items-center justify-center">
        <div className="text-center space-y-4">
          <AlertCircle className="w-12 h-12 text-red-400 mx-auto" />
          <p className="text-white text-lg">Analysis Failed</p>
          <p className="text-slate-400">{result.error}</p>
          <button
            onClick={() => router.push("/")}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
          >
            Start New Analysis
          </button>
        </div>
      </div>
    );
  }

  const matchingResult = result.matching_result;
  const feedbackResult = result.feedback;
  const learningPath = result.learning_path;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="border-b border-slate-700 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-white">Analysis Results</h1>
            <div className="flex items-center gap-4">
              <button
                onClick={() => router.push("/")}
                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition"
              >
                New Analysis
              </button>
              <UserMenu />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          {/* Overall Score Card */}
          {matchingResult && (
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-8 text-white space-y-4">
              <div className="flex items-center gap-3">
                <CheckCircle2 className="w-8 h-8" />
                <h2 className="text-2xl font-bold">Match Analysis Complete</h2>
              </div>
              <div className="grid md:grid-cols-3 gap-6 mt-6">
                <div className="space-y-2">
                  <p className="text-blue-100">Overall Match Score</p>
                  <p className="text-4xl font-bold">
                    {matchingResult.overall_score.toFixed(1)}%
                  </p>
                </div>
                <div className="space-y-2">
                  <p className="text-blue-100">Matched Skills</p>
                  <p className="text-4xl font-bold">{matchingResult.matched_skills.length}</p>
                </div>
                <div className="space-y-2">
                  <p className="text-blue-100">Skills to Develop</p>
                  <p className="text-4xl font-bold">{matchingResult.missing_skills.length}</p>
                </div>
              </div>

              {/* Interpretation */}
              <div className="mt-6 p-4 bg-white/10 rounded-lg">
                <p className="text-blue-50">
                  {matchingResult.overall_score >= 85
                    ? "Excellent match! Your profile aligns very well with the job requirements."
                    : matchingResult.overall_score >= 70
                    ? "Good match with some skill gaps to address. Focus on the recommended learning path."
                    : matchingResult.overall_score >= 55
                    ? "Moderate match. Significant skill development is recommended to strengthen your candidacy."
                    : "This role requires substantial skill development. Use the learning path to get started."}
                </p>
              </div>
            </div>
          )}

          {/* Tabs */}
          <div className="border-b border-slate-700 flex gap-4">
            {[
              { id: "overview", label: "Overview", icon: BarChart3 },
              { id: "skills", label: "Skill Matches", icon: Zap },
              { id: "path", label: "Learning Path", icon: Calendar },
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`px-4 py-3 font-medium transition-colors flex items-center gap-2 border-b-2 ${
                    activeTab === tab.id
                      ? "text-blue-400 border-blue-400"
                      : "text-slate-400 border-transparent hover:text-slate-300"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              );
            })}
          </div>

          {/* Tab Content */}
          <div className="space-y-6">
            {activeTab === "overview" && feedbackResult && (
              <div className="space-y-6">
                {/* Gap Analysis */}
                <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 space-y-3">
                  <h3 className="text-lg font-semibold text-white">Gap Analysis</h3>
                  <p className="text-slate-300">{feedbackResult.gap_analysis}</p>
                </div>

                {/* Recommendations */}
                <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 space-y-3">
                  <h3 className="text-lg font-semibold text-white">Recommendations</h3>
                  <ul className="space-y-2">
                    {feedbackResult.recommendations.map((rec, idx) => (
                      <li key={idx} className="flex gap-3 text-slate-300">
                        <span className="text-blue-400 font-bold">{idx + 1}.</span>
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Next Steps */}
                <div className="bg-blue-900/30 border border-blue-700 rounded-lg p-6 space-y-3">
                  <h3 className="text-lg font-semibold text-white">Next Steps</h3>
                  <p className="text-slate-300">{feedbackResult.next_steps}</p>
                </div>
              </div>
            )}

            {activeTab === "skills" && matchingResult && (
              <div className="space-y-4">
                {/* Matched Skills */}
                <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 space-y-4">
                  <h3 className="text-lg font-semibold text-white">
                    Matched Skills ({matchingResult.matched_skills.length})
                  </h3>
                  <div className="space-y-3">
                    {matchingResult.matched_skills.map((match, idx) => (
                      <div key={idx} className="flex items-center justify-between p-3 bg-slate-700 rounded">
                        <div className="flex-1">
                          <p className="text-white font-medium">{match.resume_skill}</p>
                          <p className="text-slate-400 text-sm">→ {match.job_skill}</p>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="w-24 bg-slate-600 rounded-full h-2">
                            <div
                              className="bg-green-500 h-2 rounded-full"
                              style={{
                                width: `${match.similarity_score * 100}%`,
                              }}
                            />
                          </div>
                          <span className="text-green-400 font-semibold text-sm">
                            {(match.similarity_score * 100).toFixed(0)}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Missing Skills */}
                <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 space-y-4">
                  <h3 className="text-lg font-semibold text-white">
                    Skills to Develop ({matchingResult.missing_skills.length})
                  </h3>
                  <div className="grid md:grid-cols-2 gap-3">
                    {matchingResult.missing_skills.map((skill, idx) => (
                      <div key={idx} className="p-3 bg-slate-700 rounded flex items-center gap-2">
                        <span className="text-yellow-400">•</span>
                        <span className="text-slate-200">{skill}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {activeTab === "path" && learningPath && (
              <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 space-y-6">
                <div className="space-y-2">
                  <h3 className="text-lg font-semibold text-white">{learningPath.title}</h3>
                  <p className="text-slate-400">
                    {learningPath.total_hours} hours over {learningPath.estimated_weeks} weeks
                  </p>
                </div>

                <div className="space-y-4">
                  {learningPath.milestones.map((milestone, idx) => (
                    <div
                      key={idx}
                      className="p-4 border border-slate-600 rounded-lg space-y-3"
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <p className="text-white font-semibold">
                            {idx + 1}. {milestone.title}
                          </p>
                          <p className="text-slate-400 text-sm">{milestone.description}</p>
                        </div>
                        <span className="px-3 py-1 bg-blue-900 text-blue-200 rounded-full text-sm">
                          {milestone.difficulty}
                        </span>
                      </div>

                      <div className="flex gap-4 text-sm text-slate-400">
                        <span>{milestone.estimated_hours}h</span>
                        {milestone.resources.length > 0 && (
                          <span>{milestone.resources.length} resources</span>
                        )}
                      </div>

                      {milestone.resources.length > 0 && (
                        <div className="mt-3 pt-3 border-t border-slate-600">
                          <p className="text-sm font-medium text-slate-300 mb-2">Resources:</p>
                          <ul className="space-y-1">
                            {milestone.resources.map((res, ridx) => (
                              <li key={ridx} className="text-sm text-slate-400">
                                • {res.title} ({res.type})
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
