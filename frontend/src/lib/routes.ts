export const ROUTES = {
  PUBLIC: {
    ROOT: "/",
  },
  AUTH: {
    LOGIN: "/login",
    REGISTER: "/register",
  },
  DASHBOARD: {
    HOME: "/dashboard",
    JOBS: "/jobs",
    JOB_DETAIL: (id: number | string) => `/jobs/${id}`,
    CANDIDATES: "/candidates",
    CANDIDATE_DETAIL: (id: number | string) => `/candidates/${id}`,
    KANBAN: "/applications/kanban",
    INTERVIEWS: "/interviews",
    SETTINGS: "/settings",
  },
} as const;

export const PROTECTED_ROUTES: string[] = [
  ROUTES.DASHBOARD.HOME,
  ROUTES.DASHBOARD.JOBS,
  ROUTES.DASHBOARD.CANDIDATES,
  ROUTES.DASHBOARD.KANBAN,
  ROUTES.DASHBOARD.INTERVIEWS,
  ROUTES.DASHBOARD.SETTINGS,
];

export const AUTH_ROUTES: string[] = [
  ROUTES.AUTH.LOGIN,
  ROUTES.AUTH.REGISTER,
];