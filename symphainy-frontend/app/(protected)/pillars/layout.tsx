"use client";
import React from "react";
import MainLayout from "@/shared/components/MainLayout";
import AuthRedirect from "@/components/auth/auth-redirect";

// Force dynamic rendering to avoid SSR issues
export const dynamic = 'force-dynamic';

export default function PillarsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <AuthRedirect />
      <MainLayout>{children}</MainLayout>
    </>
  );
}
