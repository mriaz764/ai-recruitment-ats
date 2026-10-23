import { Candidate } from "./candidates";
import { Job } from "./jobs";

export type ApplicationStage = 
  | "APPLIED" 
  | "SCREENING" 
  | "INTERVIEW" 
  | "OFFER" 
  | "HIRED" 
  | "REJECTED";

export interface Application {
  id: number;
  job_id: number;
  candidate_id: number;
  stage: ApplicationStage;
  notes?: string;
  organization_id: number;
  created_at: string;
  updated_at: string;
  candidate?: Candidate;
  job?: Job;
}

export interface UpdateStagePayload {
  stage: ApplicationStage;
  notes?: string;
}