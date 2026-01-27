"use client";
import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  useRef,
} from "react";
import { useGlobalSession } from "./GlobalSessionProvider";
import { loginUser, registerUser, validateToken, AuthResponse } from "@/lib/api/auth";

// ============================================
// Types and Interfaces
// ============================================

export interface User {
  id: string;
  email: string;
  name: string;
  avatar_url?: string;
  permissions?: string[];
  tenant_id?: string;
}

export interface AuthContextType {
  // Authentication state
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Authentication actions
  login: (email: string, password: string) => Promise<AuthResponse>;
  register: (name: string, email: string, password: string) => Promise<AuthResponse>;
  logout: () => Promise<void>;
  clearError: () => void;
  
  // Session integration
  sessionToken: string | null;
}

// ============================================
// Context Creation
// ============================================

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// ============================================
// Auth Provider Component
// ============================================

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  // Debug: Log when AuthProvider function starts (before hooks)
  console.log('[AuthProvider] Component function called');
  if (typeof window !== 'undefined') {
    (window as any).__AUTH_PROVIDER_FUNCTION_CALLED__ = true;
  }
  
  // Hooks must be called unconditionally
  const { guideSessionToken, setGuideSessionToken } = useGlobalSession();
  console.log('[AuthProvider] useGlobalSession hook succeeded');
  
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Use ref to track if we've already attempted to restore session (prevents multiple calls)
  const hasRestoredSessionRef = useRef(false);
  
  // Debug: Log when AuthProvider mounts
  // Use multiple logging methods to ensure we see it
  console.log('[AuthProvider] Component mounted');
  console.info('[AuthProvider] Component mounted (info)');
  console.warn('[AuthProvider] Component mounted (warn)');
  
  // Also try to set a window property to verify component is running
  if (typeof window !== 'undefined') {
    (window as any).__AUTH_PROVIDER_MOUNTED__ = true;
    (window as any).__AUTH_PROVIDER_MOUNT_TIME__ = Date.now();
  }

  // ============================================
  // Authentication Actions
  // ============================================

  const login = useCallback(async (email: string, password: string): Promise<AuthResponse> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await loginUser({ email, password });
      
      if (response.success && response.user && response.token) {
        // Store auth token in localStorage FIRST
        localStorage.setItem("auth_token", response.token);
        localStorage.setItem("user_data", JSON.stringify({
          id: response.user.id,
          email: response.user.email,
          name: response.user.name,
        }));
        
        // ✅ CRITICAL: Set guideSessionToken BEFORE setting auth state
        // This ensures that when isAuthenticated becomes true, guideSessionToken is already set
        // This prevents race conditions where chat components try to connect before token is ready
        await setGuideSessionToken(response.token);
        
        // Store user data
        setUser({
          id: response.user.id,
          email: response.user.email,
          name: response.user.name,
          permissions: response.user.permissions || ['read', 'write'], // Use from backend or default
          tenant_id: response.user.tenant_id, // From backend (if provided)
        });
        
        setIsAuthenticated(true);
        
        return response;
      } else {
        setError(response.message);
        return response;
      }
    } catch (error) {
      const errorMessage = "An unexpected error occurred. Please try again.";
      setError(errorMessage);
      return {
        success: false,
        message: errorMessage,
      };
    } finally {
      setIsLoading(false);
    }
  }, [setGuideSessionToken]);

  const register = useCallback(async (name: string, email: string, password: string): Promise<AuthResponse> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await registerUser({ name, email, password });
      
      if (response.success && response.user && response.token) {
        // Store auth token in localStorage FIRST
        localStorage.setItem("auth_token", response.token);
        localStorage.setItem("user_data", JSON.stringify({
          id: response.user.id,
          email: response.user.email,
          name: response.user.name,
        }));
        
        // ✅ CRITICAL: Set guideSessionToken BEFORE setting auth state
        // This ensures that when isAuthenticated becomes true, guideSessionToken is already set
        // This prevents race conditions where chat components try to connect before token is ready
        await setGuideSessionToken(response.token);
        
        // Store user data
        // ✅ Tenant ID now comes from backend, not generated client-side
        setUser({
          id: response.user.id,
          email: response.user.email,
          name: response.user.name,
          permissions: response.user.permissions || ['read', 'write'],
          tenant_id: response.user.tenant_id, // From backend
        });
        
        setIsAuthenticated(true);
        
        return response;
      } else {
        setError(response.message);
        return response;
      }
    } catch (error) {
      const errorMessage = "An unexpected error occurred. Please try again.";
      setError(errorMessage);
      return {
        success: false,
        message: errorMessage,
      };
    } finally {
      setIsLoading(false);
    }
  }, [setGuideSessionToken]);

  const logout = useCallback(async (): Promise<void> => {
    setIsLoading(true);
    
    try {
      // Clear local storage
      localStorage.removeItem("auth_token");
      localStorage.removeItem("user_data");
      
      // Clear state
      setUser(null);
      setIsAuthenticated(false);
      setError(null);
      
      // Reset restoration ref so we can restore on next login
      hasRestoredSessionRef.current = false;
      
      // Clear global session
      await setGuideSessionToken("");
      
      console.log("User logged out successfully");
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      setIsLoading(false);
    }
  }, [setGuideSessionToken]);

  const clearError = useCallback((): void => {
    setError(null);
  }, []);

  // ============================================
  // Session Restoration
  // ============================================

  useEffect(() => {
    console.log('[AuthProvider] useEffect running - checking localStorage...');
    
    const restoreSession = async () => {
      try {
        // Skip if we've already restored session (prevents multiple calls)
        if (hasRestoredSessionRef.current) {
          console.log('[AuthProvider] Session already restored, skipping restoreSession');
          return;
        }
        
        // Mark that we're attempting to restore (prevents concurrent calls)
        hasRestoredSessionRef.current = true;
        
        console.log('[AuthProvider] restoreSession function called');
        
        // 1. IMMEDIATE SYNCHRONOUS CHECK: Get token and user from localStorage
        const storedToken = localStorage.getItem("auth_token");
        const storedUser = localStorage.getItem("user_data");
        
        console.log('[AuthProvider] restoreSession called - token:', !!storedToken, 'user:', !!storedUser, 'token length:', storedToken?.length);
        
        // If no valid auth data, set loading to false and return immediately
        if (!storedToken || !storedUser || storedToken === 'token_placeholder') {
          hasRestoredSessionRef.current = false;
          setIsLoading(false);
          console.log('[AuthProvider] No valid auth data found');
          
          if (typeof window !== 'undefined') {
            (window as any).__AUTH_IS_AUTHENTICATED__ = false;
          }
          return;
        }
        
        // 2. PARSE USER DATA (synchronous)
        let userData;
        try {
          userData = JSON.parse(storedUser);
          console.log('[AuthProvider] Parsed user data:', userData.email, '| ID:', userData.id);
        } catch (parseError) {
          console.error('[AuthProvider] ❌ Failed to parse user data:', parseError);
          localStorage.removeItem("auth_token");
          localStorage.removeItem("user_data");
          hasRestoredSessionRef.current = false;
          setIsLoading(false);
          return;
        }
        
        // 3. VALIDATE TOKEN WITH BACKEND (async, but only once)
        // This ensures the token is still valid before setting auth state
        try {
          const isValid = await validateToken(storedToken);
          
          if (isValid) {
            // ✅ CRITICAL: Set guideSessionToken FIRST, then auth state
            // This ensures that when isAuthenticated becomes true, guideSessionToken is already set
            // This prevents race conditions where chat components try to connect before token is ready
            if (!guideSessionToken || guideSessionToken !== storedToken) {
              await setGuideSessionToken(storedToken);
              console.log('[AuthProvider] ✅ Global session token set (before auth state)');
            }
            
            // ✅ Token is valid - set auth state atomically (AFTER token is set)
            setUser({
              id: userData.id,
              email: userData.email,
              name: userData.name,
              permissions: userData.permissions || ['read', 'write'],
              tenant_id: userData.tenant_id,
            });
            setIsAuthenticated(true);
            console.log('[AuthProvider] ✅ Authentication state set to true (token validated)');
            
            // Expose authentication state to window for debugging
            if (typeof window !== 'undefined') {
              (window as any).__AUTH_IS_AUTHENTICATED__ = true;
              (window as any).__AUTH_USER_EMAIL__ = userData.email;
              (window as any).__AUTH_RESTORE_SESSION_COMPLETE__ = Date.now();
            }
          } else {
            // ❌ Token is invalid - clear auth data
            console.log('[AuthProvider] ❌ Token validation failed - clearing auth data');
            localStorage.removeItem("auth_token");
            localStorage.removeItem("user_data");
            hasRestoredSessionRef.current = false;
            
            if (typeof window !== 'undefined') {
              (window as any).__AUTH_IS_AUTHENTICATED__ = false;
            }
          }
        } catch (validationError) {
          // Error during validation - clear auth data to be safe
          console.error('[AuthProvider] ❌ Token validation error:', validationError);
          localStorage.removeItem("auth_token");
          localStorage.removeItem("user_data");
          hasRestoredSessionRef.current = false;
        }
      } catch (error) {
        console.error("[AuthProvider] Session restoration error:", error);
        // Clear invalid session data
        localStorage.removeItem("auth_token");
        localStorage.removeItem("user_data");
        hasRestoredSessionRef.current = false;
      } finally {
        setIsLoading(false);
      }
    };

    // Run restoreSession immediately
    restoreSession();
    
    // Listen for storage events (for when Playwright populates localStorage after page load)
    const handleStorageChange = (e: StorageEvent) => {
      console.log('[AuthProvider] Storage event detected:', e.key);
      if (e.key === 'auth_token' || e.key === 'user_data') {
        // Reset ref to allow restoration from storage event
        hasRestoredSessionRef.current = false;
        console.log('[AuthProvider] Triggering restoreSession from storage event');
        restoreSession();
      }
    };
    
    window.addEventListener('storage', handleStorageChange);
    
    // Listen for custom events (for manual triggers from tests)
    const handleAuthCheckRequest = () => {
      console.log('[AuthProvider] Custom auth-check-request event received, triggering restoreSession');
      // Reset ref to allow restoration from custom event
      hasRestoredSessionRef.current = false;
      restoreSession();
    };
    
    window.addEventListener('auth-check-request', handleAuthCheckRequest);
    
    // ✅ REMOVED PERIODIC POLLING - replaced with single validation call
    // The periodic polling was causing race conditions and unnecessary checks
    // Now we rely on:
    // 1. Immediate synchronous check
    // 2. Single async validation call
    // 3. Storage events for external changes
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('auth-check-request', handleAuthCheckRequest);
    };
  }, [guideSessionToken, setGuideSessionToken]);

  // ============================================
  // Context Value
  // ============================================

  const contextValue: AuthContextType = {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    register,
    logout,
    clearError,
    sessionToken: guideSessionToken,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

// ============================================
// Hook for Using Auth Context
// ============================================

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};





























