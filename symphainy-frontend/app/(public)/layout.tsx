"use client";
import React from "react";
import { TenantProvider } from "@/shared/contexts/TenantContext";

/**
 * Public Routes Layout
 * 
 * For routes that don't need MainLayout (login, register, etc.)
 * No chat panel, no navigation - just the page content
 * Includes TenantProvider for tenant selection on login page
 */
export default function PublicLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <TenantProvider>
      {children}
    </TenantProvider>
  );
}
