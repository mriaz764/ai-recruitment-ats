// src/types/job.ts

export type JobStatus = "draft" | "active" | "on_hold" | "closed" | "archived";
export type EmploymentType = "full_time" | "part_time" | "contract" | "internship" | "temporary";
export type WorkModel = "on_site" | "hybrid" | "remote";
export type ExperienceLevel = "entry" | "mid" | "senior" | "lead" | "executive";

export interface SalaryRange {
  min: number;
  max: number;
  currency: string; // e.g., "USD", "EUR", "PKR"
  interval: "yearly" | "monthly" | "hourly";
}

export interface HiringTeamMember {
  user_id: number;
  name: string;
  email: string;
  role: "hiring_manager" | "recruiter" | "interviewer";
}

export interface JobMatchCriteria {
  id: number;
  job_id: number;
  keyword: string;
  category: "skill" | "certification" | "education" | "domain_knowledge";
  weight: number; // 1 to 5 scale for AI scoring algorithms
  is_required: boolean; // Hard filter / Knockout requirement
}

export interface Job {
  id: number;
  organization_id: number;
  title: string;
  code?: string; // Requisition Code, e.g., "ENG-2026-042"
  department: string;
  location: string;
  work_model: WorkModel;
  employment_type: EmploymentType;
  experience_level: ExperienceLevel;
  status: JobStatus;
  
  description: string;
  requirements?: string;
  benefits?: string;
  
  salary_range?: SalaryRange;
  hiring_team?: HiringTeamMember[];
  match_criteria?: JobMatchCriteria[];
  
  applicant_count: number;
  pipeline_id?: number;
  
  created_by_id: number;
  created_at: string;
  updated_at?: string;
  closed_at?: string;
}

// Data Transfer Objects (DTOs)
export interface CreateJobPayload {
  title: string;
  code?: string;
  department: string;
  location: string;
  work_model: WorkModel;
  employment_type: EmploymentType;
  experience_level: ExperienceLevel;
  description: string;
  requirements?: string;
  benefits?: string;
  salary_range?: SalaryRange;
  pipeline_id?: number;
  hiring_team_ids?: { user_id: number; role: HiringTeamMember["role"] }[];
}

export interface UpdateJobPayload extends Partial<CreateJobPayload> {
  status?: JobStatus;
}

export interface JobQueryParams {
  page?: number;
  size?: number;
  search?: string;
  status?: JobStatus;
  department?: string;
  work_model?: WorkModel;
}
