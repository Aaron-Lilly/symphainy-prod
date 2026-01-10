"use client";

import React, { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  ArrowLeft,
  BarChart3,
  Database,
  FileText,
  Loader,
  TrendingUp,
} from "lucide-react";
import { FileMetadata } from "@/shared/types/file";
import { AGUIEventProvider } from "@/shared/agui/AGUIEventProvider";
import { useGlobalSession } from "@/shared/agui/GlobalSessionProvider";
import {
  startInsightsSession,
  getEDAAnalysis,
  getVisualizationAnalysis,
  getAnomalyDetectionAnalysis,
  getBusinessAnalysis,
} from "@/lib/api/insights";
import { listFiles } from "@/lib/api/fms-insights";
import dynamic from "next/dynamic";

const AGUIInsightsPanel = dynamic(
  () => import("@/components/insights/AGUIInsightsPanel"),
  { ssr: false },
);
const InsightsResultDisplay = dynamic(
  () => import("@/components/insights/InsightsResultDisplay"),
  { ssr: false },
);
const BusinessAnalysisDisplay = dynamic(
  () => import("@/components/insights/BusinessAnalysisDisplay"),
  { ssr: false },
);
const VisualizationDisplay = dynamic(
  () => import("@/components/insights/VisualizationDisplay"),
  { ssr: false },
);

export default function FileInsightsPage() {
  const router = useRouter();
  const params = useParams();
  const fileId = params.fileId as string;
  const { guideSessionToken, setGuideSessionToken } = useGlobalSession();

  const [file, setFile] = useState<FileMetadata | null>(null);
  const [activeCard, setActiveCard] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [sessionLoading, setSessionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [analysisResults, setAnalysisResults] = useState<any>(null);
  const [currentAnalysisType, setCurrentAnalysisType] = useState<string>("");

  // Fetch file details
  useEffect(() => {
    async function fetchFileDetails() {
      try {
        const fileList = await listFiles();
        const foundFile = fileList.find((f) => f.uuid === fileId);

        if (!foundFile) {
          setError("File not found");
          return;
        }

        setFile(foundFile);
      } catch (err) {
        setError("Failed to load file details");
        console.error("Error fetching file:", err);
      } finally {
        setLoading(false);
      }
    }

    if (fileId) {
      fetchFileDetails();
    }
  }, [fileId]);

  // Start insights session when needed
  // useEffect(() => {
  // //   if (!guideSessionToken && fileId && !sessionLoading) {
  // //     handleStartSession();
  // //   }
  // // }, [fileId, guideSessionToken]);

  // const handleStartSession = async () => {
  //   try {
  //     setSessionLoading(true);
  //     setError(null);
  //     const sessionResponse = await startInsightsSession(fileId);
  //     await setGuideSessionToken(sessionResponse.session_token);
  //   } catch (err: any) {
  //     setError(
  //       `Failed to start insights session: ${
  //         err.message || "Please try again later."
  //       }`
  //     );
  //   } finally {
  //     setSessionLoading(false);
  //   }
  // };

  const handleBack = () => {
    router.push("/pillars/insight");
  };

  const handleCardClick = async (cardType: string) => {
    alert("🔍 handleCardClick called with cardType: " + cardType); // FORCE VISIBLE CHANGE
    console.log("🔍 handleCardClick called with cardType:", cardType);
    
    if (!file || !file.parsed_path) {
      setError(
        "File URL not available. Please ensure the file is properly parsed.",
      );
      return;
    }

    try {
      setAnalysisLoading(true);
      setError(null);
      setCurrentAnalysisType(cardType);

      let results;
      const fileUrl = file.parsed_path;

      switch (cardType) {
        case "anomaly":
          console.log("Calling anomaly detection...");
          results = await getAnomalyDetectionAnalysis(fileUrl, guideSessionToken);
          console.log("Anomaly detection results:", results);
          break;
        case "business":
          alert("🔍 BUSINESS ANALYSIS CASE - THIS SHOULD BE VISIBLE"); // FORCE VISIBLE CHANGE
          console.log("🔍 BUSINESS ANALYSIS CASE - THIS SHOULD BE VISIBLE");
          console.log("Calling business analysis...");
          console.log("fileUrl:", fileUrl);
          console.log("guideSessionToken:", guideSessionToken);
          console.log("🔍 About to call getBusinessAnalysis function");
          console.log("🔍 getBusinessAnalysis function:", getBusinessAnalysis);
          // Temporarily call EDA to test if the issue is with the function
          console.log("🔍 TEMPORARY: Calling EDA instead of business analysis to test");
          results = await getEDAAnalysis(fileUrl, guideSessionToken);
          console.log("Business analysis results:", results);
          break;
        case "eda":
          console.log("Calling EDA analysis...");
          results = await getEDAAnalysis(fileUrl, guideSessionToken);
          console.log("EDA results:", results);
          break;
        case "visualization":
          console.log("Calling visualization analysis...");
          results = await getVisualizationAnalysis(fileUrl, guideSessionToken);
          console.log("Visualization results:", results);
          break;
        default:
          throw new Error("Unknown analysis type");
      }

      setAnalysisResults(results);
      setActiveCard(cardType);
    } catch (err: any) {
      setError(
        `Failed to run ${cardType} analysis: ${
          err.message || "Please try again later."
        }`,
      );
      console.error(`${cardType} analysis error:`, err);
    } finally {
      setAnalysisLoading(false);
    }
  };

  const handleClosePanel = () => {
    setActiveCard(null);
    setAnalysisResults(null);
    setCurrentAnalysisType("");
  };

  const insightCards = [
    {
      id: "anomaly",
      title: "Anomaly Detection",
      description: "Overview of anomalies in your data",
      icon: <FileText className="h-6 w-6" />,
    },
    {
      id: "business",
      title: "Business Analysis",
      description: "Deep dive analysis and patterns in your business",
      icon: <BarChart3 className="h-6 w-6" />,
    },
    {
      id: "eda",
      title: "EDA",
      description: "Exploratory Data Analysis of your data",
      icon: <TrendingUp className="h-6 w-6" />,
    },
    {
      id: "visualization",
      title: "Visualization",
      description: "Visualize your data insights",
      icon: <Database className="h-6 w-6" />,
    },
  ];

  if (loading) {
    return (
      <div className="flex-grow space-y-8 min-h-screen">
        <div className="text-center py-12 flex justify-center items-center">
          <Loader className="w-10 h-10 animate-spin" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex-grow space-y-8 min-h-screen">
        <div className="text-center py-12">
          <h2 className="text-xl font-semibold mb-2 text-red-600">Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <Button variant="outline" onClick={handleBack}>
            Back to Insights
          </Button>
        </div>
      </div>
    );
  }

  // Show analysis results when available
  if (activeCard && analysisResults) {
    const cardInfo = insightCards.find((card) => card.id === activeCard);
    const title = cardInfo?.title || currentAnalysisType;
    const description =
      cardInfo?.description || `Results from ${currentAnalysisType} analysis`;

    // Use specific components based on analysis type
    switch (activeCard) {
      case "business":
        return (
          <BusinessAnalysisDisplay
            title={title}
            description={description}
            data={analysisResults}
            onBack={handleClosePanel}
            loading={analysisLoading}
          />
        );
      case "visualization":
        return (
          <VisualizationDisplay
            title={title}
            description={description}
            data={analysisResults}
            onBack={handleClosePanel}
            loading={analysisLoading}
          />
        );
      default:
        // Use generic display for anomaly detection and EDA
        return (
          <InsightsResultDisplay
            title={title}
            description={description}
            data={analysisResults}
            onBack={handleClosePanel}
            loading={analysisLoading}
          />
        );
    }
  }

  // Show loading state during analysis
  if (analysisLoading) {
    return (
      <div className="flex-grow space-y-8 min-h-screen">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p>Running {currentAnalysisType} analysis...</p>
          <p className="text-sm text-gray-500 mt-2">
            This may take a few moments
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-grow space-y-8 min-h-screen">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">File Insights</h1>
          {file && (
            <p className="text-gray-600 text-sm">
              {file.ui_name} • {file.file_type} •{" "}
              {new Date(file.created_at).toLocaleDateString()}
            </p>
          )}
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={handleBack}
          //   className="flex items-center gap-2 bg-white text-black border border-primary hover:bg-primary hover:text-white"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back{" "}
        </Button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="p-4 bg-red-100 text-red-700 rounded-md">{error}</div>
      )}

      {/* Loading State */}
      {sessionLoading && (
        <div className="text-center py-8">
          <p>Starting insights session...</p>
        </div>
      )}

      {/* Insights Cards Grid - 2x2 layout */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {insightCards.map((card) => (
          <Card
            key={card.id}
            className={`transition-all duration-200 min-h-[200px] flex flex-col justify-between ${
              analysisLoading
                ? "opacity-50 cursor-not-allowed"
                : "cursor-pointer hover:shadow-md border hover:border-primary"
            }`}
            onClick={() => !analysisLoading && handleCardClick(card.id)}
          >
            <CardHeader className="pb-3">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-gray-50 text-gray-600">
                  {analysisLoading && currentAnalysisType === card.id ? (
                    <Loader className="h-6 w-6 animate-spin" />
                  ) : (
                    card.icon
                  )}
                </div>
                <div>
                  <CardTitle className="text-lg">{card.title}</CardTitle>
                </div>
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <CardDescription className="text-gray-600 mb-4">
                {card.description}
              </CardDescription>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Click to analyze</span>
                <ArrowLeft className="h-4 w-4 rotate-180 text-gray-400" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Session Status
      <div className="text-center text-sm text-gray-500 mt-8">
        {guideSessionToken ? (
          <span className="text-green-600">✓ Insights session active</span>
        ) : (
          <span>Preparing insights session...</span>
        )}
      </div> */}
    </div>
  );
}
