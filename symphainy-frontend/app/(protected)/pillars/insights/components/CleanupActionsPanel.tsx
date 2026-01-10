/**
 * CleanupActionsPanel Component
 * 
 * Displays cleanup actions for structured→structured mappings
 * Shows prioritized actions with examples and export functionality
 */

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { 
  Download, 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  ArrowRight,
  FileText
} from 'lucide-react';
import { CleanupAction } from '@/shared/services/insights/types';

interface CleanupActionsPanelProps {
  cleanupActions: CleanupAction[];
  onExport?: () => void;
}

export function CleanupActionsPanel({ 
  cleanupActions,
  onExport 
}: CleanupActionsPanelProps) {
  const [selectedPriority, setSelectedPriority] = useState<string>('all');
  const [selectedActionType, setSelectedActionType] = useState<string>('all');
  const [expandedAction, setExpandedAction] = useState<string | null>(null);

  // Filter actions
  const filteredActions = cleanupActions.filter(action => {
    if (selectedPriority !== 'all' && action.priority !== selectedPriority) return false;
    if (selectedActionType !== 'all' && action.action_type !== selectedActionType) return false;
    return true;
  });

  // Sort by priority (high > medium > low)
  const sortedActions = [...filteredActions].sort((a, b) => {
    const priorityOrder = { high: 3, medium: 2, low: 1 };
    return priorityOrder[b.priority] - priorityOrder[a.priority];
  });

  // Group by priority
  const actionsByPriority = cleanupActions.reduce((acc, action) => {
    if (!acc[action.priority]) acc[action.priority] = [];
    acc[action.priority].push(action);
    return acc;
  }, {} as Record<string, CleanupAction[]>);

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'medium':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      case 'low':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      default:
        return null;
    }
  };

  const getActionTypeLabel = (actionType: string) => {
    const labels: Record<string, string> = {
      fix_missing: 'Fix Missing Fields',
      fix_format: 'Fix Format Issues',
      fix_type: 'Fix Type Issues',
      transform: 'Transform Data'
    };
    return labels[actionType] || actionType;
  };

  return (
    <div className="space-y-6">
      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Actions</p>
                <p className="text-2xl font-bold">{cleanupActions.length}</p>
              </div>
              <FileText className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">High Priority</p>
                <p className="text-2xl font-bold text-red-600">
                  {actionsByPriority.high?.length || 0}
                </p>
              </div>
              <XCircle className="h-8 w-8 text-red-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Medium Priority</p>
                <p className="text-2xl font-bold text-yellow-600">
                  {actionsByPriority.medium?.length || 0}
                </p>
              </div>
              <AlertTriangle className="h-8 w-8 text-yellow-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Low Priority</p>
                <p className="text-2xl font-bold text-green-600">
                  {actionsByPriority.low?.length || 0}
                </p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Export */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-lg">Cleanup Actions</CardTitle>
              <CardDescription>
                {filteredActions.length} of {cleanupActions.length} actions
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <Select value={selectedPriority} onValueChange={setSelectedPriority}>
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="Priority" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Priority</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="low">Low</SelectItem>
                </SelectContent>
              </Select>
              <Select value={selectedActionType} onValueChange={setSelectedActionType}>
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="Action Type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  <SelectItem value="fix_missing">Fix Missing</SelectItem>
                  <SelectItem value="fix_format">Fix Format</SelectItem>
                  <SelectItem value="fix_type">Fix Type</SelectItem>
                  <SelectItem value="transform">Transform</SelectItem>
                </SelectContent>
              </Select>
              {onExport && (
                <Button variant="outline" onClick={onExport}>
                  <Download className="h-4 w-4 mr-2" />
                  Export Report
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {sortedActions.length > 0 ? (
              sortedActions.map((action) => (
                <Card
                  key={action.action_id}
                  className={`border-l-4 ${
                    action.priority === 'high' ? 'border-l-red-500' :
                    action.priority === 'medium' ? 'border-l-yellow-500' :
                    'border-l-green-500'
                  }`}
                >
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3 flex-1">
                        {getPriorityIcon(action.priority)}
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <CardTitle className="text-base">{getActionTypeLabel(action.action_type)}</CardTitle>
                            <Badge
                              variant={
                                action.priority === 'high' ? 'destructive' :
                                action.priority === 'medium' ? 'default' : 'secondary'
                              }
                            >
                              {action.priority}
                            </Badge>
                          </div>
                          <CardDescription>{action.description}</CardDescription>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium text-gray-700">
                          {action.affected_records} records
                        </p>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {action.example_fix && (
                        <div className="bg-gray-50 rounded-lg p-3">
                          <p className="text-xs font-medium text-gray-700 mb-1">Example Fix:</p>
                          <div className="flex items-center gap-2">
                            <code className="text-xs bg-white px-2 py-1 rounded border flex-1">
                              {action.example_fix}
                            </code>
                          </div>
                        </div>
                      )}
                      {action.suggested_transformation && (
                        <div className="bg-blue-50 rounded-lg p-3">
                          <p className="text-xs font-medium text-blue-700 mb-1">Suggested Transformation:</p>
                          <code className="text-xs bg-white px-2 py-1 rounded border block">
                            {action.suggested_transformation}
                          </code>
                        </div>
                      )}
                      <div className="flex items-center gap-2 text-xs text-gray-500">
                        <span>Action ID: {action.action_id}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            ) : (
              <div className="text-center text-gray-500 py-8">
                No cleanup actions found matching your filters
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}









