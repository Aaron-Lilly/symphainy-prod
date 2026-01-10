# Troubleshooting Guide

This document provides comprehensive troubleshooting guidance for common issues, debugging techniques, and solutions in the Symphainy frontend application.

## 📋 Table of Contents

- [Overview](#overview)
- [Common Issues](#common-issues)
- [Debugging Techniques](#debugging-techniques)
- [Performance Issues](#performance-issues)
- [Build Issues](#build-issues)
- [Runtime Issues](#runtime-issues)
- [Network Issues](#network-issues)
- [State Management Issues](#state-management-issues)
- [Testing Issues](#testing-issues)
- [Getting Help](#getting-help)

## 🎯 Overview

This troubleshooting guide covers:

- **Common Issues** - Frequently encountered problems and solutions
- **Debugging Techniques** - Tools and methods for problem diagnosis
- **Performance Issues** - Performance problems and optimization
- **Build Issues** - Compilation and deployment problems
- **Runtime Issues** - Application runtime errors and fixes
- **Network Issues** - API and WebSocket connection problems
- **State Management Issues** - Jotai and session state problems
- **Testing Issues** - Test failures and debugging

## 🚨 Common Issues

### Issue 1: Module Resolution Errors

**Symptoms:**
```
Module not found: Can't resolve '@/components/Button'
Error: Cannot find module '@/shared/services'
```

**Causes:**
- Incorrect import paths
- Missing TypeScript path configuration
- File doesn't exist

**Solutions:**

1. **Check TypeScript Configuration**:
   ```bash
   # Verify tsconfig.json paths
   cat tsconfig.json | grep paths
   ```

2. **Verify File Structure**:
   ```bash
   # Check if file exists
   ls -la components/Button.tsx
   ls -la shared/services/index.ts
   ```

3. **Fix Import Paths**:
   ```typescript
   // Correct import paths
   import { Button } from '@/components/ui/button';
   import { apiService } from '@/shared/services';
   ```

4. **Update tsconfig.json**:
   ```json
   {
     "compilerOptions": {
       "baseUrl": ".",
       "paths": {
         "@/*": ["./*"],
         "@/components/*": ["./components/*"],
         "@/shared/*": ["./shared/*"],
         "@/lib/*": ["./lib/*"]
       }
     }
   }
   ```

### Issue 2: TypeScript Compilation Errors

**Symptoms:**
```
Type 'string' is not assignable to type 'number'
Property 'x' does not exist on type 'Y'
```

**Solutions:**

1. **Check Type Definitions**:
   ```typescript
   // Add proper type annotations
   const count: number = 42;
   const user: User = { id: 1, name: 'John' };
   ```

2. **Fix Interface Definitions**:
   ```typescript
   interface User {
     id: number;
     name: string;
     email?: string; // Optional property
   }
   ```

3. **Use Type Assertions**:
   ```typescript
   // When you know the type better than TypeScript
   const data = response.data as User[];
   ```

4. **Run Type Checking**:
   ```bash
   npm run type-check
   ```

### Issue 3: Build Failures

**Symptoms:**
```
Build failed with exit code 1
Error: ENOENT: no such file or directory
```

**Solutions:**

1. **Clear Build Cache**:
   ```bash
   # Remove build artifacts
   rm -rf .next
   rm -rf node_modules/.cache
   
   # Reinstall dependencies
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **Check Environment Variables**:
   ```bash
   # Verify environment file exists
   ls -la .env.local
   
   # Check required variables
   cat .env.local | grep NEXT_PUBLIC
   ```

3. **Run Build with Verbose Output**:
   ```bash
   npm run build 2>&1 | tee build.log
   ```

4. **Check for Missing Dependencies**:
   ```bash
   # Check for missing packages
   npm ls
   
   # Install missing dependencies
   npm install missing-package
   ```

### Issue 4: Runtime Errors

**Symptoms:**
```
Uncaught TypeError: Cannot read property 'x' of undefined
ReferenceError: variable is not defined
```

**Solutions:**

1. **Add Error Boundaries**:
   ```typescript
   import { ErrorBoundary } from '@/shared/components/ErrorBoundary';

   function App() {
     return (
       <ErrorBoundary fallback={<ErrorFallback />}>
         <YourComponent />
       </ErrorBoundary>
     );
   }
   ```

2. **Add Null Checks**:
   ```typescript
   // Safe property access
   const value = data?.property?.subProperty;
   
   // Conditional rendering
   {data && <DataComponent data={data} />}
   ```

3. **Use Try-Catch Blocks**:
   ```typescript
   try {
     const result = await riskyOperation();
     setData(result);
   } catch (error) {
     console.error('Operation failed:', error);
     setError(error.message);
   }
   ```

4. **Enable Source Maps**:
   ```javascript
   // next.config.js
   module.exports = {
     productionBrowserSourceMaps: true,
   };
   ```

## 🔍 Debugging Techniques

### Browser Developer Tools

1. **Console Debugging**:
   ```typescript
   // Add debug logs
   console.log('Data:', data);
   console.log('State:', state);
   console.log('Props:', props);
   
   // Use console.table for objects
   console.table(users);
   
   // Use console.group for grouped logs
   console.group('API Call');
   console.log('Request:', request);
   console.log('Response:', response);
   console.groupEnd();
   ```

2. **React Developer Tools**:
   ```bash
   # Install React Developer Tools extension
   # Available for Chrome, Firefox, and Edge
   ```

3. **Network Tab**:
   - Check API requests and responses
   - Monitor WebSocket connections
   - Verify request headers and payloads

4. **Performance Tab**:
   - Monitor component render times
   - Identify performance bottlenecks
   - Check memory usage

### Debugging Tools

1. **VS Code Debugging**:
   ```json
   // .vscode/launch.json
   {
     "version": "0.2.0",
     "configurations": [
       {
         "name": "Next.js: debug server-side",
         "type": "node",
         "request": "launch",
         "program": "${workspaceFolder}/node_modules/next/dist/bin/next",
         "args": ["dev"],
         "cwd": "${workspaceFolder}",
         "console": "integratedTerminal"
       },
       {
         "name": "Next.js: debug client-side",
         "type": "chrome",
         "request": "launch",
         "url": "http://localhost:3000"
       }
     ]
   }
   ```

2. **React DevTools Profiler**:
   ```typescript
   // Wrap components for profiling
   import { Profiler } from 'react';

   function onRenderCallback(id, phase, actualDuration) {
     console.log(`Component ${id} took ${actualDuration}ms to render`);
   }

   <Profiler id="MyComponent" onRender={onRenderCallback}>
     <MyComponent />
   </Profiler>
   ```

3. **Custom Debug Hooks**:
   ```typescript
   // hooks/useDebug.ts
   export const useDebug = (name: string, value: any) => {
     useEffect(() => {
       console.log(`${name} changed:`, value);
     }, [name, value]);
   };

   // Usage
   const [data, setData] = useState(null);
   useDebug('Data', data);
   ```

## ⚡ Performance Issues

### Issue 1: Slow Page Load

**Symptoms:**
- Long loading times
- Poor Core Web Vitals scores
- User complaints about slowness

**Solutions:**

1. **Analyze Bundle Size**:
   ```bash
   npm run analyze
   ```

2. **Implement Code Splitting**:
   ```typescript
   // Lazy load components
   const HeavyComponent = lazy(() => import('./HeavyComponent'));

   function App() {
     return (
       <Suspense fallback={<Loading />}>
         <HeavyComponent />
       </Suspense>
     );
   }
   ```

3. **Optimize Images**:
   ```typescript
   import Image from 'next/image';

   <Image
     src="/image.jpg"
     alt="Description"
     width={500}
     height={300}
     priority={true}
   />
   ```

4. **Enable Compression**:
   ```javascript
   // next.config.js
   module.exports = {
     compress: true,
   };
   ```

### Issue 2: Memory Leaks

**Symptoms:**
- Increasing memory usage
- Application slowdown over time
- Browser crashes

**Solutions:**

1. **Clean Up Event Listeners**:
   ```typescript
   useEffect(() => {
     const handleResize = () => {
       // Handle resize
     };

     window.addEventListener('resize', handleResize);
     
     return () => {
       window.removeEventListener('resize', handleResize);
     };
   }, []);
   ```

2. **Clean Up Timers**:
   ```typescript
   useEffect(() => {
     const timer = setInterval(() => {
       // Do something
     }, 1000);

     return () => {
       clearInterval(timer);
     };
   }, []);
   ```

3. **Clean Up Subscriptions**:
   ```typescript
   useEffect(() => {
     const subscription = apiService.subscribe((data) => {
       setData(data);
     });

     return () => {
       subscription.unsubscribe();
     };
   }, []);
   ```

### Issue 3: Re-render Issues

**Symptoms:**
- Excessive re-renders
- Performance degradation
- Component flickering

**Solutions:**

1. **Use React.memo**:
   ```typescript
   const ExpensiveComponent = React.memo(({ data }) => {
     return <div>{/* Expensive rendering */}</div>;
   });
   ```

2. **Use useMemo**:
   ```typescript
   const expensiveValue = useMemo(() => {
     return expensiveCalculation(data);
   }, [data]);
   ```

3. **Use useCallback**:
   ```typescript
   const handleClick = useCallback(() => {
     // Handle click
   }, []);
   ```

4. **Optimize State Updates**:
   ```typescript
   // Batch state updates
   const handleUpdate = () => {
     setState(prev => ({
       ...prev,
       count: prev.count + 1,
       lastUpdated: Date.now()
     }));
   };
   ```

## 🔧 Build Issues

### Issue 1: TypeScript Errors

**Symptoms:**
```
TypeScript compilation failed
```

**Solutions:**

1. **Check TypeScript Version**:
   ```bash
   npx tsc --version
   ```

2. **Run Type Checking**:
   ```bash
   npm run type-check
   ```

3. **Fix Type Errors**:
   ```typescript
   // Add proper types
   interface Props {
     data: string[];
     onUpdate: (data: string[]) => void;
   }

   const Component: React.FC<Props> = ({ data, onUpdate }) => {
     // Component implementation
   };
   ```

4. **Update TypeScript Configuration**:
   ```json
   // tsconfig.json
   {
     "compilerOptions": {
       "strict": true,
       "noImplicitAny": true,
       "strictNullChecks": true
     }
   }
   ```

### Issue 2: ESLint Errors

**Symptoms:**
```
ESLint found 5 problems
```

**Solutions:**

1. **Run ESLint**:
   ```bash
   npm run lint
   ```

2. **Fix ESLint Issues**:
   ```bash
   npm run lint:fix
   ```

3. **Check ESLint Configuration**:
   ```json
   // .eslintrc.json
   {
     "extends": [
       "next/core-web-vitals",
       "next/typescript"
     ],
     "rules": {
       "@typescript-eslint/no-unused-vars": "error"
     }
   }
   ```

### Issue 3: Dependency Issues

**Symptoms:**
```
Cannot resolve module 'package-name'
```

**Solutions:**

1. **Check Package.json**:
   ```bash
   cat package.json | grep package-name
   ```

2. **Reinstall Dependencies**:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Check for Version Conflicts**:
   ```bash
   npm ls package-name
   ```

4. **Update Dependencies**:
   ```bash
   npm update
   npm audit fix
   ```

## 🌐 Network Issues

### Issue 1: API Request Failures

**Symptoms:**
```
Failed to fetch
Network error
```

**Solutions:**

1. **Check API Endpoint**:
   ```typescript
   // Verify API URL
   console.log('API URL:', process.env.NEXT_PUBLIC_API_BASE_URL);
   ```

2. **Add Error Handling**:
   ```typescript
   try {
     const response = await fetch('/api/data');
     if (!response.ok) {
       throw new Error(`HTTP error! status: ${response.status}`);
     }
     const data = await response.json();
   } catch (error) {
     console.error('API request failed:', error);
   }
   ```

3. **Check CORS Configuration**:
   ```typescript
   // Add CORS headers to requests
   const response = await fetch('/api/data', {
     headers: {
       'Content-Type': 'application/json',
     },
     credentials: 'include',
   });
   ```

4. **Test API Endpoint**:
   ```bash
   curl -X GET http://localhost:8000/api/health
   ```

### Issue 2: WebSocket Connection Issues

**Symptoms:**
```
WebSocket connection failed
Connection timeout
```

**Solutions:**

1. **Check WebSocket URL**:
   ```typescript
   console.log('WebSocket URL:', process.env.NEXT_PUBLIC_WS_BASE_URL);
   ```

2. **Add Connection Error Handling**:
   ```typescript
   const ws = new WebSocket(wsUrl);
   
   ws.onerror = (error) => {
     console.error('WebSocket error:', error);
   };
   
   ws.onclose = (event) => {
     console.log('WebSocket closed:', event.code, event.reason);
   };
   ```

3. **Implement Reconnection Logic**:
   ```typescript
   const connectWebSocket = () => {
     const ws = new WebSocket(wsUrl);
     
     ws.onclose = () => {
       setTimeout(connectWebSocket, 1000);
     };
     
     return ws;
   };
   ```

4. **Test WebSocket Connection**:
   ```bash
   wscat -c ws://localhost:8000/ws
   ```

## 🔄 State Management Issues

### Issue 1: Jotai Atom Problems

**Symptoms:**
```
Atom not updating
State not persisting
```

**Solutions:**

1. **Check Atom Definition**:
   ```typescript
   // Ensure atom is properly defined
   const countAtom = atom(0);
   const doubleCountAtom = atom((get) => get(countAtom) * 2);
   ```

2. **Use Atom Correctly**:
   ```typescript
   const [count, setCount] = useAtom(countAtom);
   
   // Update atom
   setCount(prev => prev + 1);
   ```

3. **Debug Atom State**:
   ```typescript
   const [count] = useAtom(countAtom);
   console.log('Count atom value:', count);
   ```

4. **Check Atom Dependencies**:
   ```typescript
   // Derived atom with proper dependencies
   const derivedAtom = atom((get) => {
     const value1 = get(atom1);
     const value2 = get(atom2);
     return value1 + value2;
   });
   ```

### Issue 2: Session State Issues

**Symptoms:**
```
Session not persisting
State lost on refresh
```

**Solutions:**

1. **Check Session Provider**:
   ```typescript
   // Ensure GlobalSessionProvider wraps the app
   function App() {
     return (
       <GlobalSessionProvider>
         <YourApp />
       </GlobalSessionProvider>
     );
   }
   ```

2. **Verify Session Storage**:
   ```typescript
   // Check localStorage
   console.log('Session token:', localStorage.getItem('guideSessionToken'));
   console.log('Pillar states:', localStorage.getItem('pillarStates'));
   ```

3. **Handle Session Restoration**:
   ```typescript
   useEffect(() => {
     const token = localStorage.getItem('guideSessionToken');
     if (token) {
       setGuideSessionToken(token);
     }
   }, []);
   ```

4. **Add Session Validation**:
   ```typescript
   const validateSession = async (token: string) => {
     try {
       const response = await fetch('/api/validate-session', {
         headers: { Authorization: `Bearer ${token}` }
       });
       return response.ok;
     } catch (error) {
       return false;
     }
   };
   ```

## 🧪 Testing Issues

### Issue 1: Jest Test Failures

**Symptoms:**
```
Test failed
Cannot find module
```

**Solutions:**

1. **Check Jest Configuration**:
   ```javascript
   // jest.config.js
   module.exports = {
     testEnvironment: 'jsdom',
     setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
     moduleNameMapping: {
       '^@/(.*)$': '<rootDir>/$1',
     },
   };
   ```

2. **Run Tests with Verbose Output**:
   ```bash
   npm run test -- --verbose
   ```

3. **Clear Jest Cache**:
   ```bash
   npm run test -- --clearCache
   ```

4. **Check Test Setup**:
   ```javascript
   // jest.setup.js
   import '@testing-library/jest-dom';
   
   global.fetch = jest.fn();
   ```

### Issue 2: Playwright Test Failures

**Symptoms:**
```
Playwright test failed
Element not found
```

**Solutions:**

1. **Check Playwright Configuration**:
   ```typescript
   // playwright.config.ts
   import { defineConfig, devices } from '@playwright/test';

   export default defineConfig({
     testDir: './tests/e2e',
     use: {
       baseURL: 'http://localhost:3000',
       trace: 'on-first-retry',
     },
   });
   ```

2. **Run Tests with Debug Mode**:
   ```bash
   npm run test:e2e -- --debug
   ```

3. **Check Element Selectors**:
   ```typescript
   // Use reliable selectors
   await page.click('[data-testid="submit-button"]');
   await page.fill('[data-testid="email-input"]', 'test@example.com');
   ```

4. **Add Wait Conditions**:
   ```typescript
   // Wait for elements to be ready
   await page.waitForSelector('[data-testid="loading"]', { state: 'hidden' });
   await page.waitForResponse(response => response.url().includes('/api/data'));
   ```

## 📞 Getting Help

### Documentation Resources

- [API Documentation](./API.md) - Service layer interfaces
- [Component Library](./components.md) - Component documentation
- [State Management](./state-management.md) - State management patterns
- [Configuration Guide](./configuration.md) - Environment setup

### Debugging Checklist

1. **Check Console Errors**:
   - Open browser developer tools
   - Look for error messages in console
   - Check network tab for failed requests

2. **Verify Environment**:
   - Check environment variables
   - Verify API endpoints
   - Test backend connectivity

3. **Check Dependencies**:
   - Verify package versions
   - Check for version conflicts
   - Update outdated packages

4. **Test Isolation**:
   - Create minimal reproduction
   - Test in different browsers
   - Check on different devices

### Support Channels

1. **Repository Issues**:
   - Check existing issues
   - Create new issue with details
   - Include error messages and steps

2. **Documentation**:
   - Review relevant documentation
   - Check code examples
   - Verify configuration

3. **Community**:
   - Ask in community forums
   - Check Stack Overflow
   - Review GitHub discussions

### Issue Reporting Template

When reporting issues, include:

```markdown
## Issue Description
Brief description of the problem

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., Windows 10, macOS 12]
- Browser: [e.g., Chrome 100, Firefox 99]
- Node.js: [e.g., 18.0.0]
- npm: [e.g., 8.0.0]

## Error Messages
```
Error message here
```

## Additional Information
Any other relevant details
```

---

**Last Updated**: [Automated Update]
**Version**: 1.0.0 