/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: false, // React Flow and high-frequency canvas renders work more smoothly
  experimental: {
    serverActions: {
      allowedOrigins: ['localhost:3333', 'localhost:3000'],
    },
  },
  images: {
    domains: ['images.unsplash.com', 'raw.githubusercontent.com'],
  },
};

export default nextConfig;
