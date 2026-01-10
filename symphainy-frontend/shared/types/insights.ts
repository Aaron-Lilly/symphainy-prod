import {
  TrendingUp,
  Database,
  FileText,
  BarChart3,
  LucideIcon,
} from "lucide-react";

// Type definition for insight card
export interface InsightCard {
  id: string;
  title: string;
  description: string;
  icon: LucideIcon;
}

// Insight card data
export const insightCards: InsightCard[] = [
  {
    id: "anomaly",
    title: "Anomaly Detection",
    description: "Detect anomalies and outliers in your data",
    icon: FileText,
  },
  {
    id: "business",
    title: "Business Analysis",
    description: "Get business insights, recommendations, and risk analysis",
    icon: TrendingUp,
  },
  {
    id: "eda",
    title: "EDA Analysis",
    description: "Exploratory Data Analysis of your dataset",
    icon: BarChart3,
  },
  {
    id: "visualization",
    title: "Data Visualization",
    description: "Generate charts and visual representations of your data",
    icon: Database,
  },
];

// Helper function to get insight card by id
export const getInsightCardById = (id: string): InsightCard | undefined => {
  return insightCards.find(card => card.id === id);
};

// Helper function to get insight card titles
export const getInsightCardTitles = (): string[] => {
  return insightCards.map(card => card.title);
};

// Export individual card IDs as constants
export const INSIGHT_CARD_IDS = {
  ANOMALY: "anomaly",
  BUSINESS: "business", 
  EDA: "eda",
  VISUALIZATION: "visualization",
} as const;

export type InsightCardId = typeof INSIGHT_CARD_IDS[keyof typeof INSIGHT_CARD_IDS];