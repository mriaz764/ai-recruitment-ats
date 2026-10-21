import { apiClient } from "@/lib/api";
import { Interview, ScheduleInterviewPayload } from "@/types/api";

export const interviewsService = {
  async getInterviews(): Promise<Interview[]> {
    return apiClient.get<Interview[]>("/interviews/");
  },

  async scheduleInterview(payload: ScheduleInterviewPayload): Promise<Interview> {
    return apiClient.post<Interview>("/interviews/", payload);
  },
};