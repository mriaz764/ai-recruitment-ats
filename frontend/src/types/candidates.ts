export interface Candidate {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  skills?: string[];
  organization_id: number;
  created_at: string;
}

export interface CandidateResume {
  id: number;
  candidate_id: number;
  file_name: string;
  file_path: string;
  raw_text?: string;
  uploaded_at: string;
}