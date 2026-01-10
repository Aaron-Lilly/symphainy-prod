# Session Management Migration Guide

## Overview

This guide helps you migrate from the old session management patterns to the new unified session management system. The new system provides a single source of truth for all session-related state with automatic synchronization and error handling.

## Migration Summary

### Before (Old Patterns)
```typescript
// Multiple session patterns scattered across components
import { useGlobalSession } from '@/shared/agui/GlobalSessionProvider';
import { useSessionElements } from '@/shared/hooks/useSessionElements';
import { mainChatbotOpenAtom } from '@/shared/atoms/chatbot-atoms';

// Different state management approaches
const { guideSessionToken } = useGlobalSession();
const { sessionState, sessionElements } = useSessionElements(sessionToken);
const [mainChatbotOpen] = useAtom(mainChatbotOpenAtom);
```

### After (New Unified System)
```typescript
// Single unified session management
import { useSessionContext } from '@/shared/components/SessionProvider';

// All session state in one place
const { 
  sessionState, 
  sessionElements, 
  setChatbotOpen, 
  refreshSession 
} = useSessionContext();
```

## Step-by-Step Migration

### Step 1: Update Application Root

#### Before
```typescript
// app/layout.tsx or similar
import { GlobalSessionProvider } from '@/shared/agui/GlobalSessionProvider';

export default function RootLayout({ children }) {
  return (
    <GlobalSessionProvider>
      {children}
    </GlobalSessionProvider>
  );
}
```

#### After
```typescript
// app/layout.tsx
import { SessionProvider } from '@/shared/components/SessionProvider';

export default function RootLayout({ children }) {
  return (
    <SessionProvider 
      autoInitialize={true}
      sessionTimeoutMinutes={30}
    >
      {children}
    </SessionProvider>
  );
}
```

### Step 2: Update Component Session Usage

#### Before
```typescript
// components/SomeComponent.tsx
import { useGlobalSession } from '@/shared/agui/GlobalSessionProvider';
import { useSessionElements } from '@/shared/hooks/useSessionElements';

export function SomeComponent() {
  const { guideSessionToken } = useGlobalSession();
  const { sessionState, sessionElements, refreshSession } = useSessionElements(guideSessionToken);
  
  // Component logic...
}
```

#### After
```typescript
// components/SomeComponent.tsx
import { useSessionContext } from '@/shared/components/SessionProvider';

export function SomeComponent() {
  const { sessionState, sessionElements, refreshSession } = useSessionContext();
  
  // Component logic...
}
```

### Step 3: Update Chatbot State Management

#### Before
```typescript
// components/chatbot/PrimaryChatbot.tsx
import { useAtom } from 'jotai';
import { mainChatbotOpenAtom, chatbotAgentInfoAtom } from '@/shared/atoms/chatbot-atoms';

export function PrimaryChatbot() {
  const [mainChatbotOpen, setMainChatbotOpen] = useAtom(mainChatbotOpenAtom);
  const [chatbotAgentInfo, setChatbotAgentInfo] = useAtom(chatbotAgentInfoAtom);
  
  // Component logic...
}
```

#### After
```typescript
// components/chatbot/PrimaryChatbot.tsx
import { useSessionContext } from '@/shared/components/SessionProvider';

export function PrimaryChatbot() {
  const { 
    sessionState, 
    setChatbotOpen, 
    setChatbotAgentInfo 
  } = useSessionContext();
  
  const { chatbotOpen, chatbotAgentInfo } = sessionState;
  
  // Component logic...
}
```

### Step 4: Update Session Operations

#### Before
```typescript
// Multiple different session operations
const { refreshSession } = useSessionElements(sessionToken);
const { clearSession } = useSessionElements(sessionToken);

// Manual session state updates
setMainChatbotOpen(false);
setChatbotAgentInfo({ title: "New Agent", agent: "agent1" });
```

#### After
```typescript
// Unified session operations
const { 
  refreshSession, 
  clearSession, 
  setChatbotOpen, 
  setChatbotAgentInfo 
} = useSessionContext();

// Automatic state synchronization
setChatbotOpen(false);
setChatbotAgentInfo({ title: "New Agent", agent: "agent1" });
```

## Migration Checklist

### Phase 1: Foundation Setup
- [ ] Install new session management system
- [ ] Update application root with SessionProvider
- [ ] Remove old GlobalSessionProvider
- [ ] Test basic session initialization

### Phase 2: Component Migration
- [ ] Update components using `useGlobalSession`
- [ ] Update components using `useSessionElements`
- [ ] Update components using chatbot atoms
- [ ] Test session state synchronization

### Phase 3: Advanced Features
- [ ] Implement session expiration handling
- [ ] Add session activity tracking
- [ ] Configure automatic session refresh
- [ ] Test error handling and recovery

### Phase 4: Cleanup
- [ ] Remove old session hooks and providers
- [ ] Remove old chatbot atoms
- [ ] Update TypeScript types
- [ ] Update documentation

## Common Migration Patterns

### Pattern 1: Session Token Access

#### Before
```typescript
const { guideSessionToken } = useGlobalSession();
```

#### After
```typescript
const { sessionState } = useSessionContext();
const sessionToken = sessionState.globalToken;
```

### Pattern 2: Session State Access

#### Before
```typescript
const { sessionState } = useSessionElements(sessionToken);
const { has_sop, has_workflow } = sessionState;
```

#### After
```typescript
const { sessionState } = useSessionContext();
const { has_sop, has_workflow } = sessionState;
```

### Pattern 3: Session Operations

#### Before
```typescript
const { refreshSession, clearSession } = useSessionElements(sessionToken);
```

#### After
```typescript
const { refreshSession, clearSession } = useSessionContext();
```

### Pattern 4: Chatbot State

#### Before
```typescript
const [mainChatbotOpen, setMainChatbotOpen] = useAtom(mainChatbotOpenAtom);
const [chatbotAgentInfo, setChatbotAgentInfo] = useAtom(chatbotAgentInfoAtom);
```

#### After
```typescript
const { sessionState, setChatbotOpen, setChatbotAgentInfo } = useSessionContext();
const { chatbotOpen, chatbotAgentInfo } = sessionState;
```

## Error Handling Migration

### Before
```typescript
const { sessionState, error } = useSessionElements(sessionToken);

if (error) {
  console.error('Session error:', error);
  // Manual error handling
}
```

### After
```typescript
const { sessionState } = useSessionContext();

if (sessionState.error) {
  // Automatic error handling with SessionProvider
  // Error states are handled automatically
}
```

## Testing Migration

### Before
```typescript
// Test individual session hooks
import { renderHook } from '@testing-library/react';
import { useSessionElements } from '@/shared/hooks/useSessionElements';

test('session elements hook', () => {
  const { result } = renderHook(() => useSessionElements('test-token'));
  // Test logic...
});
```

### After
```typescript
// Test unified session context
import { renderHook } from '@testing-library/react';
import { SessionProvider, useSessionContext } from '@/shared/components/SessionProvider';

test('unified session context', () => {
  const { result } = renderHook(() => useSessionContext(), {
    wrapper: ({ children }) => (
      <SessionProvider initialToken="test-token">
        {children}
      </SessionProvider>
    ),
  });
  // Test logic...
});
```

## Performance Considerations

### Automatic Optimizations
- **State Synchronization**: Automatic synchronization prevents race conditions
- **Memory Management**: Automatic cleanup prevents memory leaks
- **Activity Tracking**: Automatic activity tracking for session expiration
- **Error Recovery**: Automatic error recovery and retry logic

### Manual Optimizations
- **Component Memoization**: Use React.memo for components that depend on session state
- **Selective Updates**: Use specific session hooks for targeted updates
- **Lazy Loading**: Session initialization can be lazy-loaded for better performance

## Troubleshooting

### Common Issues

#### Issue 1: Session not initializing
**Cause**: Missing SessionProvider or incorrect token
**Solution**: Ensure SessionProvider wraps your app and token is valid

#### Issue 2: State not synchronizing
**Cause**: Multiple session instances or race conditions
**Solution**: Use only the unified session context, remove old patterns

#### Issue 3: Session expiring unexpectedly
**Cause**: Activity tracking not working or timeout too short
**Solution**: Check activity tracking setup and adjust timeout

#### Issue 4: Performance issues
**Cause**: Too many re-renders from session updates
**Solution**: Use specific session hooks and component memoization

### Debug Tools

```typescript
// Development only - shows session debug info
import { SessionDebug } from '@/shared/components/SessionProvider';

function App() {
  return (
    <SessionProvider>
      <YourApp />
      <SessionDebug /> {/* Shows in development only */}
    </SessionProvider>
  );
}
```

## Rollback Plan

If issues arise during migration:

1. **Keep old session patterns** alongside new system
2. **Gradually migrate** components one by one
3. **Test thoroughly** after each migration
4. **Monitor performance** and error rates
5. **Rollback individual components** if needed

## Support

For migration support:
1. Check this guide for common patterns
2. Review the session management documentation
3. Test with the provided examples
4. Use the debug tools for troubleshooting 