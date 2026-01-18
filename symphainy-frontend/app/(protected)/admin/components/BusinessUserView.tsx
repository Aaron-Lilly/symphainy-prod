'use client';

/**
 * Business User View
 * 
 * Solution composition, templates, and feature requests.
 * Displays:
 * - Solution Composition Guide
 * - Solution Templates (gated)
 * - Solution Builder (advanced - gated)
 * - Feature Request System
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader } from '@/components/ui/loader';
import { useAdminAPIManager } from '@/shared/hooks/useAdminAPIManager';
import type {
  CompositionGuide,
  SolutionTemplates,
} from '@/shared/managers/AdminAPIManager';
import { CompositionGuidePanel } from './business/CompositionGuidePanel';
import { SolutionTemplatesPanel } from './business/SolutionTemplatesPanel';
import { SolutionBuilderPanel } from './business/SolutionBuilderPanel';
import { FeatureRequestPanel } from './business/FeatureRequestPanel';
import { BookOpen, Layout, Wrench, FileText } from 'lucide-react';

export function BusinessUserView() {
  const adminAPIManager = useAdminAPIManager();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Data state
  const [compositionGuide, setCompositionGuide] = useState<CompositionGuide | null>(null);
  const [solutionTemplates, setSolutionTemplates] = useState<SolutionTemplates | null>(null);

  useEffect(() => {
    loadBusinessData();
  }, []);

  const loadBusinessData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Load business view data
      const [guide, templates] = await Promise.all([
        adminAPIManager.getCompositionGuide().catch(err => {
          console.error('Failed to load composition guide:', err);
          return null;
        }),
        adminAPIManager.getSolutionTemplates().catch(err => {
          // Templates are gated, so this might fail - that's OK
          console.warn('Solution templates not available (may be gated):', err);
          return null;
        }),
      ]);

      setCompositionGuide(guide);
      setSolutionTemplates(templates);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load business view data');
      console.error('Error loading business view data:', err);
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
    <Tabs defaultValue="guide" className="w-full">
      <TabsList className="grid w-full grid-cols-4 mb-6">
        <TabsTrigger value="guide" className="flex items-center gap-2">
          <BookOpen className="h-4 w-4" />
          Composition Guide
        </TabsTrigger>
        <TabsTrigger value="templates" className="flex items-center gap-2">
          <Layout className="h-4 w-4" />
          Templates
        </TabsTrigger>
        <TabsTrigger value="builder" className="flex items-center gap-2">
          <Wrench className="h-4 w-4" />
          Builder
        </TabsTrigger>
        <TabsTrigger value="features" className="flex items-center gap-2">
          <FileText className="h-4 w-4" />
          Feature Requests
        </TabsTrigger>
      </TabsList>

      <TabsContent value="guide" className="mt-0">
        {compositionGuide ? (
          <CompositionGuidePanel data={compositionGuide} />
        ) : (
          <Alert>
            <AlertDescription>Composition guide not available</AlertDescription>
          </Alert>
        )}
      </TabsContent>

      <TabsContent value="templates" className="mt-0">
        {solutionTemplates ? (
          <SolutionTemplatesPanel data={solutionTemplates} adminAPIManager={adminAPIManager} />
        ) : (
          <Alert>
            <AlertDescription>
              Solution templates are not available. This feature may be gated or not yet enabled.
            </AlertDescription>
          </Alert>
        )}
      </TabsContent>

      <TabsContent value="builder" className="mt-0">
        <SolutionBuilderPanel adminAPIManager={adminAPIManager} />
      </TabsContent>

      <TabsContent value="features" className="mt-0">
        <FeatureRequestPanel adminAPIManager={adminAPIManager} />
      </TabsContent>
    </Tabs>
  );
}
