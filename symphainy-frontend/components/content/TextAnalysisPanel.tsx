"use client";

import React from "react";

interface TextAnalysisPanelProps {
  text: string;
  metadata: any;
}

export const TextAnalysisPanel: React.FC<TextAnalysisPanelProps> = ({ 
  text, 
  metadata 
}) => {
  if (!text) {
    return null;
  }
  
  const analysis = analyzeText(text);
  
  return (
    <div className="bg-orange-50 border border-orange-200 rounded p-3">
      <h4 className="font-semibold text-orange-800 mb-2">Text Analysis</h4>
      
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div className="text-orange-700">
          <span className="font-medium">Characters:</span> {analysis.characters}
        </div>
        <div className="text-orange-700">
          <span className="font-medium">Words:</span> {analysis.words}
        </div>
        <div className="text-orange-700">
          <span className="font-medium">Sentences:</span> {analysis.sentences}
        </div>
        <div className="text-orange-700">
          <span className="font-medium">Paragraphs:</span> {analysis.paragraphs}
        </div>
      </div>
      
      {analysis.keywords.length > 0 && (
        <div className="mt-3">
          <div className="font-medium text-orange-800 mb-1">Key Terms:</div>
          <div className="flex flex-wrap gap-1">
            {analysis.keywords.slice(0, 10).map((keyword, idx) => (
              <span 
                key={idx} 
                className="bg-orange-200 text-orange-800 px-2 py-1 rounded text-xs"
              >
                {keyword}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

const analyzeText = (text: string) => {
  const characters = text.length;
  const words = text.split(/\s+/).filter(word => word.length > 0).length;
  const sentences = text.split(/[.!?]+/).filter(sentence => sentence.trim().length > 0).length;
  const paragraphs = text.split(/\n\s*\n/).filter(para => para.trim().length > 0).length;
  
  // Simple keyword extraction (words that appear multiple times)
  const wordCounts: { [key: string]: number } = {};
  const wordsList = text.toLowerCase()
    .replace(/[^\w\s]/g, '')
    .split(/\s+/)
    .filter(word => word.length > 3); // Only words longer than 3 characters
  
  wordsList.forEach(word => {
    wordCounts[word] = (wordCounts[word] || 0) + 1;
  });
  
  const keywords = Object.entries(wordCounts)
    .filter(([_, count]) => count > 1)
    .sort(([_, a], [__, b]) => b - a)
    .map(([word, _]) => word)
    .slice(0, 10);
  
  return {
    characters,
    words,
    sentences,
    paragraphs,
    keywords
  };
}; 