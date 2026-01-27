# Phase 7: Routing Refactoring - Test Plan

**Date:** January 22, 2026  
**Status:** Ready for Testing

---

## 🧪 Test Suite Overview

### Quick Validation Test
**File:** `symphainy-frontend/scripts/test-phase7-routing-validation.ts`

**Purpose:** Validates code structure and patterns without requiring running services.

**Tests:**
1. ✅ Route utilities file exists
2. ✅ Route utilities have required functions
3. ✅ TopNavBar uses routing utilities
4. ✅ Content page syncs route params
5. ✅ Pillar data has correct route
6. ✅ PlatformStateProvider has realm state methods
7. ✅ Documentation exists

**Run:** `cd symphainy-frontend && npx tsx scripts/test-phase7-routing-validation.ts`

---

### Integration Test Script
**File:** `scripts/test-phase7-integration.sh`

**Purpose:** Starts all containers and runs comprehensive tests.

**Steps:**
1. Starts infrastructure (consul, traefik, redis, arango)
2. Starts backend services (runtime, experience)
3. Starts frontend
4. Performs health checks
5. Runs Playwright tests

**Run:** `./scripts/test-phase7-integration.sh`

---

### Browser-Based Tests (Playwright)
**File:** `symphainy-frontend/scripts/test-phase7-routing.ts`

**Purpose:** End-to-end browser testing of routing functionality.

**Test Categories:**

#### 1. Navigation Flow
- ✅ Clicking pillars updates state first, then routes
- ✅ Journey state preserved in URLs
- ✅ Browser back/forward works

#### 2. Route → State Sync
- ✅ URL params sync to realm state
- ✅ Deep linking works (URL → state → UI)
- ✅ State drives UI correctly

#### 3. Backend Integration
- ✅ State sync doesn't break API calls
- ✅ Session state works correctly
- ✅ Realm state persists properly

#### 4. Content Pillar (Example)
- ✅ Full workflow works end-to-end
- ✅ Route params reflect current step
- ✅ State changes update routes

**Run:** `cd symphainy-frontend && npx playwright test scripts/test-phase7-routing.ts`

---

## 📋 Manual Testing Checklist

### Navigation Flow
- [ ] Click Content pillar → state updates, then route changes
- [ ] Click Insights pillar → state updates, then route changes
- [ ] Click Journey pillar → state updates, then route changes
- [ ] Click Business Outcomes pillar → state updates, then route changes
- [ ] Navigate with URL params → state syncs correctly
- [ ] Use browser back button → previous state restored
- [ ] Use browser forward button → next state restored

### Route → State Sync
- [ ] Navigate to `/pillars/content?file=test&step=parse`
  - [ ] URL params are in URL
  - [ ] State reflects URL params
  - [ ] UI reflects state
- [ ] Change state (e.g., select file)
  - [ ] Route updates to reflect state
  - [ ] URL params update
- [ ] Deep link to `/pillars/journey?artifact=sop-123&view=blueprint`
  - [ ] State syncs from URL
  - [ ] UI renders correctly

### Backend Integration
- [ ] Upload file in Content pillar
  - [ ] API call succeeds
  - [ ] State updates
  - [ ] Route updates
- [ ] Parse file
  - [ ] API call succeeds
  - [ ] State updates
  - [ ] Route reflects parse step
- [ ] Navigate between pillars
  - [ ] Session persists
  - [ ] API calls still work
  - [ ] No errors in console

### Content Pillar Workflow
- [ ] Start at `/pillars/content`
  - [ ] Initial state is upload step
- [ ] Upload file
  - [ ] Route updates (if implemented)
  - [ ] State updates
- [ ] Parse file
  - [ ] Route reflects parse step
  - [ ] State reflects parse step
- [ ] Complete workflow
  - [ ] All steps work
  - [ ] Route reflects current step
  - [ ] State drives UI

---

## 🚀 Running Tests

### Option 1: Quick Validation (No Containers)
```bash
cd symphainy-frontend
npx tsx scripts/test-phase7-routing-validation.ts
```

### Option 2: Full Integration Test (Starts Containers)
```bash
./scripts/test-phase7-integration.sh
```

### Option 3: Manual Browser Testing
1. Start containers: `docker-compose up -d`
2. Start frontend: `cd symphainy-frontend && npm run dev`
3. Open browser: `http://localhost:3000`
4. Follow manual testing checklist above

### Option 4: Playwright Tests Only (Containers Already Running)
```bash
cd symphainy-frontend
npx playwright test scripts/test-phase7-routing.ts
```

---

## 📊 Expected Results

### Quick Validation
- ✅ All 8 validation tests should pass
- ✅ Confirms code structure is correct

### Integration Test
- ✅ All containers start successfully
- ✅ Health checks pass
- ✅ Playwright tests pass (or manual testing confirms functionality)

### Browser Tests
- ✅ All navigation flow tests pass
- ✅ All route → state sync tests pass
- ✅ All backend integration tests pass
- ✅ All content pillar workflow tests pass

---

## 🔍 Troubleshooting

### Containers Not Starting
- Check Docker is running: `docker ps`
- Check ports are available: `netstat -tuln | grep -E '3000|8000|8001|8080'`
- Check logs: `docker-compose logs [service-name]`

### Frontend Not Accessible
- Check if frontend is running: `curl http://localhost:3000`
- Check Traefik routing: `curl http://localhost`
- Check frontend logs: `docker-compose logs frontend`

### Tests Failing
- Check browser console for errors
- Check network tab for failed API calls
- Verify session is active
- Check state in React DevTools

---

## ✅ Success Criteria

**Phase 7 is validated when:**
1. ✅ Quick validation tests pass
2. ✅ All containers start successfully
3. ✅ Navigation flow works correctly
4. ✅ Route → state sync works
5. ✅ Backend integration works
6. ✅ Content pillar workflow works end-to-end
7. ✅ No console errors
8. ✅ No API errors

---

**Status:** Ready for testing. Run `./scripts/test-phase7-integration.sh` to start.
