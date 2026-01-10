# Insights Data Usage Guide

## Overview

The `shared/types/insights.ts` file provides a centralized data structure for insight cards used throughout the application. This guide shows various ways to use this data.

## Basic Imports

```typescript
import { 
  insightCards,           // Array of all insight cards
  getInsightCardById,     // Function to get card by ID
  getInsightCardTitles,   // Function to get all titles
  INSIGHT_CARD_IDS,       // Constants for card IDs
  type InsightCard,       // TypeScript type
  type InsightCardId      // TypeScript type for IDs
} from "@/shared/types/insights";
```

## Usage Examples

### 1. Render All Cards in a Grid

```typescript
import { insightCards } from "@/shared/types/insights";

function InsightGrid() {
  return (
    <div className="grid grid-cols-2 gap-4">
      {insightCards.map((card) => {
        const IconComponent = card.icon;
        return (
          <div key={card.id} className="p-4 border rounded">
            <IconComponent className="h-5 w-5 mb-2" />
            <h3>{card.title}</h3>
            <p className="text-sm">{card.description}</p>
          </div>
        );
      })}
    </div>
  );
}
```

### 2. Get Specific Card by ID

```typescript
import { getInsightCardById, INSIGHT_CARD_IDS } from "@/shared/types/insights";

function BusinessAnalysisButton() {
  const card = getInsightCardById(INSIGHT_CARD_IDS.BUSINESS);
  if (!card) return null;
  
  const IconComponent = card.icon;
  
  return (
    <button className="flex items-center space-x-2">
      <IconComponent className="h-4 w-4" />
      <span>{card.title}</span>
    </button>
  );
}
```

### 3. Create a Dropdown Selector

```typescript
import { insightCards } from "@/shared/types/insights";

function InsightSelector({ onSelect }: { onSelect: (id: string) => void }) {
  return (
    <select onChange={(e) => onSelect(e.target.value)}>
      <option value="">Choose insight type...</option>
      {insightCards.map((card) => (
        <option key={card.id} value={card.id}>
          {card.title}
        </option>
      ))}
    </select>
  );
}
```

### 4. Use with Secondary Chatbot

```typescript
import { useSetAtom } from "jotai";
import { chatbotAgentInfoAtom } from "@/shared/atoms/chatbot-atoms";
import { insightCards } from "@/shared/types/insights";

function ChatbotAgentSelector({ fileUrl }: { fileUrl: string }) {
  const setChatbotAgentInfo = useSetAtom(chatbotAgentInfoAtom);
  
  const selectAgent = (card: InsightCard) => {
    setChatbotAgentInfo({
      agent: card.id,
      title: card.title,
      file_url: fileUrl,
    });
  };

  return (
    <div className="space-y-2">
      {insightCards.map((card) => (
        <button 
          key={card.id}
          onClick={() => selectAgent(card)}
          className="w-full text-left p-3 border rounded hover:bg-gray-50"
        >
          {card.title}
        </button>
      ))}
    </div>
  );
}
```

### 5. Get All Titles for Other Uses

```typescript
import { getInsightCardTitles } from "@/shared/types/insights";

function InsightsList() {
  const titles = getInsightCardTitles();
  
  return (
    <ul>
      {titles.map((title, index) => (
        <li key={index}>{title}</li>
      ))}
    </ul>
  );
}
```

### 6. Type-Safe Usage

```typescript
import { type InsightCardId, INSIGHT_CARD_IDS } from "@/shared/types/insights";

// Use the type for function parameters
function handleInsightSelection(cardId: InsightCardId) {
  // TypeScript will enforce that only valid card IDs are passed
  console.log(`Selected: ${cardId}`);
}

// Usage with constants (type-safe)
handleInsightSelection(INSIGHT_CARD_IDS.ANOMALY); // ✅ Valid
handleInsightSelection("invalid-id"); // ❌ TypeScript error
```

### 7. Dynamic Icon Rendering

```typescript
import { getInsightCardById } from "@/shared/types/insights";

function DynamicInsightIcon({ cardId, className }: { cardId: string; className?: string }) {
  const card = getInsightCardById(cardId);
  if (!card) return null;
  
  const IconComponent = card.icon;
  return <IconComponent className={className} />;
}

// Usage
<DynamicInsightIcon cardId="business" className="h-6 w-6 text-blue-500" />
```

## Available Card IDs

- `anomaly` - Anomaly Detection
- `business` - Business Analysis
- `eda` - EDA Analysis
- `visualization` - Data Visualization

## Available Constants

```typescript
INSIGHT_CARD_IDS.ANOMALY        // "anomaly"
INSIGHT_CARD_IDS.BUSINESS       // "business"
INSIGHT_CARD_IDS.EDA           // "eda"
INSIGHT_CARD_IDS.VISUALIZATION // "visualization"
```

## TypeScript Types

```typescript
interface InsightCard {
  id: string;
  title: string;
  description: string;
  icon: LucideIcon;
}

type InsightCardId = "anomaly" | "business" | "eda" | "visualization";
```

## Best Practices

1. **Use constants**: Always use `INSIGHT_CARD_IDS` instead of hardcoded strings
2. **Type safety**: Use `InsightCardId` type for function parameters
3. **Icon rendering**: Extract the icon component and render as JSX `<IconComponent />`
4. **Error handling**: Check if `getInsightCardById()` returns a card before using it
5. **Reusability**: Import only what you need from the module 