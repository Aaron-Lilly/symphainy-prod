'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import type { SystemHealth } from '@/shared/managers/AdminAPIManager';
import { Server, Database, HardDrive, Activity } from 'lucide-react';

interface SystemHealthCardProps {
  data: SystemHealth;
}

export function SystemHealthCard({ data }: SystemHealthCardProps) {
  const getHealthBadge = (status: string) => {
    const colors = {
      healthy: 'bg-green-100 text-green-800 border-green-200',
      degraded: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      unhealthy: 'bg-red-100 text-red-800 border-red-200',
    };
    return (
      <span
        className={`px-2 py-1 rounded text-xs font-medium border ${
          colors[status as keyof typeof colors] || colors.degraded
        }`}
      >
        {status}
      </span>
    );
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Server className="h-5 w-5" />
          System Health
        </CardTitle>
        <CardDescription>Infrastructure and observability status</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Runtime Health */}
        <div className="space-y-3">
          <div className="flex items-center gap-2 font-semibold">
            <Activity className="h-4 w-4" />
            Runtime
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 pl-6">
            <div>
              <div className="text-xs text-muted-foreground mb-1">Status</div>
              {getHealthBadge(data.runtime.status)}
            </div>
            <div>
              <div className="text-xs text-muted-foreground mb-1">WAL</div>
              {getHealthBadge(data.runtime.wal_health)}
            </div>
            <div>
              <div className="text-xs text-muted-foreground mb-1">State Surface</div>
              {getHealthBadge(data.runtime.state_surface_health)}
            </div>
          </div>
        </div>

        {/* Infrastructure Health */}
        <div className="space-y-3 pt-3 border-t">
          <div className="flex items-center gap-2 font-semibold">
            <Database className="h-4 w-4" />
            Infrastructure
          </div>
          <div className="pl-6 space-y-3">
            <div>
              <div className="text-xs text-muted-foreground mb-2">Databases</div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <div className="text-xs mb-1">ArangoDB</div>
                  {getHealthBadge(data.infrastructure.database.arangodb)}
                </div>
                <div>
                  <div className="text-xs mb-1">Redis</div>
                  {getHealthBadge(data.infrastructure.database.redis)}
                </div>
              </div>
            </div>
            <div>
              <div className="text-xs text-muted-foreground mb-2">Storage</div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <div className="text-xs mb-1">GCS</div>
                  {getHealthBadge(data.infrastructure.storage.gcs)}
                </div>
                <div>
                  <div className="text-xs mb-1">Supabase</div>
                  {getHealthBadge(data.infrastructure.storage.supabase)}
                </div>
              </div>
            </div>
            <div>
              <div className="text-xs text-muted-foreground mb-1">Telemetry</div>
              {getHealthBadge(data.infrastructure.telemetry)}
            </div>
          </div>
        </div>

        {/* Observability Health */}
        <div className="space-y-3 pt-3 border-t">
          <div className="flex items-center gap-2 font-semibold">
            <HardDrive className="h-4 w-4" />
            Observability
          </div>
          <div className="grid grid-cols-3 gap-3 pl-6">
            <div>
              <div className="text-xs text-muted-foreground mb-1">OpenTelemetry</div>
              {getHealthBadge(data.observability.opentelemetry)}
            </div>
            <div>
              <div className="text-xs text-muted-foreground mb-1">Prometheus</div>
              {getHealthBadge(data.observability.prometheus)}
            </div>
            <div>
              <div className="text-xs text-muted-foreground mb-1">Tempo</div>
              {getHealthBadge(data.observability.tempo)}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
