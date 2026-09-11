/** @type {import('next').NextConfig} */
// Destino del proxy /api/* → backend.
//
// OJO: Next.js resuelve `rewrites()` en BUILD time (queda en
// .next/routes-manifest.json), así que este valor NO se puede cambiar en
// runtime: hay que rehacer el build de la imagen si cambia la URL del backend.
//   - local / docker-compose: http://localhost:8000 o http://backend:8000
//   - Render: https://<tu-backend>.onrender.com  (Render pasa las env vars del
//     servicio Docker como build args, así que basta definirlo en el dashboard)
const apiTarget = process.env.API_PROXY_TARGET || "http://localhost:8000";

const nextConfig = {
  // Enable gzip compression for responses
  compress: true,
  // Backend API proxy para evitar CORS (mismo origen para el navegador)
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${apiTarget}/api/:path*`,
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
