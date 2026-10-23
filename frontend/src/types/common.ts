export interface ApiErrorDetail {
  detail: string | Array<{ msg: string; type?: string }>;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
}