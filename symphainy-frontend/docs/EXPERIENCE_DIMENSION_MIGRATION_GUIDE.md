# Experience Dimension API Migration Guide

## 🎯 **Overview**

This guide helps you migrate from the old API integration patterns to the new **Experience Dimension API** that uses the extracted working patterns from `business_orchestrator_old`.

## 🔄 **What's Changed**

### **Before (Old Pattern):**
```typescript
// Old direct API calls
import { startInsightsSession } from '../lib/api/insights';
import { uploadFile } from '../lib/api/content';

const response = await startInsightsSession(sessionData);
const fileResponse = await uploadFile(file);
```

### **After (New Pattern):**
```typescript
// New Experience Dimension API
import { useExperienceDimensionAPI } from '../lib/hooks/useExperienceDimensionAPI';

const { startInsightsSession, uploadFile } = useExperienceDimensionAPI();
const response = await startInsightsSession(sessionData);
const fileResponse = await uploadFile(file);
```

## 🚀 **Migration Steps**

### **Step 1: Update Imports**

**Replace:**
```typescript
import { startInsightsSession } from '../lib/api/insights';
import { uploadFile } from '../lib/api/content';
import { convertSOPToWorkflow } from '../lib/api/operations';
```

**With:**
```typescript
import { useExperienceDimensionAPI } from '../lib/hooks/useExperienceDimensionAPI';
```

### **Step 2: Use the Hook**

**Replace:**
```typescript
function MyComponent() {
  const handleAnalysis = async () => {
    const response = await startInsightsSession(sessionData);
    // Handle response
  };
}
```

**With:**
```typescript
function MyComponent() {
  const { startInsightsSession, loading, error } = useExperienceDimensionAPI();
  
  const handleAnalysis = async () => {
    const response = await startInsightsSession(sessionData);
    // Handle response
  };
}
```

### **Step 3: Add Context Provider**

**Add to your app root:**
```typescript
import { ExperienceDimensionProvider } from '../lib/contexts/ExperienceDimensionContext';

function App() {
  return (
    <ExperienceDimensionProvider>
      {/* Your app components */}
    </ExperienceDimensionProvider>
  );
}
```

## 📋 **API Method Mapping**

### **Insights Pillar**

| Old Method | New Method | Notes |
|------------|------------|-------|
| `startInsightsSession()` | `startInsightsSession()` | Same interface |
| `analyzeDataset()` | `analyzeDataset()` | Same interface |
| `createVisualization()` | `createVisualization()` | Same interface |
| `sendChatMessage()` | `sendChatMessage()` | Same interface |
| `getConversationHistory()` | `getConversationHistory()` | Same interface |

### **Content Pillar**

| Old Method | New Method | Notes |
|------------|------------|-------|
| `uploadFile()` | `uploadFile()` | Same interface |
| `parseFile()` | `parseFile()` | Same interface |
| `analyzeFile()` | `analyzeFile()` | Same interface |
| `getFilePreview()` | `getFilePreview()` | Same interface |
| `getFileMetadata()` | `getFileMetadata()` | Same interface |

### **Operations Pillar**

| Old Method | New Method | Notes |
|------------|------------|-------|
| `convertSOPToWorkflow()` | `convertSOPToWorkflow()` | Same interface |
| `convertWorkflowToSOP()` | `convertWorkflowToSOP()` | Same interface |
| `createCoexistenceBlueprint()` | `createCoexistenceBlueprint()` | Same interface |
| `sendOperationsChatMessage()` | `sendOperationsChatMessage()` | Same interface |

### **Business Outcomes Pillar**

| Old Method | New Method | Notes |
|------------|------------|-------|
| `generateStrategicPlan()` | `generateStrategicPlan()` | Same interface |
| `performROIAnalysis()` | `performROIAnalysis()` | Same interface |
| `getBusinessMetrics()` | `getBusinessMetrics()` | Same interface |

## 🎭 **New Features**

### **1. Unified State Management**
```typescript
const { loading, error, data, lastResponse } = useExperienceDimensionAPI();
```

### **2. Connection Status**
```typescript
const { isConnected, connectionError } = useConnectionStatus();
```

### **3. User Context Management**
```typescript
const { setUserContext, userContext } = useExperienceDimensionContext();
```

### **4. Error Handling**
```typescript
const { clearError } = useExperienceDimensionAPI();

// Clear errors
clearError();
```

## 🔧 **Component Examples**

### **Simple Component Migration**

**Before:**
```typescript
import { startInsightsSession } from '../lib/api/insights';

function InsightsComponent() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const handleStartSession = async () => {
    setLoading(true);
    try {
      const response = await startInsightsSession(sessionData);
      // Handle success
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div>
      {loading && <p>Loading...</p>}
      {error && <p>Error: {error}</p>}
      <button onClick={handleStartSession}>Start Session</button>
    </div>
  );
}
```

**After:**
```typescript
import { useExperienceDimensionAPI } from '../lib/hooks/useExperienceDimensionAPI';

function InsightsComponent() {
  const { startInsightsSession, loading, error, clearError } = useExperienceDimensionAPI();
  
  const handleStartSession = async () => {
    try {
      const response = await startInsightsSession(sessionData);
      // Handle success
    } catch (err) {
      // Error is automatically handled by the hook
    }
  };
  
  return (
    <div>
      {loading && <p>Loading...</p>}
      {error && <p>Error: {error}</p>}
      <button onClick={handleStartSession}>Start Session</button>
    </div>
  );
}
```

### **Complex Component with Multiple APIs**

**Before:**
```typescript
import { startInsightsSession } from '../lib/api/insights';
import { uploadFile } from '../lib/api/content';
import { convertSOPToWorkflow } from '../lib/api/operations';

function ComplexComponent() {
  const [insightsLoading, setInsightsLoading] = useState(false);
  const [contentLoading, setContentLoading] = useState(false);
  const [operationsLoading, setOperationsLoading] = useState(false);
  
  // Multiple loading states and error handling...
}
```

**After:**
```typescript
import { useExperienceDimensionAPI } from '../lib/hooks/useExperienceDimensionAPI';

function ComplexComponent() {
  const { 
    startInsightsSession, 
    uploadFile, 
    convertSOPToWorkflow,
    loading, 
    error, 
    clearError 
  } = useExperienceDimensionAPI();
  
  // Single loading state and error handling for all APIs
}
```

## 🧪 **Testing**

### **Test Connection**
```typescript
const { testConnection } = useExperienceDimensionAPI();

const handleTestConnection = async () => {
  const result = await testConnection();
  console.log('Connection test result:', result);
};
```

### **Run Comprehensive Tests**
```typescript
import { ExperienceDimensionExample } from '../components/examples/ExperienceDimensionExample';

function TestPage() {
  return <ExperienceDimensionExample />;
}
```

## 🚨 **Breaking Changes**

### **1. Import Changes**
- All old API imports need to be replaced with the new hook
- Context provider must be added to app root

### **2. State Management**
- Loading and error states are now managed by the hook
- No need to manually manage loading states

### **3. Error Handling**
- Errors are automatically captured by the hook
- Use `clearError()` to clear errors

## ✅ **Migration Checklist**

- [ ] Update all API imports to use `useExperienceDimensionAPI`
- [ ] Add `ExperienceDimensionProvider` to app root
- [ ] Remove manual loading state management
- [ ] Update error handling to use hook's error state
- [ ] Test all API calls with new integration
- [ ] Verify connection status and user context
- [ ] Run comprehensive tests

## 🎉 **Benefits**

1. **Unified API**: Single hook for all API calls
2. **Automatic State Management**: Loading and error states handled automatically
3. **Real Backend Integration**: Uses extracted working patterns from business_orchestrator_old
4. **Better Error Handling**: Centralized error management
5. **Connection Monitoring**: Real-time connection status
6. **User Context**: Automatic user context management
7. **Type Safety**: Full TypeScript support

## 📞 **Support**

If you encounter issues during migration:

1. Check the example component: `components/examples/ExperienceDimensionExample.tsx`
2. Verify the context provider is properly set up
3. Test connection with `testConnection()`
4. Check browser console for detailed error messages

The new Experience Dimension API provides a much cleaner and more maintainable way to interact with the backend while preserving all existing functionality.


