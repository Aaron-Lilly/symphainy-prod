"use client";
import React, { useState, useEffect } from "react";
// Linear animation component for connections
export default function AnimatedEdge({
  start,
  end,
  isActive,
  delay = 0,
}: {
  start: { x: number; y: number };
  end: { x: number; y: number };
  isActive: boolean;
  delay?: number;
}) {
  const startX = start.x + 56; // Center of smaller card (w-28 = 112px / 2 = 56)
  const startY = start.y + 35; // Bottom of card for better visual flow
  const endX = end.x + 56;
  const endY = end.y + 5; // Top of next card

  const length = Math.sqrt(
    Math.pow(endX - startX, 2) + Math.pow(endY - startY, 2),
  );

  return (
    <svg
      className="absolute top-0 left-0 pointer-events-none w-full h-full"
      style={{ zIndex: 1 }}
    >
      {/* Static line (always visible but faded when not active) */}
      <line
        x1={startX}
        y1={startY}
        x2={endX}
        y2={endY}
        stroke={isActive ? "transparent" : "#d1d5db"}
        strokeWidth="2"
        opacity={isActive ? 0 : 0.4}
      />

      {/* Animated line that draws from origin to destination */}
      {isActive && (
        <line
          x1={startX}
          y1={startY}
          x2={endX}
          y2={endY}
          stroke="#007A87"
          strokeWidth="3"
          strokeDasharray={length}
          strokeDashoffset={length}
          style={{
            animation: `drawLine-${start.x}-${start.y} 0.8s ease-in-out ${delay}s forwards`,
          }}
        />
      )}

      {/* Traveling dot that moves once along the path */}
      {isActive && (
        <circle
          r="4"
          fill="#007A87"
          className="drop-shadow-md"
          style={{
            opacity: 0,
            animation: `travelDot-${start.x}-${start.y} 0.8s ease-in-out ${delay}s forwards`,
          }}
        >
          <animateMotion
            dur="0.8s"
            begin={`${delay}s`}
            repeatCount="1"
            fill="freeze"
          >
            <mpath href={`#path-${start.x}-${start.y}-${end.x}-${end.y}`} />
          </animateMotion>
        </circle>
      )}

      {/* Hidden path for the dot animation */}
      <path
        id={`path-${start.x}-${start.y}-${end.x}-${end.y}`}
        d={`M ${startX} ${startY} L ${endX} ${endY}`}
        fill="none"
        stroke="none"
      />

      {/* Dynamic styles for this specific connection */}
      <style>
        {`
            @keyframes drawLine-${start.x}-${start.y} {
              from {
                stroke-dashoffset: ${length};
              }
              to {
                stroke-dashoffset: 0;
              }
            }
            
            @keyframes travelDot-${start.x}-${start.y} {
              0% {
                opacity: 0;
              }
              10% {
                opacity: 1;
              }
              90% {
                opacity: 1;
              }
              100% {
                opacity: 0;
              }
            }
          `}
      </style>
    </svg>
  );
}
