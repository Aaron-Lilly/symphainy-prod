'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import type { ExecutionMetrics } from '@/shared/managers/AdminAPIManager';
import { TrendingUp, Timer, AlertCircle } from 'lucide-react';

interface ExecutionMetricsCardProps {
  data: ExecutionMetrics;
}

export function ExecutionMetricsCard({ data }: ExecutionMetricsCardProps) {
  const successRate = data.total_executions > 0
    ? (data.successful_executions / data.total_executions) * 100
    : 0;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5" />
          Execution Metrics
        </CardTitle>
        <CardDescription>Performance metrics for {data.time_range}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Key Metrics */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-sm text-muted-foreground">Total Executions</div>
            <div className="text-2xl font-bold">{data.total_executions.toLocaleString()}</div>
          </div>
          <div>
            <div className="text-sm text-muted-foreground">Throughput</div>
            <div className="text-2xl font-bold">{data.throughput.toFixed(1)}/min</div>
          </div>
        </div>

        {/* Success/Failure */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-sm text-muted-foreground">Successful</div>
            <div className="text-xl font-semibold text-green-600">
              {data.successful_executions.toLocaleString()}
            </div>
            <div className="text-xs text-muted-foreground">
              {successRate.toFixed(1)}% success rate
            </div>
          </div>
          <div>
            <div className="text-sm text-muted-foreground">Failed</div>
            <div className="text-xl font-semibold text-red-600">
              {data.failed_executions.toLocaleString()}
            </div>
            <div className="text-xs text-muted-foreground">
              {data.error_rate.toFixed(2)}% error rate
            </div>
          </div>
        </div>

        {/* Performance Times */}
        <div className="pt-2 border-t space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="flex items-center gap-2 text-muted-foreground">
              <Timer className="h-4 w-4" />
              Average Time
            </span>
            <span className="font-semibold">
              {(data.average_execution_time / 1000).toFixed(2)}s
            </span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">P95 Time</span>
            <span className="font-semibold">
              {(data.p95_execution_time / 1000).toFixed(2)}s
            </span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">P99 Time</span>
            <span className="font-semibold">
              {(data.p99_execution_time / 1000).toFixed(2)}s
            </span>
          </div>
        </div>

        {/* Executions by Type */}
        {Object.keys(data.executions_by_type).length > 0 && (
          <div className="pt-2 border-t">
            <div className="text-sm font-semibold mb-2">By Intent Type</div>
            <div className="space-y-1 max-h-32 overflow-y-auto">
              {Object.entries(data.executions_by_type)
                .sort(([, a], [, b]) => b - a)
                .slice(0, 5)
                .map(([type, count]) => (
                  <div key={type} className="flex items-center justify-between text-sm">
                    <span className="truncate">{type}</span>
                    <span className="font-medium">{count}</span>
                  </div>
                ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
