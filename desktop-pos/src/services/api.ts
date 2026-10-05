import axios, { AxiosResponse } from "axios";

const BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

export const axiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 10_000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor – attach Bearer token
axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor – handle 401
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      // TODO: redirect to login once auth module is implemented
    }
    return Promise.reject(error);
  },
);

/** Thin wrapper for GET requests returning the response data directly. */
export const apiClient = {
  get: async <T = unknown>(url: string, params?: Record<string, unknown>): Promise<T> => {
    const response: AxiosResponse<T> = await axiosInstance.get(url, { params });
    return response.data;
  },
  post: async <T = unknown>(url: string, data?: unknown): Promise<T> => {
    const response: AxiosResponse<T> = await axiosInstance.post(url, data);
    return response.data;
  },
  put: async <T = unknown>(url: string, data?: unknown): Promise<T> => {
    const response: AxiosResponse<T> = await axiosInstance.put(url, data);
    return response.data;
  },
  delete: async <T = unknown>(url: string): Promise<T> => {
    const response: AxiosResponse<T> = await axiosInstance.delete(url);
    return response.data;
  },
};
