// Spinner.tsx
import React from "react";
import { Loader2 as LucideLoader } from "lucide-react";
import { cn } from "@/lib/utils";

interface LoaderProps {
  className?: string;
  size?: "sm" | "md" | "lg" | "xl";
}

const sizeClasses = {
  sm: "h-4 w-4",
  md: "h-6 w-6",
  lg: "h-8 w-8",
  xl: "h-12 w-12",
};

export const Loader: React.FC<LoaderProps> = ({ className, size = "md" }) => {
  return (
    <LucideLoader
      className={cn("animate-spin text-gray-500", sizeClasses[size], className)}
      style={{ animationDuration: "1s" }}
    />
  );
};
