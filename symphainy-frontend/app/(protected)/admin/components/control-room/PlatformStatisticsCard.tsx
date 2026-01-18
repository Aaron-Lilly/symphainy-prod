'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import type { PlatformStatistics } from '@/shared/managers/AdminAPIManager';
import { CheckCircle2, XCircle, Clock, Activity } from 'lucide-react';

interface PlatformStatisticsCardProps {
  data: PlatformStatistics;
}

export function PlatformStatisticsCard({ data }: PlatformStatisticsCardProps) {
  const successRate = data.success_rate * 100;
  const failureRate = (1 - data.success_rate) * 100;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-5 w-5" />
          Platform Statistics
        </CardTitle>
        <CardDescription>Overall platform execution metrics</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Intent Metrics */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-sm text-muted-foreground">Total Intents</div>
            <div className="text-2xl font-bold">{data.total_intents.toLocaleString()}</div>
          </div>
          <div>
            <div className="text-sm text-muted-foreground">Active Sessions</div>
            <div className="text-2xl font-bold">{data.active_sessions.toLocaleString()}</div>
          </div>
        </div>

        {/* Success/Failure Rates */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="flex items-center gap-2 text-green-600">
              <CheckCircle2 className="h-4 w-4" />
              Success Rate
            </span>
            <span className="font-semibold">{successRate.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-muted rounded-full h-2">
            <div
              className="bg-green-600 h-2 rounded-full transition-all"
              style={{ width: `${successRate}%` }}
            />
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="flex items-center gap-2 text-red-600">
              <XCircle className="h-4 w-4" />
              Failure Rate
            </span>
            <span className="font-semibold">{failureRate.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-muted rounded-full h-2">
            <div
              className="bg-red-600 h-2 rounded-full transition-all"
              style={{ width: `${failureRate}%` }}
            />
          </div>
        </div>

        {/* Average Execution Time */}
        <div className="pt-2 border-t">
          <div className="flex items-center justify-between">
            <span className="flex items-center gap-2 text-sm text-muted-foreground">
              <Clock className="h-4 w-4" />
              Avg Execution Time
            </span>
            <span className="font-semibold">
              {(data.average_execution_time / 1000).toFixed(2)}s
            </span>
          </div>
        </div>

        {/* Realm Health Summary */}
        {Object.keys(data.realm_health).length > 0 && (
          <div className="pt-2 border-t">
            <div className="text-sm font-semibold mb-2">Realm Health</div>
            <div className="space-y-1">
              {Object.entries(data.realm_health).map(([realm, health]) => (
                <div key={realm} className="flex items-center justify-between text-sm">
                  <span className="capitalize">{realm}</span>
                  <span
                    className={`px-2 py-1 rounded text-xs font-medium ${
                      health.status === 'healthy'
                        ? 'bg-green-100 text-green-800'
                        : health.status === 'degraded'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-red-100 text-red-800'
                    }`}
                  >
                    {health.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
