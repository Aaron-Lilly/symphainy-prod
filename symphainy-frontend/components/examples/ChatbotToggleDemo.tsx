"use client";

import React from 'react';
// ✅ PHASE 5: Use PlatformStateProvider instead of Jotai atoms
import { usePlatformState } from '@/shared/state/PlatformStateProvider';
import { Button } from '@/components/ui/button';

export default function ChatbotToggleDemo() {
  // ✅ PHASE 5: Use PlatformStateProvider instead of Jotai atoms
  const { state, setMainChatbotOpen, getShouldShowSecondaryChatbot, getPrimaryChatbotTransform, getSecondaryChatbotPosition } = usePlatformState();
  const mainChatbotOpen = state.ui.chatbot.mainChatbotOpen;
  
  // Debug info - all derived automatically
  const shouldShowSecondary = getShouldShowSecondaryChatbot();
  const primaryTransform = getPrimaryChatbotTransform();
  const secondaryPosition = getSecondaryChatbotPosition();

  return (
    <div className="fixed top-4 left-4 z-[60] bg-white p-4 rounded-lg shadow-lg border">
      <h3 className="font-semibold mb-3">Chatbot Animation Demo</h3>
      
      <div className="space-y-2 mb-4">
        <div className="text-xs text-gray-600">
          <strong>Current State:</strong> {mainChatbotOpen ? 'Main Only' : 'Main + Secondary'}
        </div>
        <div className="text-xs text-gray-600">
          <strong>Show Secondary:</strong> {shouldShowSecondary ? 'Yes' : 'No'}
        </div>
        <div className="text-xs text-gray-600">
          <strong>Primary Transform:</strong> {primaryTransform}
        </div>
        <div className="text-xs text-gray-600">
          <strong>Secondary Position:</strong> {secondaryPosition}
        </div>
      </div>
      
      <div className="space-y-2">
        <Button 
          onClick={() => setMainChatbotOpen(!mainChatbotOpen)}
          className="w-full"
          size="sm"
        >
          Toggle Chatbots
        </Button>
        
        <div className="flex gap-2">
          <Button 
            onClick={() => setMainChatbotOpen(true)}
            variant={mainChatbotOpen ? "default" : "outline"}
            size="sm"
            className="flex-1"
          >
            Main Only
          </Button>
          
          <Button 
            onClick={() => setMainChatbotOpen(false)}
            variant={!mainChatbotOpen ? "default" : "outline"}
            size="sm"
            className="flex-1"
          >
            Both Visible
          </Button>
        </div>
      </div>
      
      <div className="mt-3 p-2 bg-green-50 rounded text-xs">
        <strong>✅ PHASE 5: PlatformStateProvider Usage:</strong><br/>
        • Use <code>usePlatformState()</code> hook<br/>
        • Access <code>state.ui.chatbot.mainChatbotOpen</code><br/>
        • Call <code>setMainChatbotOpen(true)</code> = Main only<br/>
        • Call <code>setMainChatbotOpen(false)</code> = Both visible<br/>
        • Derived state via <code>getShouldShowSecondaryChatbot()</code> etc.
      </div>
    </div>
  );
} 