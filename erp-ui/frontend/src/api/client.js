import axios from 'axios';
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
class ApiClient {
    constructor() {
        Object.defineProperty(this, "client", {
            enumerable: true,
            configurable: true,
            writable: true,
            value: void 0
        });
        this.client = axios.create({
            baseURL: API_URL,
            headers: {
                'Content-Type': 'application/json',
            },
        });
        // Add token to requests
        this.client.interceptors.request.use((config) => {
            const token = localStorage.getItem('access_token');
            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
            }
            return config;
        });
        // Handle auth errors
        this.client.interceptors.response.use((response) => response, (error) => {
            if (error.response?.status === 401) {
                localStorage.removeItem('access_token');
                localStorage.removeItem('user');
                window.location.href = '/login';
            }
            return Promise.reject(error);
        });
    }
    // Auth endpoints
    async register(username, email, password, fullName) {
        const { data } = await this.client.post('/auth/register', {
            username,
            email,
            password,
            full_name: fullName,
        });
        return data;
    }
    async login(username, password) {
        const { data } = await this.client.post('/auth/login', {
            username,
            password,
        });
        return data;
    }
    async refreshToken() {
        const { data } = await this.client.post('/auth/refresh');
        return data;
    }
    async getCurrentUser() {
        const { data } = await this.client.get('/auth/me');
        return data;
    }
    async changePassword(oldPassword, newPassword) {
        await this.client.post('/auth/change-password', {
            old_password: oldPassword,
            new_password: newPassword,
        });
    }
    // PPIC endpoints
    async createManufacturingOrder(params) {
        const { data } = await this.client.post('/ppic/manufacturing-order', params);
        return data;
    }
    async getManufacturingOrder(moId) {
        const { data } = await this.client.get(`/ppic/manufacturing-order/${moId}`);
        return data;
    }
    async listManufacturingOrders(filters) {
        const { data } = await this.client.get('/ppic/manufacturing-orders', { params: filters });
        return data;
    }
    async approveManufacturingOrder(moId) {
        const { data } = await this.client.post(`/ppic/manufacturing-order/${moId}/approve`);
        return data;
    }
    // Cutting endpoints
    async receiveSPK(params) {
        const { data } = await this.client.post('/cutting/receive-spk', params);
        return data;
    }
    async completeCutting(workOrderId, params) {
        const { data } = await this.client.post(`/cutting/complete/${workOrderId}`, params);
        return data;
    }
    async checkLineCleanance(department, lineId) {
        const { data } = await this.client.get('/cutting/line-clearance', {
            params: { department, line_id: lineId }
        });
        return data;
    }
    // Sewing endpoints
    async acceptSewingTransfer(params) {
        const { data } = await this.client.post('/sewing/accept-transfer', params);
        return data;
    }
    async completeSewing(workOrderId, params) {
        const { data } = await this.client.post(`/sewing/complete/${workOrderId}`, params);
        return data;
    }
    // Finishing endpoints
    async acceptFinishingWIP(params) {
        const { data } = await this.client.post('/finishing/accept-wip', params);
        return data;
    }
    async performMetalDetector(batchNumber) {
        const { data } = await this.client.post('/finishing/metal-detector', { batch_number: batchNumber });
        return data;
    }
    async convertToFinishGood(params) {
        const { data } = await this.client.post('/finishing/convert-fg', params);
        return data;
    }
    // Packing endpoints
    async sortByDestination(params) {
        const { data } = await this.client.post('/packing/sort-destination', params);
        return data;
    }
    async packageCartons(params) {
        const { data } = await this.client.post('/packing/package-cartons', params);
        return data;
    }
    // Quality endpoints
    async performLabTest(params) {
        const { data } = await this.client.post('/quality/lab-test/perform', params);
        return data;
    }
    async getLabTestSummary(batchNumber) {
        const { data } = await this.client.get(`/quality/lab-test/batch/${batchNumber}/summary`);
        return data;
    }
    async performInlineQC(params) {
        const { data } = await this.client.post('/quality/inspection/inline', params);
        return data;
    }
    // Warehouse endpoints
    async getStockLevel(productId) {
        const { data } = await this.client.get(`/warehouse/stock/${productId}`);
        return data;
    }
    async createTransfer(params) {
        const { data } = await this.client.post('/warehouse/transfer', params);
        return data;
    }
    async listLocations() {
        const { data } = await this.client.get('/warehouse/locations');
        return data;
    }
    // Admin endpoints
    async listUsers(filters) {
        const { data } = await this.client.get('/admin/users', { params: filters });
        return data;
    }
    async getUserDetails(userId) {
        const { data } = await this.client.get(`/admin/users/${userId}`);
        return data;
    }
    async updateUser(userId, params) {
        const { data } = await this.client.put(`/admin/users/${userId}`, params);
        return data;
    }
    async deactivateUser(userId) {
        await this.client.post(`/admin/users/${userId}/deactivate`);
    }
    async reactivateUser(userId) {
        await this.client.post(`/admin/users/${userId}/reactivate`);
    }
    async resetUserPassword(userId) {
        const { data } = await this.client.post(`/admin/users/${userId}/reset-password`);
        return data;
    }
}
export const apiClient = new ApiClient();
