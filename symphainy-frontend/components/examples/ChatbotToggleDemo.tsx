"use client";

import React from 'react';
import { useAtom, useAtomValue } from 'jotai';
import { 
  mainChatbotOpenAtom,
  shouldShowSecondaryChatbotAtom,
  primaryChatbotTransformAtom,
  secondaryChatbotPositionAtom
} from '@/shared/atoms';
import { Button } from '@/components/ui/button';

export default function ChatbotToggleDemo() {
  // 🎯 SINGLE SOURCE OF TRUTH - Only atom you need to use/set
  const [mainChatbotOpen, setMainChatbotOpen] = useAtom(mainChatbotOpenAtom);
  
  // Debug info - all derived automatically
  const shouldShowSecondary = useAtomValue(shouldShowSecondaryChatbotAtom);
  const primaryTransform = useAtomValue(primaryChatbotTransformAtom);
  const secondaryPosition = useAtomValue(secondaryChatbotPositionAtom);

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
        <strong>✅ Simplified Usage:</strong><br/>
        • Only use <code>mainChatbotOpenAtom</code><br/>
        • All other states derive automatically<br/>
        • <code>setMainChatbotOpen(true)</code> = Main only<br/>
        • <code>setMainChatbotOpen(false)</code> = Both visible
      </div>
    </div>
  );
} 