import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // El ícono de herramientas de Next.js (modo desarrollo) tapaba "Inicio" en la barra,
  // y quien prueba por el túnel lo ve. Se oculta.
  devIndicators: false,
  async rewrites() {
    const apiInternalUrl = process.env.API_INTERNAL_URL ?? "http://localhost:8000";
    return [{ source: "/api/:path*", destination: `${apiInternalUrl}/:path*` }];
  },
};

export default nextConfig;
