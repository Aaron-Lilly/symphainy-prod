"use client";

import React, { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
// ✅ PHASE 4: Session-First - Use SessionBoundary for session state
import { useSessionBoundary, SessionStatus } from "@/shared/state/SessionBoundaryProvider";

interface AuthGuardProps {
  children: React.ReactNode;
}

export default function AuthGuard({ children }: AuthGuardProps) {
  const router = useRouter();
  const pathname = usePathname();
  // ✅ PHASE 4: Session-First - Use SessionBoundary for session state
  const { state: sessionState } = useSessionBoundary();
  const [isClient, setIsClient] = useState(false);
  const [authChecked, setAuthChecked] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  useEffect(() => {
    if (!isClient) return;

    // Skip auth check for login page
    if (pathname === "/login") {
      setAuthChecked(true);
      return;
    }

    // ✅ PHASE 4: Session-First - Check SessionStatus instead of isAuthenticated
    if (sessionState.status !== SessionStatus.Active) {
      router.push("/login");
      return;
    }

    setAuthChecked(true);
  }, [isClient, pathname, router, sessionState.status]);

  // Wait for client-side hydration
  if (!isClient) {
    return <>{children}</>;
  }

  // If we're on the login page, show content
  if (pathname === "/login") {
    return <>{children}</>;
  }

  // If auth hasn't been checked yet, show loading or content
  if (!authChecked) {
    return <>{children}</>;
  }

  // ✅ PHASE 4: Session-First - Check SessionStatus instead of isAuthenticated
  if (sessionState.status === SessionStatus.Active) {
    return <>{children}</>;
  }

  // While redirecting, show nothing
  return null;
}
