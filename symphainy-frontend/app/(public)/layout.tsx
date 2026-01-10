"use client";
import React from "react";

/**
 * Public Routes Layout
 * 
 * For routes that don't need MainLayout (login, register, etc.)
 * No chat panel, no navigation - just the page content
 */
export default function PublicLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
