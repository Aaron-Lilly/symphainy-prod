'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { Documentation } from '@/shared/managers/AdminAPIManager';

interface DocumentationPanelProps {
  data: Documentation;
}

export function DocumentationPanel({ data }: DocumentationPanelProps) {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Platform SDK Documentation</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="prose max-w-none">
            {data.sections && data.sections.length > 0 ? (
              <div className="space-y-4">
                {data.sections.map((section) => (
                  <div key={section.id} className="border-b pb-4">
                    <h3 className="text-lg font-semibold mb-2">{section.title}</h3>
                    <div className="text-sm text-muted-foreground whitespace-pre-wrap">
                      {section.content}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-muted-foreground">Documentation content will be displayed here.</p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
