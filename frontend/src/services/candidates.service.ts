import { apiClient } from "@/lib/api";
import { Candidate, PaginatedResponse } from "@/types";

export const candidateService = {
  async getCandidates(params?: { limit?: number; skip?: number }): Promise<PaginatedResponse<Candidate>> {
    return apiClient.get<PaginatedResponse<Candidate>>("/candidates", { params });
  },

  async getCandidateById(id: number | string): Promise<Candidate> {
    return apiClient.get<Candidate>(`/candidates/${id}`);
  },
};

export const candidatesService = candidateService;