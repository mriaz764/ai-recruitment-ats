import { apiClient } from "@/lib/api";
import { Candidate, CandidateResume } from "@/types/api";

export const candidatesService = {
  async getCandidates(): Promise<Candidate[]> {
    return apiClient.get<Candidate[]>("/candidates/");
  },

  async searchCandidates(query: string): Promise<Candidate[]> {
    return apiClient.get<Candidate[]>(`/candidates/search?q=${encodeURIComponent(query)}`);
  },

  async uploadResume(candidateId: number, file: File): Promise<CandidateResume> {
    const formData = new FormData();
    formData.append("file", file);

    return apiClient.post<CandidateResume>(`/candidates/${candidateId}/resumes`, formData);
  },
};