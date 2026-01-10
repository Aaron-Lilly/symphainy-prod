"use client";

import React, { useState, useEffect } from "react";
import { ConnectionData } from "@/shared/types";
import AnimatedCard from "./animated-card";
import AnimatedEdge from "./animated-edge";

// Sample data - Vertical flow for chatbot with better spacing
const sampleData: ConnectionData = {
  cards: [
    { id: "1", text: "User Input", x: 75, y: 25 },
    { id: "2", text: "Process Query", x: 75, y: 105 },
    { id: "3", text: "Analyze Data", x: 75, y: 185 },
    { id: "4", text: "Generate Response", x: 75, y: 265 },
    { id: "5", text: "Send Reply", x: 75, y: 345 },
  ],
  connections: [
    { source: "1", destination: "2" },
    { source: "2", destination: "3" },
    { source: "3", destination: "4" },
    { source: "4", destination: "5" },
  ],
};

// Main component
export default function Component({
  shouldStart = true,
}: {
  shouldStart?: boolean;
}) {
  const [data, setData] = useState<ConnectionData>(sampleData);
  const [activeConnections, setActiveConnections] = useState<Set<string>>(
    new Set(),
  );
  const [highlightedCards, setHighlightedCards] = useState<Set<string>>(
    new Set(),
  );

  // Animate connections in sequence
  useEffect(() => {
    if (!shouldStart) return;

    const animateConnections = async () => {
      // Reset first
      setActiveConnections(new Set());
      setHighlightedCards(new Set());

      // Wait a bit before starting
      await new Promise((resolve) => setTimeout(resolve, 500));

      for (let i = 0; i < data.connections.length; i++) {
        const connection = data.connections[i];
        const connectionKey = `${connection.source}-${connection.destination}`;

        // Activate this connection
        setActiveConnections((prev) => {
          const newSet = new Set(prev);
          newSet.add(connectionKey);
          return newSet;
        });
        setHighlightedCards((prev) => {
          const newSet = new Set(prev);
          newSet.add(connection.source);
          newSet.add(connection.destination);
          return newSet;
        });

        // Wait for animation to complete before next one
        await new Promise((resolve) => setTimeout(resolve, 1000));
      }

      // Animation complete - stay in final state
      console.log("Animation sequence completed");
    };

    // Run when shouldStart becomes true
    animateConnections();
  }, [data.connections, shouldStart]);

  // Calculate connection positions
  const getConnectionPositions = () => {
    return data.connections
      .map((connection, index) => {
        const sourceCard = data.cards.find(
          (card) => card.id === connection.source,
        );
        const destCard = data.cards.find(
          (card) => card.id === connection.destination,
        );

        if (!sourceCard || !destCard) return null;

        return {
          start: { x: sourceCard.x, y: sourceCard.y },
          end: { x: destCard.x, y: destCard.y },
          key: `${connection.source}-${connection.destination}`,
          isActive: activeConnections.has(
            `${connection.source}-${connection.destination}`,
          ),
          delay: index * 0.01, // Stagger the animations
        };
      })
      .filter(Boolean);
  };

  return (
    <div className="w-full h-full">
      <style jsx>{`
        @keyframes drawLine {
          from {
            stroke-dashoffset: var(--line-length);
          }
          to {
            stroke-dashoffset: 0;
          }
        }
      `}</style>

      <div className="relative w-full h-[400px] pl-4 bg-gray-50 rounded-lg border border-gray-200 overflow-hidden py-4">
        {/* Render connections first (behind cards) */}
        {getConnectionPositions().map(
          (connection, index) =>
            connection && (
              <AnimatedEdge
                key={connection.key}
                start={connection.start}
                end={connection.end}
                isActive={connection.isActive}
                delay={connection.delay}
              />
            ),
        )}

        {/* Render cards */}
        {data.cards.map((card) => (
          <AnimatedCard
            key={card.id}
            card={card}
            isHighlighted={highlightedCards.has(card.id)}
          />
        ))}
      </div>
    </div>
  );
}
