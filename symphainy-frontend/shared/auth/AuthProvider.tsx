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
import { useSessionBoundary } from "@/shared/state/SessionBoundaryProvider";

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
  const { upgradeSession, invalidateSession, state: sessionState } = useSessionBoundary();
  
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

        // Check for access_token first - if not present, user is not authenticated
        const accessToken = sessionStorage.getItem("access_token");
        
        if (!accessToken) {
          // No access_token means user is not authenticated - clear any stale session data
          sessionStorage.removeItem("session_id");
          sessionStorage.removeItem("tenant_id");
          sessionStorage.removeItem("user_id");
          sessionStorage.removeItem("user_data");
          // Also clear from localStorage (old storage location)
          localStorage.removeItem("session_id");
          localStorage.removeItem("tenant_id");
          localStorage.removeItem("user_id");
          localStorage.removeItem("user_data");
          setIsLoading(false);
          return;
        }

        // User is authenticated - restore session data
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
        // Clear stale data on error
        if (typeof window !== 'undefined') {
          sessionStorage.removeItem("session_id");
          sessionStorage.removeItem("tenant_id");
          sessionStorage.removeItem("user_id");
          sessionStorage.removeItem("user_data");
        }
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
      // ✅ PHASE 2: Use ServiceLayerAPI instead of direct fetch
      const { loginUser } = await import('@/shared/services/ServiceLayerAPI');
      const data = await loginUser({ email, password });
      
      if (!data.success) {
        throw new Error(data.message || 'Login failed');
      }
      
      // ✅ PHASE 2: ServiceLayerAPI returns standardized format
      const accessToken = data.token;
      const userId = data.user?.id;
      const tenantId = data.user?.tenant_id || "default_tenant";
      const userEmail = data.user?.email || email;
      const userName = data.user?.name || email.split("@")[0];
      const permissions = data.user?.permissions || ["read", "write"];

      if (!accessToken || !userId) {
        throw new Error("Invalid authentication response: missing token or user ID");
      }

      // ✅ SESSION BOUNDARY PATTERN: Upgrade existing session via SessionBoundaryProvider
      // SessionBoundaryProvider manages session lifecycle - we just trigger the upgrade
      await upgradeSession({
        user_id: userId,
        tenant_id: tenantId,
        access_token: accessToken,
        metadata: { email: userEmail, authenticated_at: new Date().toISOString() },
      });

      // Store user data
      const userData: User = {
        id: userId,
        email: userEmail,
        name: userName,
        avatar_url: data.user?.avatar_url,
        tenant_id: tenantId,
        permissions: permissions,
      };

      setUser(userData);
      setIsAuthenticated(true);
      
      // SessionBoundaryProvider handles session storage - we just store user_data for UI
      if (typeof window !== "undefined") {
        sessionStorage.setItem("user_data", JSON.stringify(userData));
        
        if (data.refresh_token) {
          sessionStorage.setItem("refresh_token", data.refresh_token);
        }
      }
      
      setIsLoading(false);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Login failed";
      setError(errorMessage);
      setIsLoading(false);
      throw err;
    }
  }, [upgradeSession]);

  // Register
  const register = useCallback(async (
    name: string,
    email: string,
    password: string
  ): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      // ✅ PHASE 2: Use ServiceLayerAPI instead of direct fetch
      const { registerUser } = await import('@/shared/services/ServiceLayerAPI');
      const data = await registerUser({ name, email, password });
      
      if (!data.success) {
        throw new Error(data.message || 'Registration failed');
      }
      
      // ✅ PHASE 2: ServiceLayerAPI returns standardized format
      const accessToken = data.token;
      const userId = data.user?.id;
      const tenantId = data.user?.tenant_id || "default_tenant";
      const userEmail = data.user?.email || email;
      const userName = data.user?.name || name;
      const permissions = data.user?.permissions || ["read", "write"];

      if (!accessToken || !userId) {
        throw new Error("Invalid registration response: missing token or user ID");
      }

      // ✅ SESSION BOUNDARY PATTERN: Upgrade existing session via SessionBoundaryProvider
      await upgradeSession({
        user_id: userId,
        tenant_id: tenantId,
        access_token: accessToken,
        metadata: { email: userEmail, name: userName, registered_at: new Date().toISOString() },
      });

      // Store user data
      const userData: User = {
        id: userId,
        email: userEmail,
        name: userName,
        avatar_url: data.user?.avatar_url,
        tenant_id: tenantId,
        permissions: permissions,
      };

      setUser(userData);
      setIsAuthenticated(true);
      
      // SessionBoundaryProvider handles session storage - we just store user_data for UI
      if (typeof window !== "undefined") {
        sessionStorage.setItem("user_data", JSON.stringify(userData));
        
        if (data.refresh_token) {
          sessionStorage.setItem("refresh_token", data.refresh_token);
        }
      }
      
      setIsLoading(false);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Registration failed";
      setError(errorMessage);
      setIsLoading(false);
      throw err;
    }
  }, [upgradeSession]);

  // Logout
  const logout = useCallback(async (): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      // Invalidate session via SessionBoundaryProvider
      invalidateSession();
      
      // Clear user data
      setUser(null);
      setIsAuthenticated(false);
      
      // Clear user_data (SessionBoundaryProvider handles session storage)
      if (typeof window !== "undefined") {
        sessionStorage.removeItem("user_data");
        sessionStorage.removeItem("refresh_token");
      }
      
      setIsLoading(false);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Logout failed";
      setError(errorMessage);
      setIsLoading(false);
      throw err;
    }
  }, [invalidateSession]);

  // Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Get session token from SessionBoundaryProvider
  const sessionToken = sessionState.sessionId;

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
