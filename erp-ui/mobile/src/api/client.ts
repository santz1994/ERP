import axios, { AxiosInstance } from 'axios';
import * as SecureStore from 'expo-secure-store';

const API_BASE_URL = 'http://localhost:8000/api/v1';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add token interceptor
    this.client.interceptors.request.use(async (config) => {
      try {
        const token = await SecureStore.getItemAsync('authToken');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
      } catch (error) {
        console.error('Error getting token:', error);
      }
      return config;
    });

    // Error interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized
          SecureStore.deleteItemAsync('authToken');
        }
        return Promise.reject(error);
      }
    );
  }

  // Authentication
  async login(username: string, password: string) {
    const response = await this.client.post('/auth/login', {
      username,
      password,
    });
    return response.data;
  }

  async logout() {
    await this.client.post('/auth/logout');
  }

  async getMe() {
    const response = await this.client.get('/auth/me');
    return response.data;
  }

  // Dashboard
  async getDashboardStats() {
    const response = await this.client.get('/dashboard/stats');
    return response.data;
  }

  // Cutting
  async getCuttingLines() {
    const response = await this.client.get('/cutting/lines');
    return response.data;
  }

  async getCuttingLineStatus(lineId: string) {
    const response = await this.client.get(`/cutting/lines/${lineId}/status`);
    return response.data;
  }

  async startCuttingLine(lineId: string) {
    const response = await this.client.post(`/cutting/lines/${lineId}/start`);
    return response.data;
  }

  async stopCuttingLine(lineId: string) {
    const response = await this.client.post(`/cutting/lines/${lineId}/stop`);
    return response.data;
  }

  // Sewing
  async getSewingLines() {
    const response = await this.client.get('/sewing/lines');
    return response.data;
  }

  async getSewingLineStatus(lineId: string) {
    const response = await this.client.get(`/sewing/lines/${lineId}/status`);
    return response.data;
  }

  async startSewingLine(lineId: string) {
    const response = await this.client.post(`/sewing/lines/${lineId}/start`);
    return response.data;
  }

  async stopSewingLine(lineId: string) {
    const response = await this.client.post(`/sewing/lines/${lineId}/stop`);
    return response.data;
  }

  // Finishing
  async getFinishingLines() {
    const response = await this.client.get('/finishing/lines');
    return response.data;
  }

  async getFinishingLineStatus(lineId: string) {
    const response = await this.client.get(`/finishing/lines/${lineId}/status`);
    return response.data;
  }

  async startFinishingLine(lineId: string) {
    const response = await this.client.post(`/finishing/lines/${lineId}/start`);
    return response.data;
  }

  async stopFinishingLine(lineId: string) {
    const response = await this.client.post(`/finishing/lines/${lineId}/stop`);
    return response.data;
  }

  // Finishing Barcode Scanning
  async scanFinishingProduct(sku: string, batchId?: string) {
    const response = await this.client.post('/finishing/products/scan', {
      sku,
      batchId,
    });
    return response.data;
  }

  async getFinishingProductDetails(productId: string) {
    const response = await this.client.get(`/finishing/products/${productId}`);
    return response.data;
  }

  async completeFinishing(data: any) {
    const response = await this.client.post('/finishing/complete', data);
    return response.data;
  }

  async rejectFinishingProduct(data: any) {
    const response = await this.client.post('/finishing/reject', data);
    return response.data;
  }

  async getBatchStatus(batchId: string) {
    const response = await this.client.get(`/finishing/batch/${batchId}/status`);
    return response.data;
  }

  async getOperatorStats(operator: string) {
    const response = await this.client.get(`/finishing/operator/${operator}/stats`);
    return response.data;
  }

  async getQualityGateSummary() {
    const response = await this.client.get('/finishing/quality-gate/summary');
    return response.data;
  }

  // QC
  async getQCInspections() {
    const response = await this.client.get('/qc/inspections');
    return response.data;
  }

  async recordQCInspection(data: any) {
    const response = await this.client.post('/qc/inspections', data);
    return response.data;
  }

  // Reports
  async getDailyReport() {
    const response = await this.client.get('/reports/daily');
    return response.data;
  }

  async getWeeklyReport() {
    const response = await this.client.get('/reports/weekly');
    return response.data;
  }
}

export const apiClient = new ApiClient();
