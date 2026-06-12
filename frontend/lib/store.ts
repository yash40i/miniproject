import { create } from "zustand";
import { AnalysisResult } from "./api";

interface AnalysisStore {
  currentAnalysisId: string | null;
  analysisResult: AnalysisResult | null;
  isLoading: boolean;
  error: string | null;
  
  setAnalysisId: (id: string) => void;
  setAnalysisResult: (result: AnalysisResult) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

export const useAnalysisStore = create<AnalysisStore>((set) => ({
  currentAnalysisId: null,
  analysisResult: null,
  isLoading: false,
  error: null,

  setAnalysisId: (id: string) => set({ currentAnalysisId: id }),
  setAnalysisResult: (result: AnalysisResult) => set({ analysisResult: result }),
  setLoading: (loading: boolean) => set({ isLoading: loading }),
  setError: (error: string | null) => set({ error }),
  reset: () => set({
    currentAnalysisId: null,
    analysisResult: null,
    isLoading: false,
    error: null,
  }),
}));

interface UIStore {
  sidebarOpen: boolean;
  theme: "light" | "dark";
  
  toggleSidebar: () => void;
  setTheme: (theme: "light" | "dark") => void;
}

export const useUIStore = create<UIStore>((set) => ({
  sidebarOpen: true,
  theme: "light",

  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setTheme: (theme: "light" | "dark") => set({ theme }),
}));
