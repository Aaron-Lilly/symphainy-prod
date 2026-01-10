import React from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Lightbulb, Sparkles } from 'lucide-react';

interface QuerySuggestionsProps {
  suggestions: string[];
  onSuggestionClick: (suggestion: string) => void;
  className?: string;
}

export function QuerySuggestions({ suggestions, onSuggestionClick, className = '' }: QuerySuggestionsProps) {
  return (
    <div className={`space-y-2 ${className}`}>
      <div className="flex items-center gap-2 text-sm text-gray-600">
        <Lightbulb className="h-4 w-4" />
        <span>Try these example queries:</span>
      </div>
      <div className="flex flex-wrap gap-2">
        {suggestions.map((suggestion, index) => (
          <Button
            key={index}
            variant="outline"
            size="sm"
            onClick={() => onSuggestionClick(suggestion)}
            className="text-xs h-auto py-1 px-2 whitespace-normal text-left"
          >
            <Sparkles className="h-3 w-3 mr-1 flex-shrink-0" />
            {suggestion}
          </Button>
        ))}
      </div>
    </div>
  );
} 