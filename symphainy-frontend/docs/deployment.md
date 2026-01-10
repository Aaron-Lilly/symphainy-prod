# Deployment Guide

This document provides comprehensive instructions for deploying the Symphainy frontend application to production, including optimization, monitoring, and maintenance.

## 📋 Table of Contents

- [Overview](#overview)
- [Production Build](#production-build)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Performance Optimization](#performance-optimization)
- [Monitoring & Logging](#monitoring--logging)
- [Security](#security)
- [Maintenance](#maintenance)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

The Symphainy frontend deployment process includes:

- **Production Build** - Optimized build for production
- **Containerization** - Docker-based deployment
- **Cloud Platforms** - Deployment to various cloud providers
- **Performance Optimization** - Bundle optimization and caching
- **Monitoring** - Application monitoring and alerting
- **Security** - Security headers and best practices
- **CI/CD** - Automated deployment pipelines

## 🏗️ Production Build

### Build Process

```bash
# Install dependencies
npm ci --only=production

# Run type checking
npm run type-check

# Run linting
npm run lint

# Run tests
npm run test

# Build for production
npm run build

# Verify build
npm run start
```

### Build Optimization

```bash
# Analyze bundle size
npm run analyze

# Check build output
ls -la .next/

# Verify static assets
ls -la .next/static/
```

### Environment Configuration

```bash
# Production environment variables
NODE_ENV=production
NEXT_PUBLIC_API_BASE_URL=https://api.symphainy.com
NEXT_PUBLIC_WS_BASE_URL=wss://ws.symphainy.com
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
NEXT_PUBLIC_ENABLE_ANALYTICS=true
NEXT_PUBLIC_ENABLE_ERROR_TRACKING=true
```

## 🐳 Docker Deployment

### Dockerfile

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

### Docker Compose

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
    restart: unless-stopped

  backend:
    image: symphainy-backend:latest
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    networks:
      - symphainy-network
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    networks:
      - symphainy-network
    restart: unless-stopped

networks:
  symphainy-network:
    driver: bridge
```

### Docker Commands

```bash
# Build the Docker image
docker build -t symphainy-frontend:latest .

# Run the container
docker run -p 3000:3000 symphainy-frontend:latest

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f frontend

# Stop services
docker-compose down
```

## ☁️ Cloud Deployment

### Vercel Deployment

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Deploy to Vercel**:
   ```bash
   # Login to Vercel
   vercel login

   # Deploy
   vercel --prod

   # Set environment variables
   vercel env add NEXT_PUBLIC_API_BASE_URL
   vercel env add NEXT_PUBLIC_WS_BASE_URL
   vercel env add NEXT_PUBLIC_SUPABASE_URL
   vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY
   ```

3. **Vercel Configuration** (`vercel.json`):
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "package.json",
         "use": "@vercel/next"
       }
     ],
     "env": {
       "NEXT_PUBLIC_API_BASE_URL": "@api_base_url",
       "NEXT_PUBLIC_WS_BASE_URL": "@ws_base_url",
       "NEXT_PUBLIC_SUPABASE_URL": "@supabase_url",
       "NEXT_PUBLIC_SUPABASE_ANON_KEY": "@supabase_anon_key"
     }
   }
   ```

### AWS Deployment

1. **AWS Amplify**:
   ```bash
   # Install Amplify CLI
   npm install -g @aws-amplify/cli

   # Initialize Amplify
   amplify init

   # Add hosting
   amplify add hosting

   # Deploy
   amplify publish
   ```

2. **AWS S3 + CloudFront**:
   ```bash
   # Build the application
   npm run build

   # Sync to S3
   aws s3 sync .next s3://your-bucket-name

   # Invalidate CloudFront cache
   aws cloudfront create-invalidation --distribution-id YOUR_DISTRIBUTION_ID --paths "/*"
   ```

### Google Cloud Platform

1. **Google Cloud Run**:
   ```bash
   # Build and push to Google Container Registry
   docker build -t gcr.io/PROJECT_ID/symphainy-frontend .
   docker push gcr.io/PROJECT_ID/symphainy-frontend

   # Deploy to Cloud Run
   gcloud run deploy symphainy-frontend \
     --image gcr.io/PROJECT_ID/symphainy-frontend \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

## ⚡ Performance Optimization

### Bundle Optimization

```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    optimizeCss: true,
    optimizePackageImports: ['@radix-ui/react-icons', 'lucide-react'],
  },
  
  // Enable compression
  compress: true,
  
  // Optimize images
  images: {
    formats: ['image/webp', 'image/avif'],
    minimumCacheTTL: 60,
  },
  
  // Bundle analyzer
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
      };
    }
    return config;
  },
};

module.exports = nextConfig;
```

### Caching Strategy

```javascript
// Cache configuration
const cacheConfig = {
  // Static assets
  static: {
    maxAge: 31536000, // 1 year
    immutable: true,
  },
  
  // API responses
  api: {
    maxAge: 300, // 5 minutes
    staleWhileRevalidate: 3600, // 1 hour
  },
  
  // Service worker
  serviceWorker: {
    cacheName: 'symphainy-cache-v1',
    maxEntries: 100,
    maxAgeSeconds: 24 * 60 * 60, // 24 hours
  },
};
```

### CDN Configuration

```nginx
# Nginx configuration for CDN
location /_next/static/ {
    alias /app/.next/static/;
    expires 1y;
    add_header Cache-Control "public, immutable";
    add_header Vary "Accept-Encoding";
}

location /static/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
    add_header Vary "Accept-Encoding";
}
```

## 📊 Monitoring & Logging

### Application Monitoring

```typescript
// monitoring/analytics.ts
export const analytics = {
  // Page views
  trackPageView: (url: string) => {
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('config', 'GA_MEASUREMENT_ID', {
        page_path: url,
      });
    }
  },

  // Custom events
  trackEvent: (action: string, category: string, label?: string) => {
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', action, {
        event_category: category,
        event_label: label,
      });
    }
  },

  // Error tracking
  trackError: (error: Error, context?: any) => {
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', 'exception', {
        description: error.message,
        fatal: false,
        custom_map: context,
      });
    }
  },
};
```

### Performance Monitoring

```typescript
// monitoring/performance.ts
export const performance = {
  // Core Web Vitals
  trackCoreWebVitals: () => {
    if (typeof window !== 'undefined') {
      import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
        getCLS(analytics.trackEvent);
        getFID(analytics.trackEvent);
        getFCP(analytics.trackEvent);
        getLCP(analytics.trackEvent);
        getTTFB(analytics.trackEvent);
      });
    }
  },

  // Custom performance metrics
  trackCustomMetric: (name: string, value: number) => {
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', 'custom_metric', {
        metric_name: name,
        metric_value: value,
      });
    }
  },
};
```

### Error Tracking

```typescript
// monitoring/error-tracking.ts
export const errorTracking = {
  // Initialize error tracking
  init: () => {
    if (typeof window !== 'undefined') {
      window.addEventListener('error', (event) => {
        analytics.trackError(event.error, {
          filename: event.filename,
          lineno: event.lineno,
          colno: event.colno,
        });
      });

      window.addEventListener('unhandledrejection', (event) => {
        analytics.trackError(new Error(event.reason), {
          type: 'unhandledrejection',
        });
      });
    }
  },

  // Manual error tracking
  captureException: (error: Error, context?: any) => {
    analytics.trackError(error, context);
  },
};
```

### Logging Configuration

```typescript
// logging/logger.ts
export const logger = {
  info: (message: string, data?: any) => {
    console.log(`[INFO] ${message}`, data);
    // Send to logging service
  },

  warn: (message: string, data?: any) => {
    console.warn(`[WARN] ${message}`, data);
    // Send to logging service
  },

  error: (message: string, error?: Error, data?: any) => {
    console.error(`[ERROR] ${message}`, error, data);
    // Send to logging service
    errorTracking.captureException(error || new Error(message), data);
  },

  debug: (message: string, data?: any) => {
    if (process.env.NODE_ENV === 'development') {
      console.debug(`[DEBUG] ${message}`, data);
    }
  },
};
```

## 🔒 Security

### Security Headers

```javascript
// next.config.js
const securityHeaders = [
  {
    key: 'X-DNS-Prefetch-Control',
    value: 'on',
  },
  {
    key: 'Strict-Transport-Security',
    value: 'max-age=63072000; includeSubDomains; preload',
  },
  {
    key: 'X-XSS-Protection',
    value: '1; mode=block',
  },
  {
    key: 'X-Frame-Options',
    value: 'SAMEORIGIN',
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff',
  },
  {
    key: 'Referrer-Policy',
    value: 'origin-when-cross-origin',
  },
  {
    key: 'Content-Security-Policy',
    value: "default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https: wss:;",
  },
];

module.exports = {
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: securityHeaders,
      },
    ];
  },
};
```

### Content Security Policy

```typescript
// security/csp.ts
export const cspConfig = {
  'default-src': ["'self'"],
  'script-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
  'style-src': ["'self'", "'unsafe-inline'"],
  'img-src': ["'self'", 'data:', 'https:'],
  'font-src': ["'self'", 'data:', 'https:'],
  'connect-src': ["'self'", 'https:', 'wss:'],
  'frame-src': ["'none'"],
  'object-src': ["'none'"],
  'base-uri': ["'self'"],
  'form-action': ["'self'"],
  'frame-ancestors': ["'none'"],
  'upgrade-insecure-requests': [],
};
```

### Authentication Security

```typescript
// security/auth.ts
export const authSecurity = {
  // Token validation
  validateToken: (token: string) => {
    // Implement token validation logic
    return true;
  },

  // Session management
  sessionConfig: {
    maxAge: 24 * 60 * 60, // 24 hours
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
  },

  // Rate limiting
  rateLimit: {
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // limit each IP to 100 requests per windowMs
  },
};
```

## 🔧 Maintenance

### Health Checks

```typescript
// health/health-check.ts
export const healthCheck = {
  // Application health
  check: async () => {
    try {
      // Check API connectivity
      const apiResponse = await fetch('/api/health');
      if (!apiResponse.ok) {
        throw new Error('API health check failed');
      }

      // Check WebSocket connectivity
      const wsConnection = await checkWebSocketConnection();
      if (!wsConnection) {
        throw new Error('WebSocket health check failed');
      }

      return {
        status: 'healthy',
        timestamp: new Date().toISOString(),
        services: {
          api: 'healthy',
          websocket: 'healthy',
        },
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        timestamp: new Date().toISOString(),
        error: error.message,
      };
    }
  },

  // WebSocket connection check
  checkWebSocketConnection: async () => {
    return new Promise((resolve) => {
      const ws = new WebSocket(process.env.NEXT_PUBLIC_WS_BASE_URL);
      const timeout = setTimeout(() => {
        ws.close();
        resolve(false);
      }, 5000);

      ws.onopen = () => {
        clearTimeout(timeout);
        ws.close();
        resolve(true);
      };

      ws.onerror = () => {
        clearTimeout(timeout);
        resolve(false);
      };
    });
  },
};
```

### Backup Strategy

```bash
# Database backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# File backup
tar -czf files_backup_$(date +%Y%m%d_%H%M%S).tar.gz /path/to/files

# Configuration backup
cp .env.production .env.production.backup
```

### Update Process

```bash
# 1. Create backup
git checkout -b backup/$(date +%Y%m%d)

# 2. Pull latest changes
git pull origin main

# 3. Install dependencies
npm ci

# 4. Run tests
npm run test

# 5. Build application
npm run build

# 6. Deploy
docker-compose up -d --build

# 7. Verify deployment
curl http://localhost/health
```

## 🚨 Troubleshooting

### Common Deployment Issues

#### Build Failures

```bash
# Check build logs
npm run build 2>&1 | tee build.log

# Check for TypeScript errors
npm run type-check

# Check for linting errors
npm run lint

# Clear cache and rebuild
rm -rf .next node_modules
npm install
npm run build
```

#### Runtime Errors

```bash
# Check application logs
docker-compose logs -f frontend

# Check nginx logs
docker-compose logs -f nginx

# Check for memory issues
docker stats

# Restart services
docker-compose restart
```

#### Performance Issues

```bash
# Check bundle size
npm run analyze

# Check Core Web Vitals
npm run lighthouse

# Monitor performance
curl -s https://your-domain.com/api/health | jq '.performance'
```

### Monitoring Commands

```bash
# Check application status
curl http://localhost/health

# Check API connectivity
curl http://localhost/api/health

# Check WebSocket connectivity
wscat -c ws://localhost/ws

# Monitor logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

---

**Last Updated**: [Automated Update]
**Version**: 1.0.0 