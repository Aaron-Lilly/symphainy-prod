# CORS Issue - Production-Grade Solution

**Date:** January 23, 2026  
**Issue:** CORS error when frontend accessed on port 3000, API calls go to port 80  
**Status:** Strategic Solution

---

## The Problem

**Error:**
```
Access to fetch at 'http://35.215.64.103/api/auth/login' from origin 'http://35.215.64.103:3000' 
has been blocked by CORS policy
```

**Root Cause:**
- Frontend accessed on port 3000 (direct access, bypassing Traefik)
- API calls go to port 80 (via Traefik)
- Different origins = CORS violation

---

## Production Best Practice: Traefik Reverse Proxy Pattern

### Architecture

```
User → Traefik (port 80) → Frontend (port 3000, internal)
                        → Backend APIs (port 8000/8001, internal)
```

**Key Principle:** All traffic flows through Traefik on port 80 (standard HTTP)

### Benefits

1. **No CORS Issues:**
   - Frontend and API on same origin (port 80)
   - Relative URLs work perfectly
   - No cross-origin requests

2. **Production-Ready:**
   - Standard HTTP port 80
   - Works with standard firewall rules
   - Ready for SSL/TLS at Traefik level

3. **Security:**
   - Single entry point
   - Can add rate limiting, authentication at Traefik
   - Backend services not directly exposed

4. **Scalability:**
   - Easy to add load balancing
   - Can add CDN in front
   - Can scale frontend/backend independently

---

## Solution: Use Relative URLs (Production Pattern)

### Frontend API Configuration

**When in browser (client-side):**
- Use **relative URLs** (`/api/auth/login`)
- Same origin = no CORS needed
- Works automatically with Traefik routing

**When in SSR/build-time:**
- Use absolute URLs (for Next.js rewrites)
- Next.js rewrites handle routing

### Implementation

```typescript
// lib/config.ts
export const config = {
  // Client-side: Use relative URLs (same origin via Traefik)
  // Server-side: Use absolute URL for Next.js rewrites
  apiUrl: typeof window !== 'undefined' 
    ? ''  // Relative URL - same origin as frontend
    : (API_BASE ? API_BASE.replace(/\/api\/?$/, '') : "http://35.215.64.103"),
};
```

This ensures:
- ✅ Browser requests use relative URLs → same origin → no CORS
- ✅ SSR/build uses absolute URLs → Next.js rewrites work
- ✅ Works with Traefik routing automatically

---

## Additional: CORS Configuration (Defense in Depth)

Even with relative URLs, configure CORS properly:

### Backend CORS Configuration

```python
# experience_service.py
allowed_origins = [
    "http://35.215.64.103",      # Production (via Traefik)
    "http://35.215.64.103:3000", # Direct access (development)
    "http://localhost:3000",     # Local development
]
```

**Why:** Defense in depth - if someone bypasses Traefik, CORS still works

---

## Access Pattern

### ✅ Correct (Production)
```
User → http://35.215.64.103/ (Traefik port 80)
     → Frontend: http://35.215.64.103/
     → API: http://35.215.64.103/api/* (same origin)
```

### ❌ Incorrect (Development/Debugging)
```
User → http://35.215.64.103:3000/ (direct frontend)
     → API: http://35.215.64.103/api/* (different origin)
     → CORS error
```

---

## Implementation Steps

1. ✅ **Update Frontend Config** - Use relative URLs in browser
2. ✅ **Update CORS** - Allow frontend origin (defense in depth)
3. ✅ **Documentation** - Access via Traefik on port 80
4. ✅ **Firewall** - Only expose port 80 (not 3000) in production

---

## Why This Is Production-Grade

1. **Standard Pattern:**
   - Reverse proxy is industry standard
   - Used by all major platforms
   - Works with CDNs, load balancers

2. **Security:**
   - Single entry point
   - Can add WAF, rate limiting
   - Backend not exposed

3. **Performance:**
   - Can add caching at Traefik
   - Can add compression
   - Can add SSL termination

4. **Scalability:**
   - Easy to scale horizontally
   - Can add multiple frontend instances
   - Can add multiple backend instances

---

**Last Updated:** January 23, 2026
