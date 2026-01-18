'use client';

/**
 * Developer View
 * 
 * Platform SDK documentation, playground, and feature submission.
 * Displays:
 * - Platform SDK Documentation
 * - Code Examples
 * - Patterns & Best Practices
 * - Solution Builder Playground (gated)
 * - Feature Submission (gated - "Coming Soon" for MVP)
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader } from '@/components/ui/loader';
import { useAdminAPIManager } from '@/shared/hooks/useAdminAPIManager';
import type {
  Documentation,
  CodeExamples,
  Patterns,
} from '@/shared/managers/AdminAPIManager';
import { DocumentationPanel } from './developer/DocumentationPanel';
import { CodeExamplesPanel } from './developer/CodeExamplesPanel';
import { PatternsPanel } from './developer/PatternsPanel';
import { SolutionBuilderPlayground } from './developer/SolutionBuilderPlayground';
import { FeatureSubmissionPanel } from './developer/FeatureSubmissionPanel';
import { BookOpen, Code2, Sparkles, Play, FileText } from 'lucide-react';

export function DeveloperView() {
  const adminAPIManager = useAdminAPIManager();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Data state
  const [documentation, setDocumentation] = useState<Documentation | null>(null);
  const [codeExamples, setCodeExamples] = useState<CodeExamples | null>(null);
  const [patterns, setPatterns] = useState<Patterns | null>(null);

  useEffect(() => {
    loadDeveloperData();
  }, []);

  const loadDeveloperData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Load developer view data in parallel
      const [docs, examples, pats] = await Promise.all([
        adminAPIManager.getDocumentation().catch(err => {
          console.error('Failed to load documentation:', err);
          return null;
        }),
        adminAPIManager.getCodeExamples().catch(err => {
          console.error('Failed to load code examples:', err);
          return null;
        }),
        adminAPIManager.getPatterns().catch(err => {
          console.error('Failed to load patterns:', err);
          return null;
        }),
      ]);

      setDocumentation(docs);
      setCodeExamples(examples);
      setPatterns(pats);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load developer view data');
      console.error('Error loading developer view data:', err);
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
    <Tabs defaultValue="documentation" className="w-full">
      <TabsList className="grid w-full grid-cols-5 mb-6">
        <TabsTrigger value="documentation" className="flex items-center gap-2">
          <BookOpen className="h-4 w-4" />
          Documentation
        </TabsTrigger>
        <TabsTrigger value="examples" className="flex items-center gap-2">
          <Code2 className="h-4 w-4" />
          Examples
        </TabsTrigger>
        <TabsTrigger value="patterns" className="flex items-center gap-2">
          <Sparkles className="h-4 w-4" />
          Patterns
        </TabsTrigger>
        <TabsTrigger value="playground" className="flex items-center gap-2">
          <Play className="h-4 w-4" />
          Playground
        </TabsTrigger>
        <TabsTrigger value="features" className="flex items-center gap-2">
          <FileText className="h-4 w-4" />
          Features
        </TabsTrigger>
      </TabsList>

      <TabsContent value="documentation" className="mt-0">
        {documentation ? (
          <DocumentationPanel data={documentation} />
        ) : (
          <Alert>
            <AlertDescription>Documentation not available</AlertDescription>
          </Alert>
        )}
      </TabsContent>

      <TabsContent value="examples" className="mt-0">
        {codeExamples ? (
          <CodeExamplesPanel data={codeExamples} />
        ) : (
          <Alert>
            <AlertDescription>Code examples not available</AlertDescription>
          </Alert>
        )}
      </TabsContent>

      <TabsContent value="patterns" className="mt-0">
        {patterns ? (
          <PatternsPanel data={patterns} />
        ) : (
          <Alert>
            <AlertDescription>Patterns not available</AlertDescription>
          </Alert>
        )}
      </TabsContent>

      <TabsContent value="playground" className="mt-0">
        <SolutionBuilderPlayground adminAPIManager={adminAPIManager} />
      </TabsContent>

      <TabsContent value="features" className="mt-0">
        <FeatureSubmissionPanel adminAPIManager={adminAPIManager} />
      </TabsContent>
    </Tabs>
  );
}
