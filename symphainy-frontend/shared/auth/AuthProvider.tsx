/**
 * Auth Provider (New Architecture)
 * 
 * Authentication provider using Security Guard SDK via Experience Plane.
 * 
 * Architecture:
 * - Login/Register → Experience Plane API → Security Guard SDK → Runtime
 * - Session management via PlatformStateProvider
 * - No hardcoded bypasses
 * - Proper authentication flow
 */

"use client";

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
} from "react";
import { ExperiencePlaneClient } from "@/shared/services/ExperiencePlaneClient";
import { getGlobalExperiencePlaneClient } from "@/shared/services/ExperiencePlaneClient";
import { usePlatformState } from "@/shared/state/PlatformStateProvider";

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
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
  
  // Session token (for backward compatibility)
  sessionToken: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
};

interface AuthProviderProps {
  children: React.ReactNode;
  experiencePlaneClient?: ExperiencePlaneClient;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({
  children,
  experiencePlaneClient,
}) => {
  const client = experiencePlaneClient || getGlobalExperiencePlaneClient();
  const { createSession, clearSession, state } = usePlatformState();
  
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Restore session from sessionStorage on mount
  // Using sessionStorage instead of localStorage for better security (cleared on tab close)
  useEffect(() => {
    const restoreSession = async () => {
      try {
        if (typeof window === "undefined") {
          setIsLoading(false);
          return;
        }

        const storedUser = sessionStorage.getItem("user_data");
        const storedTenantId = sessionStorage.getItem("tenant_id");
        const storedUserId = sessionStorage.getItem("user_id");
        const storedSessionId = sessionStorage.getItem("session_id");

        if (storedUser && storedTenantId && storedUserId && storedSessionId) {
          const userData = JSON.parse(storedUser);
          setUser({
            id: storedUserId,
            email: userData.email,
            name: userData.name,
            avatar_url: userData.avatar_url,
            permissions: userData.permissions,
            tenant_id: storedTenantId,
          });
          setIsAuthenticated(true);

          // Restore session in PlatformStateProvider
          // Note: Session will be synced via PlatformStateProvider's syncWithRuntime
        }
      } catch (error) {
        console.error("Failed to restore session:", error);
      } finally {
        setIsLoading(false);
      }
    };

    restoreSession();
  }, []);

  // Login
  const login = useCallback(async (email: string, password: string): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      // Call Experience Plane API for authentication
      // POST /api/auth/login → Security Guard SDK → Runtime
      const { getApiEndpointUrl } = require('@/shared/config/api-config');
      const loginUrl = getApiEndpointUrl('/api/auth/login');
      
      const response = await fetch(loginUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: 'Login failed' }));
        throw new Error(errorData.message || errorData.error || `Login failed: ${response.statusText}`);
      }

      const data = await response.json();
      
      // Handle different response formats
      const authData = data.data || data;
      const accessToken = authData.access_token || authData.token;
      const userId = authData.user_id || authData.id;
      const tenantId = authData.tenant_id || "default_tenant";
      const userEmail = authData.email || email;
      const userName = authData.name || authData.full_name || email.split("@")[0];
      const roles = authData.roles || ["user"];
      const permissions = authData.permissions || ["read", "write"];

      if (!accessToken || !userId) {
        throw new Error("Invalid authentication response: missing token or user ID");
      }

      // Create session via Experience Plane after successful authentication
      const sessionId = await createSession(tenantId, userId, {
        email: userEmail,
        authenticated_at: new Date().toISOString(),
      });

      // Store user data
      const userData: User = {
        id: userId,
        email: userEmail,
        name: userName,
        avatar_url: authData.avatar_url,
        tenant_id: tenantId,
        permissions: permissions,
      };

      setUser(userData);
      setIsAuthenticated(true);
      
      // Store in sessionStorage (better security - cleared on tab close)
      // TODO: Production - migrate to HttpOnly cookies (see docs/execution/auth_security_migration_plan.md)
      if (typeof window !== "undefined") {
        sessionStorage.setItem("user_data", JSON.stringify(userData));
        sessionStorage.setItem("auth_token", accessToken);
        sessionStorage.setItem("session_id", sessionId);
        sessionStorage.setItem("tenant_id", tenantId);
        sessionStorage.setItem("user_id", userId);
        
        if (authData.refresh_token) {
          sessionStorage.setItem("refresh_token", authData.refresh_token);
        }
      }
      
      setIsLoading(false);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Login failed";
      setError(errorMessage);
      setIsLoading(false);
      throw err;
    }
  }, [createSession]);

  // Register
  const register = useCallback(async (
    name: string,
    email: string,
    password: string
  ): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      // Call Experience Plane API for registration
      // POST /api/auth/register → Security Guard SDK → Runtime
      const { getApiEndpointUrl } = require('@/shared/config/api-config');
      const registerUrl = getApiEndpointUrl('/api/auth/register');
      
      const response = await fetch(registerUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, email, password }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: 'Registration failed' }));
        throw new Error(errorData.message || errorData.error || `Registration failed: ${response.statusText}`);
      }

      const data = await response.json();
      
      // Handle different response formats
      const authData = data.data || data;
      const accessToken = authData.access_token || authData.token;
      const userId = authData.user_id || authData.id;
      const tenantId = authData.tenant_id || "default_tenant";
      const userEmail = authData.email || email;
      const userName = authData.name || authData.full_name || name;
      const roles = authData.roles || ["user"];
      const permissions = authData.permissions || ["read", "write"];

      if (!accessToken || !userId) {
        throw new Error("Invalid registration response: missing token or user ID");
      }

      // Create session via Experience Plane after successful registration
      const sessionId = await createSession(tenantId, userId, {
        email: userEmail,
        name: userName,
        registered_at: new Date().toISOString(),
      });

      // Store user data
      const userData: User = {
        id: userId,
        email: userEmail,
        name: userName,
        avatar_url: authData.avatar_url,
        tenant_id: tenantId,
        permissions: permissions,
      };

      setUser(userData);
      setIsAuthenticated(true);
      
      // Store in sessionStorage (better security - cleared on tab close)
      // TODO: Production - migrate to HttpOnly cookies (see docs/execution/auth_security_migration_plan.md)
      if (typeof window !== "undefined") {
        sessionStorage.setItem("user_data", JSON.stringify(userData));
        sessionStorage.setItem("auth_token", accessToken);
        sessionStorage.setItem("session_id", sessionId);
        sessionStorage.setItem("tenant_id", tenantId);
        sessionStorage.setItem("user_id", userId);
        
        if (authData.refresh_token) {
          sessionStorage.setItem("refresh_token", authData.refresh_token);
        }
      }
      
      setIsLoading(false);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Registration failed";
      setError(errorMessage);
      setIsLoading(false);
      throw err;
    }
  }, [createSession]);

  // Logout
  const logout = useCallback(async (): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      // Clear session
      clearSession();
      
      // Clear user data
      setUser(null);
      setIsAuthenticated(false);
      
      // Clear sessionStorage
      if (typeof window !== "undefined") {
        sessionStorage.removeItem("user_data");
        sessionStorage.removeItem("auth_token");
        sessionStorage.removeItem("session_id");
        sessionStorage.removeItem("tenant_id");
        sessionStorage.removeItem("user_id");
        sessionStorage.removeItem("refresh_token");
      }
      
      setIsLoading(false);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Logout failed";
      setError(errorMessage);
      setIsLoading(false);
      throw err;
    }
  }, [clearSession]);

  // Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Get session token from PlatformStateProvider
  const sessionToken = state.session.sessionId;

  const contextValue: AuthContextType = {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    register,
    logout,
    clearError,
    sessionToken,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};
