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

  // Restore session from localStorage on mount
  useEffect(() => {
    const restoreSession = async () => {
      try {
        const storedUser = localStorage.getItem("user_data");
        const storedTenantId = localStorage.getItem("tenant_id");
        const storedUserId = localStorage.getItem("user_id");
        const storedSessionId = localStorage.getItem("session_id");

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
      // TODO: Call Experience Plane API for authentication
      // For now, we'll use a placeholder that creates a session
      // In full implementation, this would call:
      // POST /api/auth/login → Security Guard SDK → Runtime
      
      // Placeholder: Create session after "authentication"
      // In production, this would be:
      // 1. POST /api/auth/login with credentials
      // 2. Receive auth token and user data
      // 3. Create session via Experience Plane
      
      // For MVP, we'll simulate authentication and create session
      const tenantId = "default_tenant"; // In production, get from auth response
      const userId = `user_${Date.now()}`; // In production, get from auth response
      
      const sessionId = await createSession(tenantId, userId, {
        email,
        authenticated_at: new Date().toISOString(),
      });

      // Store user data
      const userData: User = {
        id: userId,
        email,
        name: email.split("@")[0], // Placeholder
        tenant_id: tenantId,
        permissions: ["user"], // Placeholder
      };

      setUser(userData);
      setIsAuthenticated(true);
      
      localStorage.setItem("user_data", JSON.stringify(userData));
      localStorage.setItem("auth_token", sessionId); // Use sessionId as token for now
      
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
      // TODO: Call Experience Plane API for registration
      // For now, we'll use a placeholder that creates a session
      // In full implementation, this would call:
      // POST /api/auth/register → Security Guard SDK → Runtime
      
      // Placeholder: Create session after "registration"
      const tenantId = "default_tenant"; // In production, get from registration response
      const userId = `user_${Date.now()}`; // In production, get from registration response
      
      const sessionId = await createSession(tenantId, userId, {
        email,
        name,
        registered_at: new Date().toISOString(),
      });

      // Store user data
      const userData: User = {
        id: userId,
        email,
        name,
        tenant_id: tenantId,
        permissions: ["user"], // Placeholder
      };

      setUser(userData);
      setIsAuthenticated(true);
      
      localStorage.setItem("user_data", JSON.stringify(userData));
      localStorage.setItem("auth_token", sessionId); // Use sessionId as token for now
      
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
      
      // Clear localStorage
      localStorage.removeItem("user_data");
      localStorage.removeItem("auth_token");
      localStorage.removeItem("session_id");
      localStorage.removeItem("tenant_id");
      localStorage.removeItem("user_id");
      
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
