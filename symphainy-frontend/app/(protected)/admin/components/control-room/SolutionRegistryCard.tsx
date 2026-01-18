'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import type { SolutionRegistryStatus } from '@/shared/managers/AdminAPIManager';
import { Package, CheckCircle2, XCircle, AlertCircle } from 'lucide-react';

interface SolutionRegistryCardProps {
  data: SolutionRegistryStatus;
}

export function SolutionRegistryCard({ data }: SolutionRegistryCardProps) {
  const activeRate = data.total_solutions > 0
    ? (data.active_solutions / data.total_solutions) * 100
    : 0;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Package className="h-5 w-5" />
          Solution Registry
        </CardTitle>
        <CardDescription>Registered solutions and their status</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Overview */}
        <div className="grid grid-cols-3 gap-4">
          <div>
            <div className="text-sm text-muted-foreground">Total</div>
            <div className="text-2xl font-bold">{data.total_solutions}</div>
          </div>
          <div>
            <div className="text-sm text-muted-foreground">Active</div>
            <div className="text-2xl font-bold text-green-600">
              {data.active_solutions}
            </div>
          </div>
          <div>
            <div className="text-sm text-muted-foreground">Inactive</div>
            <div className="text-2xl font-bold text-gray-600">
              {data.inactive_solutions}
            </div>
          </div>
        </div>

        {/* Active Rate */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span>Active Rate</span>
            <span className="font-semibold">{activeRate.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-muted rounded-full h-2">
            <div
              className="bg-green-600 h-2 rounded-full transition-all"
              style={{ width: `${activeRate}%` }}
            />
          </div>
        </div>

        {/* Solutions by Domain */}
        {Object.keys(data.solutions_by_domain).length > 0 && (
          <div className="pt-2 border-t">
            <div className="text-sm font-semibold mb-2">By Domain</div>
            <div className="space-y-1">
              {Object.entries(data.solutions_by_domain)
                .sort(([, a], [, b]) => b - a)
                .map(([domain, count]) => (
                  <div key={domain} className="flex items-center justify-between text-sm">
                    <span className="capitalize">{domain}</span>
                    <span className="font-medium">{count}</span>
                  </div>
                ))}
            </div>
          </div>
        )}

        {/* Solution Health Summary */}
        {Object.keys(data.solution_health).length > 0 && (
          <div className="pt-2 border-t">
            <div className="text-sm font-semibold mb-2">Health Summary</div>
            <div className="space-y-1">
              {Object.entries(data.solution_health)
                .slice(0, 5)
                .map(([solution, health]) => (
                  <div key={solution} className="flex items-center justify-between text-sm">
                    <span className="truncate flex-1">{solution}</span>
                    <div className="flex items-center gap-2">
                      <span
                        className={`px-2 py-1 rounded text-xs font-medium ${
                          health.status === 'active'
                            ? 'bg-green-100 text-green-800'
                            : health.status === 'inactive'
                            ? 'bg-gray-100 text-gray-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {health.status}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {(health.success_rate * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
