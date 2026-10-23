import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // 1. Allow HMR requests from your local network IP
  allowedDevOrigins: ["192.168.1.8", "localhost:3000"],

  // 2. Perform HTTP-level redirection from / to /dashboard
  async redirects() {
    return [
      {
        source: "/",
        destination: "/dashboard",
        permanent: false,
      },
    ];
  },
};

export default nextConfig;