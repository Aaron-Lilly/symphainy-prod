# State Management Documentation

This document provides comprehensive documentation for state management patterns, Jotai atoms, session management, and state architecture used in the Symphainy frontend application.

## 📋 Table of Contents

- [Overview](#overview)
- [Jotai Atoms](#jotai-atoms)
- [Session Management](#session-management)
- [State Architecture](#state-architecture)
- [Cross-Pillar State](#cross-pillar-state)
- [State Persistence](#state-persistence)
- [Performance Optimization](#performance-optimization)
- [Testing State](#testing-state)
- [Best Practices](#best-practices)

## 🎯 Overview

The Symphainy frontend uses a comprehensive state management architecture built on:

- **Jotai** - Atomic state management for reactive UI updates
- **Session Management** - Global session state with persistence
- **Cross-Pillar Communication** - State sharing between application pillars
- **Smart City Integration** - State orchestration through Smart City components
- **State Persistence** - Local storage and backend state synchronization

## ⚛️ Jotai Atoms

### Basic Atom Patterns

Jotai atoms provide a simple and efficient way to manage state with automatic reactivity.

#### Simple Atoms

```typescript
import { atom } from 'jotai';

// Basic atom
const countAtom = atom(0);

// Object atom
const userAtom = atom({
  id: '',
  name: '',
  email: ''
});

// Array atom
const itemsAtom = atom([]);
```

#### Derived Atoms

```typescript
import { atom } from 'jotai';

// Read-only derived atom
const doubleCountAtom = atom((get) => {
  return get(countAtom) * 2;
});

// Writable derived atom
const incrementAtom = atom(
  (get) => get(countAtom),
  (get, set, increment: number) => {
    set(countAtom, get(countAtom) + increment);
  }
);
```

### Chatbot State Atoms

The chatbot system uses a sophisticated atom pattern for managing UI state and interactions.

```typescript
import { atom } from 'jotai';

// Main chatbot state - Single source of truth
export const mainChatbotOpenAtom = atom(true);

// Agent information
export const chatbotAgentInfoAtom = atom({
  title: "",
  agent: "",
  file_url: "",
  additional_info: "",
});

// Auto-derived atoms for UI state
export const shouldShowSecondaryChatbotAtom = atom((get) => {
  return !get(mainChatbotOpenAtom);
});

export const primaryChatbotHeightAtom = atom((get) => {
  const mainOpen = get(mainChatbotOpenAtom);
  return mainOpen ? 'h-[87vh]' : 'h-[30vh]';
});

export const secondaryChatbotPositionAtom = atom((get) => {
  const mainOpen = get(mainChatbotOpenAtom);
  return mainOpen 
    ? 'translate-x-full opacity-0' 
    : 'translate-x-0 opacity-100';
});
```

#### Usage in Components

```typescript
import { useAtom } from 'jotai';
import { mainChatbotOpenAtom, primaryChatbotHeightAtom } from '@/shared/atoms/chatbot-atoms';

function ChatbotComponent() {
  const [isOpen, setIsOpen] = useAtom(mainChatbotOpenAtom);
  const [height] = useAtom(primaryChatbotHeightAtom);

  return (
    <div className={height}>
      <button onClick={() => setIsOpen(!isOpen)}>
        {isOpen ? 'Close' : 'Open'} Chatbot
      </button>
    </div>
  );
}
```

### Analysis Results Atoms

Shared atoms for cross-component communication of analysis results.

```typescript
// Analysis results atoms
export const businessAnalysisResultAtom = atom<any>(null);
export const visualizationResultAtom = atom<any>(null);
export const anomalyDetectionResultAtom = atom<any>(null);
export const edaAnalysisResultAtom = atom<any>(null);

// Usage in components
function AnalysisComponent() {
  const [analysisResult, setAnalysisResult] = useAtom(businessAnalysisResultAtom);

  const handleAnalysis = async () => {
    const result = await performAnalysis();
    setAnalysisResult(result);
  };

  return (
    <div>
      {analysisResult && <AnalysisDisplay data={analysisResult} />}
      <button onClick={handleAnalysis}>Run Analysis</button>
    </div>
  );
}
```

## 🔐 Session Management

### Global Session Provider

The `GlobalSessionProvider` manages application-wide session state with persistence.

```typescript
import { GlobalSessionProvider, useGlobalSession } from '@/shared/session';

// Wrap your app
function App() {
  return (
    <GlobalSessionProvider>
      <YourApp />
    </GlobalSessionProvider>
  );
}

// Use in components
function MyComponent() {
  const {
    guideSessionToken,
    setGuideSessionToken,
    getPillarState,
    setPillarState,
    sessionStatus,
    isSessionValid
  } = useGlobalSession();

  // Access session data
  const pillarState = getPillarState('insights');
  
  // Update session data
  const updateState = () => {
    setPillarState('insights', { currentAnalysis: 'data_quality' });
  };

  return (
    <div>
      <p>Session Status: {sessionStatus}</p>
      <p>Valid: {isSessionValid ? 'Yes' : 'No'}</p>
      <button onClick={updateState}>Update State</button>
    </div>
  );
}
```

### Session Manager

The `SessionManager` class provides the core session management functionality.

```typescript
import { SessionManager } from '@/shared/session/core';

const sessionManager = new SessionManager();

// Start a new session
const token = await sessionManager.startNewSession();

// Set session token
sessionManager.setGuideSessionToken(token);

// Manage pillar states
sessionManager.setPillarState('content', { files: ['file1.csv'] });
sessionManager.setPillarState('insights', { analysis: 'data_quality' });

// Get pillar state
const contentState = sessionManager.getPillarState('content');

// Subscribe to changes
const unsubscribe = sessionManager.subscribe((state) => {
  console.log('Session state changed:', state);
});

// Cleanup
unsubscribe();
```

### Session Hooks

Custom hooks for session management.

```typescript
import { useSessionStatus, useSessionPersistence } from '@/shared/session/hooks';

function SessionAwareComponent() {
  const { status, isSessionValid, lastActivity } = useSessionStatus();
  const { persistState, restoreState } = useSessionPersistence();

  // Persist state to localStorage
  const saveState = () => {
    persistState({
      pillar: 'insights',
      data: { currentAnalysis: 'data_quality' }
    });
  };

  // Restore state from localStorage
  const loadState = () => {
    const state = restoreState('insights');
    console.log('Restored state:', state);
  };

  return (
    <div>
      <p>Status: {status}</p>
      <p>Valid: {isSessionValid ? 'Yes' : 'No'}</p>
      <p>Last Activity: {lastActivity}</p>
      <button onClick={saveState}>Save State</button>
      <button onClick={loadState}>Load State</button>
    </div>
  );
}
```

## 🏗️ State Architecture

### State Hierarchy

The application follows a hierarchical state architecture:

```
Global Session State (GlobalSessionProvider)
├── User Authentication
├── Session Token
└── Pillar States
    ├── Content Pillar State
    ├── Insights Pillar State
    ├── Operations Pillar State
    └── Experience Pillar State

Component State (Jotai Atoms)
├── UI State (chatbot, forms, etc.)
├── Data State (analysis results, file data)
└── Derived State (computed values)
```

### State Flow Patterns

#### Unidirectional Data Flow

```typescript
// 1. User Action
const handleUserAction = () => {
  // 2. Update Atom
  setCountAtom(count + 1);
  // 3. Trigger Re-render
  // 4. UI Updates
};

// Component automatically re-renders when atom changes
function Counter() {
  const [count, setCount] = useAtom(countAtom);
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
```

#### State Synchronization

```typescript
// Synchronize state between components
const sharedDataAtom = atom(null);

// Component A
function ComponentA() {
  const [data, setData] = useAtom(sharedDataAtom);
  
  const updateData = () => {
    setData({ timestamp: Date.now() });
  };

  return <button onClick={updateData}>Update Data</button>;
}

// Component B (automatically updates when Component A changes data)
function ComponentB() {
  const [data] = useAtom(sharedDataAtom);
  
  return <div>Last Update: {data?.timestamp}</div>;
}
```

## 🔗 Cross-Pillar State

### Cross-Pillar Communication

The application uses cross-pillar services for state sharing between pillars.

```typescript
import { CrossPillarService } from '@/shared/services/cross-pillar';

// Share state between pillars
const shareState = async () => {
  await CrossPillarService.shareData({
    sourcePillar: 'content',
    targetPillar: 'insights',
    data: { files: ['data.csv'] },
    metadata: { type: 'file_list' }
  });
};

// Synchronize state across pillars
const syncState = async () => {
  await CrossPillarService.syncState({
    pillar: 'insights',
    state: { currentAnalysis: 'data_quality' },
    priority: 'high'
  });
};
```

### Pillar-Specific State Atoms

```typescript
// Content pillar state
export const contentFilesAtom = atom([]);
export const contentUploadStatusAtom = atom('idle');

// Insights pillar state
export const insightsAnalysisAtom = atom(null);
export const insightsVisualizationAtom = atom(null);

// Operations pillar state
export const operationsWorkflowAtom = atom(null);
export const operationsBlueprintAtom = atom(null);

// Experience pillar state
export const experienceTimelineAtom = atom([]);
export const experienceRoadmapAtom = atom(null);
```

## 💾 State Persistence

### Local Storage Persistence

```typescript
import { atomWithStorage } from 'jotai/utils';

// Atom with localStorage persistence
const persistentUserAtom = atomWithStorage('user', {
  id: '',
  name: '',
  email: ''
});

// Atom with sessionStorage persistence
const sessionDataAtom = atomWithStorage('sessionData', null, sessionStorage);
```

### Backend State Synchronization

```typescript
import { atom } from 'jotai';
import { atomWithQuery } from 'jotai/query';

// Atom that syncs with backend
const backendDataAtom = atomWithQuery(
  (get) => ({
    queryKey: ['backendData', get(userIdAtom)],
    queryFn: () => fetchBackendData(get(userIdAtom))
  })
);

// Atom that updates backend on change
const syncableDataAtom = atom(
  (get) => get(backendDataAtom),
  async (get, set, newValue) => {
    set(backendDataAtom, newValue);
    await updateBackendData(newValue);
  }
);
```

### State Migration

```typescript
// Handle state schema changes
const migrateState = (oldState: any) => {
  if (oldState.version === 1) {
    // Migrate from v1 to v2
    return {
      ...oldState,
      version: 2,
      newField: 'default_value'
    };
  }
  return oldState;
};

const versionedStateAtom = atomWithStorage('appState', null, undefined, {
  serialize: (value) => JSON.stringify({ ...value, version: 2 }),
  deserialize: (str) => {
    const parsed = JSON.parse(str);
    return migrateState(parsed);
  }
});
```

## ⚡ Performance Optimization

### Atom Optimization

```typescript
// Use atomFamily for dynamic atoms
import { atomFamily } from 'jotai/utils';

const itemAtom = atomFamily((id: string) => atom(null));

// Use selectAtom for derived state optimization
import { selectAtom } from 'jotai/utils';

const expensiveComputationAtom = selectAtom(
  largeDataAtom,
  (data) => expensiveComputation(data)
);

// Use atomWithReset for resettable state
import { atomWithReset } from 'jotai/utils';

const resettableStateAtom = atomWithReset({
  count: 0,
  data: null
});
```

### Component Optimization

```typescript
import { useAtomValue, useSetAtom } from 'jotai';

// Optimize read-only components
function ReadOnlyComponent() {
  const value = useAtomValue(expensiveAtom);
  return <div>{value}</div>;
}

// Optimize write-only components
function WriteOnlyComponent() {
  const setValue = useSetAtom(expensiveAtom);
  return <button onClick={() => setValue(newValue)}>Update</button>;
}

// Use React.memo with atoms
const OptimizedComponent = React.memo(() => {
  const [value] = useAtom(expensiveAtom);
  return <div>{value}</div>;
});
```

### State Batching

```typescript
import { useAtomCallback } from 'jotai/utils';

// Batch multiple state updates
const batchUpdateAtom = useAtomCallback((get, set) => {
  set(atom1, newValue1);
  set(atom2, newValue2);
  set(atom3, newValue3);
});

// Usage
<button onClick={batchUpdateAtom}>Batch Update</button>
```

## 🧪 Testing State

### Testing Atoms

```typescript
import { renderHook } from '@testing-library/react';
import { Provider } from 'jotai';
import { countAtom, incrementAtom } from '@/shared/atoms';

describe('Count Atom', () => {
  it('should increment count', () => {
    const { result } = renderHook(() => useAtom(incrementAtom), {
      wrapper: Provider
    });

    const [count, increment] = result.current;
    expect(count).toBe(0);

    act(() => {
      increment(5);
    });

    expect(result.current[0]).toBe(5);
  });
});
```

### Testing Session State

```typescript
import { renderHook } from '@testing-library/react';
import { GlobalSessionProvider, useGlobalSession } from '@/shared/session';

describe('Global Session', () => {
  it('should manage session state', () => {
    const { result } = renderHook(() => useGlobalSession(), {
      wrapper: GlobalSessionProvider
    });

    const { setPillarState, getPillarState } = result.current;

    act(() => {
      setPillarState('insights', { analysis: 'data_quality' });
    });

    const state = getPillarState('insights');
    expect(state.analysis).toBe('data_quality');
  });
});
```

### Mocking State

```typescript
// Mock atoms for testing
const mockCountAtom = atom(42);
const mockUserAtom = atom({ name: 'Test User' });

// Provide mock atoms to components
function TestWrapper({ children }) {
  return (
    <Provider initialValues={[
      [countAtom, mockCountAtom],
      [userAtom, mockUserAtom]
    ]}>
      {children}
    </Provider>
  );
}
```

## 🎯 Best Practices

### 1. Atom Design

- **Single Responsibility**: Each atom should manage one piece of state
- **Derived Atoms**: Use derived atoms for computed values
- **Naming**: Use descriptive names for atoms
- **Types**: Always define TypeScript types for atom values

### 2. State Organization

- **Hierarchy**: Organize atoms in a logical hierarchy
- **Grouping**: Group related atoms together
- **Separation**: Separate UI state from business logic state
- **Global vs Local**: Use global atoms sparingly, prefer local state when possible

### 3. Performance

- **Memoization**: Use `React.memo` with atom-based components
- **Selective Updates**: Use `selectAtom` for expensive computations
- **Batching**: Batch multiple state updates when possible
- **Cleanup**: Clean up subscriptions and timers

### 4. Session Management

- **Persistence**: Use appropriate persistence strategies
- **Validation**: Validate session state on restoration
- **Migration**: Handle state schema migrations gracefully
- **Security**: Don't store sensitive data in localStorage

### 5. Testing

- **Isolation**: Test atoms in isolation
- **Mocking**: Mock external dependencies
- **Coverage**: Test all state transitions
- **Integration**: Test state integration between components

### 6. Error Handling

- **Validation**: Validate state updates
- **Fallbacks**: Provide fallback values for failed state loads
- **Recovery**: Implement state recovery mechanisms
- **Logging**: Log state errors for debugging

## 🔗 Related Documentation

- [API Documentation](./API.md) - Service layer interfaces
- [Component Library Documentation](./components.md) - Component patterns
- [Service Layer Documentation](./services.md) - Service architecture
- [Testing Guide](./testing.md) - Testing strategies

---

**Last Updated**: [Automated Update]
**Version**: 1.0.0 