'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Map, Package, ExternalLink } from 'lucide-react';
import type { AdminDashboardSummary } from '@/lib/api/admin';

interface PlatformJourneysSolutionsCardProps {
  data: AdminDashboardSummary;
}

export default function PlatformJourneysSolutionsCard({ data }: PlatformJourneysSolutionsCardProps) {
  const [activeTab, setActiveTab] = useState<'journeys' | 'solutions'>('journeys');
  
  const journeys = data.journeys?.journeys || [];
  const solutions = data.solutions?.solutions || [];

  const renderItem = (item: any, type: 'journey' | 'solution') => (
    <div key={item[`${type}_id`]} className="p-3 border rounded-lg hover:bg-muted/50 transition-colors">
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1">
          <div className="font-medium">{item[`${type}_name`]}</div>
          <div className="text-sm text-muted-foreground">
            {item[`${type}_type`]} • {item.status}
          </div>
        </div>
        <Badge variant={item.status === 'operational' ? 'default' : 'secondary'}>
          {item.status}
        </Badge>
      </div>
      
      {item.source_artifact_id && (
        <div className="text-xs text-muted-foreground mb-2">
          Source: {item.source_artifact_type} ({item.artifact_status})
        </div>
      )}
      
      {item.created_at && (
        <div className="text-xs text-muted-foreground">
          Created: {new Date(item.created_at).toLocaleDateString()}
        </div>
      )}
      
      <div className="flex gap-2 mt-2">
        {item[`${type}_url`] && (
          <a 
            href={item[`${type}_url`]} 
            className="text-xs text-blue-600 hover:underline flex items-center gap-1"
            target="_blank"
            rel="noopener noreferrer"
          >
            View {type} <ExternalLink className="h-3 w-3" />
          </a>
        )}
        {item.artifact_url && (
          <a 
            href={item.artifact_url} 
            className="text-xs text-blue-600 hover:underline flex items-center gap-1"
            target="_blank"
            rel="noopener noreferrer"
          >
            View Artifact <ExternalLink className="h-3 w-3" />
          </a>
        )}
      </div>
    </div>
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Map className="h-5 w-5" />
          Platform Journeys & Solutions
        </CardTitle>
        <CardDescription>
          Operational journeys and solutions created from artifacts
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as 'journeys' | 'solutions')}>
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="journeys">
              Journeys ({data.journeys?.total || 0})
            </TabsTrigger>
            <TabsTrigger value="solutions">
              Solutions ({data.solutions?.total || 0})
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="journeys" className="mt-4">
            {journeys.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <Map className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>No journeys found</p>
              </div>
            ) : (
              <div className="space-y-2 max-h-[400px] overflow-y-auto">
                {journeys.map((journey) => renderItem(journey, 'journey'))}
              </div>
            )}
          </TabsContent>
          
          <TabsContent value="solutions" className="mt-4">
            {solutions.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <Package className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>No solutions found</p>
              </div>
            ) : (
              <div className="space-y-2 max-h-[400px] overflow-y-auto">
                {solutions.map((solution) => renderItem(solution, 'solution'))}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}







