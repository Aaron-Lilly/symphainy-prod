"use client";

import React, { useState } from "react";
import { useSetAtom } from "jotai";
import { chatbotAgentInfoAtom } from "@/shared/atoms/chatbot-atoms";
import { 
  insightCards, 
  getInsightCardById, 
  INSIGHT_CARD_IDS,
  type InsightCard 
} from "@/shared/types/insights";

// Example: Agent selection for secondary chatbot
export function InsightAgentSelector({ 
  fileUrl, 
  onAgentSelect 
}: { 
  fileUrl: string;
  onAgentSelect?: (agent: InsightCard) => void;
}) {
  const setChatbotAgentInfo = useSetAtom(chatbotAgentInfoAtom);
  
  const handleAgentSelect = (card: InsightCard) => {
    // Set the chatbot agent info atom
    setChatbotAgentInfo({
      agent: card.id, // Maps to your SecondaryChatbotAgent enum
      title: card.title,
      file_url: fileUrl,
      additional_info: card.description || "",
    });
    
    // Optional callback
    onAgentSelect?.(card);
  };

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Select Analysis Type</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {insightCards.map((card) => {
          const IconComponent = card.icon;
          return (
            <button
              key={card.id}
              onClick={() => handleAgentSelect(card)}
              className="flex items-start space-x-3 p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors text-left"
            >
              <IconComponent className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
              <div>
                <h4 className="font-medium text-gray-900">{card.title}</h4>
                <p className="text-sm text-gray-600 mt-1">{card.description}</p>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}

// Example: Quick action buttons for specific insights
export function QuickInsightActions({ fileUrl }: { fileUrl: string }) {
  const setChatbotAgentInfo = useSetAtom(chatbotAgentInfoAtom);
  
  const runAnalysis = (cardId: string) => {
    const card = getInsightCardById(cardId);
    if (!card) return;
    
    setChatbotAgentInfo({
      agent: card.id,
      title: card.title,
      file_url: fileUrl,
      additional_info: card.description || "",
    });
  };

  return (
    <div className="flex flex-wrap gap-2">
      <button 
        onClick={() => runAnalysis(INSIGHT_CARD_IDS.BUSINESS)}
        className="px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600"
      >
        Business Analysis
      </button>
      <button 
        onClick={() => runAnalysis(INSIGHT_CARD_IDS.ANOMALY)}
        className="px-3 py-1 bg-red-500 text-white rounded text-sm hover:bg-red-600"
      >
        Detect Anomalies
      </button>
      <button 
        onClick={() => runAnalysis(INSIGHT_CARD_IDS.EDA)}
        className="px-3 py-1 bg-green-500 text-white rounded text-sm hover:bg-green-600"
      >
        EDA Analysis
      </button>
      <button 
        onClick={() => runAnalysis(INSIGHT_CARD_IDS.VISUALIZATION)}
        className="px-3 py-1 bg-purple-500 text-white rounded text-sm hover:bg-purple-600"
      >
        Create Visualizations
      </button>
    </div>
  );
}

// Example: Current agent display
export function CurrentAgentDisplay({ agentId }: { agentId: string }) {
  const card = getInsightCardById(agentId);
  
  if (!card) return <div className="text-gray-500">No agent selected</div>;
  
  const IconComponent = card.icon;
  
  return (
    <div className="flex items-center space-x-2 bg-gray-100 rounded-lg p-3">
      <IconComponent className="h-4 w-4 text-gray-600" />
      <span className="text-sm font-medium text-gray-800">
        Active: {card.title}
      </span>
    </div>
  );
} 