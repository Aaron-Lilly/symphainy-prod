'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import type { SolutionTemplates, AdminAPIManager } from '@/shared/managers/AdminAPIManager';

interface SolutionTemplatesPanelProps {
  data: SolutionTemplates;
  adminAPIManager: AdminAPIManager;
}

export function SolutionTemplatesPanel({ data, adminAPIManager }: SolutionTemplatesPanelProps) {
  const [creating, setCreating] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleCreateFromTemplate = async (templateId: string) => {
    setCreating(templateId);
    setError(null);
    setResult(null);

    try {
      const response = await adminAPIManager.composeSolution({
        solution_config: { template_id: templateId },
      });
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create solution from template');
    } finally {
      setCreating(null);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Solution Templates</CardTitle>
        <CardDescription>Pre-built solution templates (gated feature)</CardDescription>
      </CardHeader>
      <CardContent>
        {data.templates && data.templates.length > 0 ? (
          <div className="space-y-4">
            {data.templates.map((template) => (
              <div key={template.id} className="border rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h3 className="font-semibold">{template.name}</h3>
                    <p className="text-sm text-muted-foreground mt-1">{template.description}</p>
                  </div>
                  <Button
                    onClick={() => handleCreateFromTemplate(template.id)}
                    disabled={creating === template.id}
                    size="sm"
                  >
                    {creating === template.id ? 'Creating...' : 'Use Template'}
                  </Button>
                </div>
                <div className="flex items-center gap-4 mt-3 text-sm">
                  <span className="text-muted-foreground">Domain: <span className="font-medium capitalize">{template.domain}</span></span>
                  <span className="text-muted-foreground">Complexity: <span className="font-medium capitalize">{template.complexity}</span></span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <Alert>
            <AlertDescription>
              Solution templates are not available. This feature may be gated or not yet enabled.
            </AlertDescription>
          </Alert>
        )}
        {error && (
          <Alert variant="destructive" className="mt-4">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
        {result && (
          <Alert className="mt-4">
            <AlertDescription>
              {result.success
                ? `Solution created successfully! ID: ${result.solution_id}`
                : 'Failed to create solution'}
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
}
