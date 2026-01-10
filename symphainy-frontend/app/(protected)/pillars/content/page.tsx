"use client";
import React, { useEffect, useState } from "react";
import { FileUploader } from "./components/FileUploader";
import { FileDashboard } from "./components/FileDashboard";
import { FileParser } from "./components/FileParser";
import { ParsePreview } from "./components/ParsePreview";
import DataMash from "./components/DataMash";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { useSetAtom } from "jotai";
import { chatbotAgentInfoAtom, mainChatbotOpenAtom } from "@/shared/atoms/chatbot-atoms";
import { SecondaryChatbotAgent, SecondaryChatbotTitle } from "@/shared/types/secondaryChatbot";
import { PillarCompletionMessage } from "../shared/components/PillarCompletionMessage";

export default function ContentPage() {
  const setAgentInfo = useSetAtom(chatbotAgentInfoAtom);
  const setMainChatbotOpen = useSetAtom(mainChatbotOpenAtom);
  
  // State for file processing workflow
  const [selectedFile, setSelectedFile] = useState<any>(null);
  const [parseResult, setParseResult] = useState<any>(null);
  const [extractedMetadata, setExtractedMetadata] = useState<any>(null);
  const [currentStep, setCurrentStep] = useState<'upload' | 'parse' | 'metadata' | 'complete'>('upload');

  // Set up Content Liaison Agent as secondary option (not default)
  useEffect(() => {
    // Configure the secondary agent but don't show it by default
    setAgentInfo({
      agent: SecondaryChatbotAgent.CONTENT_LIAISON,
      title: SecondaryChatbotTitle.CONTENT_LIAISON,
      file_url: "",
      additional_info: "Content management and file processing assistance"
    });
    // Keep main chatbot open by default - GuideAgent will be shown
    setMainChatbotOpen(true);
  }, [setAgentInfo, setMainChatbotOpen]);

  // Handler functions
  const handleFileSelected = (file: any) => {
    setSelectedFile(file);
    setCurrentStep('parse');
  };

  const handleFileParsed = (file: any, result: any) => {
    setParseResult(result);
    setCurrentStep('metadata');
  };

  const handleMetadataExtracted = (metadata: any) => {
    setExtractedMetadata(metadata);
    setCurrentStep('complete');
  };

  // Detect completion: user has uploaded, parsed, and extracted metadata
  const isComplete = currentStep === 'complete' && extractedMetadata !== null;

  return (
    <div className="flex-grow space-y-6">
      <div className="space-y-3">
        <h2 className="text-h2 font-bold text-gray-800">Data Pillar</h2>
        <p className="text-base text-sm text-gray-700 leading-relaxed">
          Connect, manage, and parse your business data to begin the journey.
        </p>
      </div>

      {/* Row 1: File Upload + File Dashboard */}
      <Card>
        <CardHeader>
          <CardTitle>File Upload & Dashboard</CardTitle>
          <CardDescription>
            Upload files and manage your uploaded files in one place.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <h3 className="text-sm font-medium mb-3">Upload Files</h3>
            <FileUploader />
          </div>
          <div className="border-t pt-6">
            <h3 className="text-sm font-medium mb-3">File Dashboard</h3>
            <FileDashboard 
              onFileSelected={handleFileSelected}
              onFileParsed={(file, parseResult) => {
                console.log('File parsed:', file, parseResult);
                handleFileSelected(file);
              }}
              onFileDeleted={(fileId) => {
                console.log('File deleted:', fileId);
              }}
            />
          </div>
        </CardContent>
      </Card>

      {/* Row 2: File Parsing (stacked on top) */}
      <Card>
        <CardHeader>
          <CardTitle>File Parsing</CardTitle>
          <CardDescription>
            Parse your uploaded files into structured formats for analysis.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <FileParser 
            selectedFile={selectedFile}
            onParseComplete={handleFileParsed}
          />
        </CardContent>
      </Card>

      {/* Row 3: Parse Preview (stacked below, full width) */}
      <Card>
        <CardHeader>
          <CardTitle>Parse Preview</CardTitle>
          <CardDescription>
            Preview parsed files and view their structured data.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ParsePreview 
            selectedFile={selectedFile}
          />
        </CardContent>
      </Card>

      {/* Row 4: Data Mash - Semantic Layer */}
      <Card>
        <CardHeader>
          <CardTitle>Data Mash</CardTitle>
          <CardDescription>
            AI-powered semantic layer that dynamically stitches together data from different sources.
            View embeddings and semantic meanings extracted from your parsed files.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <DataMash 
            selectedFile={selectedFile}
          />
        </CardContent>
      </Card>

      {/* Completion Message */}
      <PillarCompletionMessage
        show={isComplete}
        message="Congratulations! You've explored all of our content features. Please proceed to Insights or Operations to continue working with your data."
      />
    </div>
  );
}
