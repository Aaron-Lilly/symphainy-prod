"use client";

import React, { useState, useEffect } from "react";
import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import dynamic from "next/dynamic";
import ChatPanelUI from "./chatbot/ChatPanelUI";
import SecondaryChatPanelUI from "./chatbot/SecondaryChatPanelUI";

const InteractiveChat = dynamic(() => import("./chatbot/InteractiveChat"), {
  ssr: false,
  loading: () => <div className="w-full h-full bg-gray-100 animate-pulse" />
});

const InteractiveSecondaryChat = dynamic(() => import("./chatbot/InteractiveSecondaryChat"), {
  ssr: false,
  loading: () => <div className="w-full h-full bg-gray-100 animate-pulse" />
});
import { FileText, BarChart2, Settings, FlaskConical } from "lucide-react";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import TopNavBar from "./TopNavBar";
import ChatbotToggleDemo from "@/components/examples/ChatbotToggleDemo";
// ✅ PHASE 1: Removed Jotai atoms - using PlatformStateProvider instead
import { useChatbotRouteReset } from "@/shared/hooks/useChatbotRouteReset";
// ✅ PHASE 4: Session-First - Use SessionBoundary instead of AuthProvider for session state
import { useSessionBoundary, SessionStatus } from "@/shared/state/SessionBoundaryProvider";
import { usePlatformState } from "@/shared/state/PlatformStateProvider";

interface MainLayoutProps {
  children: React.ReactNode;
}

export default function MainLayout({ children }: MainLayoutProps) {
  // ✅ ONE line - automatically resets chatbot on route changes
  useChatbotRouteReset();
  
  // ✅ PHASE 4: Session-First - Use SessionBoundary for session state
  const { state: sessionState } = useSessionBoundary();
  const { state, getShouldShowSecondaryChatbot, getPrimaryChatbotHeight, getSecondaryChatbotPosition, getPrimaryChatbotTransform } = usePlatformState();
  
  // ✅ PHASE 5: Get chatbot state from PlatformStateProvider (replaces Jotai atoms)
  const mainChatbotOpen = state.ui.chatbot.mainChatbotOpen;
  const shouldShowSecondaryChatbot = getShouldShowSecondaryChatbot();
  const primaryChatbotHeight = getPrimaryChatbotHeight();
  const secondaryChatbotPosition = getSecondaryChatbotPosition();
  const primaryChatbotTransform = getPrimaryChatbotTransform();
  
  // Get session token from SessionBoundary
  const guideSessionToken = sessionState.sessionId;
  
  // ✅ PHASE 4: Session-First - Map SessionStatus to auth-like flags for compatibility
  const isAuthenticated = sessionState.status === SessionStatus.Active;
  const authLoading = sessionState.status === SessionStatus.Initializing || sessionState.status === SessionStatus.Authenticating;
  
  // Get current route to highlight the active tab
  const pathname = usePathname();
  
  // ✅ CRITICAL: Exclude ONLY authentication routes from chat panel rendering
  // Landing page (/) SHOULD have chat capabilities for guide agent showcase
  // Only exclude routes where authentication is not yet complete
  const authRoutes = ['/login', '/register'];
  const isAuthRoute = authRoutes.includes(pathname);
  
  // ✅ CRITICAL: Verify that both access_token and session_id exist
  // ✅ SESSION BOUNDARY PATTERN: Get tokens from SessionBoundaryProvider, not sessionStorage
  // access_token is for authentication, session_id is for session state
  const accessToken = sessionState.userId ? (typeof window !== 'undefined' ? sessionStorage.getItem("access_token") : null) : null;
  const sessionId = sessionState.sessionId;
  // Both tokens must exist and match what we have
  const tokenMatches = accessToken && sessionId && guideSessionToken === sessionId;
  
  // ✅ STRICT AUTH CHECK: Only render chat when:
  // 1. NOT on authentication routes (/login, /register) - landing page (/) is allowed
  // 2. Auth is not loading
  // 3. User is authenticated
  // 4. Valid session token exists (not empty, not placeholder)
  // 5. Token is a valid string (not just truthy)
  // 6. Token matches auth token (prevents using wrong token)
  // 7. Add small delay to ensure auth state is fully settled (prevents race conditions)
  const [authReady, setAuthReady] = useState(false);
  
  useEffect(() => {
    // ✅ PHASE 4: Session-First - Wait for SessionStatus === Active
    // Small delay to ensure session state is fully settled before allowing chat to render
    // This prevents race conditions where components mount before token is ready
    if (!authLoading && sessionState.status === SessionStatus.Active && guideSessionToken && tokenMatches) {
      const timer = setTimeout(() => {
        setAuthReady(true);
      }, 100); // 100ms delay to ensure state is settled
      return () => clearTimeout(timer);
    } else {
      setAuthReady(false);
    }
  }, [authLoading, sessionState.status, guideSessionToken, tokenMatches]);
  
  // ✅ PHASE 1.1: Platform Capability Showcase - Make chat panel always visible by default
  // Chat panel should be prominent to showcase multi-agent collaboration
  // Still persist in sessionStorage so it survives page refreshes
  const [chatPanelRequested, setChatPanelRequested] = useState(() => {
    if (typeof window !== 'undefined') {
      // Check if user has explicitly closed it, otherwise default to open
      const explicitlyClosed = sessionStorage.getItem('chatPanelExplicitlyClosed') === 'true';
      return !explicitlyClosed; // Default to open unless explicitly closed
    }
    return true; // Default to open
  });
  
  // Update sessionStorage when chat panel is requested
  useEffect(() => {
    if (typeof window !== 'undefined') {
      if (chatPanelRequested) {
        sessionStorage.setItem('chatPanelRequested', 'true');
      } else {
        sessionStorage.removeItem('chatPanelRequested');
      }
    }
  }, [chatPanelRequested]);
  
  // ✅ PHASE 4: Session-First - Reset chat panel when session becomes Invalid or Anonymous
  useEffect(() => {
    if (typeof window !== 'undefined' && 
        (sessionState.status === SessionStatus.Invalid || 
         sessionState.status === SessionStatus.Anonymous) && 
        !authLoading) {
      // Session invalidated or user logged out - reset chat panel to default (open)
      setChatPanelRequested(true);
      sessionStorage.removeItem('chatPanelExplicitlyClosed');
    }
  }, [sessionState.status, authLoading]);
  
  // Debug: Log auth state for troubleshooting button visibility
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      console.log('[MainLayout] Auth state:', {
        isAuthRoute,
        authLoading,
        sessionStatus: sessionState.status, // ✅ PHASE 4: Log SessionStatus instead of isAuthenticated
        isAuthenticated: sessionState.status === SessionStatus.Active,
        hasToken: !!guideSessionToken,
        tokenLength: guideSessionToken?.length || 0,
        tokenMatches,
        authReady,
        chatPanelRequested
      });
    }
  }, [isAuthRoute, authLoading, sessionState.status, guideSessionToken, tokenMatches, authReady, chatPanelRequested]);
  
  // ✅ PHASE 4: Session-First - Only render chat when SessionStatus === Active
  const shouldRenderChat = 
    !isAuthRoute && // ✅ CRITICAL: Never render on auth routes, but allow landing page
    !authLoading && 
    sessionState.status === SessionStatus.Active && // ✅ PHASE 4: Use SessionStatus instead of isAuthenticated
    guideSessionToken && 
    typeof guideSessionToken === 'string' &&
    guideSessionToken.trim() !== '' && 
    guideSessionToken !== 'token_placeholder' &&
    guideSessionToken.length > 10 && // Ensure token is substantial (not just a few chars)
    tokenMatches && // ✅ CRITICAL: Token must match auth token
    authReady && // ✅ CRITICAL: Wait for auth state to settle
    chatPanelRequested; // ✅ LAZY LOADING: Only render when user requests it
  
  // ✅ PHASE 5: Get derived chatbot state from PlatformStateProvider (replaces Jotai atoms)
  const showSecondary = shouldShowSecondaryChatbot;
  const primaryTransform = primaryChatbotTransform;
  const secondaryPosition = secondaryChatbotPosition;
  const primaryHeight = primaryChatbotHeight;

  return (
    <div className="flex min-h-screen min-w-screen overflow-hidden bg-white">
      <TopNavBar />
      <div className="flex-1 flex flex-col min-w-0">
        {/* Main Content */}
        <div className="flex flex-row bg-gray-100 overflow-y-auto gap-6 p-4 md:p-8 mt-20">
          <div className="w-[72%] bg-gray-100">{children}</div>
          <div className="w-[23%] bg-gray-100">
            {/* ✅ LAZY LOADING: Show launch button if chat not requested, otherwise show chat panel */}
            {/* Debug: Log button visibility conditions - Always log for troubleshooting */}
            {/* ✅ PHASE 1.1: Chat panel is now always visible by default, so launch button is no longer needed */}
            {/* Keeping this section empty for now - chat panel renders directly when shouldRenderChat is true */}
          </div>
        </div>
      </div>
      {/* Chatbot Container with Animations - Only render when fully authenticated with valid token */}
      {shouldRenderChat && (
        <div className="fixed bottom-0 right-0 z-50">

          {/* Secondary Chatbot - Slides in from right when main is closed */}
          <div 
            className={`
              absolute bottom-0 right-0
              transition-all duration-300 ease-in-out
              ${secondaryPosition}
              ${showSecondary ? 'z-50' : 'z-30 pointer-events-none opacity-0'}
            `}
            style={{
              transform: `${secondaryPosition}`,
            }}
          >
            <div className="h-[87vh] w-[24vw] min-w-[330px] max-w-[400px]">
              <SecondaryChatPanelUI>
                <InteractiveSecondaryChat />
              </SecondaryChatPanelUI>
            </div>
          </div>

          {/* Primary Chatbot - Always present, slides down when secondary shows */}
          <div 
            className={`
              bottom-0 right-0
              transition-all duration-300 ease-in-out
              ${primaryTransform}
              ${mainChatbotOpen ? 'z-50' : 'z-40 pointer-events-none opacity-40'}
            `}
            style={{
              transform: `${primaryTransform}`,
            }}
          >
            <div className={`${primaryHeight} w-[24vw] min-w-[330px] max-w-[400px]`}>
              <ChatPanelUI>
                <InteractiveChat />
              </ChatPanelUI>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
