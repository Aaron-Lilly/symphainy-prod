"use client";
import { useRouter } from "next/navigation";
import React, { useEffect } from "react";

// Force dynamic rendering to avoid SSR issues
export const dynamic = 'force-dynamic';

export default function PillarsPage() {
  const router = useRouter();
  
  useEffect(() => {
    router.push("/pillars/content");
  }, [router]);
  
  return <div>Redirecting...</div>;
}
