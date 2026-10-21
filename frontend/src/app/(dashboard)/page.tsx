"use client";

import React from "react";
import Link from "next/link";
import {
  Briefcase,
  Users,
  Calendar,
  ArrowUpRight,
  Plus,
  Clock,
  CheckCircle2,
  AlertCircle,
} from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { useJobs, useCandidates } from "@/hooks";
import { ROUTES } from "@/lib/routes";

export default function DashboardPage() {
  const { user } = useAuth();
  const { jobs, isLoading: isLoadingJobs } = useJobs({ limit: 5 });
  const { candidates, isLoading: isLoadingCandidates } = useCandidates({
    limit: 5,
  });

  const loading = isLoadingJobs || isLoadingCandidates;

  return (
    <div className="space-y-8">
      {/* Welcome Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-2xl bg-gradient-to-r from-blue-900/30 via-slate-900 to-slate-900 border border-slate-800">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">
            Welcome back, {user?.full_name?.split(" ")[0] ?? "Recruiter"} 👋
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Here is what is happening across your talent pipeline today.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href={ROUTES.DASHBOARD.JOBS}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition-colors shadow-lg shadow-blue-600/20"
          >
            <Plus className="w-4 h-4" />
            <span>Post New Job</span>
          </Link>
        </div>
      </div>

      {/* Pipeline Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Active Jobs
            </span>
            <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400">
              <Briefcase className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline justify-between">
            <p className="text-3xl font-bold text-slate-100">{jobs.length}</p>
            <span className="text-xs text-emerald-400 font-medium flex items-center gap-0.5">
              +12% <ArrowUpRight className="w-3 h-3" />
            </span>
          </div>
        </div>

        <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Total Candidates
            </span>
            <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
              <Users className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline justify-between">
            <p className="text-3xl font-bold text-slate-100">
              {candidates.length}
            </p>
            <span className="text-xs text-emerald-400 font-medium flex items-center gap-0.5">
              +24% <ArrowUpRight className="w-3 h-3" />
            </span>
          </div>
        </div>

        <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Interviews This Week
            </span>
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <Calendar className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline justify-between">
            <p className="text-3xl font-bold text-slate-100">8</p>
            <span className="text-xs text-slate-500">Scheduled</span>
          </div>
        </div>

        <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Time to Hire
            </span>
            <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400">
              <Clock className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline justify-between">
            <p className="text-3xl font-bold text-slate-100">18d</p>
            <span className="text-xs text-emerald-400 font-medium flex items-center gap-0.5">
              -2d avg
            </span>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Active Jobs */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-slate-100">
              Active Postings
            </h2>
            <Link
              href={ROUTES.DASHBOARD.JOBS}
              className="text-xs font-semibold text-blue-400 hover:text-blue-300 transition-colors"
            >
              View All
            </Link>
          </div>

          {loading ? (
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <div
                  key={i}
                  className="h-16 bg-slate-950 rounded-lg animate-pulse"
                />
              ))}
            </div>
          ) : jobs.length === 0 ? (
            <div className="p-8 text-center text-slate-500 border border-dashed border-slate-800 rounded-xl">
              <Briefcase className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No active job postings found.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {jobs.map((job) => (
                <div
                  key={job.id}
                  className="flex items-center justify-between p-4 rounded-xl bg-slate-950 border border-slate-800/80 hover:border-slate-700 transition-colors"
                >
                  <div>
                    <h3 className="text-sm font-semibold text-slate-200">
                      {job.title}
                    </h3>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {job.department ?? "Engineering"} •{" "}
                      {job.location ?? "Remote"}
                    </p>
                  </div>
                  <span className="px-2.5 py-1 text-xs font-medium rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 capitalize">
                    {job.status}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* System Activity Feed */}
        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
          <h2 className="text-lg font-semibold text-slate-100 mb-6">
            Pipeline Activity
          </h2>
          <div className="space-y-4">
            <div className="flex items-start gap-3 text-xs">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <div>
                <p className="text-slate-300">
                  Candidate match score updated for Senior Backend Role.
                </p>
                <span className="text-slate-500 text-[10px]">10 mins ago</span>
              </div>
            </div>
            <div className="flex items-start gap-3 text-xs">
              <Calendar className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
              <div>
                <p className="text-slate-300">
                  Interview confirmed with Sarah Jenkins.
                </p>
                <span className="text-slate-500 text-[10px]">1 hour ago</span>
              </div>
            </div>
            <div className="flex items-start gap-3 text-xs">
              <AlertCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
              <div>
                <p className="text-slate-300">
                  3 new applications pending initial AI screening.
                </p>
                <span className="text-slate-500 text-[10px]">3 hours ago</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
