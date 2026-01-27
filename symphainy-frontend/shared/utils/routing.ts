/**
 * Routing Utilities
 * 
 * Phase 7: Routes reflect journey state, not workflows
 * 
 * Functions to:
 * - Build routes with journey state params
 * - Parse route params to journey state
 * - Sync routes to state
 * - Sync state to routes
 */

import { RealmState } from "@/shared/state/PlatformStateProvider";

// Journey state params that can be encoded in URLs
export interface JourneyStateParams {
  artifact?: string; // Current artifact ID (file, SOP, analysis, etc.)
  step?: string; // Current step in workflow (upload, parse, analyze, etc.)
  view?: string; // Current view mode (list, detail, edit, etc.)
  [key: string]: string | undefined; // Allow additional params
}

// Realm type
export type Realm = "content" | "insights" | "journey" | "outcomes";

/**
 * Build a pillar route with journey state params
 * 
 * @param realm - The realm (content, insights, journey, outcomes)
 * @param params - Journey state params to encode in URL
 * @returns Route path with query params
 * 
 * @example
 * buildPillarRoute("content", { file: "abc123", step: "parse" })
 * // Returns: "/pillars/content?file=abc123&step=parse"
 */
export function buildPillarRoute(realm: Realm, params?: JourneyStateParams): string {
  const basePath = `/pillars/${realm}`;
  
  if (!params || Object.keys(params).length === 0) {
    return basePath;
  }
  
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value) {
      searchParams.append(key, value);
    }
  });
  
  const queryString = searchParams.toString();
  return queryString ? `${basePath}?${queryString}` : basePath;
}

/**
 * Parse route params from URL to journey state
 * 
 * @param pathname - Current pathname
 * @param searchParams - URL search params
 * @returns Parsed journey state params
 * 
 * @example
 * parseRouteParams("/pillars/content", new URLSearchParams("file=abc123&step=parse"))
 * // Returns: { artifact: "abc123", step: "parse" }
 */
export function parseRouteParams(
  pathname: string,
  searchParams: URLSearchParams
): JourneyStateParams {
  const params: JourneyStateParams = {};
  
  // Parse standard journey state params
  const artifact = searchParams.get("artifact") || searchParams.get("file") || searchParams.get("sop") || searchParams.get("analysis");
  if (artifact) params.artifact = artifact;
  
  const step = searchParams.get("step");
  if (step) params.step = step;
  
  const view = searchParams.get("view");
  if (view) params.view = view;
  
  // Parse any additional params
  searchParams.forEach((value, key) => {
    if (!["artifact", "file", "sop", "analysis", "step", "view"].includes(key)) {
      params[key] = value;
    }
  });
  
  return params;
}

/**
 * Extract realm from pathname
 * 
 * @param pathname - Current pathname
 * @returns Realm or null
 * 
 * @example
 * extractRealm("/pillars/content") // Returns: "content"
 * extractRealm("/pillars/journey?step=parse") // Returns: "journey"
 */
export function extractRealm(pathname: string): Realm | null {
  const match = pathname.match(/^\/pillars\/(content|insights|journey|outcomes)/);
  if (match && match[1]) {
    return match[1] as Realm;
  }
  return null;
}

/**
 * Sync route to state
 * 
 * Updates PlatformStateProvider based on current route
 * 
 * @param pathname - Current pathname
 * @param searchParams - URL search params
 * @param setRealmState - Function to set realm state
 * @param setCurrentPillar - Function to set current pillar
 */
export function syncRouteToState(
  pathname: string,
  searchParams: URLSearchParams,
  setRealmState: (realm: Realm, key: string, value: any) => void,
  setCurrentPillar: (pillar: Realm | null) => void
): void {
  // Extract realm from pathname
  const realm = extractRealm(pathname);
  
  if (realm) {
    // Set current pillar
    setCurrentPillar(realm);
    
    // Parse journey state params
    const params = parseRouteParams(pathname, searchParams);
    
    // Sync params to realm state
    if (params.artifact) {
      setRealmState(realm, "currentArtifact", params.artifact);
    }
    if (params.step) {
      setRealmState(realm, "currentStep", params.step);
    }
    if (params.view) {
      setRealmState(realm, "currentView", params.view);
    }
    
    // Store all params in realm state for reference
    setRealmState(realm, "routeParams", params);
  } else if (pathname === "/" || pathname === "/admin") {
    // Main dashboard or platform showcase - no realm
    setCurrentPillar(null);
  }
}

/**
 * Sync state to route
 * 
 * Updates route based on current state
 * 
 * @param realm - Current realm
 * @param realmState - Current realm state
 * @param navigate - Function to navigate to route
 */
export function syncStateToRoute(
  realm: Realm | null,
  realmState: Record<string, any>,
  navigate: (path: string) => void
): void {
  if (!realm) {
    return;
  }
  
  // Build route params from realm state
  const params: JourneyStateParams = {};
  
  if (realmState.currentArtifact) {
    params.artifact = realmState.currentArtifact;
  }
  if (realmState.currentStep) {
    params.step = realmState.currentStep;
  }
  if (realmState.currentView) {
    params.view = realmState.currentView;
  }
  
  // Build and navigate to route
  const route = buildPillarRoute(realm, params);
  navigate(route);
}

/**
 * Check if route is a pillar route
 * 
 * @param pathname - Current pathname
 * @returns True if route is a pillar route
 */
export function isPillarRoute(pathname: string): boolean {
  return /^\/pillars\/(content|insights|journey|outcomes)/.test(pathname);
}

/**
 * Check if route is MVP route
 * 
 * @param pathname - Current pathname
 * @returns True if route is an MVP route
 */
export function isMVPRoute(pathname: string): boolean {
  return (
    pathname === "/" ||
    isPillarRoute(pathname) ||
    pathname === "/admin" ||
    pathname === "/login"
  );
}
