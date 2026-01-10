"use client";
import React from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { FileText, Share2, Wand2, Loader2 } from "lucide-react";
import Link from "next/link";

interface JourneyChoiceProps {
  onSelectExisting: () => void;
  onStartWizard: () => void;
}

export default function JourneyChoice({
  onSelectExisting,
  onStartWizard,
}: JourneyChoiceProps) {
  return (
    <div className="text-center">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card
          className="hover:shadow-lg transition-shadow cursor-pointer text-left"
          onClick={onSelectExisting}
        >
          <CardHeader>
            <Share2 className="w-8 h-8 mb-2 text-primary" />
            <CardTitle className="text-gray-800 text-lg font-normal">
              Select Existing Files
            </CardTitle>
          </CardHeader>
          <CardContent>
            <CardDescription>
              Analyze an SOP or Workflow you've already uploaded to generate its
              counterpart.
            </CardDescription>
          </CardContent>
        </Card>
        <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full text-left">
          <Link href="/pillars/content">
            <CardHeader>
              <FileText className="w-8 h-8 mb-2 text-primary" />
              <CardTitle className="text-gray-800 text-lg font-normal">
                Upload a New File
              </CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                Go to the Content Pillar to upload a new SOP or BPMN document.
              </CardDescription>
            </CardContent>
          </Link>
        </Card>
        <Card
          className="hover:shadow-lg transition-shadow cursor-pointer text-left"
          onClick={onStartWizard}
        >
          <CardHeader>
            <Wand2 className="w-8 h-8 mb-2 text-primary" />
            <CardTitle className="text-gray-800 text-lg font-normal">
              Create From Scratch
            </CardTitle>
          </CardHeader>
          <CardContent>
            <CardDescription>
              Chat with our AI assistant to describe an existing process or design a new coexistence-enabled workflow.
            </CardDescription>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
