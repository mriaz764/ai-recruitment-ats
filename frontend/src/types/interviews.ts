export interface Interview {
  id: number;
  application_id: number;
  title: string;
  scheduled_at: string;
  duration_minutes: number;
  location_or_link?: string;
  interviewer_emails?: string[];
  organization_id: number;
  created_at: string;
}

export interface ScheduleInterviewPayload {
  application_id: number;
  title: string;
  scheduled_at: string;
  duration_minutes: number;
  location_or_link?: string;
  interviewer_emails?: string[];
}