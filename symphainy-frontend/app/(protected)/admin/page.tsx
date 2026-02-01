'use client';

/**
 * Admin Dashboard Page
 * 
 * Revolutionary Administrator/Owner Front Door with three views:
 * 1. Control Room - Real-time platform observability and governance
 * 2. Developer View - Platform SDK documentation, playground, feature submission
 * 3. Business User View - Solution composition, templates, feature requests
 */

import React from 'react';
import MainLayout from '@/shared/components/MainLayout';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ControlRoomView } from './components/ControlRoomView';
import { DeveloperView } from './components/DeveloperView';
import { BusinessUserView } from './components/BusinessUserView';
import { useTenant } from '@/shared/contexts/TenantContext';
import { BarChart3, Code, Briefcase, Building2 } from 'lucide-react';

export default function AdminDashboard() {
  const { currentTenant, tenantId } = useTenant();
  
  return (
    <MainLayout>
      <div className="container mx-auto p-6">
        {/* Header with Tenant Indicator */}
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Control Tower</h1>
            <p className="text-muted-foreground">
              Platform monitoring and administration
            </p>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-blue-50 border border-blue-200 rounded-lg">
            <Building2 className="h-4 w-4 text-blue-600" />
            <span className="text-sm font-medium">Current Tenant:</span>
            <span className="text-sm text-blue-700">{currentTenant.tenant_name}</span>
          </div>
        </div>

        {/* Three-View Tabbed Interface */}
        <Tabs defaultValue="control-room" className="w-full">
          <TabsList className="grid w-full grid-cols-3 mb-6">
            <TabsTrigger value="control-room" className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              Control Room
            </TabsTrigger>
            <TabsTrigger value="developer" className="flex items-center gap-2">
              <Code className="h-4 w-4" />
              Developer View
            </TabsTrigger>
            <TabsTrigger value="business" className="flex items-center gap-2">
              <Briefcase className="h-4 w-4" />
              Business User View
            </TabsTrigger>
          </TabsList>

          {/* Control Room View */}
          <TabsContent value="control-room" className="mt-0">
            <ControlRoomView />
          </TabsContent>

          {/* Developer View */}
          <TabsContent value="developer" className="mt-0">
            <DeveloperView />
          </TabsContent>

          {/* Business User View */}
          <TabsContent value="business" className="mt-0">
            <BusinessUserView />
          </TabsContent>
        </Tabs>
      </div>
    </MainLayout>
  );
}







