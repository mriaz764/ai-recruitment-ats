// src/components/jobs/JobStatusBadge.tsx

import React from "react";
import type { JobStatus } from "@/types";

interface JobStatusBadgeProps {
  status: JobStatus;
  className?: string;
}

const STATUS_CONFIG: Record<
  JobStatus,
  { label: string; bg: string; text: string; dot: string }
> = {
  active: {
    label: "Active",
    bg: "bg-emerald-500/10 border-emerald-500/20",
    text: "text-emerald-400",
    dot: "bg-emerald-400",
  },
  draft: {
    label: "Draft",
    bg: "bg-amber-500/10 border-amber-500/20",
    text: "text-amber-400",
    dot: "bg-amber-400",
  },
  on_hold: {
    label: "On Hold",
    bg: "bg-blue-500/10 border-blue-500/20",
    text: "text-blue-400",
    dot: "bg-blue-400",
  },
  closed: {
    label: "Closed",
    bg: "bg-zinc-500/10 border-zinc-500/20",
    text: "text-zinc-400",
    dot: "bg-zinc-400",
  },
  archived: {
    label: "Archived",
    bg: "bg-purple-500/10 border-purple-500/20",
    text: "text-purple-400",
    dot: "bg-purple-400",
  },
};

export const JobStatusBadge: React.FC<JobStatusBadgeProps> = ({
  status,
  className = "",
}) => {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.draft;

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${config.bg} ${config.text} ${className}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${config.dot}`} />
      {config.label}
    </span>
  );
};
