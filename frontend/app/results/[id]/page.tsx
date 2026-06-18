"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Loader, CheckCircle2, AlertCircle, BarChart3, Zap, Calendar, Network, Lock, Unlock, Award, Download, Sparkles } from "lucide-react";
import { apiClient, AnalysisResult, NodeActivation } from "@/lib/api";
import { useAnalysisStore } from "@/lib/store";
import UserProfileForm, { UserProfile } from "@/components/UserProfileForm";
import { toast } from "react-toastify";
import SkillGraph from "@/components/SkillGraph";
import SkillRadarChart from "@/components/SkillRadarChart";

export default function ResultsPage() {
  const params = useParams();
  const router = useRouter();
  const analysisId = params.id as string;

  const { analysisResult, setAnalysisResult, setLoading } = useAnalysisStore();
  const [result, setResult] = useState<AnalysisResult | null>(analysisResult || null);
  const [isLoading, setIsLoading] = useState(!analysisResult);
  const [activeTab, setActiveTab] = useState<"overview" | "skills" | "graph" | "path">("overview");
  const [adaptiveLoading, setAdaptiveLoading] = useState(false);
  const [adaptivePath, setAdaptivePath] = useState<any>(null);
  const [isGeneratingResume, setIsGeneratingResume] = useState(false);
  const [adaptedResume, setAdaptedResume] = useState<any>(result?.adapted_resume_json || null);

  useEffect(() => {
    const fetchResults = async () => {
      try {
        setIsLoading(true);
        const data = await apiClient.getAnalysisResults(analysisId);
        setResult(data);
        setAnalysisResult(data);
        if (data.adapted_resume_json) {
          setAdaptedResume(data.adapted_resume_json);
        }

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

  const handleGenerateResume = async () => {
    try {
      setIsGeneratingResume(true);
      const data = await apiClient.generateMatchedResume(analysisId);
      setAdaptedResume(data.adapted_resume);
      toast.success("Resume optimized to 100% match successfully!");
    } catch (error: any) {
      toast.error(error.message || "Failed to generate optimized resume");
    } finally {
      setIsGeneratingResume(false);
    }
  };

  const handleDownloadResume = async () => {
    try {
      const blob = await apiClient.downloadMatchedResume(analysisId);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      
      const candidateName = adaptedResume?.personal_info?.name || "Matched";
      const cleanName = candidateName.replace(/[^a-zA-Z0-9]/g, "_");
      link.setAttribute("download", `${cleanName}_100_Match_Resume.pdf`);
      
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error: any) {
      toast.error(error.message || "Failed to download PDF resume");
    }
  };

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
            <button
              onClick={() => router.push("/")}
              className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition"
            >
              New Analysis
            </button>
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
              { id: "graph", label: "Skill Graph", icon: Network },
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
                {/* 100% Match Resume Generator Card */}
                <div className="bg-gradient-to-br from-slate-800 to-slate-900 border border-blue-500/30 rounded-xl p-6 shadow-xl relative overflow-hidden">
                  <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/10 rounded-full blur-2xl pointer-events-none"></div>
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                    <div className="space-y-2 flex-1">
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 text-xs font-bold bg-blue-500/20 text-blue-400 rounded-full border border-blue-500/30">AI POWERED</span>
                        <span className="px-2 py-0.5 text-xs font-bold bg-purple-500/20 text-purple-400 rounded-full border border-purple-500/30">100% MATCH</span>
                      </div>
                      <h3 className="text-xl font-bold text-white flex items-center gap-2">
                        <Sparkles className="w-5 h-5 text-yellow-400 animate-pulse" />
                        Generate 100% Matched Resume
                      </h3>
                      <p className="text-slate-300 text-sm leading-relaxed">
                        Instantly optimize your resume to address all missing skills and tailor experience bullets to this job description. Your original formatting structure is retained, and you will receive a professionally formatted PDF.
                      </p>
                    </div>
                    <div className="flex flex-col sm:flex-row gap-3 self-start md:self-center shrink-0">
                      {isGeneratingResume ? (
                        <button
                          disabled
                          className="px-6 py-3 bg-blue-600/50 text-white rounded-lg flex items-center gap-2 cursor-wait"
                        >
                          <Loader className="w-4 h-4 animate-spin" />
                          Optimizing Resume...
                        </button>
                      ) : adaptedResume ? (
                        <>
                          <button
                            onClick={handleDownloadResume}
                            className="px-6 py-3 bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white font-semibold rounded-lg flex items-center justify-center gap-2 transition-all transform hover:scale-[1.02] shadow-md shadow-blue-500/20"
                          >
                            <Download className="w-4 h-4" />
                            Download PDF Resume
                          </button>
                          <button
                            onClick={handleGenerateResume}
                            className="px-4 py-3 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 rounded-lg flex items-center justify-center gap-2 transition"
                          >
                            Re-generate
                          </button>
                        </>
                      ) : (
                        <button
                          onClick={handleGenerateResume}
                          className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold rounded-lg flex items-center justify-center gap-2 transition-all transform hover:scale-[1.02] shadow-md shadow-blue-500/20"
                        >
                          <Sparkles className="w-4 h-4 text-yellow-300" />
                          Optimize Resume to 100% Match
                        </button>
                      )}
                    </div>
                  </div>
                </div>

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

            {activeTab === "graph" && matchingResult?.skill_node_map && (
              <div className="space-y-6">
                {/* Summary Cards */}
                <div className="grid grid-cols-3 gap-4">
                  {[
                    { label: "Mastered", count: matchingResult.skill_node_map.summary.mastered, icon: Award, color: "emerald", bg: "from-emerald-900/40 to-emerald-800/20", border: "border-emerald-700" },
                    { label: "Unlocked", count: matchingResult.skill_node_map.summary.unlocked, icon: Unlock, color: "amber", bg: "from-amber-900/40 to-amber-800/20", border: "border-amber-700" },
                    { label: "Locked", count: matchingResult.skill_node_map.summary.locked, icon: Lock, color: "red", bg: "from-red-900/40 to-red-800/20", border: "border-red-700" },
                  ].map((card) => {
                    const Icon = card.icon;
                    return (
                      <div key={card.label} className={`bg-gradient-to-br ${card.bg} ${card.border} border rounded-xl p-5 text-center`}>
                        <Icon className={`w-6 h-6 mx-auto mb-2 text-${card.color}-400`} />
                        <p className={`text-3xl font-bold text-${card.color}-400`}>{card.count}</p>
                        <p className="text-slate-400 text-sm mt-1">{card.label}</p>
                      </div>
                    );
                  })}
                </div>

                {/* Graph and Radar Chart Section */}
                <div className="grid lg:grid-cols-3 gap-6">
                  {/* Radar Chart */}
                  <div className="lg:col-span-1 bg-slate-800 border border-slate-700 rounded-lg p-4 flex flex-col">
                    <h3 className="text-lg font-semibold text-white mb-2">Skill Profile</h3>
                    <p className="text-sm text-slate-400 mb-4">Click a skill in the radar chart to locate it in the roadmap tree.</p>
                    <div className="flex-1 min-h-[400px]">
                      <SkillRadarChart nodesData={matchingResult.skill_node_map} />
                    </div>
                  </div>
                  
                  {/* Interactive DAG */}
                  <div className="lg:col-span-2 bg-slate-800 border border-slate-700 rounded-lg p-4 flex flex-col">
                     <h3 className="text-lg font-semibold text-white mb-4">Interactive Roadmap</h3>
                     <div className="flex-1 border border-slate-700 rounded-lg overflow-hidden min-h-[500px]">
                       <SkillGraph nodesData={matchingResult.skill_node_map} />
                     </div>
                  </div>
                </div>

                {/* Threshold info */}
                <div className="bg-slate-800/50 border border-slate-700 rounded-lg px-4 py-3 flex items-center gap-2 text-sm">
                  <Network className="w-4 h-4 text-blue-400" />
                  <span className="text-slate-300">Similarity threshold: <span className="text-blue-400 font-semibold">{(matchingResult.skill_node_map.threshold * 100).toFixed(0)}%</span> — skills below this are skill gaps</span>
                </div>

                {/* Unlocked — study NOW */}
                {matchingResult.skill_node_map.nodes.filter((n: NodeActivation) => n.state === "Unlocked").length > 0 && (
                  <div className="bg-slate-800 border border-amber-700/50 rounded-lg p-6 space-y-4">
                    <h3 className="text-lg font-semibold text-amber-400 flex items-center gap-2">
                      <Unlock className="w-5 h-5" /> Study Now — All Prerequisites Met
                    </h3>
                    <div className="grid md:grid-cols-2 gap-3">
                      {matchingResult.skill_node_map.nodes
                        .filter((n: NodeActivation) => n.state === "Unlocked")
                        .map((node: NodeActivation, idx: number) => (
                          <div key={idx} className="p-4 bg-amber-900/20 border border-amber-800/40 rounded-lg space-y-2">
                            <div className="flex items-center justify-between">
                              <span className="text-white font-medium">{node.skill}</span>
                              <span className="text-amber-400 text-xs font-mono">{(node.similarity_score * 100).toFixed(0)}%</span>
                            </div>
                            <div className="w-full bg-slate-700 rounded-full h-1.5">
                              <div className="bg-amber-500 h-1.5 rounded-full" style={{ width: `${node.similarity_score * 100}%` }} />
                            </div>
                            {node.prerequisites.length > 0 && (
                              <p className="text-xs text-slate-400">Prerequisites: {node.prerequisites.join(", ")}</p>
                            )}
                          </div>
                        ))}
                    </div>
                  </div>
                )}

                {/* Locked */}
                {matchingResult.skill_node_map.nodes.filter((n: NodeActivation) => n.state === "Locked").length > 0 && (
                  <div className="bg-slate-800 border border-red-700/50 rounded-lg p-6 space-y-4">
                    <h3 className="text-lg font-semibold text-red-400 flex items-center gap-2">
                      <Lock className="w-5 h-5" /> Locked — Prerequisites Missing
                    </h3>
                    <div className="grid md:grid-cols-2 gap-3">
                      {matchingResult.skill_node_map.nodes
                        .filter((n: NodeActivation) => n.state === "Locked")
                        .map((node: NodeActivation, idx: number) => (
                          <div key={idx} className="p-4 bg-red-900/15 border border-red-800/30 rounded-lg space-y-2">
                            <div className="flex items-center justify-between">
                              <span className="text-white font-medium">{node.skill}</span>
                              <span className="text-red-400 text-xs font-mono">{(node.similarity_score * 100).toFixed(0)}%</span>
                            </div>
                            <div className="w-full bg-slate-700 rounded-full h-1.5">
                              <div className="bg-red-500 h-1.5 rounded-full" style={{ width: `${node.similarity_score * 100}%` }} />
                            </div>
                            {node.unmet_prerequisites.length > 0 && (
                              <p className="text-xs text-red-300">Blocked by: {node.unmet_prerequisites.join(", ")}</p>
                            )}
                          </div>
                        ))}
                    </div>
                  </div>
                )}

                {/* Mastered */}
                {matchingResult.skill_node_map.nodes.filter((n: NodeActivation) => n.state === "Mastered").length > 0 && (
                  <div className="bg-slate-800 border border-emerald-700/50 rounded-lg p-6 space-y-4">
                    <h3 className="text-lg font-semibold text-emerald-400 flex items-center gap-2">
                      <Award className="w-5 h-5" /> Mastered
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {matchingResult.skill_node_map.nodes
                        .filter((n: NodeActivation) => n.state === "Mastered")
                        .map((node: NodeActivation, idx: number) => (
                          <span key={idx} className="px-3 py-1.5 bg-emerald-900/30 border border-emerald-700/40 text-emerald-300 rounded-full text-sm">
                            {node.skill} · {(node.similarity_score * 100).toFixed(0)}%
                          </span>
                        ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === "path" && (
              <div className="space-y-6">
                {!adaptivePath ? (
                  <>
                    <div className="bg-blue-900/20 border border-blue-700 rounded-lg p-6 space-y-4">
                      <h3 className="text-lg font-semibold text-white">
                        ✨ Personalize Your Learning Path
                      </h3>
                      <p className="text-slate-300">
                        Tell us about your learning preferences and we'll create a personalized, adaptive learning roadmap just for you. This considers your experience level, learning style, time availability, and budget constraints.
                      </p>
                    </div>
                    
                    <UserProfileForm
                      isLoading={adaptiveLoading}
                      onSubmit={async (profile: UserProfile) => {
                        try {
                          setAdaptiveLoading(true);
                          const response = await apiClient.post(
                            `/api/learning-path/adaptive`,
                            {
                              analysis_id: analysisId,
                              user_profile: profile,
                            }
                          );
                          setAdaptivePath(response.learning_path);
                          toast.success("Adaptive learning path generated!");
                        } catch (error: any) {
                          toast.error(error.message || "Failed to generate adaptive path");
                        } finally {
                          setAdaptiveLoading(false);
                        }
                      }}
                    />
                  </>
                ) : (
                  <>
                    {/* Adaptive Path Display */}
                    <div className="bg-gradient-to-r from-green-900/30 to-blue-900/30 border border-green-700 rounded-lg p-6 space-y-4">
                      <div className="flex items-start justify-between">
                        <div>
                          <h3 className="text-lg font-semibold text-white">
                            🎯 Your Personalized Learning Path
                          </h3>
                          <p className="text-slate-300 mt-1">
                            Adaptivity Score: <span className="text-green-400 font-semibold">{(adaptivePath.adaptivity_score * 100).toFixed(0)}%</span>
                          </p>
                        </div>
                        <button
                          onClick={() => {
                            setAdaptivePath(null);
                          }}
                          className="px-4 py-2 text-sm bg-slate-700 hover:bg-slate-600 text-white rounded transition"
                        >
                          Edit Profile
                        </button>
                      </div>

                      <div className="grid grid-cols-3 gap-4 py-4">
                        <div className="bg-slate-800/50 p-3 rounded">
                          <p className="text-xs text-slate-400">Total Hours</p>
                          <p className="text-2xl font-bold text-blue-400">
                            {adaptivePath.total_hours}
                          </p>
                        </div>
                        <div className="bg-slate-800/50 p-3 rounded">
                          <p className="text-xs text-slate-400">Weeks</p>
                          <p className="text-2xl font-bold text-purple-400">
                            {adaptivePath.estimated_weeks}
                          </p>
                        </div>
                        <div className="bg-slate-800/50 p-3 rounded">
                          <p className="text-xs text-slate-400">Progress</p>
                          <p className="text-2xl font-bold text-green-400">
                            {adaptivePath.overall_progress || 0}%
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Milestones Timeline */}
                    <div className="relative pl-6 sm:pl-8 border-l border-slate-700 space-y-8 mt-8">
                      {adaptivePath.milestones.map((milestone: any, idx: number) => {
                        const isAdvanced = milestone.difficulty?.toLowerCase() === 'advanced';
                        const isIntermediate = milestone.difficulty?.toLowerCase() === 'intermediate';
                        const nodeColor = isAdvanced ? 'from-purple-500 to-pink-500' : isIntermediate ? 'from-blue-500 to-indigo-500' : 'from-emerald-400 to-teal-500';
                        const badgeColor = isAdvanced ? 'bg-purple-900/50 text-purple-300 border-purple-700' : isIntermediate ? 'bg-blue-900/50 text-blue-300 border-blue-700' : 'bg-emerald-900/50 text-emerald-300 border-emerald-700';

                        return (
                        <div key={idx} className="relative group">
                          {/* Glowing Node */}
                          <div className="absolute -left-[35px] sm:-left-[43px] top-6 flex items-center justify-center">
                            <div className={`absolute w-full h-full rounded-full bg-gradient-to-r ${nodeColor} animate-ping opacity-20`} />
                            <div className={`w-5 h-5 rounded-full bg-gradient-to-r ${nodeColor} shadow-[0_0_10px_rgba(255,255,255,0.3)] ring-4 ring-slate-900 z-10`} />
                          </div>

                          {/* Glassmorphism Card */}
                          <div className="p-6 bg-slate-800/40 backdrop-blur-md border border-slate-700/60 rounded-xl space-y-5 shadow-lg hover:shadow-[0_0_30px_rgba(0,0,0,0.2)] hover:border-slate-500/60 transition-all duration-300 transform hover:-translate-y-1">
                            <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                              <div className="flex-1">
                                <div className="flex items-center gap-3 mb-2">
                                  <h3 className="text-xl font-bold text-white tracking-tight">
                                    <span className="text-slate-500 mr-2">{idx + 1}.</span> 
                                    {milestone.title}
                                  </h3>
                                  <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium border ${badgeColor}`}>
                                    {milestone.difficulty}
                                  </span>
                                </div>
                                <p className="text-slate-400 leading-relaxed text-sm sm:text-base">
                                  {milestone.description}
                                </p>
                              </div>
                            </div>

                            {/* Key Stats */}
                            <div className="flex flex-wrap gap-3 sm:gap-4 text-sm">
                              <div className="flex items-center gap-1.5 text-slate-300 bg-slate-900/50 px-3 py-1.5 rounded-lg border border-slate-700/50">
                                <span className="opacity-70">⏱️</span> <span className="font-semibold text-white">{milestone.estimated_hours}</span> <span className="opacity-70">hours</span>
                              </div>
                              <div className="flex items-center gap-1.5 text-slate-300 bg-slate-900/50 px-3 py-1.5 rounded-lg border border-slate-700/50">
                                <span className="opacity-70">📚</span> <span className="font-semibold text-white">{milestone.resources?.length || 0}</span> <span className="opacity-70">resources</span>
                              </div>
                              <div className="flex items-center gap-1.5 text-slate-300 bg-slate-900/50 px-3 py-1.5 rounded-lg border border-slate-700/50">
                                <span className="opacity-70">🎯</span> <span className="font-semibold text-white">{milestone.projects?.length || 0}</span> <span className="opacity-70">projects</span>
                              </div>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-5 border-t border-slate-700/40">
                              {/* Left Column: Criteria & Projects */}
                              <div className="space-y-5">
                                {/* Success Criteria */}
                                {milestone.success_criteria && milestone.success_criteria.length > 0 && (
                                  <div>
                                    <h4 className="text-sm font-semibold text-slate-200 mb-3 flex items-center gap-2">
                                      <span className="text-emerald-400">✓</span> Success Criteria
                                    </h4>
                                    <ul className="space-y-2">
                                      {milestone.success_criteria.map((criteria: string, cidx: number) => (
                                        <li key={cidx} className="text-sm text-slate-400 flex items-start gap-2.5">
                                          <div className="w-1.5 h-1.5 rounded-full bg-slate-600 mt-1.5 shrink-0" />
                                          <span className="leading-snug">{criteria}</span>
                                        </li>
                                      ))}
                                    </ul>
                                  </div>
                                )}

                                {/* Projects */}
                                {milestone.projects && milestone.projects.length > 0 && (
                                  <div>
                                    <h4 className="text-sm font-semibold text-slate-200 mb-3 flex items-center gap-2">
                                      <span>🛠️</span> Hands-On Projects
                                    </h4>
                                    <div className="space-y-2.5">
                                      {milestone.projects.map((project: any, pidx: number) => (
                                        <div key={pidx} className="p-3.5 bg-slate-900/40 border border-slate-700/50 rounded-lg">
                                          <p className="text-sm font-semibold text-slate-200">{project.title}</p>
                                          <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">{project.description}</p>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                )}
                              </div>

                              {/* Right Column: Resources */}
                              {milestone.resources && milestone.resources.length > 0 && (
                                <div>
                                  <h4 className="text-sm font-semibold text-slate-200 mb-3 flex items-center gap-2">
                                    <span>🔗</span> Learning Resources
                                  </h4>
                                  <div className="space-y-2.5">
                                    {milestone.resources.slice(0, 4).map((res: any, ridx: number) => (
                                      <a 
                                        key={ridx} 
                                        href={res.url || '#'}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="block p-3.5 bg-slate-900/40 hover:bg-slate-800/80 border border-slate-700/50 hover:border-blue-500/40 rounded-lg transition-all group/link"
                                      >
                                        <div className="flex justify-between items-start">
                                          <p className="text-sm font-medium text-slate-300 group-hover/link:text-blue-400 transition-colors line-clamp-1 pr-2">
                                            {res.title}
                                          </p>
                                          <span className="text-slate-600 group-hover/link:text-blue-400 text-xs mt-0.5 transition-colors">↗</span>
                                        </div>
                                        <div className="flex items-center gap-2 mt-2">
                                          <span className="text-[10px] uppercase tracking-wider font-semibold text-slate-500 bg-slate-800/80 px-2 py-0.5 rounded border border-slate-700">
                                            {res.type}
                                          </span>
                                          {res.free && (
                                            <span className="text-[10px] uppercase tracking-wider font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                                              Free
                                            </span>
                                          )}
                                        </div>
                                      </a>
                                    ))}
                                    {milestone.resources.length > 4 && (
                                      <div className="text-center py-2.5 text-xs font-medium text-slate-500 border border-dashed border-slate-700/60 rounded-lg">
                                        +{milestone.resources.length - 4} more available
                                      </div>
                                    )}
                                  </div>
                                </div>
                              )}
                            </div>

                            {/* Progress Indicator */}
                            <div className="pt-4 mt-2 border-t border-slate-700/40">
                              <div className="flex items-center justify-between mb-2">
                                <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Milestone Progress</span>
                                <span className="text-xs font-bold text-slate-300">{milestone.progress_percentage || 0}%</span>
                              </div>
                              <div className="w-full bg-slate-900/80 rounded-full h-1.5 overflow-hidden">
                                <div
                                  className={`bg-gradient-to-r ${nodeColor} h-full rounded-full transition-all duration-1000`}
                                  style={{ width: `${milestone.progress_percentage || 0}%` }}
                                />
                              </div>
                            </div>

                          </div>
                        </div>
                        );
                      })}
                    </div>
                  </>
                )}

                {/* Static Learning Path Fallback */}
                {!adaptivePath && learningPath && (
                  <div className="mt-8 pt-6 border-t border-slate-700">
                    <p className="text-sm text-slate-400 mb-4">
                      Or view the standard learning path:
                    </p>
                    <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 space-y-6">
                      <div className="space-y-2">
                        <h3 className="text-lg font-semibold text-white">
                          {learningPath.title}
                        </h3>
                        <p className="text-slate-400">
                          {learningPath.total_hours} hours over {learningPath.estimated_weeks} weeks
                        </p>
                      </div>

                      <div className="space-y-4">
                        {learningPath.milestones.map((milestone: any, idx: number) => (
                          <div
                            key={idx}
                            className="p-4 border border-slate-600 rounded-lg space-y-3"
                          >
                            <div className="flex items-start justify-between">
                              <div>
                                <p className="text-white font-semibold">
                                  {idx + 1}. {milestone.title}
                                </p>
                                <p className="text-slate-400 text-sm">
                                  {milestone.description}
                                </p>
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
                                <p className="text-sm font-medium text-slate-300 mb-2">
                                  Resources:
                                </p>
                                <ul className="space-y-1">
                                  {milestone.resources.map((res: any, ridx: number) => (
                                    <li
                                      key={ridx}
                                      className="text-sm text-slate-400"
                                    >
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
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
