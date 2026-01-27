# Phase 2: Service Layer Standardization - API Call Audit

## Direct API Calls Found

### 🔴 Components with Direct fetch() Calls

1. **`shared/agui/AGUIEventProvider.tsx`**
   - Line ~50: `fetch("/global/agent", ...)`
   - **Action:** Move to service layer

2. **`shared/auth/AuthProvider.tsx`**
   - Likely has fetch calls for login/register
   - **Action:** Verify if using service layer or direct calls

3. **`app/(protected)/pillars/content/components/*`**
   - Multiple content components
   - **Action:** Audit each file

4. **`components/insights/AGUIInsightsPanel.tsx`**
   - **Action:** Audit for direct API calls

### 🟡 Service Files (Acceptable - but should use SessionBoundaryProvider)

1. **`shared/services/ExperiencePlaneClient.ts`**
   - Uses fetch internally (acceptable for service layer)
   - **Action:** Ensure it uses SessionBoundaryProvider for tokens

2. **`shared/services/RuntimeClient.ts`**
   - WebSocket client (acceptable)
   - **Action:** Already updated to follow session state

3. **`shared/managers/*APIManager.ts`**
   - API managers (acceptable pattern)
   - **Action:** Ensure they use SessionBoundaryProvider for tokens

### 📋 lib/api Directory

Need to audit `lib/api/` directory - these might be direct API functions that should go through service layer.

## Action Plan

1. ✅ Create audit document (this file)
2. ⏳ Audit each component with direct fetch calls
3. ⏳ Enhance UnifiedServiceLayer to use SessionBoundaryProvider
4. ⏳ Create service layer methods for all API endpoints
5. ⏳ Refactor components to use service layer hooks
6. ⏳ Update API managers to use SessionBoundaryProvider
