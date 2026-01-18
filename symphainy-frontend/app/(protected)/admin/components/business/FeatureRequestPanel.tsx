'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import type { AdminAPIManager } from '@/shared/managers/AdminAPIManager';

interface FeatureRequestPanelProps {
  adminAPIManager: AdminAPIManager;
}

export function FeatureRequestPanel({ adminAPIManager }: FeatureRequestPanelProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [businessNeed, setBusinessNeed] = useState('');
  const [priority, setPriority] = useState<'low' | 'medium' | 'high'>('medium');
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    setSubmitting(true);
    setError(null);
    setResult(null);

    try {
      const response = await adminAPIManager.submitBusinessFeatureRequest({
        title,
        description,
        business_need: businessNeed,
        priority,
      });
      setResult(response);
      if (response.success) {
        // Clear form on success
        setTitle('');
        setDescription('');
        setBusinessNeed('');
        setPriority('medium');
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
        <CardTitle>Feature Request</CardTitle>
        <CardDescription>
          Submit feature requests for new platform capabilities
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <label className="text-sm font-medium mb-2 block">Title</label>
          <Input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Feature request title"
          />
        </div>
        <div>
          <label className="text-sm font-medium mb-2 block">Description</label>
          <Textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe the feature request"
            rows={4}
          />
        </div>
        <div>
          <label className="text-sm font-medium mb-2 block">Business Need</label>
          <Textarea
            value={businessNeed}
            onChange={(e) => setBusinessNeed(e.target.value)}
            placeholder="Explain the business need for this feature"
            rows={4}
          />
        </div>
        <div>
          <label className="text-sm font-medium mb-2 block">Priority</label>
          <Select value={priority} onValueChange={(value: 'low' | 'medium' | 'high') => setPriority(value)}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="low">Low</SelectItem>
              <SelectItem value="medium">Medium</SelectItem>
              <SelectItem value="high">High</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <Button
          onClick={handleSubmit}
          disabled={submitting || !title || !description || !businessNeed}
        >
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
              {result.success
                ? `Feature request submitted successfully!${result.request_id ? ` ID: ${result.request_id}` : ''}`
                : result.message || 'Failed to submit feature request'}
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
}
