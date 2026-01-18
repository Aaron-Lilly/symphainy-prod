'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import type { AdminAPIManager } from '@/shared/managers/AdminAPIManager';

interface SolutionBuilderPlaygroundProps {
  adminAPIManager: AdminAPIManager;
}

export function SolutionBuilderPlayground({ adminAPIManager }: SolutionBuilderPlaygroundProps) {
  const [solutionConfig, setSolutionConfig] = useState('{\n  "name": "example-solution",\n  "domain": "content"\n}');
  const [validating, setValidating] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleValidate = async () => {
    setValidating(true);
    setError(null);
    setResult(null);

    try {
      const config = JSON.parse(solutionConfig);
      const validationResult = await adminAPIManager.validateSolution({ solution_config: config });
      setResult(validationResult);
    } catch (err) {
      if (err instanceof SyntaxError) {
        setError('Invalid JSON: ' + err.message);
      } else {
        setError(err instanceof Error ? err.message : 'Validation failed');
      }
    } finally {
      setValidating(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Solution Builder Playground</CardTitle>
        <CardDescription>
          Build and validate solutions in real-time (gated feature)
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <label className="text-sm font-medium mb-2 block">Solution Configuration (JSON)</label>
          <textarea
            value={solutionConfig}
            onChange={(e) => setSolutionConfig(e.target.value)}
            className="w-full h-48 p-3 border rounded-md font-mono text-sm"
            placeholder='{"name": "example-solution", "domain": "content"}'
          />
        </div>
        <Button onClick={handleValidate} disabled={validating}>
          {validating ? 'Validating...' : 'Validate Solution'}
        </Button>
        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
        {result && (
          <div className="border rounded-lg p-4">
            <div className="font-semibold mb-2">Validation Result:</div>
            <pre className="text-sm overflow-x-auto">{JSON.stringify(result, null, 2)}</pre>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
