# Frontend Systematic Fix Plan

## Root Cause Analysis

### Primary Issues Identified:
1. **API Client Fragmentation**: Multiple conflicting API clients
   - `fms.ts` → `/api/fms` (404 - doesn't exist)
   - `content.ts` → `/api/content` (exists)
   - `experience-dimension.ts` → Experience Dimension (newest)
   - `insights.ts` → `/api/insights` (exists)
   - `operations.ts` → `/api/operations` (exists)

2. **Component Dependencies**: Components using outdated APIs
   - FileDashboard uses `@/lib/api/fms` (404)
   - Other components may have similar issues

3. **Backend Integration Gap**: Frontend not aligned with new backend architecture

## Systematic Fix Strategy

### Phase 1: API Client Standardization
- [ ] Audit all API clients and their usage
- [ ] Create unified API client strategy
- [ ] Map old endpoints to new backend endpoints
- [ ] Implement proper error handling

### Phase 2: Component Migration
- [ ] Update FileDashboard to use correct API
- [ ] Update all pillar components to use unified API
- [ ] Add proper loading states and error handling
- [ ] Test each component individually

### Phase 3: Integration Testing
- [ ] Test all pillar routes end-to-end
- [ ] Validate API integration
- [ ] Fix any remaining routing issues

### Phase 4: Type Safety & Code Quality
- [ ] Fix TypeScript `any` types
- [ ] Implement proper error boundaries
- [ ] Add comprehensive error handling
- [ ] Clean up unused imports and code

## Implementation Priority

1. **Critical**: Fix API client usage (causing timeouts)
2. **High**: Standardize API integration across components
3. **Medium**: Improve error handling and loading states
4. **Low**: Type safety and code quality improvements

## Success Criteria

- All pillar routes load without timeouts
- Components use correct backend APIs
- Proper error handling and loading states
- Type-safe implementation
- Clean, maintainable codebase
