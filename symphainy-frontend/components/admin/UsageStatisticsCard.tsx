'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart3, TrendingUp } from 'lucide-react';
import type { AdminDashboardSummary } from '@/lib/api/admin';

interface UsageStatisticsCardProps {
  data: AdminDashboardSummary;
}

export default function UsageStatisticsCard({ data }: UsageStatisticsCardProps) {
  const stats = data.usage_statistics || {};
  
  const metrics = [
    { label: 'Active Users', value: stats.active_users || 0, icon: '👥' },
    { label: 'API Requests', value: stats.api_requests || 0, icon: '📡' },
    { label: 'Agent Invocations', value: stats.agent_invocations || 0, icon: '🤖' },
    { label: 'Artifacts Created', value: stats.artifacts_created || 0, icon: '📄' },
    { label: 'Journeys Created', value: stats.journeys_created || 0, icon: '🗺️' },
    { label: 'Solutions Created', value: stats.solutions_created || 0, icon: '🎯' },
  ];

  const conversionRate = stats.artifact_conversion_rate 
    ? (stats.artifact_conversion_rate * 100).toFixed(1) 
    : '0.0';

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5" />
          Usage Statistics
        </CardTitle>
        <CardDescription>
          Platform usage metrics for {stats.time_range || '24h'}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            {metrics.map((metric) => (
              <div key={metric.label} className="flex items-center justify-between p-2 bg-muted rounded">
                <div className="flex items-center gap-2">
                  <span className="text-lg">{metric.icon}</span>
                  <span className="text-sm font-medium">{metric.label}</span>
                </div>
                <span className="text-lg font-bold">{metric.value}</span>
              </div>
            ))}
          </div>
          
          {stats.artifacts_created && stats.artifacts_created > 0 && (
            <div className="pt-4 border-t">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <TrendingUp className="h-4 w-4" />
                  <span className="text-sm font-medium">Conversion Rate</span>
                </div>
                <span className="text-lg font-bold">{conversionRate}%</span>
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                {(stats.journeys_created || 0) + (stats.solutions_created || 0)} of {stats.artifacts_created} artifacts converted
              </p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}







