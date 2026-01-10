'use client';

import React, { useState, useEffect } from 'react';
import MainLayout from '@/shared/components/MainLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader } from '@/components/ui/loader';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { getAdminDashboardSummary, type AdminDashboardSummary } from '@/lib/api/admin';
import { useGlobalSession } from '@/shared/agui/GlobalSessionProvider';
import PlatformHealthCard from '@/components/admin/PlatformHealthCard';
import UsageStatisticsCard from '@/components/admin/UsageStatisticsCard';
import PlatformJourneysSolutionsCard from '@/components/admin/PlatformJourneysSolutionsCard';
import CuratorRegistriesCard from '@/components/admin/CuratorRegistriesCard';
import ClientConfigCard from '@/components/admin/ClientConfigCard';

export default function AdminDashboard() {
  const { guideSessionToken } = useGlobalSession();
  const [dashboardData, setDashboardData] = useState<AdminDashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, [guideSessionToken]);

  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const token = guideSessionToken || "debug-token";
      const data = await getAdminDashboardSummary(token);
      setDashboardData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load admin dashboard');
      console.error('Error loading admin dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <MainLayout>
        <div className="container mx-auto p-6">
          <div className="flex items-center justify-center min-h-[400px]">
            <Loader />
          </div>
        </div>
      </MainLayout>
    );
  }

  if (error) {
    return (
      <MainLayout>
        <div className="container mx-auto p-6">
          <Alert variant="destructive">
            <AlertDescription>
              {error}
            </AlertDescription>
          </Alert>
        </div>
      </MainLayout>
    );
  }

  if (!dashboardData || !dashboardData.success) {
    return (
      <MainLayout>
        <div className="container mx-auto p-6">
          <Alert variant="destructive">
            <AlertDescription>
              {dashboardData?.error || 'Failed to load admin dashboard data'}
            </AlertDescription>
          </Alert>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="container mx-auto p-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">Admin Dashboard</h1>
          <p className="text-muted-foreground">
            Comprehensive platform monitoring and management
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <PlatformHealthCard data={dashboardData} />
          <UsageStatisticsCard data={dashboardData} />
          <PlatformJourneysSolutionsCard data={dashboardData} />
          <CuratorRegistriesCard data={dashboardData} />
        </div>
        
        <div className="mt-6">
          <ClientConfigCard data={dashboardData} />
        </div>
      </div>
    </MainLayout>
  );
}







