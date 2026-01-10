'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Activity, CheckCircle2, AlertCircle, XCircle } from 'lucide-react';
import type { AdminDashboardSummary } from '@/lib/api/admin';

interface PlatformHealthCardProps {
  data: AdminDashboardSummary;
}

export default function PlatformHealthCard({ data }: PlatformHealthCardProps) {
  const platformHealth = data.platform_health || {};
  const dashboardSummary = data.dashboard_summary || {};
  
  // Determine overall health status
  const getHealthStatus = () => {
    if (platformHealth.status === 'healthy') return { status: 'healthy', color: 'bg-green-500', icon: CheckCircle2 };
    if (platformHealth.status === 'degraded') return { status: 'degraded', color: 'bg-yellow-500', icon: AlertCircle };
    return { status: 'unhealthy', color: 'bg-red-500', icon: XCircle };
  };

  const healthStatus = getHealthStatus();
  const StatusIcon = healthStatus.icon;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-5 w-5" />
          Platform Health
        </CardTitle>
        <CardDescription>
          Overall platform health and service status
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Overall Status</span>
            <Badge variant={healthStatus.status === 'healthy' ? 'default' : 'destructive'} className="flex items-center gap-1">
              <StatusIcon className="h-3 w-3" />
              {healthStatus.status.toUpperCase()}
            </Badge>
          </div>
          
          {platformHealth.services && (
            <div className="space-y-2">
              <div className="text-sm font-medium">Service Health</div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                {Object.entries(platformHealth.services || {}).map(([service, status]: [string, any]) => (
                  <div key={service} className="flex items-center justify-between">
                    <span className="truncate">{service}</span>
                    <Badge variant={status === 'healthy' ? 'default' : 'destructive'} className="ml-2">
                      {status || 'unknown'}
                    </Badge>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {dashboardSummary.wal_operations && (
            <div className="pt-2 border-t">
              <div className="text-sm font-medium mb-2">WAL Operations</div>
              <div className="text-xs text-muted-foreground">
                {JSON.stringify(dashboardSummary.wal_operations, null, 2)}
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}







