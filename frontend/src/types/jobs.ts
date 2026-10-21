export interface JobMatchCriteria {
  id: number;
  job_id: number;
  keyword: string;
  weight: number;
  is_required: boolean;
}

export interface Job {
  id: number;
  title: string;
  description: string;
  department?: string;
  location?: string;
  employment_type?: string;
  is_active: boolean;
  organization_id: number;
  created_at: string;
  criteria?: JobMatchCriteria[];
}

export interface CreateJobPayload {
  title: string;
  description: string;
  department?: string;
  location?: string;
  employment_type?: string;
  criteria?: Array<{
    keyword: string;
    weight: number;
    is_required: boolean;
  }>;
}