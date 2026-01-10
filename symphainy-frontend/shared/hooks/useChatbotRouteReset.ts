"use client";

import React, { useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { useSetAtom } from 'jotai';
import { mainChatbotOpenAtom } from '@/shared/atoms';

/**
 * Automatically resets chatbot state when navigating between routes
 * 
 * Usage: Add this hook to your main layout component
 * 
 * @example
 * ```tsx
 * export default function MainLayout() {
 *   useChatbotRouteReset(); // ✅ Resets on any route change
 *   return <div>{children}</div>;
 * }
 * ```
 */
export function useChatbotRouteReset() {
  const pathname = usePathname();
  const setMainChatbotOpen = useSetAtom(mainChatbotOpenAtom);

  useEffect(() => {
    // Reset chatbot to initial state on route change
    setMainChatbotOpen(true);
  }, [pathname, setMainChatbotOpen]);
} 