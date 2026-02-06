import axios, { AxiosInstance } from 'axios'
import { AuthResponse, User } from '@/types'

const API_URL = (import.meta as any).env.VITE_API_URL || 'http://localhost:8000/api/v1'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Add token to requests
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    })

    // Handle auth errors and permission denials
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Unauthorized - token expired or invalid
          console.error('[API Client] 401 Unauthorized:', error.config?.url)
          
          // IMPORTANT: Don't force redirect here - let PrivateRoute handle it
          // This allows graceful handling of failed auth checks on page load
          localStorage.removeItem('access_token')
          localStorage.removeItem('user')
          
          // Only redirect if we're not already on login page
          const currentPath = window.location.pathname
          if (!currentPath.includes('/login')) {
            // Add small delay to allow cleanup
            setTimeout(() => {
              window.location.href = '/login'
            }, 100)
          }
        } else if (error.response?.status === 403) {
          // Forbidden - insufficient permissions
          const message = error.response?.data?.detail || 'Insufficient permissions'
          console.error('[API Client] Permission denied:', message)
          
          // Show notification (you can import useUIStore here if needed)
          // For now, just log it - pages should handle 403 errors individually
        }
        return Promise.reject(error)
      }
    )
  }

  // Generic HTTP methods (automatically unwrap response.data)
  async get(url: string, config?: any) {
    const response = await this.client.get(url, config)
    return response.data
  }

  async post(url: string, data?: any, config?: any) {
    const response = await this.client.post(url, data, config)
    return response.data
  }

  async put(url: string, data?: any, config?: any) {
    const response = await this.client.put(url, data, config)
    return response.data
  }

  async delete(url: string, config?: any) {
    const response = await this.client.delete(url, config)
    return response.data
  }

  // Auth endpoints
  async register(username: string, email: string, password: string, fullName: string) {
    const { data } = await this.client.post('/auth/register', {
      username,
      email,
      password,
      full_name: fullName,
    })
    return data
  }

  async login(username: string, password: string): Promise<AuthResponse> {
    const { data } = await this.client.post('/auth/login', {
      username,
      password,
    })
    return data
  }

  async refreshToken() {
    const { data } = await this.client.post('/auth/refresh')
    return data
  }

  async getCurrentUser(): Promise<User> {
    const { data } = await this.client.get('/auth/me')
    return data
  }

  async changePassword(oldPassword: string, newPassword: string) {
    await this.client.post('/auth/change-password', {
      old_password: oldPassword,
      new_password: newPassword,
    })
  }

  // PPIC endpoints
  async createManufacturingOrder(params: any) {
    const { data } = await this.client.post('/ppic/manufacturing-order', params)
    return data
  }

  async getManufacturingOrder(moId: number) {
    const { data } = await this.client.get(`/ppic/manufacturing-order/${moId}`)
    return data
  }

  async listManufacturingOrders(filters?: any) {
    const { data } = await this.client.get('/ppic/manufacturing-orders', { params: filters })
    return data
  }

  async approveManufacturingOrder(moId: number) {
    const { data } = await this.client.post(`/ppic/manufacturing-order/${moId}/approve`)
    return data
  }

  // Cutting endpoints
  async receiveSPK(params: any) {
    const { data } = await this.client.post('/cutting/receive-spk', params)
    return data
  }

  async completeCutting(workOrderId: number, params: any) {
    const { data } = await this.client.post(`/cutting/complete/${workOrderId}`, params)
    return data
  }

  async checkLineCleanance(department: string, lineId?: number) {
    const { data } = await this.client.get('/cutting/line-clearance', {
      params: { department, line_id: lineId }
    })
    return data
  }

  // Sewing endpoints
  async acceptSewingTransfer(params: any) {
    const { data } = await this.client.post('/sewing/accept-transfer', params)
    return data
  }

  async completeSewing(workOrderId: number, params: any) {
    const { data } = await this.client.post(`/sewing/complete/${workOrderId}`, params)
    return data
  }

  // Finishing endpoints
  async acceptFinishingWIP(params: any) {
    const { data } = await this.client.post('/finishing/accept-wip', params)
    return data
  }

  async performMetalDetector(batchNumber: string) {
    const { data } = await this.client.post('/finishing/metal-detector', { batch_number: batchNumber })
    return data
  }

  async convertToFinishGood(params: any) {
    const { data } = await this.client.post('/finishing/convert-fg', params)
    return data
  }

  // Packing endpoints
  async sortByDestination(params: any) {
    const { data } = await this.client.post('/packing/sort-destination', params)
    return data
  }

  async packageCartons(params: any) {
    const { data } = await this.client.post('/packing/package-cartons', params)
    return data
  }

  // Quality endpoints
  async performLabTest(params: any) {
    const { data } = await this.client.post('/quality/lab-test/perform', params)
    return data
  }

  async getLabTestSummary(batchNumber: string) {
    const { data } = await this.client.get(`/quality/lab-test/batch/${batchNumber}/summary`)
    return data
  }

  async performInlineQC(params: any) {
    const { data } = await this.client.post('/quality/inspection/inline', params)
    return data
  }

  // Warehouse endpoints
  async getStockLevel(productId: number) {
    const { data } = await this.client.get(`/warehouse/stock/${productId}`)
    return data
  }

  async createTransfer(params: any) {
    const { data } = await this.client.post('/warehouse/transfer', params)
    return data
  }

  async listLocations() {
    const { data } = await this.client.get('/warehouse/locations')
    return data
  }

  // Admin endpoints
  async listUsers(filters?: any) {
    const { data } = await this.client.get('/admin/users', { params: filters })
    return data
  }

  async getUserDetails(userId: number) {
    const { data } = await this.client.get(`/admin/users/${userId}`)
    return data
  }

  async updateUser(userId: number, params: any) {
    const { data } = await this.client.put(`/admin/users/${userId}`, params)
    return data
  }

  async deactivateUser(userId: number) {
    await this.client.post(`/admin/users/${userId}/deactivate`)
  }

  async reactivateUser(userId: number) {
    await this.client.post(`/admin/users/${userId}/reactivate`)
  }

  async resetUserPassword(userId: number) {
    const { data } = await this.client.post(`/admin/users/${userId}/reset-password`)
    return data
  }
}

export const apiClient = new ApiClient()
export const api = apiClient  // Export as 'api' for backward compatibility
