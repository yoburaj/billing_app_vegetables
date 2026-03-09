import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to include the auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add a response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Handle unauthorized error (e.g., redirect to login)
      localStorage.removeItem('token');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  login: (credentials) => {
    // Standard OAuth2 form data for FastAPI
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    return api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
  },
  signup: (userData) => api.post('/auth/signup', userData),
  forgotPassword: (data) => api.post('/auth/forgot-password', data),
  resetPassword: (data) => api.post('/auth/reset-password', data),
};

export const billingApi = {
  createBill: (billData) => api.post('/billing/create', billData),
  getBill: (id) => api.get(`/billing/${id}`),
  getHistory: () => api.get('/billing/history'),
  getDashboardStats: () => api.get('/billing/dashboard/stats'),
  getBillPdf: (id) => api.get(`/billing/${id}/pdf`, { responseType: 'blob' }),
  lookupCustomer: (phone) => api.get(`/customers/lookup/${phone}`),
  getCustomerStats: () => api.get('/customers/stats'),
};

export const inventoryApi = {
  getInventory: () => api.get('/inventory/'),
  updateItem: (id, data) => api.put(`/inventory/${id}`, data),
  setupInventory: (data) => api.post('/inventory/setup', data),
  deleteItem: (id) => api.delete(`/inventory/${id}`),
  addItems: (data) => api.post('/inventory/bulk-sync', data),
};

export default api;
