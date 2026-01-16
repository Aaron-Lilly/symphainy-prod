/**
 * Foundation Integration Test
 * 
 * Tests the foundation components in a React component tree.
 * Validates that providers work together correctly.
 */

import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { PlatformStateProvider, usePlatformState } from "@/shared/state/PlatformStateProvider";
import { AuthProvider, useAuth } from "@/shared/auth/AuthProvider";
import { ExperiencePlaneClient } from "@/shared/services/ExperiencePlaneClient";
import { ContentAPIManager, useContentAPIManager } from "@/shared/managers/ContentAPIManager";

// Mock ExperiencePlaneClient for testing
jest.mock("@/shared/services/ExperiencePlaneClient", () => ({
  ExperiencePlaneClient: jest.fn(),
  getGlobalExperiencePlaneClient: jest.fn(() => ({
    createSession: jest.fn().mockResolvedValue({
      session_id: "test_session",
      tenant_id: "test_tenant",
      user_id: "test_user",
      created_at: new Date().toISOString(),
    }),
    getSession: jest.fn().mockResolvedValue({
      session_id: "test_session",
      tenant_id: "test_tenant",
      user_id: "test_user",
      created_at: new Date().toISOString(),
    }),
  })),
}));

describe("Foundation Integration", () => {
  // Test component that uses all providers
  const TestComponent: React.FC = () => {
    const platformState = usePlatformState();
    const auth = useAuth();
    const contentManager = useContentAPIManager();

    return (
      <div>
        <div data-testid="platform-state">
          {platformState.state.session.sessionId ? "Session exists" : "No session"}
        </div>
        <div data-testid="auth-state">
          {auth.isAuthenticated ? "Authenticated" : "Not authenticated"}
        </div>
        <div data-testid="content-manager">
          {contentManager ? "ContentAPIManager available" : "ContentAPIManager not available"}
        </div>
      </div>
    );
  };

  it("should provide PlatformStateProvider context", () => {
    render(
      <PlatformStateProvider>
        <TestComponent />
      </PlatformStateProvider>
    );

    expect(screen.getByTestId("platform-state")).toBeInTheDocument();
  });

  it("should provide AuthProvider context", () => {
    render(
      <PlatformStateProvider>
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      </PlatformStateProvider>
    );

    expect(screen.getByTestId("auth-state")).toBeInTheDocument();
  });

  it("should provide ContentAPIManager via hook", () => {
    render(
      <PlatformStateProvider>
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      </PlatformStateProvider>
    );

    expect(screen.getByTestId("content-manager")).toBeInTheDocument();
  });

  it("should create session via PlatformStateProvider", async () => {
    const TestSessionComponent: React.FC = () => {
      const platformState = usePlatformState();
      const [sessionCreated, setSessionCreated] = React.useState(false);

      React.useEffect(() => {
        platformState
          .createSession("test_tenant", "test_user")
          .then(() => setSessionCreated(true))
          .catch(console.error);
      }, []);

      return <div data-testid="session-status">{sessionCreated ? "Session created" : "Creating session..."}</div>;
    };

    render(
      <PlatformStateProvider>
        <TestSessionComponent />
      </PlatformStateProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId("session-status")).toHaveTextContent("Session created");
    });
  });
});
