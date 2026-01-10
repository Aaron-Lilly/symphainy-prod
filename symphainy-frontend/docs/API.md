# API Documentation

This document provides comprehensive documentation for all frontend API services, interfaces, and patterns used in the Symphainy frontend application.

## 📋 Table of Contents

- [Overview](#overview)
- [Core Services](#core-services)
- [Cross-Pillar Services](#cross-pillar-services)
- [WebSocket Services](#websocket-services)
- [Error Handling](#error-handling)
- [Authentication](#authentication)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [Best Practices](#best-practices)

## 🎯 Overview

The Symphainy frontend uses a comprehensive service layer architecture that provides:

- **Standardized API requests** with error handling and retry logic
- **WebSocket connections** with automatic reconnection and message queuing
- **Cross-pillar communication** for data sharing between application pillars
- **Session integration** for authentication and state management
- **Configuration management** for environment-specific settings

## 🏗️ Core Services

### APIService

The `APIService` class provides standardized HTTP requests with built-in error handling, retry logic, and session integration.

#### Basic Usage

```typescript
import { APIService, apiService } from '@/shared/services';

// Using the singleton instance
const response = await apiService.get('/api/data');

// Using the class directly
const api = new APIService();
const response = await api.get('/api/data');
```

#### Request Methods

```typescript
// GET request
const data = await apiService.get('/api/users');

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

#### Request Options

```typescript
interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  headers?: Record<string, string>;
  body?: any;
  timeout?: number;
  retries?: number;
  retryDelay?: number;
  requireAuth?: boolean;
}

// Example with custom options
const response = await apiService.get('/api/data', {
  headers: { 'Custom-Header': 'value' },
  timeout: 5000,
  retries: 3,
  requireAuth: true
});
```

#### Response Format

```typescript
interface APIResponse<T = any> {
  data: T;
  status: number;
  statusText: string;
  headers: Record<string, string>;
  success: boolean;
  error?: string;
  retryCount?: number;
}
```

### WebSocketService

The `WebSocketService` class manages WebSocket connections with automatic reconnection, message queuing, and event handling.

#### Basic Usage

```typescript
import { WebSocketService, webSocketService } from '@/shared/services';

// Connect to WebSocket endpoint
const connectionId = await webSocketService.connect('/ws/chat');

// Send message
await webSocketService.send(connectionId, {
  type: 'message',
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
  requireAuth?: boolean;
  autoReconnect?: boolean;
  heartbeat?: boolean;
}

// Example with custom options
const connectionId = await webSocketService.connect('/ws/chat', {
  requireAuth: true,
  autoReconnect: true,
  heartbeat: true
});
```

#### Message Format

```typescript
interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: number;
  id?: string;
}
```

## 🔗 Cross-Pillar Services

The cross-pillar services enable communication and data sharing between the four main application pillars: Content, Insights, Operations, and Experience.

### Core Cross-Pillar Functions

```typescript
import { CrossPillarService } from '@/shared/services/cross-pillar';

// Share data between pillars
const result = await CrossPillarService.shareData({
  sourcePillar: 'content',
  targetPillar: 'insights',
  data: { files: ['file1.csv', 'file2.csv'] },
  metadata: { type: 'file_list' }
});

// Send communication between pillars
await CrossPillarService.sendCommunication({
  fromPillar: 'operations',
  toPillar: 'experience',
  messageType: 'workflow_complete',
  data: { workflowId: 'wf-123', status: 'completed' }
});

// Synchronize state across pillars
await CrossPillarService.syncState({
  pillar: 'insights',
  state: { currentAnalysis: 'data_quality' },
  priority: 'high'
});
```

### Data Sharing

```typescript
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

### Communication Patterns

```typescript
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

### Smart City Integration

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

## 🔧 Error Handling

### API Error Format

```typescript
interface APIError {
  message: string;
  status?: number;
  code?: string;
  details?: any;
  retryable: boolean;
}
```

### Error Handling Patterns

```typescript
// Basic error handling
try {
  const response = await apiService.get('/api/data');
  // Handle success
} catch (error) {
  if (error.retryable) {
    // Implement retry logic
    console.log('Retryable error:', error.message);
  } else {
    // Handle non-retryable error
    console.error('Non-retryable error:', error.message);
  }
}

// WebSocket error handling
webSocketService.subscribe(connectionId, 'error', (error) => {
  console.error('WebSocket error:', error);
  if (error.retryable) {
    // Connection will automatically retry
  } else {
    // Handle non-retryable error
  }
});
```

### Retry Logic

The API service includes built-in retry logic for transient failures:

```typescript
// Configure retry options
const response = await apiService.get('/api/data', {
  retries: 3,
  retryDelay: 1000,
  timeout: 5000
});
```

Retryable status codes: `408`, `429`, `500`, `502`, `503`, `504`

## 🔐 Authentication

### Session Integration

All API requests automatically include authentication headers when `requireAuth` is true:

```typescript
// Automatic authentication (default)
const response = await apiService.get('/api/protected-data');

// Disable authentication for public endpoints
const publicData = await apiService.get('/api/public-data', {
  requireAuth: false
});
```

### WebSocket Authentication

```typescript
// Connect with authentication
const connectionId = await webSocketService.connect('/ws/chat', {
  requireAuth: true
});
```

## ⚙️ Configuration

### Environment Configuration

```typescript
// API Configuration
const apiConfig = {
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL,
  timeout: 10000,
  maxRetries: 3,
  retryDelay: 1000
};

// WebSocket Configuration
const wsConfig = {
  baseURL: process.env.NEXT_PUBLIC_WS_BASE_URL,
  reconnectAttempts: 5,
  reconnectDelay: 1000,
  heartbeatInterval: 30000
};
```

### Service Configuration

```typescript
import { ServiceLayerManager } from '@/shared/services';

// Initialize service layer
const serviceManager = new ServiceLayerManager();
serviceManager.initialize(sessionContext);

// Update configuration
serviceManager.updateConfig({
  api: { timeout: 15000 },
  websocket: { heartbeatInterval: 60000 }
});
```

## 📝 Usage Examples

### Complete API Integration Example

```typescript
import { apiService, CrossPillarService } from '@/shared/services';

class DataAnalysisService {
  async analyzeData(fileId: string) {
    try {
      // 1. Load data from content pillar
      const fileData = await apiService.get(`/api/content/files/${fileId}`);
      
      // 2. Share data with insights pillar
      await CrossPillarService.shareData({
        sourcePillar: 'content',
        targetPillar: 'insights',
        data: { fileId, content: fileData.data },
        metadata: { type: 'analysis_request' }
      });
      
      // 3. Trigger analysis
      const analysis = await apiService.post('/api/insights/analyze', {
        fileId,
        analysisType: 'comprehensive'
      });
      
      // 4. Share results with operations pillar
      await CrossPillarService.shareData({
        sourcePillar: 'insights',
        targetPillar: 'operations',
        data: { analysis: analysis.data },
        metadata: { type: 'analysis_results' }
      });
      
      return analysis.data;
    } catch (error) {
      console.error('Analysis failed:', error);
      throw error;
    }
  }
}
```

### WebSocket Integration Example

```typescript
import { webSocketService } from '@/shared/services';

class RealTimeChatService {
  private connectionId: string | null = null;
  private messageHandlers: Map<string, Function> = new Map();

  async initialize() {
    // Connect to chat WebSocket
    this.connectionId = await webSocketService.connect('/ws/chat', {
      requireAuth: true,
      autoReconnect: true,
      heartbeat: true
    });

    // Subscribe to message events
    webSocketService.subscribe(this.connectionId, 'message', (message) => {
      this.handleMessage(message);
    });

    // Subscribe to status events
    webSocketService.subscribe(this.connectionId, 'status', (message) => {
      console.log('Connection status:', message.data);
    });
  }

  async sendMessage(text: string) {
    if (!this.connectionId) {
      throw new Error('WebSocket not connected');
    }

    await webSocketService.send(this.connectionId, {
      type: 'chat_message',
      data: { text, timestamp: Date.now() },
      timestamp: Date.now()
    });
  }

  private handleMessage(message: any) {
    const handler = this.messageHandlers.get(message.type);
    if (handler) {
      handler(message.data);
    }
  }

  onMessage(type: string, handler: Function) {
    this.messageHandlers.set(type, handler);
  }

  disconnect() {
    if (this.connectionId) {
      webSocketService.disconnect(this.connectionId);
      this.connectionId = null;
    }
  }
}
```

## 🎯 Best Practices

### 1. Error Handling

- Always wrap API calls in try-catch blocks
- Check for retryable errors and implement appropriate retry logic
- Provide meaningful error messages to users
- Log errors for debugging purposes

### 2. Performance

- Use appropriate timeouts for API requests
- Implement request caching where appropriate
- Batch operations when possible
- Use WebSocket connections efficiently

### 3. Security

- Always use authentication for sensitive endpoints
- Validate input data before sending requests
- Handle sensitive data appropriately
- Use HTTPS in production

### 4. State Management

- Use cross-pillar services for state synchronization
- Implement proper cleanup for WebSocket connections
- Handle connection state changes appropriately
- Use session context for user-specific data

### 5. Testing

- Mock API services in unit tests
- Test error scenarios and retry logic
- Test WebSocket connection lifecycle
- Test cross-pillar communication patterns

## 🔗 Related Documentation

- [Service Layer Documentation](./services.md) - Detailed service architecture
- [State Management Documentation](./state-management.md) - State management patterns
- [Configuration Guide](./configuration.md) - Environment configuration
- [Troubleshooting Guide](./troubleshooting.md) - Common issues and solutions

---

**Last Updated**: [Automated Update]
**Version**: 1.0.0 