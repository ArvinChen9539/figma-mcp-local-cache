import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
});

export const getCacheList = (params) => api.get('/cache', { params });
export const deleteCache = (id) => api.delete(`/cache/${id}`);
export const syncCache = (id) => api.post(`/sync/${id}`);
export const getCacheDetail = (id) => api.get(`/cache/${id}`);

export default api;
