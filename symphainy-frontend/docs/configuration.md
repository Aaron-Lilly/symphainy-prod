# Configuration Guide

This document provides comprehensive documentation for configuration management, environment variables, build settings, and deployment configuration used in the Symphainy frontend application.

## 📋 Table of Contents

- [Overview](#overview)
- [Environment Variables](#environment-variables)
- [Build Configuration](#build-configuration)
- [Development Configuration](#development-configuration)
- [Production Configuration](#production-configuration)
- [Feature Flags](#feature-flags)
- [Security Configuration](#security-configuration)
- [Performance Configuration](#performance-configuration)
- [Best Practices](#best-practices)

## 🎯 Overview

The Symphainy frontend uses a comprehensive configuration system that provides:

- **Environment-Specific Settings** - Different configurations for development, staging, and production
- **Feature Flags** - Dynamic feature enablement/disablement
- **Security Configuration** - Authentication and authorization settings
- **Performance Optimization** - Build and runtime performance settings
- **Service Configuration** - API endpoints, WebSocket URLs, and service settings

## 🔧 Environment Variables

### Required Environment Variables

Create a `.env.local` file in the frontend root directory with the following variables:

```bash
# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_API_TIMEOUT=10000
NEXT_PUBLIC_API_MAX_RETRIES=3

# WebSocket Configuration
NEXT_PUBLIC_WS_BASE_URL=ws://localhost:8000
NEXT_PUBLIC_WS_RECONNECT_ATTEMPTS=5
NEXT_PUBLIC_WS_HEARTBEAT_INTERVAL=30000

# Authentication
NEXT_PUBLIC_AUTH_ENABLED=true
NEXT_PUBLIC_AUTH_PROVIDER=supabase

# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# Feature Flags
NEXT_PUBLIC_ENABLE_WEBSOCKET=true
NEXT_PUBLIC_ENABLE_CROSS_PILLAR=true
NEXT_PUBLIC_ENABLE_ANALYTICS=false

# Performance
NEXT_PUBLIC_ENABLE_CACHE=true
NEXT_PUBLIC_CACHE_TTL=3600
NEXT_PUBLIC_ENABLE_COMPRESSION=true

# Monitoring
NEXT_PUBLIC_ENABLE_LOGGING=true
NEXT_PUBLIC_LOG_LEVEL=info
NEXT_PUBLIC_ENABLE_ERROR_TRACKING=true
```

### Environment-Specific Configuration

#### Development Environment (`.env.development`)

```bash
# Development-specific settings
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_WS_BASE_URL=ws://localhost:8000
NEXT_PUBLIC_ENABLE_DEBUG=true
NEXT_PUBLIC_LOG_LEVEL=debug
NEXT_PUBLIC_ENABLE_HOT_RELOAD=true
NEXT_PUBLIC_ENABLE_DEV_TOOLS=true
```

#### Staging Environment (`.env.staging`)

```bash
# Staging-specific settings
NEXT_PUBLIC_API_BASE_URL=https://api-staging.symphainy.com
NEXT_PUBLIC_WS_BASE_URL=wss://ws-staging.symphainy.com
NEXT_PUBLIC_ENABLE_DEBUG=false
NEXT_PUBLIC_LOG_LEVEL=info
NEXT_PUBLIC_ENABLE_ANALYTICS=true
```

#### Production Environment (`.env.production`)

```bash
# Production-specific settings
NEXT_PUBLIC_API_BASE_URL=https://api.symphainy.com
NEXT_PUBLIC_WS_BASE_URL=wss://ws.symphainy.com
NEXT_PUBLIC_ENABLE_DEBUG=false
NEXT_PUBLIC_LOG_LEVEL=warn
NEXT_PUBLIC_ENABLE_ANALYTICS=true
NEXT_PUBLIC_ENABLE_ERROR_TRACKING=true
```

### Configuration Validation

```typescript
// config/validation.ts
export const validateEnvironmentVariables = () => {
  const required = [
    'NEXT_PUBLIC_API_BASE_URL',
    'NEXT_PUBLIC_SUPABASE_URL',
    'NEXT_PUBLIC_SUPABASE_ANON_KEY'
  ];

  const missing = required.filter(key => !process.env[key]);
  
  if (missing.length > 0) {
    throw new Error(`Missing required environment variables: ${missing.join(', ')}`);
  }
};
```

## ⚙️ Build Configuration

### Next.js Configuration (`next.config.js`)

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Build optimization
  experimental: {
    optimizeCss: true,
    optimizePackageImports: ['@radix-ui/react-icons', 'lucide-react'],
  },

  // Image optimization
  images: {
    domains: ['localhost', 'api.symphainy.com'],
    formats: ['image/webp', 'image/avif'],
  },

  // Environment variables
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },

  // Headers for security
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
        ],
      },
    ];
  },

  // Redirects
  async redirects() {
    return [
      {
        source: '/old-page',
        destination: '/new-page',
        permanent: true,
      },
    ];
  },

  // Rewrites for API proxying
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
```

### TypeScript Configuration (`tsconfig.json`)

```json
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "es6"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "baseUrl": ".",
    "paths": {
      "@/*": ["./*"],
      "@/components/*": ["./components/*"],
      "@/shared/*": ["./shared/*"],
      "@/lib/*": ["./lib/*"],
      "@/styles/*": ["./styles/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

### Tailwind CSS Configuration (`tailwind.config.js`)

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  prefix: "",
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
```

## 🛠️ Development Configuration

### ESLint Configuration (`.eslintrc.json`)

```json
{
  "extends": [
    "next/core-web-vitals",
    "next/typescript"
  ],
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/no-explicit-any": "warn",
    "prefer-const": "error",
    "no-var": "error",
    "no-console": "warn",
    "no-debugger": "error"
  },
  "ignorePatterns": [
    "node_modules/",
    ".next/",
    "out/",
    "build/",
    "dist/"
  ]
}
```

### Prettier Configuration (`.prettierrc`)

```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2,
  "useTabs": false,
  "bracketSpacing": true,
  "arrowParens": "avoid"
}
```

### Jest Configuration (`jest.config.js`)

```javascript
const nextJest = require('next/jest')

const createJestConfig = nextJest({
  // Provide the path to your Next.js app to load next.config.js and .env files
  dir: './',
})

// Add any custom config to be passed to Jest
const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/$1',
  },
  testEnvironment: 'jest-environment-jsdom',
  collectCoverageFrom: [
    'components/**/*.{ts,tsx}',
    'shared/**/*.{ts,tsx}',
    'lib/**/*.{ts,tsx}',
    '!**/*.d.ts',
    '!**/node_modules/**',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
}

// createJestConfig is exported this way to ensure that next/jest can load the Next.js config which is async
module.exports = createJestConfig(customJestConfig)
```

### Playwright Configuration (`playwright.config.ts`)

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

## 🚀 Production Configuration

### Docker Configuration (`Dockerfile`)

```dockerfile
# Use the official Node.js runtime as the base image
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install dependencies based on the preferred package manager
COPY package.json package-lock.json* ./
RUN npm ci --only=production

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Next.js collects completely anonymous telemetry data about general usage.
# Learn more here: https://nextjs.org/telemetry
# Uncomment the following line in case you want to disable telemetry during the build.
ENV NEXT_TELEMETRY_DISABLED 1

RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Set the correct permission for prerender cache
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Automatically leverage output traces to reduce image size
# https://nextjs.org/docs/advanced-features/output-file-tracing
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
```

### Docker Compose (`docker-compose.yml`)

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL}
      - NEXT_PUBLIC_WS_BASE_URL=${NEXT_PUBLIC_WS_BASE_URL}
      - NEXT_PUBLIC_SUPABASE_URL=${NEXT_PUBLIC_SUPABASE_URL}
      - NEXT_PUBLIC_SUPABASE_ANON_KEY=${NEXT_PUBLIC_SUPABASE_ANON_KEY}
    depends_on:
      - backend
    networks:
      - symphainy-network

  backend:
    image: symphainy-backend:latest
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    networks:
      - symphainy-network

networks:
  symphainy-network:
    driver: bridge
```

### Nginx Configuration (`nginx.conf`)

```nginx
events {
    worker_connections 1024;
}

http {
    upstream frontend {
        server frontend:3000;
    }

    upstream backend {
        server backend:8000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;

    server {
        listen 80;
        server_name symphainy.com;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;
        add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
        }

        # API
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # WebSocket
        location /ws/ {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Static files
        location /_next/static/ {
            alias /app/.next/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

## 🚩 Feature Flags

### Feature Flag Configuration

```typescript
// config/feature-flags.ts
export const featureFlags = {
  // Core features
  enableWebSocket: process.env.NEXT_PUBLIC_ENABLE_WEBSOCKET === 'true',
  enableCrossPillar: process.env.NEXT_PUBLIC_ENABLE_CROSS_PILLAR === 'true',
  enableAnalytics: process.env.NEXT_PUBLIC_ENABLE_ANALYTICS === 'true',
  
  // UI features
  enableDarkMode: true,
  enableAnimations: true,
  enableAccessibility: true,
  
  // Performance features
  enableCache: process.env.NEXT_PUBLIC_ENABLE_CACHE === 'true',
  enableCompression: process.env.NEXT_PUBLIC_ENABLE_COMPRESSION === 'true',
  
  // Development features
  enableDebug: process.env.NEXT_PUBLIC_ENABLE_DEBUG === 'true',
  enableDevTools: process.env.NEXT_PUBLIC_ENABLE_DEV_TOOLS === 'true',
};

// Feature flag hook
export const useFeatureFlag = (flag: keyof typeof featureFlags) => {
  return featureFlags[flag];
};

// Conditional rendering
export const withFeatureFlag = <P extends object>(
  Component: React.ComponentType<P>,
  flag: keyof typeof featureFlags
) => {
  return (props: P) => {
    if (!featureFlags[flag]) {
      return null;
    }
    return <Component {...props} />;
  };
};
```

### Usage in Components

```typescript
import { useFeatureFlag, withFeatureFlag } from '@/config/feature-flags';

function MyComponent() {
  const enableWebSocket = useFeatureFlag('enableWebSocket');
  const enableAnalytics = useFeatureFlag('enableAnalytics');

  return (
    <div>
      {enableWebSocket && <WebSocketComponent />}
      {enableAnalytics && <AnalyticsComponent />}
    </div>
  );
}

// Conditional component
const ConditionalComponent = withFeatureFlag(SomeComponent, 'enableWebSocket');
```

## 🔒 Security Configuration

### Content Security Policy

```typescript
// config/security.ts
export const securityConfig = {
  contentSecurityPolicy: {
    'default-src': ["'self'"],
    'script-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
    'style-src': ["'self'", "'unsafe-inline'"],
    'img-src': ["'self'", 'data:', 'https:'],
    'connect-src': ["'self'", 'https:', 'wss:'],
    'font-src': ["'self'", 'https:'],
    'object-src': ["'none'"],
    'media-src': ["'self'"],
    'frame-src': ["'none'"],
  },
  
  headers: {
    'X-Frame-Options': 'DENY',
    'X-Content-Type-Options': 'nosniff',
    'Referrer-Policy': 'origin-when-cross-origin',
    'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
  },
};
```

### Authentication Configuration

```typescript
// config/auth.ts
export const authConfig = {
  providers: {
    supabase: {
      url: process.env.NEXT_PUBLIC_SUPABASE_URL,
      anonKey: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
    },
  },
  
  session: {
    maxAge: 24 * 60 * 60, // 24 hours
    updateAge: 60 * 60, // 1 hour
  },
  
  security: {
    csrfProtection: true,
    rateLimit: {
      windowMs: 15 * 60 * 1000, // 15 minutes
      max: 100, // limit each IP to 100 requests per windowMs
    },
  },
};
```

## ⚡ Performance Configuration

### Caching Configuration

```typescript
// config/cache.ts
export const cacheConfig = {
  // Browser cache
  browser: {
    static: {
      maxAge: 31536000, // 1 year
      immutable: true,
    },
    dynamic: {
      maxAge: 3600, // 1 hour
      staleWhileRevalidate: 86400, // 24 hours
    },
  },
  
  // API cache
  api: {
    maxAge: 300, // 5 minutes
    staleWhileRevalidate: 3600, // 1 hour
  },
  
  // Service worker cache
  serviceWorker: {
    cacheName: 'symphainy-cache-v1',
    maxEntries: 100,
    maxAgeSeconds: 24 * 60 * 60, // 24 hours
  },
};
```

### Bundle Optimization

```typescript
// config/bundle.ts
export const bundleConfig = {
  // Code splitting
  splitting: {
    chunks: 'all',
    cacheGroups: {
      vendor: {
        test: /[\\/]node_modules[\\/]/,
        name: 'vendors',
        chunks: 'all',
      },
      common: {
        name: 'common',
        minChunks: 2,
        chunks: 'all',
        enforce: true,
      },
    },
  },
  
  // Tree shaking
  treeShaking: {
    usedExports: true,
    sideEffects: false,
  },
  
  // Compression
  compression: {
    gzip: true,
    brotli: true,
    threshold: 1024,
  },
};
```

## 🎯 Best Practices

### 1. Environment Management

- **Never commit secrets** to version control
- **Use environment-specific files** (.env.development, .env.production)
- **Validate environment variables** at startup
- **Provide fallback values** for optional variables

### 2. Security

- **Use HTTPS/WSS** in production
- **Implement CSP headers** for XSS protection
- **Enable rate limiting** for API endpoints
- **Validate all inputs** and sanitize data

### 3. Performance

- **Optimize bundle size** with code splitting
- **Enable compression** for static assets
- **Use CDN** for static content
- **Implement caching** strategies

### 4. Monitoring

- **Log configuration changes** for debugging
- **Monitor environment variables** usage
- **Track feature flag** adoption
- **Alert on configuration** errors

### 5. Deployment

- **Use Docker** for consistent environments
- **Implement blue-green** deployments
- **Rollback capability** for configuration changes
- **Health checks** for all services

### 6. Development

- **Local development** environment setup
- **Hot reload** for configuration changes
- **Debug tools** for troubleshooting
- **Documentation** for all configuration options

## 🔗 Related Documentation

- [API Documentation](./API.md) - Service layer interfaces
- [Service Layer Documentation](./services.md) - Service architecture
- [Deployment Guide](./deployment.md) - Production deployment
- [Troubleshooting Guide](./troubleshooting.md) - Common issues

---

**Last Updated**: [Automated Update]
**Version**: 1.0.0 