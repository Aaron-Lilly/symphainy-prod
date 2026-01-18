'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import type { RealmHealth } from '@/shared/managers/AdminAPIManager';
import { Heart, AlertTriangle, XCircle } from 'lucide-react';

interface RealmHealthCardProps {
  data: RealmHealth;
}

export function RealmHealthCard({ data }: RealmHealthCardProps) {
  const getHealthIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <Heart className="h-4 w-4 text-green-600" />;
      case 'degraded':
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
      case 'unhealthy':
        return <XCircle className="h-4 w-4 text-red-600" />;
      default:
        return <AlertTriangle className="h-4 w-4 text-gray-600" />;
    }
  };

  const getHealthColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'degraded':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'unhealthy':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Heart className="h-5 w-5" />
          Realm Health
        </CardTitle>
        <CardDescription>
          Status: <span className="capitalize font-semibold">{data.overall_health}</span>
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {Object.entries(data.realms).map(([realm, health]) => (
          <div
            key={realm}
            className={`p-3 rounded-lg border ${getHealthColor(health.status)}`}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                {getHealthIcon(health.status)}
                <span className="font-semibold capitalize">{realm}</span>
              </div>
              <span className="text-xs font-medium capitalize">{health.status}</span>
            </div>
            <div className="grid grid-cols-3 gap-2 text-xs mt-2">
              <div>
                <div className="text-muted-foreground">Intents</div>
                <div className="font-semibold">{health.intent_count.toLocaleString()}</div>
              </div>
              <div>
                <div className="text-muted-foreground">Response</div>
                <div className="font-semibold">{health.response_time_ms.toFixed(0)}ms</div>
              </div>
              <div>
                <div className="text-muted-foreground">Error Rate</div>
                <div className="font-semibold">{(health.error_rate * 100).toFixed(1)}%</div>
              </div>
            </div>
            {health.last_activity && (
              <div className="text-xs text-muted-foreground mt-2">
                Last activity: {new Date(health.last_activity).toLocaleString()}
              </div>
            )}
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
