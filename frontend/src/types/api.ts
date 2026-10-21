export interface User {
  id: number;
  email: string;
  full_name: string;
  organization_id: number;
  role?: string;
  created_at?: string;
}

export interface Organization {
  id: number;
  name: string;
  slug: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
}

export interface LoginRequest {
  username: string; // Form-data email mapped to OAuth2 password flow
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
  organization_name: string;
}

export interface ApiErrorDetail {
  detail: string | { msg: string; type: string }[];
}