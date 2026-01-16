# Lightweight Content Pillar Test

**Date:** January 2026  
**Status:** 🧪 **LIGHTWEIGHT TEST PLAN**  
**Purpose:** Quick validation of migrated Content components before completing the pillar

---

## 🎯 Test Scope

**What We're Testing:**
- ✅ FileUploader component (migrated to new architecture)
- ✅ FileDashboard component (migrated to new architecture)
- ✅ PlatformStateProvider integration
- ✅ ContentAPIManager integration

**What We're NOT Testing Yet:**
- ⏳ Full end-to-end flows (wait until all components migrated)
- ⏳ Backend integration (wait until complete)
- ⏳ Error handling edge cases (wait until complete)

---

## ✅ Quick Validation Checklist

### 1. Component Import & Rendering
- [ ] FileUploader imports without errors
- [ ] FileDashboard imports without errors
- [ ] Components render without crashing
- [ ] No TypeScript errors

### 2. Hook Integration
- [ ] `usePlatformState` hook works
- [ ] `useContentAPIManager` hook works
- [ ] `useAuth` hook works
- [ ] No context errors

### 3. State Management
- [ ] FileUploader can access `state.realm.content`
- [ ] FileDashboard can access `state.realm.content`
- [ ] `setRealmState` updates state correctly
- [ ] State persists across component re-renders

### 4. API Manager Integration
- [ ] ContentAPIManager can be instantiated via hook
- [ ] Methods are accessible (uploadFile, listFiles)
- [ ] No runtime errors when calling methods

---

## 🧪 Manual Test Steps

### Test 1: Component Rendering
```bash
# Start frontend dev server
cd symphainy-frontend
npm run dev

# Navigate to Content Pillar
# Verify:
# - FileUploader renders
# - FileDashboard renders
# - No console errors
```

### Test 2: State Management
```typescript
// In browser console (on Content Pillar page):
// Check if PlatformStateProvider is working
window.__PLATFORM_STATE__ = true; // Set by provider

// Check realm state
// Should see: state.realm.content structure
```

### Test 3: File Upload Flow (If Backend Available)
1. Select a file in FileUploader
2. Click upload
3. Verify:
   - No immediate errors
   - State updates (if backend responds)
   - Toast notifications appear

### Test 4: File List (If Backend Available)
1. Load Content Pillar
2. Verify:
   - FileDashboard loads files
   - No errors in console
   - Files display (if backend has data)

---

## 🚦 Success Criteria

**Minimum for Proceeding:**
- ✅ Components import and render
- ✅ No TypeScript errors
- ✅ No runtime errors on mount
- ✅ Hooks work correctly

**Ideal:**
- ✅ Components render correctly
- ✅ State management works
- ✅ API manager accessible
- ✅ Basic interactions work

---

## 📊 Test Results

**Date:** ___________  
**Tester:** ___________  

### Component Import & Rendering
- [ ] FileUploader: PASS / FAIL / SKIP
- [ ] FileDashboard: PASS / FAIL / SKIP

### Hook Integration
- [ ] usePlatformState: PASS / FAIL / SKIP
- [ ] useContentAPIManager: PASS / FAIL / SKIP
- [ ] useAuth: PASS / FAIL / SKIP

### State Management
- [ ] State access: PASS / FAIL / SKIP
- [ ] State updates: PASS / FAIL / SKIP

### API Manager
- [ ] Instantiation: PASS / FAIL / SKIP
- [ ] Method access: PASS / FAIL / SKIP

### Notes:
_________________________________________________
_________________________________________________
_________________________________________________

---

## 🚀 Next Steps After Test

**If Tests Pass:**
- ✅ Continue with remaining Content components
- ✅ Complete FileParser, ParsePreview, DataMash, FileSelector
- ✅ Then do robust integration testing

**If Tests Fail:**
- ❌ Fix issues before proceeding
- ❌ Review foundation components
- ❌ Address root causes

---

**This lightweight test ensures we're on the right track before completing the pillar!** 🎯
