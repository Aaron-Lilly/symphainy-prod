/**
 * Experience Layer Provider
 * 
 * Legacy provider - now a simple pass-through.
 * Experience layer functionality has been moved to specialized providers:
 * - GuideAgentProvider for agent interactions
 * - SessionBoundaryProvider for session management
 * - PlatformStateProvider for platform state
 */

"use client";

import React, { ReactNode } from 'react';

interface ExperienceLayerProviderProps {
  children: ReactNode;
}

export function ExperienceLayerProvider({ children }: ExperienceLayerProviderProps) {
  // Pass-through provider - functionality moved to specialized providers
  return <>{children}</>;
}

export default ExperienceLayerProvider;
