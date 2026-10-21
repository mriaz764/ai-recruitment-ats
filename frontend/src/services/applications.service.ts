import { apiClient } from "@/lib/api";
import { Application, UpdateStagePayload } from "@/types";

export const applicationsService = {
  async getApplications(): Promise<Application[]> {
    return apiClient.get<Application[]>("/applications/");
  },

  async updateStage(applicationId: number, payload: UpdateStagePayload): Promise<Application> {
    return apiClient.put<Application>(`/applications/${payload.stage}`, payload);
  },
};