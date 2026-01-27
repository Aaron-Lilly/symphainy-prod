"use client";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import Link from "next/link";
import Image from "next/image";
import { usePathname, useRouter } from "next/navigation";
import React from "react";
import { pillars } from "../data/pillars";
import { AuthStatus } from "@/components/auth";
// ✅ PHASE 7: Routing Refactoring - Update state first, then routes
import { usePlatformState } from "@/shared/state/PlatformStateProvider";
import { buildPillarRoute, extractRealm } from "@/shared/utils/routing";

export default function TopNavBar() {
  const pathname = usePathname();
  const router = useRouter();
  // ✅ PHASE 7: Routing Refactoring - Get state management functions
  const { setCurrentPillar, getRealmState } = usePlatformState();
  
  // Map pillar names to semantic test IDs
  const getPillarTestId = (pillarName: string) => {
    const mapping: Record<string, string> = {
      "Content": "navigate-to-content-pillar",
      "Insights": "navigate-to-insights-pillar",
      "Operations": "navigate-to-operations-pillar",
      "Business Outcomes": "navigate-to-business-outcomes-pillar",
    };
    return mapping[pillarName] || `navigate-to-${pillarName.toLowerCase().replace(/\s+/g, "-")}-pillar`;
  };
  
  // ✅ PHASE 7: Routing Refactoring - Handle navigation with state update first
  const handlePillarNavigation = (realm: "content" | "insights" | "journey" | "outcomes", href: string) => {
    // Update state first
    setCurrentPillar(realm);
    
    // Get current realm state to preserve journey state
    const realmState = getRealmState(realm, "routeParams") || {};
    
    // Build route with journey state params
    const route = buildPillarRoute(realm, realmState);
    
    // Navigate to route
    router.push(route);
  };

  return (
    <nav 
      data-testid="pillar-navigation"
      className="fixed top-0 left-0 right-0 bg-white border-b border-gray-200 shadow-sm h-20 z-20 flex items-center"
    >
      <div className="w-full pl-8 pr-8 h-20 flex items-center justify-space-between">
        {/* Left side: Logo and Pillar Navigation */}
        <div className="flex items-center flex-1 gap-2">
          {/* Logo */}
          <div className="flex-shrink-0 flex items-center">
            <Image
              src="/logo.png"
              alt="SymphAIny"
              width={56}
              height={56}
              className="h-14 w-auto object-contain"
              priority
            />
          </div>
          {/* Pillar Navigation using ShadCN Tabs */}
          <Tabs defaultValue={pathname} className="flex">
            <TabsList className="flex w-full justify-space-evenly items-center bg-transparent shadow-none border-none gap-6">
              {pillars.map((pillar) => {
                // ✅ PHASE 7: Extract realm from href for state management
                const realm = extractRealm(pillar.href) as "content" | "insights" | "journey" | "outcomes" | null;
                const isActive = pathname.startsWith(pillar.href);
                
                return (
                  <TabsTrigger
                    key={pillar.name}
                    value={pillar.href}
                    asChild
                    className="p-0 bg-transparent border-none shadow-none"
                  >
                    {realm ? (
                      // ✅ PHASE 7: Use state-first navigation for pillar routes
                      <a
                        href={pillar.href}
                        onClick={(e) => {
                          e.preventDefault();
                          handlePillarNavigation(realm, pillar.href);
                        }}
                        data-testid={getPillarTestId(pillar.name)}
                        aria-label={`Navigate to ${pillar.name} Pillar`}
                        className={`group flex items-center px-3 py-2 rounded-xl transition-all border cursor-pointer ${
                          isActive
                            ? "border-gray-300 bg-gray-50 shadow-sm"
                            : "border-gray-200 bg-white hover:bg-gray-50 hover:border-gray-300 hover:shadow-sm"
                        }`}
                      >
                        <span
                          className={`w-10 h-10 rounded-lg ${pillar.color} text-white flex items-center justify-center mr-3`}
                        >
                          <pillar.icon className="w-5 h-5" />
                        </span>
                        <span>
                          <span
                            className={`block text-sm font-semibold transition-colors ${
                              isActive
                                ? "text-gray-900"
                                : "text-gray-700 group-hover:text-[#007A87]"
                            }`}
                          >
                            {pillar.name}
                          </span>
                          <span className="block text-xs text-gray-600 mt-0.5">
                            {pillar.description}
                          </span>
                        </span>
                      </a>
                    ) : (
                      // Fallback to regular Link for non-pillar routes
                      <Link
                        href={pillar.href}
                        passHref
                        legacyBehavior
                        className={`border ${isActive ? "border-gray-300 bg-gray-50 shadow-sm" : "border-gray-200 bg-white hover:bg-gray-50 hover:border-gray-300 hover:shadow-sm"}`}
                      >
                        <a
                          data-testid={getPillarTestId(pillar.name)}
                          aria-label={`Navigate to ${pillar.name} Pillar`}
                          className={`group flex items-center px-3 py-2 rounded-xl transition-all border ${
                            isActive
                              ? "border-gray-300 bg-gray-50 shadow-sm"
                              : "border-gray-200 bg-white hover:bg-gray-50 hover:border-gray-300 hover:shadow-sm"
                          }`}
                        >
                          <span
                            className={`w-10 h-10 rounded-lg ${pillar.color} text-white flex items-center justify-center mr-3`}
                          >
                            <pillar.icon className="w-5 h-5" />
                          </span>
                          <span>
                            <span
                              className={`block text-sm font-semibold transition-colors ${
                                isActive
                                  ? "text-gray-900"
                                  : "text-gray-700 group-hover:text-[#007A87]"
                              }`}
                            >
                              {pillar.name}
                            </span>
                            <span className="block text-xs text-gray-600 mt-0.5">
                              {pillar.description}
                            </span>
                          </span>
                        </a>
                      </Link>
                    )}
                  </TabsTrigger>
                );
              })}
            </TabsList>
          </Tabs>
        </div>
      </div>
      <div className="flex-shrink-0 pr-8">
        <AuthStatus />
      </div>
    </nav>
  );
}
