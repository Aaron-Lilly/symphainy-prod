'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { CodeExamples } from '@/shared/managers/AdminAPIManager';

interface CodeExamplesPanelProps {
  data: CodeExamples;
}

export function CodeExamplesPanel({ data }: CodeExamplesPanelProps) {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Code Examples</CardTitle>
        </CardHeader>
        <CardContent>
          {data.examples && data.examples.length > 0 ? (
            <div className="space-y-4">
              {data.examples.map((example) => (
                <div key={example.id} className="border rounded-lg p-4">
                  <h3 className="font-semibold mb-2">{example.title}</h3>
                  <p className="text-sm text-muted-foreground mb-3">{example.description}</p>
                  <pre className="bg-muted p-3 rounded text-sm overflow-x-auto">
                    <code>{example.code}</code>
                  </pre>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-muted-foreground">Code examples will be displayed here.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
