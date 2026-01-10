/**
 * Secondary Chat Panel UI
 * 
 * Static UI component for the secondary chat panel (liaison agents) that doesn't include 
 * any interactive functionality. This prevents SSR issues while maintaining the visual layout.
 */

"use client";

import React from "react";
import { Button } from "@/components/ui/button";
import { useAtomValue, useSetAtom } from "jotai";
import { mainChatbotOpenAtom } from "@/shared/atoms/chatbot-atoms";

interface SecondaryChatPanelUIProps {
  children?: React.ReactNode;
}

export default function SecondaryChatPanelUI({ children }: SecondaryChatPanelUIProps) {
  const mainChatbotOpen = useAtomValue(mainChatbotOpenAtom);
  const setMainChatbotOpen = useSetAtom(mainChatbotOpenAtom);

  return (
    <div className="w-full h-full bg-[#f3f6f8] border-l rounded-t-lg rounded-r-none border-[#e5eaed] flex flex-col">
      {/* Header */}
      <div className="h-[4.5rem] border-b rounded-t-lg rounded-r-none border-[#e5eaed] bg-white">
        <div className="flex items-center justify-between">
          <h2 className="text-md text-gray-900 font-semibold pl-6 pt-3">
            <span className="gradient-chatbot">Liaison Assistant</span>
          </h2>
          <div className="pr-4 pt-3">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setMainChatbotOpen(!mainChatbotOpen)}
              className="text-xs"
            >
              {mainChatbotOpen ? "Switch to Liaison" : "Switch to Guide Agent"}
            </Button>
          </div>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-hidden">
        {children || (
          <div className="flex items-center justify-center h-full text-gray-500 text-sm">
            Specialist chat functionality loading...
          </div>
        )}
      </div>
    </div>
  );
}





























