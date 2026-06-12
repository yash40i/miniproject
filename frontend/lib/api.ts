import axios, { AxiosInstance } from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const TOKEN_KEY = "auth_token";

// Auth Interfaces
export interface User {
  id: number;
  email: string;
  full_name?: string;
  is_active: boolean;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
}

// Analysis Interfaces
export interface SkillMatch {
  resume_skill: string;
  job_skill: string;
  similarity_score: number;
  match_strength: string;
}

export interface MatchingResult {
  overall_score: number;
  matched_percentage: number;
  matched_skills: SkillMatch[];
  missing_skills: string[];
}

export interface FeedbackResult {
  gap_analysis: string;
  recommendations: string[];
  priority_skills: string[];
  next_steps: string;
}

export interface Milestone {
  id: number;
  title: string;
  description: string;
  estimated_hours: number;
  difficulty: string;
  resources: Array<{ title: string; url?: string; type: string }>;
}

export interface LearningPath {
  title: string;
  total_hours: number;
  estimated_weeks: number;
  milestones: Milestone[];
}

export interface AnalysisResult {
  analysis_id: string;
  status: "processing" | "completed" | "failed";
  matching_result?: MatchingResult;
  feedback?: FeedbackResult;
  learning_path?: LearningPath;
  error?: string;
}

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      timeout: 30000,
    });

    // Add token to requests if available
    this.client.interceptors.request.use((config) => {
      const token = this.getToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
  }

  // Token Management
  private getToken(): string | null {
    if (typeof window !== "undefined") {
      return localStorage.getItem(TOKEN_KEY);
    }
    return null;
  }

  private setToken(token: string): void {
    if (typeof window !== "undefined") {
      localStorage.setItem(TOKEN_KEY, token);
    }
  }

  public clearToken(): void {
    if (typeof window !== "undefined") {
      localStorage.removeItem(TOKEN_KEY);
    }
  }

  // Auth Endpoints (use Next.js proxy to avoid CORS)
  async signup(
    email: string,
    password: string,
    fullName?: string
  ): Promise<AuthToken> {
    try {
      const response = await axios.post("/api/auth/signup", {
        email,
        password,
        full_name: fullName,
      });
      const data = response.data;
      this.setToken(data.access_token);
      return data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async login(email: string, password: string): Promise<AuthToken> {
    try {
      const response = await axios.post("/api/auth/login", {
        email,
        password,
      });
      const data = response.data;
      this.setToken(data.access_token);
      return data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getCurrentUser(): Promise<User> {
    try {
      const token = this.getToken();
      const response = await axios.get("/api/auth/me", {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  logout(): void {
    this.clearToken();
  }

  async uploadResume(
    file: File,
    jobDescription: string
  ): Promise<{ analysis_id: string }> {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("job_description", jobDescription);

    try {
      const response = await this.client.post("/api/analyze", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getAnalysisResults(analysisId: string): Promise<AnalysisResult> {
    try {
      const response = await this.client.get(`/api/results/${analysisId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async deleteAnalysis(analysisId: string): Promise<void> {
    try {
      await this.client.delete(`/api/results/${analysisId}`);
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getStats(): Promise<any> {
    try {
      const response = await this.client.get("/api/stats");
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async healthCheck(): Promise<any> {
    try {
      const response = await this.client.get("/health");
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Profile Management Endpoints
  async getProfile(): Promise<any> {
    try {
      const response = await this.client.get("/auth/profile");
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async updateProfile(data: { full_name?: string; email?: string }): Promise<any> {
    try {
      const response = await this.client.put("/auth/profile", data);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async changePassword(data: {
    current_password: string;
    new_password: string;
    confirm_password: string;
  }): Promise<any> {
    try {
      const response = await this.client.post("/auth/change-password", data);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async forgotPassword(email: string): Promise<any> {
    try {
      const response = await this.client.post("/auth/forgot-password", { email });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async verifyResetToken(token: string): Promise<any> {
    try {
      const response = await this.client.post("/auth/verify-reset-token", { token });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async resetPassword(token: string, newPassword: string, confirmPassword: string): Promise<any> {
    try {
      const response = await this.client.post("/auth/reset-password", {
        token,
        new_password: newPassword,
        confirm_password: confirmPassword,
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Generic HTTP methods
  async post(url: string, data: any): Promise<any> {
    try {
      const response = await this.client.post(url, data);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async get(url: string): Promise<any> {
    try {
      const response = await this.client.get(url);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  private handleError(error: any): Error {
    if (axios.isAxiosError(error)) {
      return new Error(
        error.response?.data?.detail ||
          error.message ||
          "An error occurred"
      );
    }
    return new Error("An unexpected error occurred");
  }
}

export const apiClient = new APIClient();
