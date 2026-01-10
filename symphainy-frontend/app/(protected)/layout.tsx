"use client";
import React from "react";
import MainLayout from "@/shared/components/MainLayout";

/**
 * Protected Routes Layout
 * 
 * For routes that need MainLayout with chat panel and navigation
 * Includes: landing page (/), /pillars/*, and other authenticated routes
 */
export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <MainLayout>{children}</MainLayout>;
}
