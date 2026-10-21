import { apiClient } from "@/lib/api";
import { Job, CreateJobPayload } from "@/types/api";

export const jobsService = {
  async getJobs(): Promise<Job[]> {
    return apiClient.get<Job[]>("/jobs/");
  },

  async getJobById(jobId: number): Promise<Job> {
    return apiClient.get<Job>(`/jobs/${jobId}`);
  },

  async createJob(payload: CreateJobPayload): Promise<Job> {
    return apiClient.post<Job>("/jobs/", payload);
  },

  async toggleJobStatus(jobId: number, isActive: boolean): Promise<Job> {
    return apiClient.put<Job>(`/jobs/${jobId}`, { is_active: isActive });
  },
};