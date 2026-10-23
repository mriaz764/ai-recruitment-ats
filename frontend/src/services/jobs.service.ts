// src/services/job.service.ts

import { apiClient } from "@/lib/api";
import type {
  Job,
  CreateJobPayload,
  UpdateJobPayload,
  JobQueryParams,
  PaginatedResponse,
  JobStatus,
  JobMatchCriteria,
} from "@/types";

export const jobService = {
  /**
   * Fetches a paginated list of job requisitions with optional filters.
   */
  async getJobs(
    params?: JobQueryParams,
    signal?: AbortSignal
  ): Promise<PaginatedResponse<Job>> {
    return apiClient.get<PaginatedResponse<Job>>("/jobs", {
      params,
      signal,
    });
  },

  /**
   * Fetches a single job requisition by ID.
   */
  async getJobById(id: number | string, signal?: AbortSignal): Promise<Job> {
    return apiClient.get<Job>(`/jobs/${id}`, { signal });
  },

  /**
   * Creates a new job requisition (defaults to "draft" or "active" based on payload).
   */
  async createJob(payload: CreateJobPayload): Promise<Job> {
    return apiClient.post<Job>("/jobs", payload);
  },

  /**
   * Updates job requisition fields.
   */
  async updateJob(id: number | string, payload: UpdateJobPayload): Promise<Job> {
    return apiClient.patch<Job>(`/jobs/${id}`, payload);
  },

  /**
   * Updates only the operational status of a job (e.g., Publish, Archive, Close).
   */
  async updateJobStatus(id: number | string, status: JobStatus): Promise<Job> {
    return apiClient.patch<Job>(`/jobs/${id}/status`, { status });
  },

  /**
   * Deletes a draft job requisition.
   */
  async deleteJob(id: number | string): Promise<void> {
    return apiClient.delete(`/jobs/${id}`);
  },

  /**
   * Configures AI matching parameters (skills/weights) for resume screening.
   */
  async updateMatchCriteria(
    jobId: number | string,
    criteria: Omit<JobMatchCriteria, "id" | "job_id">[]
  ): Promise<JobMatchCriteria[]> {
    return apiClient.put<JobMatchCriteria[]>(`/jobs/${jobId}/criteria`, { criteria });
  },
};