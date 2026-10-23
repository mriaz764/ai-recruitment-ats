import React from "react";
import { AuthProvider } from "@/context/AuthContext";
import "@/app/globals.css";

export const metadata = {
  title: "AI Recruitment ATS",
  description: "Multi-Tenant AI Recruitment Platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-slate-950 text-slate-100 antialiased min-h-screen">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
