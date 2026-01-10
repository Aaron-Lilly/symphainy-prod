"use client";

import React, { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import Loading from "@/components/ui/loading";

export default function InsightLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [loading, setLoading] = useState(false);
  const [startTime, setStartTime] = useState<number | null>(null);
  const pathname = usePathname();

  useEffect(() => {
    setLoading(true);
    const start = performance.now();
    setStartTime(start);

    const handleDone = () => {
      const duration = performance.now() - start;
      console.log(`⏱️ Page "${pathname}" loaded in ${duration.toFixed(2)}ms`);
      setLoading(false);
    };

    // Mimic async loading delay
    const timeout = setTimeout(handleDone, 500); // simulate a minimum delay (optional)
    return () => clearTimeout(timeout);
  }, [pathname]);

  return <>{loading ? <Loading /> : children}</>;
}
