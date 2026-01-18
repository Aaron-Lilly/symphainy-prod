'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import type { AdminAPIManager } from '@/shared/managers/AdminAPIManager';

interface FeatureSubmissionPanelProps {
  adminAPIManager: AdminAPIManager;
}

export function FeatureSubmissionPanel({ adminAPIManager }: FeatureSubmissionPanelProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    setSubmitting(true);
    setError(null);
    setResult(null);

    try {
      const response = await adminAPIManager.submitFeatureRequest({
        title,
        description,
        category: category || undefined,
      });
      setResult(response);
      if (response.status === 'coming_soon') {
        // Clear form on success
        setTitle('');
        setDescription('');
        setCategory('');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Submission failed');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Feature Submission</CardTitle>
        <CardDescription>
          Submit feature proposals for platform team review (gated - "Coming Soon" for MVP)
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <label className="text-sm font-medium mb-2 block">Title</label>
          <Input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Feature title"
          />
        </div>
        <div>
          <label className="text-sm font-medium mb-2 block">Description</label>
          <Textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe the feature proposal"
            rows={6}
          />
        </div>
        <div>
          <label className="text-sm font-medium mb-2 block">Category (optional)</label>
          <Input
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            placeholder="e.g., SDK, Platform, Realm"
          />
        </div>
        <Button onClick={handleSubmit} disabled={submitting || !title || !description}>
          {submitting ? 'Submitting...' : 'Submit Feature Request'}
        </Button>
        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
        {result && (
          <Alert>
            <AlertDescription>
              {result.message || result.status === 'coming_soon'
                ? 'Feature submission is coming soon! This will enable developers to submit feature proposals for platform team review.'
                : 'Feature request submitted successfully!'}
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
}
