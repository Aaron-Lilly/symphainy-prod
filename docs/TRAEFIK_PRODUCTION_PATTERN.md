# Traefik Production Pattern - Best Practices

**Date:** January 23, 2026  
**Status:** Production-Ready Implementation

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Browser                         │
└────────────────────┬──────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │   Traefik (port 80)   │  ← Single Entry Point
         │   Reverse Proxy       │
         └───────────┬────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌───────────────┐         ┌──────────────┐
│  Frontend     │         │  Backend APIs │
│  (port 3000)  │         │  (port 8000) │
│  Internal     │         │  Internal    │
└───────────────┘         └──────────────┘
```

---

## Production Best Practices

### 1. Use Relative URLs (Client-Side)

**Why:**
- Same origin = no CORS issues
- Works automatically with Traefik
- Simpler configuration

**Implementation:**
```typescript
// Client-side: Use relative URLs
apiUrl: typeof window !== 'undefined' ? '' : 'http://35.215.64.103'
```

**Result:**
- Browser: `/api/auth/login` → Same origin → No CORS
- SSR: `http://35.215.64.103/api/auth/login` → Next.js rewrites handle it

---

### 2. Access Through Traefik Only

**✅ Correct:**
```
http://35.215.64.103/          → Frontend (via Traefik)
http://35.215.64.103/api/*    → Backend (via Traefik)
```

**❌ Avoid:**
```
http://35.215.64.103:3000/     → Direct frontend (bypasses Traefik)
http://35.215.64.103:8000/    → Direct backend (bypasses Traefik)
```

**Why:**
- Direct access bypasses security layers
- Causes CORS issues
- Not production-ready

---

### 3. Configure CORS (Defense in Depth)

Even with relative URLs, configure CORS:

```python
# Backend CORS configuration
allowed_origins = [
    "http://35.215.64.103",      # Production (via Traefik)
    "http://35.215.64.103:3000", # Direct access (fallback)
    "http://localhost:3000",     # Development
]
```

**Why:**
- Defense in depth
- Handles edge cases
- Supports development scenarios

---

### 4. Firewall Configuration

**Production:**
- ✅ Expose port 80 (Traefik)
- ❌ Don't expose port 3000 (frontend)
- ❌ Don't expose port 8000/8001 (backend)

**Why:**
- Single entry point
- Better security
- Easier to manage

---

## Benefits of This Pattern

### 1. No CORS Issues
- Same origin (port 80)
- Relative URLs work perfectly
- No cross-origin requests

### 2. Security
- Single entry point
- Can add WAF, rate limiting
- Backend not exposed

### 3. Scalability
- Easy to add load balancing
- Can scale frontend/backend independently
- Can add CDN in front

### 4. Production-Ready
- Standard HTTP port 80
- Works with standard firewall rules
- Ready for SSL/TLS

---

## Implementation Checklist

- ✅ Frontend uses relative URLs in browser
- ✅ Frontend uses absolute URLs for SSR
- ✅ CORS configured for frontend origin
- ✅ Traefik routes /api/* to backend
- ✅ Traefik routes /* to frontend
- ✅ All access through Traefik on port 80
- ✅ Firewall only exposes port 80

---

## Access Instructions

**For Users:**
- Access via: `http://35.215.64.103/` (port 80)
- All API calls automatically routed correctly
- No CORS issues

**For Developers:**
- Can access directly on port 3000 for debugging
- CORS configured to allow it
- But prefer Traefik access for production testing

---

**Last Updated:** January 23, 2026
