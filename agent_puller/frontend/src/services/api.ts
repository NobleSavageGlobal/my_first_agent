/**
 * API service for communicating with the backend
 */
import axios, { AxiosInstance, AxiosError } from 'axios';

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  // ============== Company Endpoints ==============

  async getCompanies(params?: {
    skip?: number;
    limit?: number;
    sic_code?: string;
    ticker?: string;
  }) {
    const response = await this.client.get('/api/v1/companies', { params });
    return response.data;
  }

  async getCompany(id: string) {
    const response = await this.client.get(`/api/v1/companies/${id}`);
    return response.data;
  }

  async createCompany(company: any) {
    const response = await this.client.post('/api/v1/companies', company);
    return response.data;
  }

  async deleteCompany(id: string) {
    const response = await this.client.delete(`/api/v1/companies/${id}`);
    return response.data;
  }

  async getCompanyAnalysis(companyId: string) {
    const response = await this.client.get(`/api/v1/companies/${companyId}/analysis`);
    return response.data;
  }

  // ============== Analysis Endpoints ==============

  async getAnalysisResults(params?: {
    skip?: number;
    limit?: number;
    min_growth_ratio?: number;
    max_growth_ratio?: number;
  }) {
    const response = await this.client.get('/api/v1/analysis', { params });
    return response.data;
  }

  // ============== Screening Endpoints ==============

  async startScreening(request: {
    job_type: string;
    tickers?: string[];
    max_results?: number;
  }) {
    const response = await this.client.post('/api/v1/screen', request);
    return response.data;
  }

  async getScreeningJob(jobId: string) {
    const response = await this.client.get(`/api/v1/screen/${jobId}`);
    return response.data;
  }

  async getScreeningJobs(params?: {
    skip?: number;
    limit?: number;
    status?: string;
  }) {
    const response = await this.client.get('/api/v1/screen', { params });
    return response.data;
  }

  // ============== Favorites Endpoints ==============

  async getFavorites(params?: { skip?: number; limit?: number }) {
    const response = await this.client.get('/api/v1/favorites', { params });
    return response.data;
  }

  async addFavorite(companyId: string, notes?: string) {
    const response = await this.client.post('/api/v1/favorites', {
      company_id: companyId,
      notes,
    });
    return response.data;
  }

  async removeFavorite(favoriteId: string) {
    const response = await this.client.delete(`/api/v1/favorites/${favoriteId}`);
    return response.data;
  }

  // ============== Health Check ==============

  async healthCheck() {
    const response = await this.client.get('/api/v1/health');
    return response.data;
  }
}

export const api = new ApiService();
export default api;
