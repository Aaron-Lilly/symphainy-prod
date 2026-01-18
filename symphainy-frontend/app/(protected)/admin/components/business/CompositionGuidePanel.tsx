'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { CompositionGuide } from '@/shared/managers/AdminAPIManager';

interface CompositionGuidePanelProps {
  data: CompositionGuide;
}

export function CompositionGuidePanel({ data }: CompositionGuidePanelProps) {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Solution Composition Guide</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Steps */}
          {data.steps && data.steps.length > 0 && (
            <div>
              <h3 className="font-semibold mb-3">Step-by-Step Guide</h3>
              <div className="space-y-4">
                {data.steps.map((step) => (
                  <div key={step.step_number} className="border rounded-lg p-4">
                    <div className="flex items-start gap-3">
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-semibold">
                        {step.step_number}
                      </div>
                      <div className="flex-1">
                        <h4 className="font-semibold mb-2">{step.title}</h4>
                        <p className="text-sm text-muted-foreground mb-2">{step.description}</p>
                        {step.actions && step.actions.length > 0 && (
                          <ul className="list-disc list-inside space-y-1 text-sm">
                            {step.actions.map((action, idx) => (
                              <li key={idx}>{action}</li>
                            ))}
                          </ul>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Domain Selection */}
          {data.domain_selection && (
            <div className="pt-4 border-t">
              <h3 className="font-semibold mb-3">Available Domains</h3>
              <div className="grid grid-cols-2 gap-3">
                {data.domain_selection.available_domains.map((domain) => (
                  <div key={domain} className="border rounded-lg p-3">
                    <div className="font-medium capitalize mb-1">{domain}</div>
                    <div className="text-sm text-muted-foreground">
                      {data.domain_selection.domain_descriptions[domain] || 'No description available'}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
