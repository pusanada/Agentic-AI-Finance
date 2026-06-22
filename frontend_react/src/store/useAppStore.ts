import { create } from 'zustand';

export interface OCRResult {
  assessable_income: number;
  withholding_tax: number;
  other_deductions: number;
  already_purchased: number;
  confidence: number;
  document_type: string;
  session_id?: string;
  metadata?: any;
}

export interface PortfolioAllocation {
  fund_code: string;
  fund_name: string;
  weight: number; // percentage, e.g. 30
  amount: number; // THB
  risk_level: number;
  esg_rating: string;
  underlying_holdings: Array<{ ticker: string; weight: number; esg_score?: number }>;
}

export interface PortfolioResult {
  quota: {
    assessable_income: number;
    already_purchased: number;
    max_quota: number;
    remaining_quota: number;
  };
  portfolio: {
    allocations: PortfolioAllocation[];
    total_allocated: number;
    average_risk_level: number;
    average_esg_rating: string;
  };
  compliance: {
    is_compliant: boolean;
    violations: string[];
    details: Record<string, any>;
  };
  auq: {
    confidence_score: number;
    uncertainty_rating: string;
    requires_override: boolean;
    reasons: string[];
  };
  execution_trace: string[];
  session_id: string;
}

interface AppState {
  language: 'TH' | 'EN';
  theme: 'light' | 'dark';
  ocrCompleted: boolean;
  ocrResult: OCRResult | null;
  portfolioResult: PortfolioResult | null;
  isUploading: boolean;
  isAllocating: boolean;
  
  setLanguage: (lang: 'TH' | 'EN') => void;
  setTheme: (theme: 'light' | 'dark') => void;
  toggleTheme: () => void;
  setOcrCompleted: (completed: boolean) => void;
  setOcrResult: (result: OCRResult | null) => void;
  setPortfolioResult: (result: PortfolioResult | null) => void;
  setIsUploading: (uploading: boolean) => void;
  setIsAllocating: (allocating: boolean) => void;
}

export const useAppStore = create<AppState>((set) => ({
  language: 'TH',
  theme: 'dark',
  ocrCompleted: false,
  ocrResult: null,
  portfolioResult: null,
  isUploading: false,
  isAllocating: false,

  setLanguage: (language) => set({ language }),
  setTheme: (theme) => {
    set({ theme });
    if (typeof window !== 'undefined') {
      const root = window.document.documentElement;
      if (theme === 'dark') {
        root.classList.add('dark');
      } else {
        root.classList.remove('dark');
      }
      try {
        localStorage.setItem('app-theme', theme);
      } catch (e) {}
    }
  },
  toggleTheme: () => set((state) => {
    const newTheme = state.theme === 'light' ? 'dark' : 'light';
    if (typeof window !== 'undefined') {
      const root = window.document.documentElement;
      if (newTheme === 'dark') {
        root.classList.add('dark');
      } else {
        root.classList.remove('dark');
      }
      try {
        localStorage.setItem('app-theme', newTheme);
      } catch (e) {}
    }
    return { theme: newTheme };
  }),
  setOcrCompleted: (ocrCompleted) => set({ ocrCompleted }),
  setOcrResult: (ocrResult) => set({ ocrResult, ocrCompleted: !!ocrResult }),
  setPortfolioResult: (portfolioResult) => set({ portfolioResult }),
  setIsUploading: (isUploading) => set({ isUploading }),
  setIsAllocating: (isAllocating) => set({ isAllocating }),
}));
