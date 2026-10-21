"use client";

import React from "react";
import { useAuth } from "@/context/AuthContext";
import { Building2 } from "lucide-react";

export const Header: React.FC = () => {
  const { user } = useAuth();

  return (
    <header className="h-16 border-b border-slate-800 bg-slate-900/50 backdrop-blur px-8 flex items-center justify-between">
      <div className="flex items-center gap-2 text-sm font-medium text-slate-400">
        <Building2 className="w-4 h-4 text-blue-400" />
        <span>Organization ID:</span>
        <span className="text-blue-400 font-semibold">
          #{user?.organization_id ?? "—"}
        </span>
      </div>
    </header>
  );
};
