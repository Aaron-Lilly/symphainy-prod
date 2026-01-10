# Service Layer Migration Guide

## Problem
The current service layer causes SSR issues during Next.js build because it imports React and other client-side dependencies at the module level.

## Solution: Lazy Service Layer

Replace the current service layer with a client-side only implementation that lazy loads services.

## Migration Steps

### 1. Update AppProviders

Replace the current service layer initialization with the lazy service layer:

```typescript
// Before (in AppProviders.tsx)
import { useServiceLayer } from '@/shared/hooks/useServiceLayer';

// After
import { useClientServiceLayer } from '@/shared/services/ClientServiceLayer';
```

### 2. Update Component Usage

Replace direct service layer imports with the lazy service layer:

```typescript
// Before
import { useServiceLayer } from '@/shared/services';
const { api, websocket } = useServiceLayer();

// After
import { useServiceLayerClient } from '@/shared/services/ClientServiceLayer';
const { api, websocket, isInitialized, isLoading } = useServiceLayerClient({
  sessionToken: guideSessionToken
});
```

### 3. Add Loading States

Handle loading states in components:

```typescript
const { api, websocket, isInitialized, isLoading, error } = useServiceLayerClient({
  sessionToken: guideSessionToken
});

if (isLoading) {
  return <div>Loading services...</div>;
}

if (error) {
  return <div>Error: {error}</div>;
}

if (!isInitialized) {
  return <div>Services not initialized</div>;
}

// Use services normally
```

### 4. Update Pillar Pages

Update all pillar pages to use the new service layer:

```typescript
// In each pillar page
import { useServiceLayerClient } from '@/shared/services/ClientServiceLayer';

export default function PillarPage() {
  const { guideSessionToken } = useGlobalSession();
  const { api, websocket, isInitialized, isLoading } = useServiceLayerClient({
    sessionToken: guideSessionToken
  });

  // Rest of component logic
}
```

### 5. Remove Conditional Imports

Remove all the conditional imports we added during troubleshooting:

```typescript
// Remove these patterns
let ServiceName: any;
if (typeof window !== 'undefined') {
  ServiceName = require('@/shared/services/service').ServiceName;
}
```

## Benefits

1. **SSR Safe**: No more React import errors during build
2. **Performance**: Services only load when needed
3. **Clean Architecture**: Maintains sophisticated service layer design
4. **Error Handling**: Proper loading and error states
5. **Type Safety**: Full TypeScript support

## Implementation Priority

1. **High Priority**: Update AppProviders and main service layer hook
2. **Medium Priority**: Update pillar pages and chatbot components
3. **Low Priority**: Update utility components and error handlers

## Testing

After migration:
1. Run `npm run build` - should complete without SSR errors
2. Test all pillar pages in development mode
3. Test authentication flow
4. Test WebSocket connections
5. Test Guide Agent functionality

## Rollback Plan

If issues arise, the current conditional import approach can be maintained as a temporary solution while the lazy service layer is refined.





























