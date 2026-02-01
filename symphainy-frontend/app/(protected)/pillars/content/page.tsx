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
import { Badge } from "@/components/ui/badge";
import { usePlatformState } from "@/shared/state/PlatformStateProvider";
import { useTenant } from "@/shared/contexts/TenantContext";
import { SecondaryChatbotAgent, SecondaryChatbotTitle } from "@/shared/types/secondaryChatbot";
import { PillarCompletionMessage } from "../shared/components/PillarCompletionMessage";
import { usePathname, useSearchParams } from "next/navigation";
import { syncRouteToState } from "@/shared/utils/routing";
import { Suspense } from "react";
import { Database, FileCode } from "lucide-react";

export default function ContentPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <ContentPageContent />
    </Suspense>
  );
}

function ContentPageContent() {
  const { setChatbotAgentInfo, setMainChatbotOpen, setRealmState, setCurrentPillar, getRealmState } = usePlatformState();
  const setAgentInfo = setChatbotAgentInfo;
  
  // Get tenant configuration
  const { currentTenant } = useTenant();
  const contentFeatures = currentTenant.features.content;
  
  const pathname = usePathname();
  const searchParams = useSearchParams();
  
  // Sync route params to state on mount and route changes
  useEffect(() => {
    const params = new URLSearchParams(searchParams.toString());
    syncRouteToState(pathname, params, setRealmState, setCurrentPillar);
  }, [pathname, searchParams, setRealmState, setCurrentPillar]);
  
  // State for file processing workflow
  const [selectedFile, setSelectedFile] = useState<any>(null);
  const [parseResult, setParseResult] = useState<any>(null);
  const [extractedMetadata, setExtractedMetadata] = useState<any>(null);
  
  // Get current step from realm state (synced from route)
  const routeStep = getRealmState("content", "currentStep") as string | null;
  const [currentStep, setCurrentStep] = useState<'upload' | 'parse' | 'metadata' | 'complete'>(
    (routeStep as 'upload' | 'parse' | 'metadata' | 'complete') || 'upload'
  );
  
  // Update current step when route changes
  useEffect(() => {
    if (routeStep && ['upload', 'parse', 'metadata', 'complete'].includes(routeStep)) {
      setCurrentStep(routeStep as 'upload' | 'parse' | 'metadata' | 'complete');
    }
  }, [routeStep]);

  // Set up Content Liaison Agent with tenant-specific context
  useEffect(() => {
    setAgentInfo({
      agent: SecondaryChatbotAgent.CONTENT_LIAISON,
      title: SecondaryChatbotTitle.CONTENT_LIAISON,
      file_url: "",
      additional_info: currentTenant.agents?.liaison_agent_prompt_context ||
        "Content management and file processing assistance. Ask me about file uploads, parsing, and data extraction."
    });
    setMainChatbotOpen(true);
  }, [setAgentInfo, setMainChatbotOpen, currentTenant]);

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
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-h2 font-bold text-gray-800">Data Pillar</h2>
            <p className="text-base text-sm text-gray-700 leading-relaxed">
              {contentFeatures.upload_guidance || 'Connect, manage, and parse your business data to begin the journey.'}
            </p>
            {/* Show supported file types for this tenant */}
            <div className="flex flex-wrap gap-1 mt-2">
              {contentFeatures.file_types.map((type) => (
                <Badge key={type} variant="outline" className="text-xs">
                  {type.toUpperCase()}
                </Badge>
              ))}
            </div>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-blue-50 border border-blue-200 rounded-lg">
            <span className="text-xs font-semibold text-blue-900">Available:</span>
            <span className="text-xs text-blue-700">Content Liaison Agent</span>
            <span className="flex h-2 w-2 rounded-full bg-blue-500" title="Liaison agent available" />
          </div>
        </div>
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

      {/* Mainframe Parser Section - Only for VLP and Base tenants */}
      {contentFeatures.show_mainframe_parser && (
        <Card className="border-purple-200">
          <CardHeader className="bg-purple-50/50">
            <CardTitle className="flex items-center gap-2">
              <Database className="h-5 w-5 text-purple-600" />
              Mainframe Data Processing
              <Badge variant="secondary" className="ml-2">Specialized</Badge>
            </CardTitle>
            <CardDescription>
              Upload mainframe data files with optional COBOL copybook for field mapping.
              Supports EBCDIC encoding, packed decimal, and fixed-length record formats.
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 border border-purple-200 rounded-lg bg-white">
                <h4 className="font-semibold text-purple-900 mb-2">Data File Upload</h4>
                <p className="text-sm text-gray-600 mb-3">
                  Upload your mainframe extract (.dat, .txt, or raw binary files)
                </p>
                <FileUploader />
              </div>
              <div className="p-4 border border-purple-200 rounded-lg bg-white">
                <h4 className="font-semibold text-purple-900 mb-2">Copybook Upload (Optional)</h4>
                <p className="text-sm text-gray-600 mb-3">
                  Upload COBOL copybook (.cpy, .cbl) for automatic field mapping
                </p>
                <FileUploader />
              </div>
            </div>
            <div className="mt-4 p-3 bg-purple-50 rounded-lg">
              <p className="text-xs text-purple-800">
                <strong>Tip:</strong> For best results, ensure your mainframe extract uses a consistent record layout.
                The copybook helps us automatically identify field boundaries, data types, and encoding.
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* EDI Parser Section - Only for PSO and Base tenants */}
      {contentFeatures.show_edi_parser && (
        <Card className="border-green-200">
          <CardHeader className="bg-green-50/50">
            <CardTitle className="flex items-center gap-2">
              <FileCode className="h-5 w-5 text-green-600" />
              EDI Processing
              <Badge variant="secondary" className="ml-2">Specialized</Badge>
            </CardTitle>
            <CardDescription>
              Process EDI transactions from trading partners. Supports X12, EDIFACT, and HL7 formats.
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-4">
            <div className="space-y-4">
              <div className="p-4 border border-green-200 rounded-lg bg-white">
                <h4 className="font-semibold text-green-900 mb-2">EDI File Upload</h4>
                <p className="text-sm text-gray-600 mb-3">
                  Upload EDI files (.edi, .x12, .txt) for parsing and validation
                </p>
                <FileUploader />
              </div>
              <div className="grid grid-cols-3 gap-3 text-sm">
                <div className="p-3 bg-green-50 rounded-lg text-center">
                  <div className="font-semibold text-green-800">X12</div>
                  <div className="text-xs text-green-600">810, 850, 997</div>
                </div>
                <div className="p-3 bg-green-50 rounded-lg text-center">
                  <div className="font-semibold text-green-800">EDIFACT</div>
                  <div className="text-xs text-green-600">ORDERS, INVOIC</div>
                </div>
                <div className="p-3 bg-green-50 rounded-lg text-center">
                  <div className="font-semibold text-green-800">HL7</div>
                  <div className="text-xs text-green-600">v2.x, FHIR</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Row 2: File Parsing */}
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

      {/* Row 3: Parse Preview */}
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
