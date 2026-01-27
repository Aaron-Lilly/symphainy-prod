"use client";

import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
// ✅ PHASE 4: Session-First - Use SessionBoundary for session state
import { useSessionBoundary, SessionStatus } from "@/shared/state/SessionBoundaryProvider";

interface AuthRedirectProps {
  redirectTo?: string;
}

export default function AuthRedirect({
  redirectTo = "/login",
}: AuthRedirectProps) {
  const router = useRouter();
  // ✅ PHASE 4: Session-First - Use SessionBoundary for session state
  const { state: sessionState } = useSessionBoundary();
  const isLoading = sessionState.status === SessionStatus.Initializing || sessionState.status === SessionStatus.Authenticating;
  const isAuthenticated = sessionState.status === SessionStatus.Active;

  useEffect(() => {
    // ✅ PHASE 4: Redirect if session is not Active (Invalid, Anonymous, etc.)
    if (!isLoading && sessionState.status !== SessionStatus.Active) {
      router.push(redirectTo);
    }
  }, [sessionState.status, isLoading, router, redirectTo]);

  // Show loading while checking authentication
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return null;
}
