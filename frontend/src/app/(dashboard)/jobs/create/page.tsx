// src/app/(dashboard)/jobs/create/page.tsx

"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm, useFieldArray } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  createJobSchema,
  type CreateJobFormValues,
  STEP_FIELDS,
} from "@/lib/validations/job";
import { jobService } from "@/services";

const STEPS = [
  {
    id: 1,
    title: "Requisition Basics",
    desc: "Title, department & work model",
  },
  {
    id: 2,
    title: "Pay Transparency",
    desc: "Salary range & employee benefits",
  },
  { id: 3, title: "Hiring Team", desc: "Assign managers & interviewers" },
  {
    id: 4,
    title: "AI Match Parameters",
    desc: "Weighted skills & knockout criteria",
  },
];

export default function CreateJobPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const form = useForm<CreateJobFormValues>({
    resolver: zodResolver(createJobSchema),
    defaultValues: {
      title: "",
      code: "",
      department: "",
      location: "",
      work_model: "hybrid",
      employment_type: "full_time",
      experience_level: "mid",
      description: "",
      requirements: "",
      salary_range: {
        min: 80000,
        max: 120000,
        currency: "USD",
        interval: "yearly",
      },
      benefits: "",
      hiring_team: [
        {
          user_id: 1,
          name: "Lead Recruiter",
          email: "recruiter@company.com",
          role: "recruiter",
        },
      ],
      match_criteria: [
        {
          keyword: "TypeScript",
          category: "skill",
          weight: 5,
          is_required: true,
        },
        {
          keyword: "Next.js",
          category: "skill",
          weight: 4,
          is_required: false,
        },
      ],
    },
    mode: "onTouched",
  });

  const {
    register,
    handleSubmit,
    trigger,
    control,
    formState: { errors },
  } = form;

  // Field Arrays for Dynamic Steps 3 & 4
  const {
    fields: teamFields,
    append: appendTeam,
    remove: removeTeam,
  } = useFieldArray({ control, name: "hiring_team" });

  const {
    fields: criteriaFields,
    append: appendCriteria,
    remove: removeCriteria,
  } = useFieldArray({ control, name: "match_criteria" });

  // Handle Step Navigation with Validation
  const handleNext = async () => {
    const fieldsToValidate =
      STEP_FIELDS[currentStep as keyof typeof STEP_FIELDS];
    const isValid = await trigger(fieldsToValidate as any);

    if (isValid) {
      setCurrentStep((prev) => Math.min(prev + 1, STEPS.length));
    }
  };

  const handlePrev = () => {
    setCurrentStep((prev) => Math.max(prev - 1, 1));
  };

  const onSubmit = async (values: CreateJobFormValues) => {
    setIsSubmitting(true);
    setSubmitError(null);

    try {
      const createdJob = await jobService.createJob({
        title: values.title,
        code: values.code || undefined,
        department: values.department,
        location: values.location,
        work_model: values.work_model,
        employment_type: values.employment_type,
        experience_level: values.experience_level,
        description: values.description,
        requirements: values.requirements,
        benefits: values.benefits,
        salary_range: values.salary_range,
        hiring_team_ids: values.hiring_team.map((m) => ({
          user_id: m.user_id,
          role: m.role,
        })),
      });

      // If AI match criteria exists, configure parameters
      if (values.match_criteria && values.match_criteria.length > 0) {
        await jobService.updateMatchCriteria(
          createdJob.id,
          values.match_criteria,
        );
      }

      router.push("/jobs");
    } catch (err: any) {
      setSubmitError(
        err?.message ||
          "Failed to create requisition. Please check your inputs.",
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 text-slate-100 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white">
          Create Job Requisition
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Configure position details, salary compliance, hiring team
          permissions, and AI screening criteria.
        </p>
      </div>

      {/* Progress Wizard Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {STEPS.map((step) => {
          const isActive = step.id === currentStep;
          const isComplete = step.id < currentStep;

          return (
            <div
              key={step.id}
              className={`p-3 rounded-xl border transition-colors ${
                isActive
                  ? "bg-blue-600/10 border-blue-500/40 text-blue-400"
                  : isComplete
                    ? "bg-slate-900 border-emerald-500/30 text-emerald-400"
                    : "bg-slate-900/50 border-slate-800 text-slate-500"
              }`}
            >
              <div className="flex items-center gap-2">
                <span
                  className={`w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold ${
                    isActive
                      ? "bg-blue-500 text-white"
                      : isComplete
                        ? "bg-emerald-500 text-slate-950"
                        : "bg-slate-800 text-slate-400"
                  }`}
                >
                  {isComplete ? "✓" : step.id}
                </span>
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-300">
                  Step {step.id}
                </span>
              </div>
              <p className="text-xs font-medium text-white mt-1.5 truncate">
                {step.title}
              </p>
            </div>
          );
        })}
      </div>

      {/* Form Container */}
      <form
        onSubmit={handleSubmit(onSubmit)}
        className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6"
      >
        {submitError && (
          <div className="p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-lg text-sm">
            {submitError}
          </div>
        )}

        {/* STEP 1: REQUISITION BASICS */}
        {currentStep === 1 && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-white border-b border-slate-800 pb-2">
              Step 1: Requisition Basics
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="sm:col-span-2 space-y-1">
                <label className="text-xs font-medium text-slate-300">
                  Job Title *
                </label>
                <input
                  {...register("title")}
                  placeholder="e.g. Senior Full-Stack Engineer"
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                {errors.title && (
                  <p className="text-xs text-red-400">{errors.title.message}</p>
                )}
              </div>

              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-300">
                  Requisition Code
                </label>
                <input
                  {...register("code")}
                  placeholder="ENG-2026-001"
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-300">
                  Department *
                </label>
                <input
                  {...register("department")}
                  placeholder="e.g. Engineering"
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                {errors.department && (
                  <p className="text-xs text-red-400">
                    {errors.department.message}
                  </p>
                )}
              </div>

              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-300">
                  Primary Location *
                </label>
                <input
                  {...register("location")}
                  placeholder="e.g. San Francisco, CA / Remote"
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                {errors.location && (
                  <p className="text-xs text-red-400">
                    {errors.location.message}
                  </p>
                )}
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-300">
                  Work Model *
                </label>
                <select
                  {...register("work_model")}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="on_site">On-Site</option>
                  <option value="hybrid">Hybrid</option>
                  <option value="remote">Remote</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-300">
                  Employment Type *
                </label>
                <select
                  {...register("employment_type")}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="full_time">Full-time</option>
                  <option value="part_time">Part-time</option>
                  <option value="contract">Contract</option>
                  <option value="internship">Internship</option>
                  <option value="temporary">Temporary</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-300">
                  Experience Level *
                </label>
                <select
                  {...register("experience_level")}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="entry">Entry Level</option>
                  <option value="mid">Mid Level</option>
                  <option value="senior">Senior Level</option>
                  <option value="lead">Lead / Staff</option>
                  <option value="executive">Executive</option>
                </select>
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-xs font-medium text-slate-300">
                Job Description *
              </label>
              <textarea
                rows={5}
                {...register("description")}
                placeholder="Provide comprehensive details about role responsibilities..."
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              {errors.description && (
                <p className="text-xs text-red-400">
                  {errors.description.message}
                </p>
              )}
            </div>
          </div>
        )}

        {/* STEP 2: PAY TRANSPARENCY */}
        {currentStep === 2 && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-white border-b border-slate-800 pb-2">
              Step 2: Pay Transparency & Benefits
            </h2>
            <p className="text-xs text-slate-400">
              Provide structured compensation data to maintain compliance with
              global pay transparency mandates.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-300">
                  Min Salary *
                </label>
                <input
                  type="number"
                  {...register("salary_range.min", { valueAsNumber: true })}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                {errors.salary_range?.min && (
                  <p className="text-xs text-red-400">
                    {errors.salary_range.min.message}
                  </p>
                )}
              </div>

              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-300">
                  Max Salary *
                </label>
                <input
                  type="number"
                  {...register("salary_range.max", { valueAsNumber: true })}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                {errors.salary_range?.max && (
                  <p className="text-xs text-red-400">
                    {errors.salary_range.max.message}
                  </p>
                )}
              </div>

              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-300">
                  Currency *
                </label>
                <input
                  {...register("salary_range.currency")}
                  placeholder="USD"
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-300">
                  Frequency *
                </label>
                <select
                  {...register("salary_range.interval")}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="yearly">Yearly</option>
                  <option value="monthly">Monthly</option>
                  <option value="hourly">Hourly</option>
                </select>
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-xs font-medium text-slate-300">
                Benefits & Perks Summary
              </label>
              <textarea
                rows={3}
                {...register("benefits")}
                placeholder="Health insurance, 401(k) matching, flexible working hours..."
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        )}

        {/* STEP 3: HIRING TEAM */}
        {currentStep === 3 && (
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <h2 className="text-lg font-semibold text-white">
                Step 3: Hiring Team Assignments
              </h2>
              <button
                type="button"
                onClick={() =>
                  appendTeam({
                    user_id: Date.now(),
                    name: "",
                    email: "",
                    role: "interviewer",
                  })
                }
                className="text-xs px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-colors"
              >
                + Add Team Member
              </button>
            </div>

            {errors.hiring_team?.root && (
              <p className="text-xs text-red-400">
                {errors.hiring_team.root.message}
              </p>
            )}

            <div className="space-y-3">
              {teamFields.map((field, index) => (
                <div
                  key={field.id}
                  className="p-3 bg-slate-950 border border-slate-800 rounded-lg grid grid-cols-1 sm:grid-cols-4 gap-3 items-end"
                >
                  <div>
                    <label className="text-xs font-medium text-slate-400">
                      Name
                    </label>
                    <input
                      {...register(`hiring_team.${index}.name`)}
                      placeholder="Jane Doe"
                      className="w-full px-2.5 py-1.5 bg-slate-900 border border-slate-800 rounded text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-medium text-slate-400">
                      Email
                    </label>
                    <input
                      {...register(`hiring_team.${index}.email`)}
                      placeholder="jane@company.com"
                      className="w-full px-2.5 py-1.5 bg-slate-900 border border-slate-800 rounded text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-medium text-slate-400">
                      Role
                    </label>
                    <select
                      {...register(`hiring_team.${index}.role`)}
                      className="w-full px-2.5 py-1.5 bg-slate-900 border border-slate-800 rounded text-sm text-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="hiring_manager">Hiring Manager</option>
                      <option value="recruiter">Recruiter</option>
                      <option value="interviewer">Interviewer</option>
                    </select>
                  </div>
                  <div>
                    <button
                      type="button"
                      disabled={teamFields.length <= 1}
                      onClick={() => removeTeam(index)}
                      className="w-full py-1.5 text-xs text-red-400 hover:text-red-300 bg-red-500/10 border border-red-500/20 rounded disabled:opacity-30 disabled:cursor-not-allowed"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* STEP 4: AI MATCH CRITERIA */}
        {currentStep === 4 && (
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <div>
                <h2 className="text-lg font-semibold text-white">
                  Step 4: AI Match Criteria & Knockouts
                </h2>
                <p className="text-xs text-slate-400">
                  Assign weights (1–5) to skills for automated candidate
                  scoring. Mark critical items as Knockouts.
                </p>
              </div>
              <button
                type="button"
                onClick={() =>
                  appendCriteria({
                    keyword: "",
                    category: "skill",
                    weight: 3,
                    is_required: false,
                  })
                }
                className="text-xs px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-colors"
              >
                + Add Criterion
              </button>
            </div>

            <div className="space-y-3">
              {criteriaFields.map((field, index) => (
                <div
                  key={field.id}
                  className="p-3 bg-slate-950 border border-slate-800 rounded-lg grid grid-cols-1 sm:grid-cols-12 gap-3 items-center"
                >
                  <div className="sm:col-span-4">
                    <label className="text-xs font-medium text-slate-400">
                      Skill / Keyword
                    </label>
                    <input
                      {...register(`match_criteria.${index}.keyword`)}
                      placeholder="e.g. React, AWS, PMP"
                      className="w-full px-2.5 py-1.5 bg-slate-900 border border-slate-800 rounded text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div className="sm:col-span-3">
                    <label className="text-xs font-medium text-slate-400">
                      Category
                    </label>
                    <select
                      {...register(`match_criteria.${index}.category`)}
                      className="w-full px-2.5 py-1.5 bg-slate-900 border border-slate-800 rounded text-sm text-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="skill">Skill</option>
                      <option value="certification">Certification</option>
                      <option value="education">Education</option>
                      <option value="domain_knowledge">Domain Knowledge</option>
                    </select>
                  </div>

                  <div className="sm:col-span-2">
                    <label className="text-xs font-medium text-slate-400">
                      Weight (1-5)
                    </label>
                    <input
                      type="number"
                      min={1}
                      max={5}
                      {...register(`match_criteria.${index}.weight`, {
                        valueAsNumber: true,
                      })}
                      className="w-full px-2.5 py-1.5 bg-slate-900 border border-slate-800 rounded text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div className="sm:col-span-2 flex items-center gap-2 pt-4">
                    <input
                      type="checkbox"
                      id={`knockout-${index}`}
                      {...register(`match_criteria.${index}.is_required`)}
                      className="rounded border-slate-800 text-blue-600 focus:ring-blue-500 bg-slate-900"
                    />
                    <label
                      htmlFor={`knockout-${index}`}
                      className="text-xs font-medium text-amber-400 cursor-pointer"
                    >
                      Knockout
                    </label>
                  </div>

                  <div className="sm:col-span-1 pt-4 text-right">
                    <button
                      type="button"
                      onClick={() => removeCriteria(index)}
                      className="text-xs text-red-400 hover:text-red-300"
                    >
                      ✕
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Wizard Footer Controls */}
        <div className="flex items-center justify-between border-t border-slate-800 pt-4">
          <button
            type="button"
            disabled={currentStep === 1 || isSubmitting}
            onClick={handlePrev}
            className="px-4 py-2 border border-slate-800 text-slate-300 rounded-lg text-sm hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            Back
          </button>

          {currentStep < STEPS.length ? (
            <button
              type="button"
              onClick={handleNext}
              className="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition-colors"
            >
              Continue to Step {currentStep + 1}
            </button>
          ) : (
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-6 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-sm font-semibold transition-colors disabled:opacity-50"
            >
              {isSubmitting
                ? "Publishing Requisition..."
                : "Create & Publish Requisition"}
            </button>
          )}
        </div>
      </form>
    </div>
  );
}
