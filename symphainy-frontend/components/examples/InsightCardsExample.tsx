"use client";

import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { 
  insightCards, 
  getInsightCardById, 
  getInsightCardTitles,
  INSIGHT_CARD_IDS,
  type InsightCard,
  type InsightCardId 
} from "@/shared/types/insights";

// Example 1: Render all insight cards
export function InsightCardsGrid() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {insightCards.map((card) => {
        const IconComponent = card.icon;
        return (
          <Card key={card.id} className="cursor-pointer hover:shadow-lg transition-shadow">
            <CardHeader className="flex flex-row items-center space-y-0 pb-2">
              <IconComponent className="h-5 w-5 text-blue-600" />
              <CardTitle className="ml-2 text-sm font-medium">{card.title}</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription className="text-xs">{card.description}</CardDescription>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}

// Example 2: Single insight card component
export function InsightCardComponent({ cardId }: { cardId: InsightCardId }) {
  const card = getInsightCardById(cardId);
  
  if (!card) return <div>Card not found</div>;
  
  const IconComponent = card.icon;
  
  return (
    <div className="flex items-center space-x-3 p-4 border rounded-lg">
      <IconComponent className="h-6 w-6 text-blue-500" />
      <div>
        <h3 className="font-semibold">{card.title}</h3>
        <p className="text-sm text-gray-600">{card.description}</p>
      </div>
    </div>
  );
}

// Example 3: Dropdown/Select with insight options
export function InsightSelector({ onSelect }: { onSelect: (card: InsightCard) => void }) {
  return (
    <select 
      className="w-full p-2 border rounded-md"
      onChange={(e) => {
        const card = getInsightCardById(e.target.value);
        if (card) onSelect(card);
      }}
    >
      <option value="">Select an insight type...</option>
      {insightCards.map((card) => (
        <option key={card.id} value={card.id}>
          {card.title}
        </option>
      ))}
    </select>
  );
}

// Example 4: Using constants for specific cards
export function AnomalyDetectionCard() {
  const card = getInsightCardById(INSIGHT_CARD_IDS.ANOMALY);
  if (!card) return null;
  
  const IconComponent = card.icon;
  
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
      <div className="flex items-center">
        <IconComponent className="h-5 w-5 text-red-600 mr-2" />
        <span className="font-medium text-red-800">{card.title}</span>
      </div>
      <p className="text-red-600 text-sm mt-1">{card.description}</p>
    </div>
  );
}

// Example 5: Get all titles for other uses
export function InsightTitlesList() {
  const titles = getInsightCardTitles();
  
  return (
    <ul className="list-disc list-inside space-y-1">
      {titles.map((title, index) => (
        <li key={index} className="text-sm text-gray-700">{title}</li>
      ))}
    </ul>
  );
} 