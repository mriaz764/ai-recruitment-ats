import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { ROUTES, PROTECTED_ROUTES, AUTH_ROUTES } from "@/lib/routes";

export function middleware(request: NextRequest) {
  const token = request.cookies.get("access_token")?.value;
  const { pathname } = request.nextUrl;

  const isProtectedRoute = PROTECTED_ROUTES.some((route) => pathname.startsWith(route));
  const isAuthRoute = AUTH_ROUTES.some((route) => pathname === route);

  // Redirect unauthenticated user attempting to access protected workspace routes
  if (isProtectedRoute && !token) {
    const loginUrl = new URL(ROUTES.AUTH.LOGIN, request.url);
    loginUrl.searchParams.set("redirect", pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Redirect authenticated user attempting to access login/register back to dashboard
  if (isAuthRoute && token) {
    return NextResponse.redirect(new URL(ROUTES.DASHBOARD.HOME, request.url));
  }

  // Handle root route (/) redirect based on token state
  if (pathname === ROUTES.PUBLIC.ROOT) {
    const target = token ? ROUTES.DASHBOARD.HOME : ROUTES.AUTH.LOGIN;
    return NextResponse.redirect(new URL(target, request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/",
    "/dashboard/:path*",
    "/jobs/:path*",
    "/candidates/:path*",
    "/applications/:path*",
    "/interviews/:path*",
    "/settings/:path*",
    "/login",
    "/register",
  ],
};