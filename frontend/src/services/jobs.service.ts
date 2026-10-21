import { apiClient } from "@/lib/api";
import { Job, CreateJobPayload, PaginatedResponse } from "@/types";

export const jobService = {
  async getJobs(params?: { limit?: number; skip?: number }): Promise<PaginatedResponse<Job>> {
    return apiClient.get<PaginatedResponse<Job>>("/jobs", { params });
  },

  async getJobById(id: number | string): Promise<Job> {
    return apiClient.get<Job>(`/jobs/${id}`);
  },

  async createJob(payload: CreateJobPayload): Promise<Job> {
    return apiClient.post<Job>("/jobs", payload);
  },
};

export const jobsService = jobService;