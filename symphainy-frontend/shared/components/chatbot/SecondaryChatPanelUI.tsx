/**
 * Secondary Chat Panel UI
 * 
 * Static UI component for the secondary chat panel (liaison agents) that doesn't include 
 * any interactive functionality. This prevents SSR issues while maintaining the visual layout.
 */

"use client";

import React from "react";
import { Button } from "@/components/ui/button";
// ✅ PHASE 5: Use PlatformStateProvider instead of Jotai atoms
import { usePlatformState } from "@/shared/state/PlatformStateProvider";

interface SecondaryChatPanelUIProps {
  children?: React.ReactNode;
}

export default function SecondaryChatPanelUI({ children }: SecondaryChatPanelUIProps) {
  // ✅ PHASE 5: Use PlatformStateProvider instead of Jotai atoms
  const { state, setMainChatbotOpen } = usePlatformState();
  const mainChatbotOpen = state.ui.chatbot.mainChatbotOpen;
  const agentInfo = state.ui.chatbot.agentInfo;

  // ✅ PHASE 1.2: Display which Liaison Agent is active
  const liaisonAgentTitle = agentInfo.title || "Liaison Agent";
  const liaisonAgentType = agentInfo.agent || "liaison";

  return (
    <div className="w-full h-full bg-[#f3f6f8] border-l rounded-t-lg rounded-r-none border-[#e5eaed] flex flex-col">
      {/* Header */}
      <div className="h-[4.5rem] border-b rounded-t-lg rounded-r-none border-[#e5eaed] bg-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 pl-6 pt-3">
            <h2 className="text-md text-gray-900 font-semibold">
              <span className="gradient-chatbot">{liaisonAgentTitle}</span>
            </h2>
            {/* ✅ PHASE 1.1: Agent activity indicator */}
            <span className="flex h-2 w-2 rounded-full bg-blue-500 animate-pulse" title={`${liaisonAgentTitle} active`} />
          </div>
          <div className="pr-4 pt-3">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setMainChatbotOpen(!mainChatbotOpen)}
              className="text-xs"
              title="Toggle between Guide Agent and Liaison Agent"
            >
              {mainChatbotOpen ? "Switch to Liaison" : "Switch to Guide"}
            </Button>
          </div>
        </div>
        {/* ✅ PHASE 1.2: Show Liaison Agent domain expertise */}
        {agentInfo.additional_info && (
          <div className="px-6 pb-2">
            <p className="text-xs text-gray-600">{agentInfo.additional_info}</p>
          </div>
        )}
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





























