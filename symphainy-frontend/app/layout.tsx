"use client";
import "../styles/globals.css";
import React from "react";
import AppProviders from "@/shared/agui/AppProviders";
import { Toaster } from "sonner";

/**
 * Root Layout
 * 
 * Minimal root layout - only provides providers
 * Route-specific layouts handle MainLayout:
 * - (public)/layout.tsx - No MainLayout (login, register)
 * - (protected)/layout.tsx - With MainLayout (landing, pillars, etc.)
 */
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <AppProviders>
          {children}
          <Toaster
            position="top-right"
            expand={false}
            richColors
            closeButton
            visibleToasts={1}
            duration={2000}
          />
        </AppProviders>
      </body>
    </html>
  );
}
