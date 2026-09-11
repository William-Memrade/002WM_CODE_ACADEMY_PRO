/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable gzip compression for responses
  compress: true,
  // Backend API proxy to avoid CORS in development
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8000/api/:path*",
      },
    ];
  },
  // Cache static assets aggressively
  async headers() {
    return [
      {
        source: "/favicon.ico",
        headers: [
          { key: "Cache-Control", value: "public, max-age=86400" },
        ],
      },
    ];
  },
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "*.supabase.co",
      },
    ],
  },
  // Reduce bundle size
  reactStrictMode: true,
  poweredByHeader: false,
};

export default nextConfig;
