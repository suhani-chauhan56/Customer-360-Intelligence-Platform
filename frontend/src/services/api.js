import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Dashboard APIs
export const getDashboardOverview = (params) => apiClient.get('/dashboard', { params });

// Customer APIs
export const getCustomers = (params) => apiClient.get('/customers', { params });
export const getCustomerDetails = (id) => apiClient.get(`/customers/${id}`);
export const getCustomerDossier = (id) => apiClient.get(`/customers/${id}/dossier`);

// RFM Segmentation APIs
export const getRfmOverview = () => apiClient.get('/rfm');
export const getSegmentDetails = (segment) => apiClient.get(`/rfm/${segment}`);
export const compareSegments = (segmentA, segmentB) => apiClient.get('/rfm/compare', { params: { segmentA, segmentB } });
export const buildCohort = (payload) => apiClient.post('/rfm/cohort', payload);

// CLV APIs
export const getClvOverview = () => apiClient.get('/clv');
export const simulateClv = (payload) => apiClient.post('/clv/simulate', payload);

// Churn Intelligence APIs
export const getChurnOverview = () => apiClient.get('/churn');
export const simulateChurn = (payload) => apiClient.post('/churn/simulate', payload);

// Sentiment APIs
export const getSentimentOverview = () => apiClient.get('/sentiment');
export const searchReviews = (params) => apiClient.get('/sentiment/reviews', { params });

// Recommendations APIs
export const getRecommendations = (params) => apiClient.get('/recommendations', { params });
export const getCustomerNextBestCategory = (customerId) => apiClient.get(`/recommendations/customer/${customerId}`);

// Analytics Explorer APIs
export const getAnalyticsExplorer = (params) => apiClient.get('/analytics/explorer', { params });
export const exportCohortCsv = (params) => apiClient.get('/analytics/export', { params, responseType: 'blob' });

// Data Quality APIs
export const getDataQuality = () => apiClient.get('/data-quality');
export const logAuditEvent = (payload) => apiClient.post('/data-quality/audit', payload);

// Grounded AI APIs
export const askGroundedQuestion = (payload) => apiClient.post('/grounded-ai/ask', payload);

export default apiClient;
