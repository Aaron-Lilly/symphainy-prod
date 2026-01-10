# Service Layer Documentation

This document provides comprehensive documentation for the service layer architecture, patterns, and integration used in the Symphainy frontend application.

## 📋 Table of Contents

- [Overview](#overview)
- [Service Architecture](#service-architecture)
- [Core Services](#core-services)
- [Cross-Pillar Services](#cross-pillar-services)
- [Service Layer Manager](#service-layer-manager)
- [Configuration Management](#configuration-management)
- [Error Handling](#error-handling)
- [Testing Services](#testing-services)
- [Best Practices](#best-practices)

## 🎯 Overview

The Symphainy frontend service layer provides a comprehensive abstraction for:

- **API Communication** - Standardized HTTP requests with error handling
- **WebSocket Management** - Real-time communication with connection pooling
- **Cross-Pillar Integration** - Data sharing and communication between pillars
- **Smart City Integration** - Orchestration through Smart City components
- **Session Management** - Authentication and state synchronization
- **Configuration Management** - Environment-specific service configuration

## 🏗️ Service Architecture

### Service Layer Structure

```
Service Layer Manager
├── APIService
│   ├── HTTP Client
│   ├── Error Handling
│   ├── Retry Logic
│   └── Authentication
├── WebSocketService
│   ├── Connection Pooling
│   ├── Auto-reconnection
│   ├── Message Queuing
│   └── Event Handling
├── CrossPillarService
│   ├── Data Sharing
│   ├── Communication
│   ├── State Synchronization
│   └── Smart City Integration
└── Configuration
    ├── Environment Settings
    ├── Service Configuration
    └── Dynamic Updates
```

### Service Integration Pattern

```typescript
// Service layer provides unified interface
import { 
  ServiceLayerManager, 
  useServiceLayer,
  apiService,
  webSocketService,
  CrossPillarService 
} from '@/shared/services';

// Initialize service layer
const serviceManager = new ServiceLayerManager();
serviceManager.initialize(sessionContext);

// Use in components
function MyComponent() {
  const { apiService, webSocketService } = useServiceLayer();
  
  // Use services
  const fetchData = async () => {
    const data = await apiService.get('/api/data');
    return data;
  };
  
  return <div>Component using services</div>;
}
```

## 🔧 Core Services

### APIService

The `APIService` provides standardized HTTP communication with built-in error handling and retry logic.

#### Basic Usage

```typescript
import { APIService, apiService } from '@/shared/services';

// Using singleton instance
const response = await apiService.get('/api/users');

// Using class directly
const api = new APIService();
const response = await api.get('/api/users');
```

#### Request Methods

```typescript
// GET request
const users = await apiService.get('/api/users');

// POST request with body
const newUser = await apiService.post('/api/users', {
  name: 'John Doe',
  email: 'john@example.com'
});

// PUT request
const updatedUser = await apiService.put('/api/users/123', {
  name: 'Jane Doe'
});

// DELETE request
await apiService.delete('/api/users/123');

// PATCH request
const partialUpdate = await apiService.patch('/api/users/123', {
  email: 'jane@example.com'
});
```

#### Advanced Configuration

```typescript
// Custom request options
const response = await apiService.get('/api/data', {
  headers: { 'Custom-Header': 'value' },
  timeout: 5000,
  retries: 3,
  retryDelay: 1000,
  requireAuth: true
});

// Custom request method
const response = await apiService.request('/api/custom', {
  method: 'POST',
  body: { custom: 'data' },
  headers: { 'Content-Type': 'application/json' }
});
```

#### Error Handling

```typescript
try {
  const response = await apiService.get('/api/data');
  // Handle success
} catch (error) {
  if (error.retryable) {
    // Handle retryable error
    console.log('Retryable error:', error.message);
  } else {
    // Handle non-retryable error
    console.error('Non-retryable error:', error.message);
  }
}
```

### WebSocketService

The `WebSocketService` manages WebSocket connections with automatic reconnection and message queuing.

#### Connection Management

```typescript
import { WebSocketService, webSocketService } from '@/shared/services';

// Connect to WebSocket
const connectionId = await webSocketService.connect('/ws/chat', {
  requireAuth: true,
  autoReconnect: true,
  heartbeat: true
});

// Send message
await webSocketService.send(connectionId, {
  type: 'chat_message',
  data: { text: 'Hello, world!' },
  timestamp: Date.now()
});

// Subscribe to events
const unsubscribe = webSocketService.subscribe(connectionId, 'message', (message) => {
  console.log('Received message:', message);
});

// Disconnect
webSocketService.disconnect(connectionId);
```

#### Connection Options

```typescript
interface WebSocketConnectionOptions {
  requireAuth?: boolean;      // Include authentication headers
  autoReconnect?: boolean;    // Automatically reconnect on disconnect
  heartbeat?: boolean;        // Enable heartbeat monitoring
}

// Example with custom options
const connectionId = await webSocketService.connect('/ws/chat', {
  requireAuth: true,
  autoReconnect: true,
  heartbeat: true
});
```

#### Message Handling

```typescript
// Message format
interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: number;
  id?: string;
}

// Subscribe to specific message types
webSocketService.subscribe(connectionId, 'user_joined', (message) => {
  console.log('User joined:', message.data);
});

webSocketService.subscribe(connectionId, 'user_left', (message) => {
  console.log('User left:', message.data);
});

// Send typed messages
await webSocketService.send(connectionId, {
  type: 'chat_message',
  data: { 
    text: 'Hello!',
    userId: 'user123'
  },
  timestamp: Date.now()
});
```

#### Connection Status

```typescript
// Check connection status
const status = webSocketService.getConnectionStatus(connectionId);
console.log('Connection status:', status); // 'connecting' | 'connected' | 'disconnected' | 'error'

// Check if connected
const isConnected = webSocketService.isConnected(connectionId);

// Get all active connections
const activeConnections = webSocketService.getActiveConnections();
```

## 🔗 Cross-Pillar Services

### CrossPillarService

The `CrossPillarService` enables communication and data sharing between application pillars.

#### Data Sharing

```typescript
import { CrossPillarService } from '@/shared/services/cross-pillar';

// Share data between pillars
const result = await CrossPillarService.shareData({
  sourcePillar: 'content',
  targetPillar: 'insights',
  data: { files: ['file1.csv', 'file2.csv'] },
  metadata: { type: 'file_list' }
});

// Share data with validation
const validatedData = await CrossPillarService.shareDataWithValidation({
  sourcePillar: 'content',
  targetPillar: 'insights',
  data: { dataset: 'sales_data' },
  validationRules: {
    required: ['dataset'],
    format: 'json'
  }
});

// Batch share multiple data items
const batchResult = await CrossPillarService.batchShareData([
  {
    sourcePillar: 'content',
    targetPillar: 'insights',
    data: { files: ['data1.csv'] }
  },
  {
    sourcePillar: 'content',
    targetPillar: 'operations',
    data: { files: ['data2.csv'] }
  }
]);
```

#### Communication

```typescript
// Send communication between pillars
await CrossPillarService.sendCommunication({
  fromPillar: 'operations',
  toPillar: 'experience',
  messageType: 'workflow_complete',
  data: { workflowId: 'wf-123', status: 'completed' }
});

// Broadcast message to multiple pillars
await CrossPillarService.broadcastMessage({
  fromPillar: 'content',
  targetPillars: ['insights', 'operations', 'experience'],
  messageType: 'data_updated',
  data: { timestamp: Date.now() }
});

// Send message with retry logic
await CrossPillarService.sendMessageWithRetry({
  fromPillar: 'insights',
  toPillar: 'experience',
  messageType: 'analysis_complete',
  data: { analysisId: 'analysis-123' },
  retryOptions: {
    maxRetries: 3,
    retryDelay: 1000
  }
});
```

#### State Synchronization

```typescript
// Synchronize state across pillars
await CrossPillarService.syncState({
  pillar: 'insights',
  state: { currentAnalysis: 'data_quality' },
  priority: 'high'
});

// Handle state conflicts
const conflictResolution = await CrossPillarService.handleStateConflicts({
  pillar: 'operations',
  conflicts: [
    { field: 'workflow', value1: 'workflow1', value2: 'workflow2' }
  ],
  resolutionStrategy: 'latest_wins'
});
```

#### Smart City Integration

```typescript
// Route request through Smart City
const routedResponse = await CrossPillarService.routeRequest({
  pillar: 'operations',
  requestType: 'workflow_execution',
  data: { workflowId: 'wf-123' }
});

// Orchestrate workflow
const workflowResult = await CrossPillarService.orchestrateWorkflow({
  workflowId: 'wf-123',
  steps: [
    { pillar: 'content', action: 'load_data' },
    { pillar: 'insights', action: 'analyze_data' },
    { pillar: 'operations', action: 'create_workflow' }
  ]
});

// Persist state
await CrossPillarService.persistState({
  pillar: 'insights',
  state: { currentAnalysis: 'data_quality' },
  metadata: { timestamp: Date.now() }
});
```

## 🎛️ Service Layer Manager

### ServiceLayerManager

The `ServiceLayerManager` provides unified management of all services.

#### Initialization

```typescript
import { ServiceLayerManager } from '@/shared/services';

// Create service manager
const serviceManager = new ServiceLayerManager();

// Initialize with session context
serviceManager.initialize(sessionContext);

// Update configuration
serviceManager.updateConfig({
  api: { 
    timeout: 15000,
    maxRetries: 5
  },
  websocket: { 
    heartbeatInterval: 60000,
    reconnectAttempts: 10
  }
});
```

#### Service Access

```typescript
// Get service instances
const apiService = serviceManager.getAPIService();
const webSocketService = serviceManager.getWebSocketService();

// Use services
const data = await apiService.get('/api/data');
const connectionId = await webSocketService.connect('/ws/chat');
```

#### Configuration Management

```typescript
// Create service configuration
const config = createServiceConfig('production');

// Initialize with configuration
initializeServiceLayer('production');

// Update configuration dynamically
serviceManager.updateConfig({
  api: { baseURL: 'https://api.production.com' },
  websocket: { baseURL: 'wss://ws.production.com' }
});
```

#### Cleanup

```typescript
// Cleanup all services
serviceManager.cleanup();

// This will:
// - Close all WebSocket connections
// - Cancel pending API requests
// - Clear event listeners
// - Reset service state
```

### React Hook Integration

```typescript
import { useServiceLayer } from '@/shared/services';

function MyComponent() {
  const { 
    apiService, 
    webSocketService, 
    serviceManager 
  } = useServiceLayer();

  // Use services in component
  const fetchData = async () => {
    const data = await apiService.get('/api/data');
    return data;
  };

  const connectWebSocket = async () => {
    const connectionId = await webSocketService.connect('/ws/chat');
    return connectionId;
  };

  return (
    <div>
      <button onClick={fetchData}>Fetch Data</button>
      <button onClick={connectWebSocket}>Connect WebSocket</button>
    </div>
  );
}
```

## ⚙️ Configuration Management

### Environment Configuration

```typescript
// Environment-specific configuration
const environments = {
  development: {
    api: {
      baseURL: 'http://localhost:8000',
      timeout: 10000,
      maxRetries: 3
    },
    websocket: {
      baseURL: 'ws://localhost:8000',
      reconnectAttempts: 5,
      heartbeatInterval: 30000
    }
  },
  production: {
    api: {
      baseURL: 'https://api.symphainy.com',
      timeout: 15000,
      maxRetries: 5
    },
    websocket: {
      baseURL: 'wss://ws.symphainy.com',
      reconnectAttempts: 10,
      heartbeatInterval: 60000
    }
  }
};
```

### Dynamic Configuration

```typescript
// Update configuration at runtime
serviceManager.updateConfig({
  api: {
    timeout: 20000,
    headers: { 'Custom-Header': 'value' }
  }
});

// Get current configuration
const currentConfig = serviceManager.getConfig();
console.log('Current config:', currentConfig);
```

### Feature Flags

```typescript
// Feature flag configuration
const featureFlags = {
  enableWebSocket: true,
  enableRetryLogic: true,
  enableHeartbeat: true,
  enableCrossPillar: true
};

// Conditional service initialization
if (featureFlags.enableWebSocket) {
  webSocketService.enable();
} else {
  webSocketService.disable();
}
```

## 🚨 Error Handling

### Service Error Types

```typescript
// API Error
interface APIError {
  message: string;
  status?: number;
  code?: string;
  details?: any;
  retryable: boolean;
}

// WebSocket Error
interface WebSocketError {
  message: string;
  code: string;
  connectionId?: string;
  retryable: boolean;
}

// Cross-Pillar Error
interface CrossPillarError {
  message: string;
  pillar?: string;
  operation?: string;
  retryable: boolean;
}
```

### Error Handling Patterns

```typescript
// Global error handler
const handleServiceError = (error: any) => {
  if (error.retryable) {
    // Implement retry logic
    console.log('Retryable error:', error.message);
  } else {
    // Handle non-retryable error
    console.error('Non-retryable error:', error.message);
  }
};

// Service-specific error handling
try {
  const data = await apiService.get('/api/data');
} catch (error) {
  if (error.status === 401) {
    // Handle authentication error
    handleAuthenticationError();
  } else if (error.status === 500) {
    // Handle server error
    handleServerError();
  } else {
    // Handle other errors
    handleGenericError(error);
  }
}
```

### Retry Logic

```typescript
// Configure retry behavior
const retryConfig = {
  maxRetries: 3,
  retryDelay: 1000,
  backoffMultiplier: 2,
  retryableStatuses: [408, 429, 500, 502, 503, 504]
};

// Use in API calls
const response = await apiService.get('/api/data', {
  retries: retryConfig.maxRetries,
  retryDelay: retryConfig.retryDelay
});
```

## 🧪 Testing Services

### Mocking Services

```typescript
// Mock API service
const mockApiService = {
  get: jest.fn().mockResolvedValue({ data: 'mocked data' }),
  post: jest.fn().mockResolvedValue({ data: 'mocked response' }),
  put: jest.fn().mockResolvedValue({ data: 'mocked update' }),
  delete: jest.fn().mockResolvedValue({ data: 'mocked delete' })
};

// Mock WebSocket service
const mockWebSocketService = {
  connect: jest.fn().mockResolvedValue('mock-connection-id'),
  send: jest.fn().mockResolvedValue(undefined),
  subscribe: jest.fn().mockReturnValue(() => {}),
  disconnect: jest.fn()
};

// Provide mocks to components
function TestWrapper({ children }) {
  return (
    <ServiceProvider
      apiService={mockApiService}
      webSocketService={mockWebSocketService}
    >
      {children}
    </ServiceProvider>
  );
}
```

### Service Testing

```typescript
import { renderHook, act } from '@testing-library/react';
import { useServiceLayer } from '@/shared/services';

describe('Service Layer', () => {
  it('should provide service instances', () => {
    const { result } = renderHook(() => useServiceLayer(), {
      wrapper: ServiceProvider
    });

    expect(result.current.apiService).toBeDefined();
    expect(result.current.webSocketService).toBeDefined();
  });

  it('should handle API calls', async () => {
    const { result } = renderHook(() => useServiceLayer(), {
      wrapper: ServiceProvider
    });

    await act(async () => {
      const response = await result.current.apiService.get('/api/test');
      expect(response.data).toBe('mocked data');
    });
  });
});
```

### Integration Testing

```typescript
// Test cross-pillar communication
describe('Cross-Pillar Communication', () => {
  it('should share data between pillars', async () => {
    const result = await CrossPillarService.shareData({
      sourcePillar: 'content',
      targetPillar: 'insights',
      data: { files: ['test.csv'] }
    });

    expect(result.success).toBe(true);
    expect(result.data.targetPillar).toBe('insights');
  });
});
```

## 🎯 Best Practices

### 1. Service Design

- **Single Responsibility**: Each service should have one clear purpose
- **Interface Segregation**: Provide focused interfaces for different use cases
- **Dependency Injection**: Use dependency injection for service dependencies
- **Error Handling**: Implement comprehensive error handling

### 2. Performance

- **Connection Pooling**: Reuse connections when possible
- **Request Batching**: Batch multiple requests when appropriate
- **Caching**: Implement caching for frequently accessed data
- **Lazy Loading**: Load services on demand

### 3. Security

- **Authentication**: Always use authentication for sensitive operations
- **Input Validation**: Validate all input data
- **HTTPS/WSS**: Use secure protocols in production
- **Token Management**: Handle authentication tokens securely

### 4. Reliability

- **Retry Logic**: Implement retry logic for transient failures
- **Circuit Breaker**: Use circuit breaker pattern for external services
- **Health Checks**: Monitor service health
- **Graceful Degradation**: Handle service failures gracefully

### 5. Monitoring

- **Logging**: Log all service interactions
- **Metrics**: Track service performance metrics
- **Alerting**: Set up alerts for service failures
- **Tracing**: Implement distributed tracing

### 6. Testing

- **Unit Tests**: Test individual service methods
- **Integration Tests**: Test service interactions
- **Mocking**: Mock external dependencies
- **Error Scenarios**: Test error handling scenarios

## 🔗 Related Documentation

- [API Documentation](./API.md) - Service interfaces and patterns
- [State Management Documentation](./state-management.md) - State management patterns
- [Configuration Guide](./configuration.md) - Environment configuration
- [Testing Guide](./testing.md) - Testing strategies

---

**Last Updated**: [Automated Update]
**Version**: 1.0.0 