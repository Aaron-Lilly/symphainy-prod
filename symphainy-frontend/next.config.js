/** @type {import('next').NextConfig} */
const nextConfig = {
  // Standalone output for Docker production builds
  output: 'standalone',
  // Disable SWC compiler - use Babel instead (required for Alpine Linux)
  swcMinify: false,
  compiler: {
    // Disable SWC to use Babel (needed for Alpine Linux compatibility)
    removeConsole: false,
  },
  typescript: {
    // TypeScript errors should be fixed, not ignored
    // Test files are excluded via tsconfig.json and .dockerignore
    ignoreBuildErrors: false,
  },
  eslint: {
    // Warning: This allows production builds to successfully complete even if
    // your project has ESLint errors.
    ignoreDuringBuilds: true,
  },
  // Skip prerendering errors for archived pages (they use old providers)
  // These pages will be dynamically rendered at runtime instead
  experimental: {
    missingSuspenseWithCSRBailout: false,
  },
  // API proxy configuration to route API calls to backend
  // Option C: Configure via NEXT_PUBLIC_BACKEND_URL or NEXT_PUBLIC_API_URL environment variable
  async rewrites() {
    // Traefik routing: Backend API accessible via /api path through Traefik
    // Traefik routes /api to backend service on port 80
    const backendURL = 
      process.env.NEXT_PUBLIC_BACKEND_URL || 
      process.env.NEXT_PUBLIC_API_URL || 
      (process.env.NODE_ENV === 'development' ? 'http://localhost:8000/api' : null);
    
    if (!backendURL) {
      throw new Error(
        'Backend URL is required but not configured. ' +
        'Please set NEXT_PUBLIC_BACKEND_URL or NEXT_PUBLIC_API_URL environment variable.'
      );
    }
    
    return [
      {
        source: '/api/:path*',
        destination: `${backendURL.replace(/\/$/, '')}/:path*`,  // Remove /api prefix since backendURL already includes it
      },
    ];
  },
  // Force cache-busting for JavaScript chunks
  generateBuildId: async () => {
    return `build-${Date.now()}`;
  },
  // Exclude archived pages from build (they use old providers)
  // These pages will be dynamically rendered at runtime if accessed
  pageExtensions: ['tsx', 'ts', 'jsx', 'js'],
  webpack: (config, { isServer }) => {
    // Test files are excluded via tsconfig.json exclude and .dockerignore
    // Only modify if config exists and has resolve
    if (config && config.resolve) {
      // Add TypeScript support (if not already present)
      if (config.resolve.extensions && !config.resolve.extensions.includes('.ts')) {
        config.resolve.extensions.push('.ts', '.tsx');
      }
      
      // Handle module resolution (only if alias doesn't exist or needs updating)
      if (config.resolve.alias) {
        const path = require('path');
        config.resolve.alias = {
          ...config.resolve.alias,
          '@': path.resolve(__dirname, './'),
          'shared': path.resolve(__dirname, '../shared'),
        };
      }
    }
    
    return config;
  },
}

module.exports = nextConfig
