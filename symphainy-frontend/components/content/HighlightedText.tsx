"use client";

import React from "react";

interface HighlightedTextProps {
  text: string;
  searchTerm: string;
  maxLength?: number;
}

export const HighlightedText: React.FC<HighlightedTextProps> = ({ 
  text, 
  searchTerm, 
  maxLength 
}) => {
  if (!text) {
    return <span>No text content available</span>;
  }
  
  // Truncate text if maxLength is specified
  const displayText = maxLength && text.length > maxLength 
    ? text.substring(0, maxLength) + "..."
    : text;
  
  // If no search term, just return the text
  if (!searchTerm.trim()) {
    return <span>{displayText}</span>;
  }
  
  // Split text by search term and highlight matches
  const parts = displayText.split(new RegExp(`(${searchTerm})`, 'gi'));
  
  return (
    <span>
      {parts.map((part, index) => 
        part.toLowerCase() === searchTerm.toLowerCase() ? (
          <mark key={index} className="bg-yellow-200 px-1 rounded">
            {part}
          </mark>
        ) : (
          <span key={index}>{part}</span>
        )
      )}
    </span>
  );
}; 