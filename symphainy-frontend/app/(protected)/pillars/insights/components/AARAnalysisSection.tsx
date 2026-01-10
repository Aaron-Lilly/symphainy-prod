/**
 * AARAnalysisSection Component
 * 
 * Expandable Navy AAR (After Action Report) analysis display
 * Shows lessons learned, risks, recommendations, and timeline
 */

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  ChevronDown, 
  ChevronUp, 
  Lightbulb, 
  AlertTriangle, 
  Target, 
  Clock 
} from 'lucide-react';

interface AARAnalysisSectionProps {
  aarAnalysis: {
    lessons_learned: Array<{
      lesson_id: string;
      category: string;
      description: string;
      importance: 'high' | 'medium' | 'low';
      actionable_steps?: string[];
    }>;
    risks: Array<{
      risk_id: string;
      category: string;
      description: string;
      severity: 'critical' | 'high' | 'medium' | 'low';
      mitigation_strategies?: string[];
    }>;
    recommendations: Array<{
      recommendation_id: string;
      area: string;
      recommendation: string;
      priority: 'high' | 'medium' | 'low';
      estimated_impact: string;
    }>;
    timeline?: Array<{
      timestamp: string;
      event: string;
      event_type: 'milestone' | 'incident' | 'decision' | 'outcome';
    }>;
  };
  defaultExpanded?: boolean;
}

export function AARAnalysisSection({ 
  aarAnalysis, 
  defaultExpanded = false 
}: AARAnalysisSectionProps) {
  const [expanded, setExpanded] = useState(defaultExpanded);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getImportanceColor = (importance: string) => {
    switch (importance) {
      case 'high':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'medium':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'low':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getEventTypeIcon = (eventType: string) => {
    switch (eventType) {
      case 'milestone':
        return '🎯';
      case 'incident':
        return '⚠️';
      case 'decision':
        return '🤔';
      case 'outcome':
        return '✅';
      default:
        return '📌';
    }
  };

  return (
    <Card className="border-2 border-blue-200">
      <CardHeader className="bg-gradient-to-r from-blue-50 to-indigo-50">
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Target className="h-5 w-5 text-blue-600" />
            <span>Navy AAR Analysis</span>
            <Badge variant="secondary" className="ml-2">Specialized</Badge>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? (
              <>
                <ChevronUp className="h-4 w-4 mr-1" />
                Collapse
              </>
            ) : (
              <>
                <ChevronDown className="h-4 w-4 mr-1" />
                Expand
              </>
            )}
          </Button>
        </CardTitle>
      </CardHeader>

      {expanded && (
        <CardContent className="pt-6 space-y-6">
          {/* Lessons Learned */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Lightbulb className="h-5 w-5 text-yellow-600" />
              <h3 className="text-lg font-semibold">Lessons Learned</h3>
              <Badge variant="outline">{aarAnalysis.lessons_learned.length}</Badge>
            </div>
            <div className="space-y-3">
              {aarAnalysis.lessons_learned.map((lesson) => (
                <div
                  key={lesson.lesson_id}
                  className={`p-4 rounded-lg border ${getImportanceColor(lesson.importance)}`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <Badge variant="secondary" className="text-xs mb-2">
                        {lesson.category}
                      </Badge>
                      <p className="font-medium text-sm">{lesson.description}</p>
                    </div>
                    <Badge className={getImportanceColor(lesson.importance)}>
                      {lesson.importance}
                    </Badge>
                  </div>
                  {lesson.actionable_steps && lesson.actionable_steps.length > 0 && (
                    <div className="mt-3 pl-4 border-l-2 border-current">
                      <p className="text-xs font-medium mb-1">Actionable Steps:</p>
                      <ul className="text-xs space-y-1">
                        {lesson.actionable_steps.map((step, idx) => (
                          <li key={idx}>• {step}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Risks */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <AlertTriangle className="h-5 w-5 text-red-600" />
              <h3 className="text-lg font-semibold">Risk Assessment</h3>
              <Badge variant="outline">{aarAnalysis.risks.length}</Badge>
            </div>
            <div className="space-y-3">
              {aarAnalysis.risks.map((risk) => (
                <div
                  key={risk.risk_id}
                  className={`p-4 rounded-lg border ${getSeverityColor(risk.severity)}`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <Badge variant="secondary" className="text-xs mb-2">
                        {risk.category}
                      </Badge>
                      <p className="font-medium text-sm">{risk.description}</p>
                    </div>
                    <Badge className={getSeverityColor(risk.severity)}>
                      {risk.severity}
                    </Badge>
                  </div>
                  {risk.mitigation_strategies && risk.mitigation_strategies.length > 0 && (
                    <div className="mt-3 pl-4 border-l-2 border-current">
                      <p className="text-xs font-medium mb-1">Mitigation Strategies:</p>
                      <ul className="text-xs space-y-1">
                        {risk.mitigation_strategies.map((strategy, idx) => (
                          <li key={idx}>• {strategy}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Recommendations */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Target className="h-5 w-5 text-green-600" />
              <h3 className="text-lg font-semibold">Recommendations</h3>
              <Badge variant="outline">{aarAnalysis.recommendations.length}</Badge>
            </div>
            <div className="space-y-3">
              {aarAnalysis.recommendations.map((rec) => (
                <div
                  key={rec.recommendation_id}
                  className="p-4 rounded-lg border border-green-200 bg-green-50"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <Badge variant="secondary" className="text-xs mb-2">
                        {rec.area}
                      </Badge>
                      <p className="font-medium text-sm text-green-900">{rec.recommendation}</p>
                    </div>
                    <Badge className={getImportanceColor(rec.priority)}>
                      {rec.priority}
                    </Badge>
                  </div>
                  <p className="text-xs text-green-700 mt-2">
                    <span className="font-medium">Estimated Impact:</span> {rec.estimated_impact}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Timeline */}
          {aarAnalysis.timeline && aarAnalysis.timeline.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-4">
                <Clock className="h-5 w-5 text-indigo-600" />
                <h3 className="text-lg font-semibold">Timeline</h3>
                <Badge variant="outline">{aarAnalysis.timeline.length}</Badge>
              </div>
              <div className="relative pl-8 border-l-2 border-indigo-200">
                {aarAnalysis.timeline.map((item, idx) => (
                  <div key={idx} className="mb-4 relative">
                    <div className="absolute left-[-2.15rem] top-1 w-6 h-6 rounded-full bg-indigo-100 border-2 border-indigo-300 flex items-center justify-center text-xs">
                      {getEventTypeIcon(item.event_type)}
                    </div>
                    <div className="bg-white p-3 rounded-lg border border-gray-200">
                      <p className="text-xs text-gray-500 mb-1">
                        {new Date(item.timestamp).toLocaleString()}
                      </p>
                      <p className="text-sm font-medium text-gray-900">{item.event}</p>
                      <Badge variant="outline" className="text-xs mt-2">
                        {item.event_type}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      )}
    </Card>
  );
}








