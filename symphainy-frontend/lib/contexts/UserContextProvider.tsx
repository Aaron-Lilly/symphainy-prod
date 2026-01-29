/**
 * User Context Provider
 * 
 * Legacy provider - now a simple pass-through.
 * User context is managed by:
 * - AuthProvider for user authentication state
 * - SessionBoundaryProvider for session state
 */

"use client";

import React, { ReactNode } from 'react';

interface UserContextProviderProps {
  children: ReactNode;
}

export function UserContextProviderComponent({ children }: UserContextProviderProps) {
  // Pass-through provider - functionality moved to AuthProvider
  return <>{children}</>;
}

export default UserContextProviderComponent;
