import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  async rewrites() {
    return [
      { source: "/api/:path*", destination: "http://127.0.0.1:8898/api/:path*" },
      { source: "/v1/:path*", destination: "http://127.0.0.1:8900/v1/:path*" },
    ];
  },
};

export default nextConfig;
