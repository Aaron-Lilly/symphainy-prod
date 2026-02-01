'use client';

/**
 * Control Room View
 * 
 * Real-time platform observability and governance.
 * Automatically includes tenant context via useAdminAPIManager hook.
 * 
 * Displays:
 * - Platform Statistics
 * - Execution Metrics
 * - Realm Health
 * - Solution Registry Status
 * - System Health
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader } from '@/components/ui/loader';
import { useAdminAPIManager } from '@/shared/hooks/useAdminAPIManager';
import { useTenant } from '@/shared/contexts/TenantContext';
import type {
  PlatformStatistics,
  ExecutionMetrics,
  RealmHealth,
  SolutionRegistryStatus,
  SystemHealth,
} from '@/shared/managers/AdminAPIManager';
import { PlatformStatisticsCard } from './control-room/PlatformStatisticsCard';
import { ExecutionMetricsCard } from './control-room/ExecutionMetricsCard';
import { RealmHealthCard } from './control-room/RealmHealthCard';
import { SolutionRegistryCard } from './control-room/SolutionRegistryCard';
import { SystemHealthCard } from './control-room/SystemHealthCard';

export function ControlRoomView() {
  const adminAPIManager = useAdminAPIManager();
  const { tenantId } = useTenant();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Data state
  const [statistics, setStatistics] = useState<PlatformStatistics | null>(null);
  const [executionMetrics, setExecutionMetrics] = useState<ExecutionMetrics | null>(null);
  const [realmHealth, setRealmHealth] = useState<RealmHealth | null>(null);
  const [solutionRegistry, setSolutionRegistry] = useState<SolutionRegistryStatus | null>(null);
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);

  // Reload data when tenant changes
  useEffect(() => {
    loadControlRoomData();
  }, [tenantId]);

  const loadControlRoomData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Load all control room data in parallel
      const [
        stats,
        metrics,
        health,
        registry,
        system,
      ] = await Promise.all([
        adminAPIManager.getPlatformStatistics().catch(err => {
          console.error('Failed to load platform statistics:', err);
          return null;
        }),
        adminAPIManager.getExecutionMetrics('1h').catch(err => {
          console.error('Failed to load execution metrics:', err);
          return null;
        }),
        adminAPIManager.getRealmHealth().catch(err => {
          console.error('Failed to load realm health:', err);
          return null;
        }),
        adminAPIManager.getSolutionRegistryStatus().catch(err => {
          console.error('Failed to load solution registry:', err);
          return null;
        }),
        adminAPIManager.getSystemHealth().catch(err => {
          console.error('Failed to load system health:', err);
          return null;
        }),
      ]);

      setStatistics(stats);
      setExecutionMetrics(metrics);
      setRealmHealth(health);
      setSolutionRegistry(registry);
      setSystemHealth(system);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load control room data');
      console.error('Error loading control room data:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader />
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      {/* Platform Statistics & Execution Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {statistics && <PlatformStatisticsCard data={statistics} />}
        {executionMetrics && <ExecutionMetricsCard data={executionMetrics} />}
      </div>

      {/* Realm Health & Solution Registry */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {realmHealth && <RealmHealthCard data={realmHealth} />}
        {solutionRegistry && <SolutionRegistryCard data={solutionRegistry} />}
      </div>

      {/* System Health (Full Width) */}
      {systemHealth && <SystemHealthCard data={systemHealth} />}
    </div>
  );
}
