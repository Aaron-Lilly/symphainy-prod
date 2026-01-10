"use client";

import React from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from "@/components/ui/card";
import { CheckCircle2 } from "lucide-react";

interface PillarCompletionMessageProps {
  message: string;
  show: boolean;
}

export function PillarCompletionMessage({ message, show }: PillarCompletionMessageProps) {
  if (!show) return null;

  return (
    <Card className="border-green-200 bg-green-50">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-green-800">
          <CheckCircle2 className="h-5 w-5 text-green-600" />
          Congratulations!
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-gray-700 leading-relaxed">
          {message}
        </p>
      </CardContent>
    </Card>
  );
}






