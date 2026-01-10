'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Database, Server, Wrench, FileText, Box } from 'lucide-react';
import type { AdminDashboardSummary } from '@/lib/api/admin';

interface CuratorRegistriesCardProps {
  data: AdminDashboardSummary;
}

export default function CuratorRegistriesCard({ data }: CuratorRegistriesCardProps) {
  const registries = data.curator_registries?.registries || {};
  
  const registryItems = [
    { 
      label: 'Services', 
      value: registries.services || 0, 
      icon: Server,
      color: 'text-blue-600' 
    },
    { 
      label: 'SOA APIs', 
      value: registries.soa_apis || 0, 
      icon: Database,
      color: 'text-green-600' 
    },
    { 
      label: 'MCP Tools', 
      value: registries.mcp_tools || 0, 
      icon: Wrench,
      color: 'text-purple-600' 
    },
    { 
      label: 'Artifacts', 
      value: registries.artifacts || 0, 
      icon: FileText,
      color: 'text-orange-600' 
    },
    { 
      label: 'Capabilities', 
      value: registries.capabilities || 0, 
      icon: Box,
      color: 'text-pink-600' 
    },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Database className="h-5 w-5" />
          Curator Registries
        </CardTitle>
        <CardDescription>
          Platform service and capability registries
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {registryItems.map((item) => {
            const Icon = item.icon;
            return (
              <div key={item.label} className="flex flex-col items-center p-4 bg-muted rounded-lg">
                <Icon className={`h-6 w-6 mb-2 ${item.color}`} />
                <div className="text-2xl font-bold">{item.value}</div>
                <div className="text-xs text-muted-foreground text-center">{item.label}</div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}







