'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Settings, CheckCircle2, AlertCircle } from 'lucide-react';
import type { AdminDashboardSummary } from '@/lib/api/admin';

interface ClientConfigCardProps {
  data: AdminDashboardSummary;
}

export default function ClientConfigCard({ data }: ClientConfigCardProps) {
  const clientConfig = data.client_config_status || {};
  const instances = clientConfig.instances_summary || {};
  
  const infrastructure = instances.infrastructure || {};
  const heads = instances.heads || {};

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Settings className="h-5 w-5" />
          Client Config Foundation
        </CardTitle>
        <CardDescription>
          Infrastructure and head SDK status
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* SDK Status */}
          <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
            <div className="flex items-center gap-2">
              {clientConfig.sdk_status === 'ready' ? (
                <CheckCircle2 className="h-5 w-5 text-green-600" />
              ) : (
                <AlertCircle className="h-5 w-5 text-yellow-600" />
              )}
              <span className="font-medium">SDK Status</span>
            </div>
            <Badge variant={clientConfig.sdk_status === 'ready' ? 'default' : 'secondary'}>
              {clientConfig.sdk_status || 'unknown'}
            </Badge>
          </div>
          
          {/* Infrastructure Summary */}
          <div className="space-y-2">
            <div className="text-sm font-medium">Infrastructure Abstractions</div>
            <div className="flex items-center justify-between p-2 bg-muted rounded">
              <span className="text-sm">Total Registered</span>
              <span className="font-bold">{infrastructure.total || 0}</span>
            </div>
            {infrastructure.by_type && Object.keys(infrastructure.by_type).length > 0 && (
              <div className="text-xs text-muted-foreground">
                {Object.entries(infrastructure.by_type).map(([type, count]) => (
                  <div key={type} className="flex justify-between">
                    <span>{type}</span>
                    <span>{count as number}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          {/* Heads Summary */}
          <div className="space-y-2">
            <div className="text-sm font-medium">Custom Heads</div>
            <div className="flex items-center justify-between p-2 bg-muted rounded">
              <span className="text-sm">Total Created</span>
              <span className="font-bold">{heads.total || 0}</span>
            </div>
            {heads.by_type && Object.keys(heads.by_type).length > 0 && (
              <div className="text-xs text-muted-foreground">
                {Object.entries(heads.by_type).map(([type, count]) => (
                  <div key={type} className="flex justify-between">
                    <span>{type}</span>
                    <span>{count as number}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          {/* Service Status */}
          <div className="pt-4 border-t">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Service Status</span>
              <Badge variant={clientConfig.status === 'healthy' ? 'default' : 'destructive'}>
                {clientConfig.status || 'unknown'}
              </Badge>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}







