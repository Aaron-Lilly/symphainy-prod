"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import { Button } from "./button";

interface EmptyStateProps extends React.HTMLAttributes<HTMLDivElement> {
  icon?: React.ReactElement;
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}

const EmptyState = React.forwardRef<HTMLDivElement, EmptyStateProps>(
  ({ className, icon, title, description, action, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "flex flex-col items-center justify-center space-y-4 text-center p-8 bg-background border-2 border-dashed rounded-lg",
          className,
        )}
        {...props}
      >
        {icon && <div className="text-muted-foreground">{icon}</div>}
        <h3 className="text-gray-800 text-lg font-normal">{title}</h3>
        <p className="text-subtle text-xs max-w-sm">{description}</p>
        {action && (
          <div className="mt-6">
            <Button onClick={action.onClick}>{action.label}</Button>
          </div>
        )}
      </div>
    );
  },
);

EmptyState.displayName = "EmptyState";

export { EmptyState };
