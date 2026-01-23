# Frontend Build Issue Analysis & Strategic Solution

**Date:** January 23, 2026  
**Status:** Analysis & Strategic Planning

---

## The Issue

### What's Happening

The Next.js production build (`npm run build`) is failing during the **prerendering phase** with errors like:

```
Error: useExperienceLayer must be used within an ExperienceLayerProvider
Error occurred prerendering page "/"
```

### Root Cause

1. **Next.js Standalone Mode Behavior:**
   - `output: 'standalone'` still attempts to **prerender pages during build time**
   - Even with `export const dynamic = 'force-dynamic'`, Next.js tries to generate static HTML first
   - During prerendering, React components execute in a Node.js context **without the full provider tree**

2. **Provider Context Missing During Build:**
   - During build, Next.js runs components in isolation
   - Provider contexts (AppProvider, ExperienceLayerProvider, etc.) aren't available
   - Components that use hooks like `useApp()`, `useExperienceLayer()`, `useGuideAgent()` throw errors

3. **Recent Changes:**
   - We migrated from `GlobalSessionProvider` to `PlatformStateProvider` + `AuthProvider` + `AppProvider`
   - We added `ExperienceLayerProvider` to the provider tree
   - These providers weren't designed with SSR/build-time execution in mind

---

## Why This Didn't Happen Before

### Root Cause Identified

**The old setup had `UserContextProvider` in the provider tree, but our new setup is missing it!**

**Old Provider Tree (from `/symphainy_source/`):**
```typescript
<GlobalSessionProvider>
  <AuthProvider>
    <AppProvider>
      <UserContextProviderComponent>  // ✅ WAS PRESENT
        <ExperienceLayerProvider>
          <GuideAgentProvider>
            {children}
          </GuideAgentProvider>
        </ExperienceLayerProvider>
      </UserContextProviderComponent>
    </AppProvider>
  </AuthProvider>
</GlobalSessionProvider>
```

**New Provider Tree (current):**
```typescript
<PlatformStateProvider>
  <AuthProvider>
    <AppProvider>
      <ExperienceLayerProvider>  // ❌ MISSING UserContextProvider!
        <GuideAgentProvider>
          {children}
        </GuideAgentProvider>
      </ExperienceLayerProvider>
    </AppProvider>
  </AuthProvider>
</PlatformStateProvider>
```

**The Problem:**
- `ExperienceLayerProvider` calls `useUserContext()` on line 72
- `UserContextProvider` is **not in the new provider tree**
- During build/prerender, the provider isn't available → build fails

### Why It Worked Before

1. **Complete Provider Tree:**
   - Old setup had all required providers in the correct order
   - `UserContextProvider` was present, so `ExperienceLayerProvider` worked

2. **Provider Dependencies Satisfied:**
   - All provider dependencies were in the tree
   - No missing providers during build

---

## Strategic Solution Options

### Option 1: SSR-Safe Providers (Recommended - Production-Ready)

**Approach:** Make all providers handle SSR/build-time gracefully

**Implementation:**
- Add SSR fallbacks to all provider hooks (like we did for `useApp`)
- Ensure providers return safe defaults during build-time
- This is the **proper Next.js pattern** for production

**Pros:**
- ✅ Production-ready
- ✅ Works with standalone output
- ✅ Proper SSR support
- ✅ No workarounds needed

**Cons:**
- ⚠️ Requires updating all provider hooks
- ⚠️ Need to ensure all hooks have SSR fallbacks

**Files to Update:**
- `shared/agui/AppProvider.tsx` - ✅ Already done
- `lib/contexts/ExperienceLayerProvider.tsx` - ⚠️ Needs SSR fallback
- `shared/auth/AuthProvider.tsx` - ⚠️ May need SSR fallback
- `shared/state/PlatformStateProvider.tsx` - ⚠️ May need SSR fallback

---

### Option 2: Skip Prerendering Entirely

**Approach:** Configure Next.js to skip static generation

**Implementation:**
- Use `output: 'standalone'` with all pages marked as dynamic
- Configure build to skip prerendering phase
- All pages render dynamically at runtime

**Pros:**
- ✅ Quick fix
- ✅ No provider changes needed

**Cons:**
- ⚠️ Loses static optimization benefits
- ⚠️ Slower initial page loads
- ⚠️ Not ideal for production performance

---

### Option 3: Hybrid Approach

**Approach:** 
- Make providers SSR-safe (Option 1)
- Mark pages that need providers as dynamic
- Keep static pages static

**Pros:**
- ✅ Best of both worlds
- ✅ Performance optimized
- ✅ Production-ready

**Cons:**
- ⚠️ More complex configuration
- ⚠️ Need to categorize pages

---

## Recommended Solution: Option 1 (SSR-Safe Providers)

This is the **strategic, production-ready approach** that aligns with Next.js best practices.

### Implementation Plan

1. **Add SSR Fallbacks to All Provider Hooks:**
   ```typescript
   export const useExperienceLayer = () => {
     const context = useContext(ExperienceLayerContext);
     if (context === undefined) {
       // SSR/build-time fallback
       if (typeof window === 'undefined') {
         return {
           client: experienceLayerClient,
           // ... safe defaults
         };
       }
       throw new Error("useExperienceLayer must be used within ExperienceLayerProvider");
     }
     return context;
   };
   ```

2. **Update All Provider Hooks:**
   - `useExperienceLayer` - Add SSR fallback
   - `useGuideAgent` - Add SSR fallback  
   - `useAuth` - Verify SSR fallback exists
   - `usePlatformState` - Verify SSR fallback exists

3. **Test Build:**
   - Run `npm run build` locally
   - Verify no prerender errors
   - Deploy to production

---

## Why This Is The Right Approach

1. **Aligns with Next.js Architecture:**
   - Next.js is designed for SSR
   - Providers should handle SSR gracefully
   - This is the standard pattern

2. **Production-Ready:**
   - Works with standalone output
   - Supports static optimization where possible
   - Proper error handling

3. **Maintainable:**
   - Clear pattern for future providers
   - No workarounds or hacks
   - Follows React/Next.js best practices

4. **Scalable:**
   - Works as the app grows
   - Handles new pages automatically
   - No special configuration needed per page

---

## Next Steps

1. ✅ **Analysis Complete** - Understanding the issue
2. ⏳ **Implement SSR Fallbacks** - Update all provider hooks
3. ⏳ **Test Build** - Verify it works
4. ⏳ **Deploy** - Production-ready solution

---

**Last Updated:** January 23, 2026
