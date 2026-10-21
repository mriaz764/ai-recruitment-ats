"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Briefcase,
  Users,
  Kanban,
  Calendar,
  Settings,
  LogOut,
} from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { ROUTES } from "@/lib/routes";

interface NavItem {
  label: string;
  href: string;
  icon: React.ElementType;
}

const NAV_ITEMS: NavItem[] = [
  { label: "Dashboard", href: ROUTES.DASHBOARD.HOME, icon: LayoutDashboard },
  { label: "Jobs", href: ROUTES.DASHBOARD.JOBS, icon: Briefcase },
  { label: "Candidates", href: ROUTES.DASHBOARD.CANDIDATES, icon: Users },
  { label: "Kanban Pipeline", href: ROUTES.DASHBOARD.KANBAN, icon: Kanban },
  { label: "Interviews", href: ROUTES.DASHBOARD.INTERVIEWS, icon: Calendar },
  { label: "Settings", href: ROUTES.DASHBOARD.SETTINGS, icon: Settings },
];

export const Sidebar: React.FC = () => {
  const pathname = usePathname();
  const { logout, user } = useAuth();

  return (
    <aside className="w-64 bg-slate-900 text-slate-100 flex flex-col h-screen border-r border-slate-800 shrink-0">
      {/* Brand Header */}
      <div className="p-6 border-b border-slate-800">
        <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
          RecruitAI ATS
        </h1>
        <p className="text-xs text-slate-400 mt-1">Enterprise Multi-Tenant</p>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive =
            pathname === item.href ||
            (item.href !== ROUTES.DASHBOARD.HOME &&
              pathname.startsWith(item.href));

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? "bg-blue-600 text-white shadow-lg shadow-blue-600/30"
                  : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
              }`}
            >
              <Icon className="w-5 h-5" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* User Footer & Logout */}
      <div className="p-4 border-t border-slate-800 bg-slate-950/50">
        <div className="mb-3 px-2">
          <p className="text-sm font-semibold text-slate-200 truncate">
            {user?.full_name ?? "Recruiter"}
          </p>
          <p className="text-xs text-slate-500 truncate">
            {user?.email ?? "—"}
          </p>
        </div>
        <button
          onClick={logout}
          className="w-full flex items-center justify-center gap-2 px-4 py-2 text-xs font-medium text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors border border-rose-500/20"
        >
          <LogOut className="w-4 h-4" />
          Sign Out
        </button>
      </div>
    </aside>
  );
};
