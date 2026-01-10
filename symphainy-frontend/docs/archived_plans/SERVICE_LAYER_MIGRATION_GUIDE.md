# Service Layer Migration Guide

## Overview

This guide helps you migrate from direct API calls and WebSocket connections to the new service layer. The service layer provides standardized error handling, retry logic, session integration, and better maintainability.

## Migration Summary

### Before (Direct Service Calls)
```typescript
// Direct API calls scattered across components
const response = await fetch('/api/endpoint', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(data),
});

// Direct WebSocket connections
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Handle message
};
```

### After (Service Layer)
```typescript
// Unified service layer
import { useServiceLayer } from '@/shared/services';

const { api, websocket } = useServiceLayer();

// API calls with automatic error handling and retries
const response = await api.post('/api/endpoint', data);

// WebSocket with connection management
const connectionId = await websocket.connect('/ws');
websocket.subscribe(connectionId, 'message', handleMessage);
```

## Step-by-Step Migration

### Step 1: Update Component Imports

#### Before
```typescript
// components/SomeComponent.tsx
import { listFiles } from '@/lib/api/fms';
import { getSessionElements } from '@/lib/api/operations';

export function SomeComponent() {
  // Direct API calls
  const fetchFiles = async () => {
    try {
      const files = await listFiles();
      setFiles(files);
    } catch (error) {
      console.error('Failed to fetch files:', error);
    }
  };
}
```

#### After
```typescript
// components/SomeComponent.tsx
import { useServiceLayer } from '@/shared/services';

export function SomeComponent() {
  const { api } = useServiceLayer();
  
  // Service layer API calls
  const fetchFiles = async () => {
    try {
      const response = await api.get('/api/fms/files');
      setFiles(response.data);
    } catch (error) {
      // Automatic error handling
      console.error('Failed to fetch files:', error);
    }
  };
}
```

### Step 2: Update WebSocket Usage

#### Before
```typescript
// components/chatbot/PrimaryChatbot.tsx
export function PrimaryChatbot() {
  const [ws, setWs] = useState<WebSocket | null>(null);
  
  useEffect(() => {
    const websocket = new WebSocket('ws://127.0.0.1:8000/api/ws/agent-chat');
    
    websocket.onopen = () => {
      console.log('WebSocket connected');
    };
    
    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      // Handle message
    };
    
    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    setWs(websocket);
    
    return () => {
      websocket.close();
    };
  }, []);
}
```

#### After
```typescript
// components/chatbot/PrimaryChatbot.tsx
import { useServiceLayer } from '@/shared/services';

export function PrimaryChatbot() {
  const { websocket } = useServiceLayer();
  const [connectionId, setConnectionId] = useState<string | null>(null);
  
  useEffect(() => {
    const connectWebSocket = async () => {
      try {
        const id = await websocket.connect('/api/ws/agent-chat');
        setConnectionId(id);
        
        // Subscribe to messages
        const unsubscribe = websocket.subscribe(id, 'message', (message) => {
          // Handle message
        });
        
        return unsubscribe;
      } catch (error) {
        console.error('Failed to connect WebSocket:', error);
      }
    };
    
    const unsubscribe = connectWebSocket();
    return () => {
      if (connectionId) {
        websocket.disconnect(connectionId);
      }
      unsubscribe?.then(unsub => unsub());
    };
  }, [websocket]);
}
```

### Step 3: Update Error Handling

#### Before
```typescript
// Manual error handling
const handleAPIError = (error: any) => {
  if (error.status === 404) {
    // Handle not found
  } else if (error.status === 401) {
    // Handle unauthorized
  } else {
    // Handle other errors
  }
};

try {
  const response = await fetch('/api/endpoint');
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  const data = await response.json();
} catch (error) {
  handleAPIError(error);
}
```

#### After
```typescript
// Automatic error handling with service layer
try {
  const response = await api.get('/api/endpoint');
  // Response is automatically validated
  const data = response.data;
} catch (error) {
  // Service layer provides structured error information
  if (error.retryable) {
    // Automatic retry logic
  } else {
    // Handle non-retryable errors
  }
}
```

### Step 4: Update Session Integration

#### Before
```typescript
// Manual session token handling
const { guideSessionToken } = useGlobalSession();

const makeAuthenticatedRequest = async () => {
  const response = await fetch('/api/authenticated', {
    headers: {
      'Authorization': `Bearer ${guideSessionToken}`,
      'Content-Type': 'application/json',
    },
  });
};
```

#### After
```typescript
// Automatic session integration
const { api } = useServiceLayer();

const makeAuthenticatedRequest = async () => {
  // Session token automatically included
  const response = await api.get('/api/authenticated', { requireAuth: true });
};
```

## Migration Checklist

### Phase 1: Foundation Setup
- [ ] Install service layer dependencies
- [ ] Update application root with service layer initialization
- [ ] Test basic service layer functionality
- [ ] Verify session integration

### Phase 2: API Migration
- [ ] Identify all direct API calls in components
- [ ] Replace `fetch` calls with service layer API methods
- [ ] Update error handling to use service layer error structure
- [ ] Test API functionality with service layer

### Phase 3: WebSocket Migration
- [ ] Identify all WebSocket connections in components
- [ ] Replace direct WebSocket usage with service layer methods
- [ ] Update message handling to use service layer subscriptions
- [ ] Test WebSocket functionality with service layer

### Phase 4: Advanced Features
- [ ] Implement retry logic for failed requests
- [ ] Add connection pooling for WebSockets
- [ ] Configure environment-specific settings
- [ ] Test error recovery and reconnection

### Phase 5: Cleanup
- [ ] Remove old API utility functions
- [ ] Remove direct WebSocket implementations
- [ ] Update TypeScript types
- [ ] Update documentation

## Common Migration Patterns

### Pattern 1: Simple API Call

#### Before
```typescript
const response = await fetch('/api/users', {
  method: 'GET',
  headers: { 'Content-Type': 'application/json' },
});
const users = await response.json();
```

#### After
```typescript
const { api } = useServiceLayer();
const response = await api.get('/api/users');
const users = response.data;
```

### Pattern 2: POST Request with Data

#### Before
```typescript
const response = await fetch('/api/users', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(userData),
});
const newUser = await response.json();
```

#### After
```typescript
const { api } = useServiceLayer();
const response = await api.post('/api/users', userData);
const newUser = response.data;
```

### Pattern 3: Authenticated Request

#### Before
```typescript
const response = await fetch('/api/protected', {
  headers: {
    'Authorization': `Bearer ${sessionToken}`,
    'Content-Type': 'application/json',
  },
});
```

#### After
```typescript
const { api } = useServiceLayer();
const response = await api.get('/api/protected', { requireAuth: true });
```

### Pattern 4: WebSocket Connection

#### Before
```typescript
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  handleMessage(data);
};
```

#### After
```typescript
const { websocket } = useServiceLayer();
const connectionId = await websocket.connect('/ws');
const unsubscribe = websocket.subscribe(connectionId, 'message', handleMessage);
```

### Pattern 5: Error Handling

#### Before
```typescript
try {
  const response = await fetch('/api/endpoint');
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  const data = await response.json();
} catch (error) {
  if (error.message.includes('404')) {
    // Handle not found
  } else if (error.message.includes('401')) {
    // Handle unauthorized
  }
}
```

#### After
```typescript
const { api } = useServiceLayer();

try {
  const response = await api.get('/api/endpoint');
  const data = response.data;
} catch (error) {
  if (error.status === 404) {
    // Handle not found
  } else if (error.status === 401) {
    // Handle unauthorized
  } else if (error.retryable) {
    // Automatic retry logic
  }
}
```

## Testing Migration

### Before
```typescript
// Test individual API calls
import { renderHook } from '@testing-library/react';
import { listFiles } from '@/lib/api/fms';

test('list files API', async () => {
  // Mock fetch and test
});
```

### After
```typescript
// Test service layer
import { renderHook } from '@testing-library/react';
import { useServiceLayer } from '@/shared/services';

test('service layer API', async () => {
  const { result } = renderHook(() => useServiceLayer(), {
    wrapper: SessionProvider,
  });
  
  // Test with service layer
});
```

## Performance Considerations

### Automatic Optimizations
- **Connection Pooling**: WebSocket connections are pooled and reused
- **Request Deduplication**: Identical requests are deduplicated
- **Automatic Retries**: Failed requests are automatically retried
- **Error Recovery**: Automatic error recovery and reconnection

### Manual Optimizations
- **Request Caching**: Implement caching for frequently accessed data
- **Batch Requests**: Group multiple requests into single calls
- **Lazy Loading**: Load data only when needed
- **Connection Management**: Properly manage WebSocket connections

## Troubleshooting

### Common Issues

#### Issue 1: Service layer not initialized
**Cause**: Missing service layer initialization
**Solution**: Ensure service layer is initialized in app root

#### Issue 2: Session not available
**Cause**: Session context not provided to service layer
**Solution**: Ensure SessionProvider wraps components using service layer

#### Issue 3: WebSocket connection failures
**Cause**: Incorrect WebSocket URL or authentication
**Solution**: Check WebSocket configuration and authentication

#### Issue 4: API request failures
**Cause**: Incorrect API endpoint or authentication
**Solution**: Verify API endpoints and authentication headers

### Debug Tools

```typescript
// Development only - shows service layer debug info
import { useServiceLayer } from '@/shared/services';

function DebugComponent() {
  const { api, websocket } = useServiceLayer();
  
  // Log service layer state
  console.log('API Service:', api.getConfig());
  console.log('WebSocket Service:', websocket.getConfig());
  console.log('Active Connections:', websocket.getActiveConnections());
}
```

## Rollback Plan

If issues arise during migration:

1. **Keep old patterns** alongside new service layer
2. **Gradually migrate** components one by one
3. **Test thoroughly** after each migration
4. **Monitor performance** and error rates
5. **Rollback individual components** if needed

## Support

For migration support:
1. Check this guide for common patterns
2. Review the service layer documentation
3. Test with the provided examples
4. Use the debug tools for troubleshooting
5. Check the test suite for usage examples 