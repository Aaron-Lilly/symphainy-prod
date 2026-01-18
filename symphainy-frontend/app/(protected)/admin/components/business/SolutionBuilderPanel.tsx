'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import type { AdminAPIManager } from '@/shared/managers/AdminAPIManager';

interface SolutionBuilderPanelProps {
  adminAPIManager: AdminAPIManager;
}

export function SolutionBuilderPanel({ adminAPIManager }: SolutionBuilderPanelProps) {
  const [solutionConfig, setSolutionConfig] = useState('{\n  "name": "my-solution",\n  "domain": "content",\n  "intents": []\n}');
  const [composing, setComposing] = useState(false);
  const [registering, setRegistering] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleCompose = async () => {
    setComposing(true);
    setError(null);
    setResult(null);

    try {
      const config = JSON.parse(solutionConfig);
      const response = await adminAPIManager.composeSolution({ solution_config: config });
      setResult(response);
    } catch (err) {
      if (err instanceof SyntaxError) {
        setError('Invalid JSON: ' + err.message);
      } else {
        setError(err instanceof Error ? err.message : 'Composition failed');
      }
    } finally {
      setComposing(false);
    }
  };

  const handleRegister = async () => {
    setRegistering(true);
    setError(null);
    setResult(null);

    try {
      const config = JSON.parse(solutionConfig);
      const response = await adminAPIManager.registerSolution({ solution_config: config });
      setResult(response);
    } catch (err) {
      if (err instanceof SyntaxError) {
        setError('Invalid JSON: ' + err.message);
      } else {
        setError(err instanceof Error ? err.message : 'Registration failed');
      }
    } finally {
      setRegistering(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Solution Builder</CardTitle>
        <CardDescription>
          Advanced solution builder for composing custom solutions (gated feature)
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <label className="text-sm font-medium mb-2 block">Solution Configuration (JSON)</label>
          <Textarea
            value={solutionConfig}
            onChange={(e) => setSolutionConfig(e.target.value)}
            className="w-full h-64 p-3 font-mono text-sm"
            placeholder='{"name": "my-solution", "domain": "content", "intents": []}'
          />
        </div>
        <div className="flex gap-2">
          <Button onClick={handleCompose} disabled={composing || registering}>
            {composing ? 'Composing...' : 'Compose Solution'}
          </Button>
          <Button onClick={handleRegister} disabled={registering || composing} variant="outline">
            {registering ? 'Registering...' : 'Register Solution'}
          </Button>
        </div>
        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
        {result && (
          <Alert>
            <AlertDescription>
              {result.success
                ? `Solution ${result.solution_id ? `created with ID: ${result.solution_id}` : 'processed successfully'}`
                : 'Operation failed'}
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
}
