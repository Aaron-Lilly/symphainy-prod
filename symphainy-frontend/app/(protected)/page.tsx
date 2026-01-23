"use client";
import React from "react";
import { WelcomeJourney } from "@/components/landing/WelcomeJourney";
import { useRouter } from "next/navigation";
import AuthRedirect from "@/components/auth/auth-redirect";

// Force dynamic rendering to avoid SSR issues with providers
export const dynamic = 'force-dynamic';

export default function HomePage() {
  const router = useRouter();

  const handleWelcomeComplete = () => {
    // Navigate directly to content pillar
    router.push("/pillars/content");
  };

  return (
    <>
      <AuthRedirect />
      <WelcomeJourney handleWelcomeComplete={handleWelcomeComplete} />
    </>
  );
}
