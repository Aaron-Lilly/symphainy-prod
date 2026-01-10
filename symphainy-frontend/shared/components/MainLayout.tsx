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
import { 
  mainChatbotOpenAtom,
  shouldShowSecondaryChatbotAtom,
  primaryChatbotTransformAtom,
  secondaryChatbotPositionAtom,
  primaryChatbotHeightAtom
} from "../atoms";
import { useAtomValue } from "jotai";
import { useChatbotRouteReset } from "@/shared/hooks/useChatbotRouteReset";
import { useAuth } from "@/shared/agui/AuthProvider";
import { useGlobalSession } from "@/shared/agui/GlobalSessionProvider";

interface MainLayoutProps {
  children: React.ReactNode;
}

export default function MainLayout({ children }: MainLayoutProps) {
  // ✅ ONE line - automatically resets chatbot on route changes
  useChatbotRouteReset();
  
  // ✅ Check authentication status - only render chat panel when authenticated
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { guideSessionToken } = useGlobalSession();
  
  // Get current route to highlight the active tab
  const pathname = usePathname();
  
  // ✅ CRITICAL: Exclude ONLY authentication routes from chat panel rendering
  // Landing page (/) SHOULD have chat capabilities for guide agent showcase
  // Only exclude routes where authentication is not yet complete
  const authRoutes = ['/login', '/register'];
  const isAuthRoute = authRoutes.includes(pathname);
  
  // ✅ CRITICAL: Verify that guideSessionToken matches auth_token
  // This prevents rendering chat with an invalid or mismatched token
  const authToken = typeof window !== 'undefined' ? localStorage.getItem("auth_token") : null;
  const tokenMatches = authToken && guideSessionToken && authToken === guideSessionToken;
  
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
    // Small delay to ensure auth state is fully settled before allowing chat to render
    // This prevents race conditions where components mount before token is ready
    if (!authLoading && isAuthenticated && guideSessionToken && tokenMatches) {
      const timer = setTimeout(() => {
        setAuthReady(true);
      }, 100); // 100ms delay to ensure state is settled
      return () => clearTimeout(timer);
    } else {
      setAuthReady(false);
    }
  }, [authLoading, isAuthenticated, guideSessionToken, tokenMatches]);
  
  // ✅ LAZY LOADING: State to control when chat panel should be loaded
  // Persist in sessionStorage so it survives page refreshes
  const [chatPanelRequested, setChatPanelRequested] = useState(() => {
    if (typeof window !== 'undefined') {
      return sessionStorage.getItem('chatPanelRequested') === 'true';
    }
    return false;
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
  
  // ✅ Clear chatPanelRequested when user logs out (isAuthenticated becomes false)
  useEffect(() => {
    if (typeof window !== 'undefined' && !isAuthenticated && !authLoading) {
      // User logged out - clear chat panel state
      setChatPanelRequested(false);
      sessionStorage.removeItem('chatPanelRequested');
    }
  }, [isAuthenticated, authLoading]);
  
  // Debug: Log auth state for troubleshooting button visibility
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      console.log('[MainLayout] Auth state:', {
        isAuthRoute,
        authLoading,
        isAuthenticated,
        hasToken: !!guideSessionToken,
        tokenLength: guideSessionToken?.length || 0,
        tokenMatches,
        authReady,
        chatPanelRequested
      });
    }
  }, [isAuthRoute, authLoading, isAuthenticated, guideSessionToken, tokenMatches, authReady, chatPanelRequested]);
  
  const shouldRenderChat = 
    !isAuthRoute && // ✅ CRITICAL: Never render on auth routes, but allow landing page
    !authLoading && 
    isAuthenticated && 
    guideSessionToken && 
    typeof guideSessionToken === 'string' &&
    guideSessionToken.trim() !== '' && 
    guideSessionToken !== 'token_placeholder' &&
    guideSessionToken.length > 10 && // Ensure token is substantial (not just a few chars)
    tokenMatches && // ✅ CRITICAL: Token must match auth token
    authReady && // ✅ CRITICAL: Wait for auth state to settle
    chatPanelRequested; // ✅ LAZY LOADING: Only render when user requests it
  const mainChatbotOpen = useAtomValue(mainChatbotOpenAtom);
  
  // Get derived atoms for animations
  const showSecondary = useAtomValue(shouldShowSecondaryChatbotAtom);
  const primaryTransform = useAtomValue(primaryChatbotTransformAtom);
  const secondaryPosition = useAtomValue(secondaryChatbotPositionAtom);
  const primaryHeight = useAtomValue(primaryChatbotHeightAtom);

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
            {(() => {
              const canShowButton = !isAuthRoute && !authLoading && isAuthenticated && guideSessionToken && tokenMatches && authReady && !chatPanelRequested;
              // Always log for troubleshooting (not just in development)
              console.log('[MainLayout] Button visibility check:', {
                isAuthRoute,
                authLoading,
                isAuthenticated,
                hasToken: !!guideSessionToken,
                tokenLength: guideSessionToken?.length || 0,
                tokenMatches,
                authReady,
                chatPanelRequested,
                canShowButton,
                pathname
              });
              return canShowButton;
            })() && (
              <div className="sticky top-24 h-fit">
                <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-6">
                  <div className="flex flex-col items-center space-y-4">
                    <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
                      <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                      </svg>
                    </div>
                    <div className="text-center">
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">Chat Experience</h3>
                      <p className="text-sm text-gray-600 mb-4">
                        Connect with our AI guide and liaison agents for assistance
                      </p>
                      <Button
                        onClick={() => setChatPanelRequested(true)}
                        className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                        size="lg"
                      >
                        Launch Chat Experience
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            )}
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
