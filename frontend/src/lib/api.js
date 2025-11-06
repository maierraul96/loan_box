import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Applications API
export const applications = {
  list: async (params = {}) => {
    const response = await api.get('/applications', { params });
    return response.data;
  },
  get: async (id) => {
    const response = await api.get(`/applications/${id}`);
    return response.data;
  },
  create: async (data) => {
    const response = await api.post('/applications', data);
    return response.data;
  },
};

// Pipelines API
export const pipelines = {
  list: async (params = {}) => {
    const response = await api.get('/pipelines', { params });
    return response.data;
  },
  get: async (id) => {
    const response = await api.get(`/pipelines/${id}`);
    return response.data;
  },
  create: async (data) => {
    const response = await api.post('/pipelines', data);
    return response.data;
  },
  update: async (id, data) => {
    const response = await api.put(`/pipelines/${id}`, data);
    return response.data;
  },
  delete: async (id) => {
    const response = await api.delete(`/pipelines/${id}`);
    return response.data;
  },
};

// Runs API
export const runs = {
  list: async (params = {}) => {
    const response = await api.get('/runs', { params });
    return response.data;
  },
  get: async (id) => {
    const response = await api.get(`/runs/${id}`);
    return response.data;
  },
  execute: async (data) => {
    const response = await api.post('/runs', data);
    return response.data;
  },
};

// Step Catalog API
export const catalog = {
  getSteps: async () => {
    const response = await api.get('/steps/catalog');
    return response.data.steps; // Extract steps array from { steps: [...] }
  },
};

export default api;
