# Phase 7: Route Audit - MVP vs Non-MVP Routes

**Date:** January 22, 2026  
**Purpose:** Identify which routes are in scope for Phase 7 MVP routing refactoring

---

## ✅ MVP Routes (In Scope for Phase 7)

These routes are **core to the MVP** and should be refactored in Phase 7:

### Core Journey Routes
1. **`/` (protected)** - Main dashboard/landing
   - Entry point for authenticated users
   - Should reflect current journey state

2. **`/pillars/content`** - Content Pillar
   - File upload, parsing, data mash
   - Core MVP functionality

3. **`/pillars/insights`** - Insights Pillar
   - Data analysis, VARK insights
   - Core MVP functionality

4. **`/pillars/journey`** - Journey Pillar
   - SOP/workflow generation, coexistence blueprint
   - Core MVP functionality

5. **`/pillars/business-outcomes`** - Business Outcomes Pillar
   - Artifact generation, insights ecosystem
   - Core MVP functionality

6. **`/login`** - Authentication
   - Session initialization
   - Core MVP functionality

---

## ❌ Non-MVP Routes (Out of Scope for Phase 7)

These routes are **NOT part of the MVP** and should be **excluded** from Phase 7 refactoring:

### 1. `/admin` - Admin Dashboard ⚠️ **MAJOR NON-MVP ROUTE**
**Location:** `app/(protected)/admin/page.tsx`

**Features:**
- Control Room View - Platform observability and governance
- Developer View - SDK documentation, playground, feature submission
- Business User View - Solution composition, templates, feature requests

**Why Out of Scope:**
- Platform administration features (post-MVP)
- Developer tooling (post-MVP)
- Solution composition tools (post-MVP)
- Not part of core user journey

**Recommendation:** 
- **Exclude from Phase 7**
- Can be refactored later if needed
- Focus Phase 7 on core journey routes only

---

### 2. `/smart-city-test` - Smart City Test Page
**Location:** `app/smart-city-test/page.tsx`

**Purpose:** Test page for Smart City Chat component

**Why Out of Scope:**
- Test/development route
- Not part of production MVP

**Recommendation:**
- **Exclude from Phase 7**
- Can be removed or kept as-is

---

### 3. `/test` - Simple Test Page
**Location:** `app/test/page.tsx`

**Purpose:** Simple test page to verify routing works

**Why Out of Scope:**
- Test/development route
- Not part of production MVP

**Recommendation:**
- **Exclude from Phase 7**
- Can be removed or kept as-is

---

### 4. `/test-experience-layer` - Experience Layer Test Page
**Location:** `app/test-experience-layer/page.tsx`

**Purpose:** Test page for Experience Layer Client

**Why Out of Scope:**
- Test/development route
- Not part of production MVP

**Recommendation:**
- **Exclude from Phase 7**
- Can be removed or kept as-is

---

## 📊 Summary

### In Scope (Phase 7): **7 routes**
- `/` (protected)
- `/pillars/content`
- `/pillars/insights`
- `/pillars/journey`
- `/pillars/business-outcomes`
- `/admin` - Platform Showcase ✅ **IN SCOPE**
- `/login`

### Out of Scope (Phase 7): **3 routes**
- `/smart-city-test`
- `/test`
- `/test-experience-layer`

---

## 🎯 Phase 7 Focus

**Phase 7 should focus on:**
1. Core journey routes (`/pillars/*`)
2. Main dashboard (`/`)
3. Platform Showcase (`/admin`) ✅ **INCLUDED**
4. Authentication (`/login`)

**Phase 7 should EXCLUDE:**
1. Test routes (`/test*`, `/smart-city-test`) - Development/testing

**Phase 7.5 will handle:**
1. Platform Showcase sync with backend vision
2. Navigation access (titlebar link, visually distinct but lower key)

---

## 💡 Recommendation

**For Phase 7 implementation:**
- Apply "capability by design, implementation by policy" approach
- Establish routing patterns/foundations
- **Implement only MVP routes** (6 routes listed above)
- **Document patterns** for future routes (like `/admin`) but don't implement them
- Test routes can remain as-is or be removed

**This aligns with:**
- MVP focus
- "Capability by design, implementation by policy" approach
- Avoiding scope creep
- Establishing patterns for future expansion

---

## ✅ Action Items for Phase 7

1. **Audit MVP routes** (7 routes including Platform Showcase)
2. **Map journey state to MVP routes**
3. **Refactor MVP routes** to reflect journey state
4. **Include Platform Showcase (`/admin`)** in refactoring
5. **Exclude test routes** from refactoring
6. **Keep test routes as-is** (or remove if desired)

## ✅ Action Items for Phase 7.5

1. **Sync Platform Showcase with backend vision**
   - Review backend requirements
   - Ensure frontend alignment
   - Update components as needed

2. **Add navigation access**
   - Add Platform Showcase link to main layout titlebar
   - Make it visually distinct but "lower key" than pillars
   - Use hyperlink or subtle visual treatment
   - Ensure accessibility without competing with primary navigation

3. **Consider renaming**
   - `/admin` → `/platform-showcase` or similar
   - Better reflects its purpose as platform showcase

---

**Conclusion:** Phase 7 should focus on the **7 core MVP routes** (including Platform Showcase). Phase 7.5 will ensure Platform Showcase is in sync with backend vision and accessible via titlebar navigation.
