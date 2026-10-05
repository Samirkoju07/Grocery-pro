/** Health check API response types. */
export interface ServiceStatus {
  status: "ok" | "degraded" | "down";
  message: string;
}

export interface HealthResponse {
  status: "ok" | "degraded" | "down";
  version: string;
  environment: string;
  services: Record<string, ServiceStatus>;
}

/** Generic paginated response. */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

/** Generic API error. */
export interface ApiError {
  code: string;
  message: string;
  field?: string;
}
