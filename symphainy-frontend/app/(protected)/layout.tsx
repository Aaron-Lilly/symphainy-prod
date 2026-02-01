"use client";
import React from "react";
import MainLayout from "@/shared/components/MainLayout";
import { TenantProvider } from "@/shared/contexts/TenantContext";

/**
 * Protected Routes Layout
 * 
 * For routes that need MainLayout with chat panel and navigation
 * Includes: landing page (/), /pillars/*, and other authenticated routes
 * TenantProvider wraps everything to provide tenant context throughout
 */
export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <TenantProvider>
      <MainLayout>{children}</MainLayout>
    </TenantProvider>
  );
}
