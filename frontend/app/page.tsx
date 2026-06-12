"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Upload, Loader } from "lucide-react";
import { apiClient } from "@/lib/api";
import { useAnalysisStore } from "@/lib/store";
import UserMenu from "@/components/UserMenu";
import { toast } from "react-toastify";

export default function Home() {
  const router = useRouter();
  const { setAnalysisId, setLoading, setError } = useAnalysisStore();

  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isDragActive, setIsDragActive] = useState(false);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragActive(true);
    } else if (e.type === "dragleave") {
      setIsDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      const file = files[0];
      if (file.type === "application/pdf") {
        setResumeFile(file);
      } else {
        toast.error("Please upload a PDF file");
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setResumeFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!resumeFile) {
      toast.error("Please upload a resume PDF");
      return;
    }

    if (!jobDescription.trim()) {
      toast.error("Please enter a job description");
      return;
    }

    try {
      setIsLoading(true);
      setLoading(true);

      const response = await apiClient.uploadResume(resumeFile, jobDescription);
      const analysisId = response.analysis_id;

      setAnalysisId(analysisId);
      toast.success("Analysis started! Redirecting to results...");

      // Redirect to results page
      router.push(`/results/${analysisId}`);
    } catch (error: any) {
      toast.error(error.message || "Failed to start analysis");
      setError(error.message);
    } finally {
      setIsLoading(false);
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="border-b border-slate-700 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold">RI</span>
              </div>
              <h1 className="text-2xl font-bold text-white">Resume-Insight AI</h1>
            </div>
            <div className="flex items-center gap-4">
              <p className="text-slate-400 text-sm hidden md:block">
                Semantic Resume Analysis & Learning Paths
              </p>
              <UserMenu />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-20">
        <div className="space-y-8">
          {/* Title Section */}
          <div className="text-center space-y-4">
            <h2 className="text-4xl md:text-5xl font-bold text-white">
              Optimize Your Resume
            </h2>
            <p className="text-lg text-slate-400 max-w-2xl mx-auto">
              Upload your resume and a job description to get instant semantic matching,
              skill gap analysis, and a personalized learning roadmap.
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Resume Upload */}
            <div className="space-y-3">
              <label className="block text-sm font-semibold text-white">
                Upload Resume (PDF)
              </label>
              <div
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                  isDragActive
                    ? "border-blue-400 bg-blue-400/10"
                    : resumeFile
                    ? "border-green-500 bg-green-500/10"
                    : "border-slate-600 hover:border-slate-500 bg-slate-800"
                }`}
              >
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handleFileChange}
                  className="hidden"
                  id="resume-upload"
                />
                <label htmlFor="resume-upload" className="cursor-pointer block">
                  {resumeFile ? (
                    <div className="flex items-center justify-center gap-2">
                      <span className="text-green-400 text-lg">✓</span>
                      <span className="text-white font-medium">{resumeFile.name}</span>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <Upload className="w-8 h-8 mx-auto text-slate-400" />
                      <p className="text-white font-medium">
                        Drag and drop your resume or click to browse
                      </p>
                      <p className="text-slate-400 text-sm">PDF files up to 10MB</p>
                    </div>
                  )}
                </label>
              </div>
            </div>

            {/* Job Description */}
            <div className="space-y-3">
              <label className="block text-sm font-semibold text-white">
                Job Description
              </label>
              <textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Paste the full job description here..."
                className="w-full px-4 py-3 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all resize-none"
                rows={8}
              />
              <p className="text-slate-400 text-sm">
                {jobDescription.length} characters
              </p>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading || !resumeFile || !jobDescription.trim()}
              className="w-full px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold rounded-lg hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader className="w-5 h-5 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Upload className="w-5 h-5" />
                  Analyze Resume
                </>
              )}
            </button>
          </form>

          {/* Features */}
          <div className="grid md:grid-cols-3 gap-6 mt-12">
            {[
              {
                icon: "📊",
                title: "Semantic Matching",
                desc: "Advanced ML finds conceptual skill matches beyond keywords",
              },
              {
                icon: "🎯",
                title: "Skill Gap Analysis",
                desc: "Identifies missing skills with detailed recommendations",
              },
              {
                icon: "📈",
                title: "Learning Roadmap",
                desc: "Structured milestones with realistic timelines",
              },
            ].map((feature, idx) => (
              <div
                key={idx}
                className="bg-slate-800/50 border border-slate-700 rounded-lg p-6 space-y-3"
              >
                <p className="text-3xl">{feature.icon}</p>
                <h3 className="font-semibold text-white">{feature.title}</h3>
                <p className="text-slate-400 text-sm">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
