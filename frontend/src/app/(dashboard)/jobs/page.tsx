// src/app/(dashboard)/jobs/page.tsx

"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useJobs } from "@/hooks/useJobs";
import { JobStatusBadge } from "@/components/jobs/JobStatusBadge";
import type { JobStatus, WorkModel } from "@/types";

export default function JobsDashboardPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedStatus, setSelectedStatus] = useState<JobStatus | "all">(
    "all",
  );
  const [selectedWorkModel, setSelectedWorkModel] = useState<WorkModel | "all">(
    "all",
  );
  const [page, setPage] = useState(1);
  const pageSize = 10;

  // Consume hook with query params
  const { jobs, total, totalPages, isLoading, error, refetch } = useJobs({
    page,
    size: pageSize,
    search: searchQuery,
    status: selectedStatus === "all" ? undefined : selectedStatus,
    work_model: selectedWorkModel === "all" ? undefined : selectedWorkModel,
  });

  const handleTabChange = (status: JobStatus | "all") => {
    setSelectedStatus(status);
    setPage(1); // Reset to page 1 on tab filter change
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
    setPage(1);
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto text-slate-100">
      {/* 1. Header & Requisition Creation CTA */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">
            Job Requisitions
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Manage open requisitions, hiring pipelines, and candidate match
            parameters.
          </p>
        </div>
        <Link
          href="/jobs/create"
          className="inline-flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white font-medium text-sm rounded-lg transition-colors shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <svg
            className="w-4 h-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 4v16m8-8H4"
            />
          </svg>
          Create Requisition
        </Link>
      </div>

      {/* 2. HR Metric Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl">
          <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">
            Total Requisitions
          </p>
          <p className="text-2xl font-bold text-white mt-1">{total}</p>
        </div>
        <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl">
          <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">
            Active Openings
          </p>
          <p className="text-2xl font-bold text-emerald-400 mt-1">
            {jobs.filter((j) => j.status === "active").length}
          </p>
        </div>
        <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl">
          <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">
            Draft Requisitions
          </p>
          <p className="text-2xl font-bold text-amber-400 mt-1">
            {jobs.filter((j) => j.status === "draft").length}
          </p>
        </div>
        <div className="p-4 bg-slate-900 border border-slate-800 rounded-xl">
          <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">
            Active Applicants
          </p>
          <p className="text-2xl font-bold text-blue-400 mt-1">
            {jobs.reduce((acc, curr) => acc + (curr.applicant_count || 0), 0)}
          </p>
        </div>
      </div>

      {/* 3. Filter Navigation & Controls */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-4">
        {/* Status Tabs */}
        <div className="flex items-center gap-1 border-b border-slate-800 pb-3 overflow-x-auto">
          {(["all", "active", "draft", "on_hold", "closed"] as const).map(
            (status) => (
              <button
                key={status}
                onClick={() => handleTabChange(status)}
                className={`px-3 py-1.5 text-xs font-medium rounded-lg capitalize whitespace-nowrap transition-colors ${
                  selectedStatus === status
                    ? "bg-slate-800 text-white shadow-sm"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
                }`}
              >
                {status === "all" ? "All Statuses" : status.replace("_", " ")}
              </button>
            ),
          )}
        </div>

        {/* Search & Secondary Dropdowns */}
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <svg
              className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
            <input
              type="text"
              placeholder="Search by job title, req code, or department..."
              value={searchQuery}
              onChange={handleSearchChange}
              className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <select
            value={selectedWorkModel}
            onChange={(e) =>
              setSelectedWorkModel(e.target.value as WorkModel | "all")
            }
            className="px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Work Models</option>
            <option value="on_site">On-Site</option>
            <option value="hybrid">Hybrid</option>
            <option value="remote">Remote</option>
          </select>
        </div>
      </div>

      {/* 4. Table / List View */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        {error && (
          <div className="p-4 bg-red-500/10 border-b border-red-500/20 text-red-400 text-sm flex items-center justify-between">
            <span>{error}</span>
            <button
              onClick={() => refetch()}
              className="underline text-xs hover:text-red-300"
            >
              Retry
            </button>
          </div>
        )}

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-sm">
            <thead>
              <tr className="bg-slate-950/50 border-b border-slate-800 text-xs uppercase tracking-wider text-slate-400">
                <th className="py-3.5 px-4 font-semibold">
                  Requisition & Title
                </th>
                <th className="py-3.5 px-4 font-semibold">Department</th>
                <th className="py-3.5 px-4 font-semibold">Work Model</th>
                <th className="py-3.5 px-4 font-semibold">Pay Range</th>
                <th className="py-3.5 px-4 font-semibold">Applicants</th>
                <th className="py-3.5 px-4 font-semibold">Status</th>
                <th className="py-3.5 px-4 font-semibold text-right">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {isLoading ? (
                // Skeleton Rows
                Array.from({ length: 5 }).map((_, i) => (
                  <tr key={i} className="animate-pulse">
                    <td className="py-4 px-4">
                      <div className="h-4 bg-slate-800 rounded w-36 mb-1" />
                      <div className="h-3 bg-slate-800/60 rounded w-20" />
                    </td>
                    <td className="py-4 px-4">
                      <div className="h-4 bg-slate-800 rounded w-24" />
                    </td>
                    <td className="py-4 px-4">
                      <div className="h-4 bg-slate-800 rounded w-16" />
                    </td>
                    <td className="py-4 px-4">
                      <div className="h-4 bg-slate-800 rounded w-28" />
                    </td>
                    <td className="py-4 px-4">
                      <div className="h-4 bg-slate-800 rounded w-12" />
                    </td>
                    <td className="py-4 px-4">
                      <div className="h-5 bg-slate-800 rounded-full w-16" />
                    </td>
                    <td className="py-4 px-4 text-right">
                      <div className="h-4 bg-slate-800 rounded w-8 ml-auto" />
                    </td>
                  </tr>
                ))
              ) : jobs.length === 0 ? (
                // Empty State
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-500">
                    <svg
                      className="w-12 h-12 mx-auto text-slate-600 mb-3"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={1.5}
                        d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                      />
                    </svg>
                    <p className="text-base font-medium text-slate-300">
                      No requisitions found
                    </p>
                    <p className="text-xs text-slate-500 mt-1">
                      Try adjusting your filters or create a new requisition.
                    </p>
                  </td>
                </tr>
              ) : (
                // Data Rows
                jobs.map((job) => (
                  <tr
                    key={job.id}
                    className="hover:bg-slate-800/30 transition-colors group"
                  >
                    <td className="py-4 px-4">
                      <Link
                        href={`/jobs/${job.id}`}
                        className="font-semibold text-white hover:text-blue-400 transition-colors"
                      >
                        {job.title}
                      </Link>
                      <div className="text-xs text-slate-500 font-mono mt-0.5">
                        {job.code || `REQ-${job.id}`}
                      </div>
                    </td>
                    <td className="py-4 px-4 text-slate-300">
                      {job.department || "General"}
                    </td>
                    <td className="py-4 px-4 text-slate-300 capitalize">
                      {job.work_model?.replace("_", " ") || "N/A"}
                    </td>
                    <td className="py-4 px-4 text-slate-300">
                      {job.salary_range ? (
                        <span>
                          {job.salary_range.currency}{" "}
                          {job.salary_range.min.toLocaleString()} -{" "}
                          {job.salary_range.max.toLocaleString()}
                        </span>
                      ) : (
                        <span className="text-slate-500 italic">
                          Not specified
                        </span>
                      )}
                    </td>
                    <td className="py-4 px-4 font-medium text-blue-400">
                      {job.applicant_count || 0}
                    </td>
                    <td className="py-4 px-4">
                      <JobStatusBadge status={job.status} />
                    </td>
                    <td className="py-4 px-4 text-right">
                      <Link
                        href={`/jobs/${job.id}`}
                        className="text-xs font-medium text-slate-400 hover:text-white px-2.5 py-1.5 rounded-lg border border-slate-800 hover:border-slate-700 bg-slate-950 transition-colors"
                      >
                        Manage
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* 5. Pagination Toolbar */}
        {!isLoading && jobs.length > 0 && (
          <div className="py-3 px-4 bg-slate-950/50 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
            <span>
              Showing Page <strong className="text-white">{page}</strong> of{" "}
              <strong className="text-white">{totalPages || 1}</strong> ({total}{" "}
              total requisitions)
            </span>
            <div className="flex items-center gap-2">
              <button
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                className="px-3 py-1.5 rounded-md border border-slate-800 bg-slate-900 hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              >
                Previous
              </button>
              <button
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
                className="px-3 py-1.5 rounded-md border border-slate-800 bg-slate-900 hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
