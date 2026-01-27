# Phase 2: Updated Strategy - Breaking Changes

## Decision: Breaking Changes ✅

We're making **breaking changes** to enforce the architecture properly. This is the right time to "break shit" and do it right.

## Updated Approach

### 1. Mark `lib/api/*` as Internal
- ✅ Added deprecation warnings to `lib/api/fms.ts` and `lib/api/auth.ts`
- ⏳ Add to remaining `lib/api/*` files
- Components should NOT import directly

### 2. Update All Components to Use Hooks
- ✅ FileDashboard - uses `useFileAPI()`
- ✅ AuthProvider - uses `ServiceLayerAPI` directly
- ✅ AGUIEventProvider - uses `ServiceLayerAPI` directly
- ⏳ Remaining components - update to use hooks

### 3. Remove Direct Access (Final Step)
- After all components updated
- Make `lib/api/*` truly internal (or remove exports)
- Build will fail if anyone tries to import directly

## Migration Status

### ✅ Completed
- ServiceLayerAPI created
- useServiceLayerAPI hook created
- useFileAPI hook created
- AuthProvider updated
- AGUIEventProvider updated
- FileDashboard updated

### ⏳ In Progress
- Marking remaining `lib/api/*` files as internal
- Updating remaining components

### 📋 Next Steps
1. Test current changes
2. Update remaining components by feature area
3. Remove direct access to `lib/api/*`

## Benefits of Breaking Changes

1. **Single Source of Truth** - All API calls go through service layer
2. **Forced Architecture** - Can't bypass the service layer
3. **Automatic Token Management** - No manual token passing
4. **Consistent Error Handling** - All calls handled the same way
5. **Easier Maintenance** - One way to do things, not two
