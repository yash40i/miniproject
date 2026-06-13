import type { NextConfig } from "next";

let rawApiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
// Force HTTPS for Railway to prevent 301 redirects that turn POST into GET
if (rawApiUrl.includes("railway.app") && rawApiUrl.startsWith("http://")) {
  rawApiUrl = rawApiUrl.replace("http://", "https://");
}
const API_URL = rawApiUrl.endsWith('/') ? rawApiUrl.slice(0, -1) : rawApiUrl;

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
