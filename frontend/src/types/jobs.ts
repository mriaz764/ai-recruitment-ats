export interface JobMatchCriteria {
  id: number;
  job_id: number;
  keyword: string;
  weight: number;
  is_required: boolean;
}

export interface Job {
  id: number;
  organization_id: number;
  title: string;
  description: string;
  department?: string;
  location?: string;
  employment_type?: string;
  is_active: boolean;
  status: "draft" | "active" | "archived" | "closed";
  created_at: string;
  updated_at?: string;
}

export interface CreateJobPayload {
  title: string;
  description: string;
  department?: string;
  location?: string;
  employment_type?: string;
}