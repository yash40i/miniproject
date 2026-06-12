import type { NextConfig } from "next";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  output: "standalone",
  outputFileTracingRoot: process.cwd(),
  env: {
    NEXT_PUBLIC_API_URL: API_URL,
  },
  images: {
    unoptimized: true,
  },
  typescript: {
    ignoreBuildErrors: false,
  },
  async rewrites() {
    return [
      // Proxy auth routes: /api/auth/* → backend /auth/*
      {
        source: "/api/auth/:path*",
        destination: `${API_URL}/auth/:path*`,
      },
      // Proxy all other /api/* routes → backend /api/*
      {
        source: "/api/:path*",
        destination: `${API_URL}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
