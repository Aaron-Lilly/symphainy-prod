"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Clock, CheckCircle, AlertCircle, Loader2, RefreshCw } from "lucide-react";

interface WorkflowStatusProps {
  workflowId: string;
  fileName: string;
  status: "processing" | "completed" | "error" | "pending";
  startedAt?: string;
  completedAt?: string;
  estimatedDuration?: number;
  onRefresh?: () => void;
}

export function WorkflowStatus({
  workflowId,
  fileName,
  status,
  startedAt,
  completedAt,
  estimatedDuration,
  onRefresh
}: WorkflowStatusProps) {
  const [progress, setProgress] = useState(0);
  const [elapsedTime, setElapsedTime] = useState(0);

  // Calculate progress based on elapsed time and estimated duration
  useEffect(() => {
    if (status === "processing" && estimatedDuration && startedAt) {
      const startTime = new Date(startedAt).getTime();
      const updateProgress = () => {
        const now = Date.now();
        const elapsed = Math.floor((now - startTime) / 1000);
        setElapsedTime(elapsed);
        
        const calculatedProgress = Math.min((elapsed / estimatedDuration) * 100, 95);
        setProgress(calculatedProgress);
      };

      updateProgress();
      const interval = setInterval(updateProgress, 1000);
      return () => clearInterval(interval);
    } else if (status === "completed") {
      setProgress(100);
    }
  }, [status, estimatedDuration, startedAt]);

  const getStatusIcon = () => {
    switch (status) {
      case "processing":
        return <Loader2 className="h-4 w-4 animate-spin" />;
      case "completed":
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case "error":
        return <AlertCircle className="h-4 w-4 text-red-600" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case "processing":
        return "bg-blue-100 text-blue-800";
      case "completed":
        return "bg-green-100 text-green-800";
      case "error":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const formatDuration = (seconds: number) => {
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  return (
    <Card className="w-full max-w-md">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium">Workflow Status</CardTitle>
          {onRefresh && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onRefresh}
              className="h-6 w-6 p-0"
            >
              <RefreshCw className="h-3 w-3" />
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* File Info */}
        <div className="flex items-center space-x-2">
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">
              {fileName}
            </p>
            <p className="text-xs text-gray-500 font-mono">
              {workflowId}
            </p>
          </div>
        </div>

        {/* Status Badge */}
        <div className="flex items-center space-x-2">
          {getStatusIcon()}
          <Badge className={getStatusColor()}>
            {status.charAt(0).toUpperCase() + status.slice(1)}
          </Badge>
        </div>

        {/* Progress Bar */}
        {status === "processing" && (
          <div className="space-y-2">
            <Progress value={progress} className="h-2" />
            <div className="flex justify-between text-xs text-gray-500">
              <span>{formatDuration(elapsedTime)} elapsed</span>
              {estimatedDuration && (
                <span>~{formatDuration(estimatedDuration)} total</span>
              )}
            </div>
          </div>
        )}

        {/* Timestamps */}
        <div className="text-xs text-gray-500 space-y-1">
          {startedAt && (
            <div>Started: {new Date(startedAt).toLocaleTimeString()}</div>
          )}
          {completedAt && (
            <div>Completed: {new Date(completedAt).toLocaleTimeString()}</div>
          )}
        </div>

        {/* Status-specific messages */}
        {status === "processing" && (
          <p className="text-xs text-blue-600">
            Processing your file... This may take a few moments.
          </p>
        )}
        {status === "completed" && (
          <p className="text-xs text-green-600">
            ✅ Processing complete! Your file has been analyzed.
          </p>
        )}
        {status === "error" && (
          <p className="text-xs text-red-600">
            ❌ An error occurred during processing. Please try again.
          </p>
        )}
      </CardContent>
    </Card>
  );
} 