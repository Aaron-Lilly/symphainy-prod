"use client";
import React, { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { CardData } from "@/shared/types";
// Individual card component - Smaller size for chatbot
export default function AnimatedCard({
  card,
  isHighlighted,
}: {
  card: CardData;
  isHighlighted: boolean;
}) {
  return (
    <div
      className={`absolute transition-all duration-300 ${isHighlighted ? "scale-105 z-10" : "scale-100 z-0"}`}
      style={{ left: card.x, top: card.y }}
    >
      <Card
        className={`w-32 h-12 cursor-pointer transition-all duration-300 flex items-center justify-center ${
          isHighlighted
            ? "border-[#007A87] bg-blue-50 shadow-lg"
            : "border-gray-300 bg-white shadow-sm"
        }`}
      >
        <CardContent className="pt-4 flex items-center justify-center h-full">
          <p className="text-xs font-medium text-center text-gray-700 leading-tight">
            {card.text}
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
