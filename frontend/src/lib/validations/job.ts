// src/lib/validations/job.ts

import { z } from "zod";

export const salaryRangeSchema = z
  .object({
    min: z
      .number({ message: "Min salary is required" })
      .min(0, "Min salary must be positive"),
    max: z
      .number({ message: "Max salary is required" })
      .min(0, "Max salary must be positive"),
    currency: z.string().min(1, "Currency is required"),
    interval: z.enum(["yearly", "monthly", "hourly"]),
  })
  .refine((data) => data.max >= data.min, {
    message: "Max salary must be greater than or equal to min salary",
    path: ["max"],
  });

export const hiringTeamMemberSchema = z.object({
  user_id: z.number().min(1, "Team member selection is required"),
  name: z.string().min(1, "Name is required"),
  email: z.string().email("Valid email required"),
  role: z.enum(["hiring_manager", "recruiter", "interviewer"]),
});

export const matchCriteriaSchema = z.object({
  keyword: z.string().min(1, "Keyword/Skill cannot be empty"),
  category: z.enum(["skill", "certification", "education", "domain_knowledge"]),
  weight: z.number().min(1).max(5),
  is_required: z.boolean().default(false),
});

// Step-specific field field names for React Hook Form trigger()
export const STEP_FIELDS = {
  1: [
    "title",
    "code",
    "department",
    "location",
    "work_model",
    "employment_type",
    "experience_level",
    "description",
    "requirements",
  ],
  2: ["salary_range", "benefits"],
  3: ["hiring_team"],
  4: ["match_criteria"],
} as const;

export const createJobSchema = z.object({
  // Step 1: Basics
  title: z.string().min(3, "Job title must be at least 3 characters"),
  code: z.string().optional(),
  department: z.string().min(1, "Department is required"),
  location: z.string().min(1, "Location is required"),
  work_model: z.enum(["on_site", "hybrid", "remote"]),
  employment_type: z.enum(["full_time", "part_time", "contract", "internship", "temporary"]),
  experience_level: z.enum(["entry", "mid", "senior", "lead", "executive"]),
  description: z.string().min(20, "Job description must be at least 20 characters"),
  requirements: z.string().optional(),

  // Step 2: Pay Transparency
  salary_range: salaryRangeSchema.optional(),
  benefits: z.string().optional(),

  // Step 3: Hiring Team
  hiring_team: z.array(hiringTeamMemberSchema).min(1, "Assign at least one hiring team member"),

  // Step 4: AI Match Criteria
  match_criteria: z.array(matchCriteriaSchema).optional(),
});

export type CreateJobFormValues = z.infer<typeof createJobSchema>;