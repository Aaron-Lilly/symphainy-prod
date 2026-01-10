import React, { useState, useEffect } from "react";

interface StreamingMessageProps {
  content: string;
  isComplete?: boolean;
  typingSpeed?: number; // milliseconds per character
  onComplete?: () => void;
}

export default function StreamingMessage({
  content,
  isComplete = false,
  typingSpeed = 30,
  onComplete,
}: StreamingMessageProps) {
  const [displayedContent, setDisplayedContent] = useState("");
  const [isTyping, setIsTyping] = useState(!isComplete);
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (isComplete) {
      setDisplayedContent(content);
      setIsTyping(false);
      setCurrentIndex(content.length);
      return;
    }

    if (currentIndex < content.length && isTyping) {
      const timer = setTimeout(() => {
        setDisplayedContent(content.slice(0, currentIndex + 1));
        setCurrentIndex((prev) => prev + 1);
      }, typingSpeed);

      return () => clearTimeout(timer);
    } else if (currentIndex >= content.length && isTyping) {
      setIsTyping(false);
      onComplete?.();
    }
  }, [content, currentIndex, isTyping, typingSpeed, isComplete, onComplete]);

  // Reset when content changes
  useEffect(() => {
    if (!isComplete) {
      setDisplayedContent("");
      setCurrentIndex(0);
      setIsTyping(true);
    }
  }, [content, isComplete]);

  return (
    <div className="text-gray-800 text-sm mr-auto text-left rounded-lg py-2 px-3 shadow-md max-w-[80%]">
      <div className="text-sm">
        {displayedContent.split("\n").map((line, lineIdx) => (
          <React.Fragment key={lineIdx}>
            {line}
            {lineIdx < displayedContent.split("\n").length - 1 && <br />}
          </React.Fragment>
        ))}
        {isTyping && (
          <span className="inline-block w-2 h-4 bg-gray-600 ml-1 animate-pulse" />
        )}
      </div>
    </div>
  );
}
