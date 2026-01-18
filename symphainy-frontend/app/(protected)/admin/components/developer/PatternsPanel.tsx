'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { Patterns } from '@/shared/managers/AdminAPIManager';

interface PatternsPanelProps {
  data: Patterns;
}

export function PatternsPanel({ data }: PatternsPanelProps) {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Patterns & Best Practices</CardTitle>
        </CardHeader>
        <CardContent>
          {data.patterns && data.patterns.length > 0 ? (
            <div className="space-y-4">
              {data.patterns.map((pattern) => (
                <div key={pattern.id} className="border rounded-lg p-4">
                  <h3 className="font-semibold mb-2">{pattern.title}</h3>
                  <p className="text-sm text-muted-foreground mb-3">{pattern.description}</p>
                  {pattern.best_practices && pattern.best_practices.length > 0 && (
                    <div className="mt-3">
                      <div className="text-sm font-semibold mb-2">Best Practices:</div>
                      <ul className="list-disc list-inside space-y-1 text-sm">
                        {pattern.best_practices.map((practice, idx) => (
                          <li key={idx}>{practice}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-muted-foreground">Patterns will be displayed here.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
