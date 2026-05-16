/**
 * TypeScript types for the Agent Puller application
 */

// Company Types
export interface Company {
  id: string;
  cik: string;
  ticker: string | null;
  company_name: string;
  sic_code: string | null;
  sic_description: string | null;
  created_at: string;
  updated_at: string;
}

export interface CompanyCreate {
  cik: string;
  ticker?: string;
  company_name: string;
  sic_code?: string;
  sic_description?: string;
}

// Analysis Types
export interface SegmentData {
  name: string;
  revenue: number;
  account?: string;
  type?: 'growth' | 'legacy' | 'uncategorized';
}

export interface AnalysisResult {
  id: string;
  company_id: string;
  legacy_growth_rate: number | null;
  new_segment_growth_rate: number | null;
  growth_ratio: number | null;
  new_segment_revenue_pct: number | null;
  segments_data: SegmentData[] | null;
  analysis_date: string;
  fiscal_year: number | null;
  form_type: string | null;
  created_at: string;
}

// Screening Types
export interface ScreeningJob {
  id: string;
  job_type: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  total_companies: number;
  processed_companies: number;
  results_count: number;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
}

export interface ScreeningRequest {
  job_type: 'narrative_shift' | 'specific_tickers';
  tickers?: string[];
  max_results?: number;
}

// Favorite Types
export interface Favorite {
  id: string;
  company_id: string;
  notes: string | null;
  created_at: string;
  company?: Company;
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}

// Dashboard Types
export interface DashboardStats {
  total_companies: number;
  total_analyses: number;
  narrative_shifts_found: number;
  recent_jobs: ScreeningJob[];
}

// Chart Data Types
export interface GrowthRatioData {
  ticker: string;
  growth_ratio: number;
  new_segment_pct: number;
}
