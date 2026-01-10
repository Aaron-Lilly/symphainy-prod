import React from "react";

interface LoadingDotsProps {
  className?: string;
  size?: "sm" | "md" | "lg";
}

const LoadingDots: React.FC<LoadingDotsProps> = ({
  className = "",
  size = "md",
}) => {
  const sizeClasses = {
    sm: "w-1 h-1",
    md: "w-1.5 h-1.5",
    lg: "w-2 h-2",
  };

  const dotClass = `${sizeClasses[size]} bg-gray-500 rounded-full animate-pulse`;

  return (
    <div className={`flex items-center space-x-1 ${className}`}>
      <div
        className={dotClass}
        style={{
          animationDelay: "0ms",
          animationDuration: "1.4s",
        }}
      />
      <div
        className={dotClass}
        style={{
          animationDelay: "200ms",
          animationDuration: "1.4s",
        }}
      />
      <div
        className={dotClass}
        style={{
          animationDelay: "400ms",
          animationDuration: "1.4s",
        }}
      />
    </div>
  );
};

export default LoadingDots;
