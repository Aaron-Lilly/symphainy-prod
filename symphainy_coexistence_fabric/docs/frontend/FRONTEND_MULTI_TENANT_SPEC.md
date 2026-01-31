# Frontend Multi-Tenant Demo Implementation Specification

**Status:** Ready for Implementation  
**Target:** symphainy-frontend  
**Scope:** Transform single-tenant frontend into multi-tenant demo platform  
**Estimated Effort:** 5-7 days

---

## Executive Summary

Transform the SymphAIny frontend from a single mixed-demo experience into a proper multi-tenant platform where each demo (Base, AAR, PSO, VLP) runs as a separate tenant configuration on the same platform.

**Current State:** Demo-specific components (AAR analysis, PSO viewer, VLP fields) are hardcoded into pillar pages, creating a confusing mixed experience.

**Target State:** Clean tenant separation where:
- Login includes tenant selection
- Each tenant sees only their relevant features
- Same platform code serves all tenants
- Demos prove the platform (not vice versa)

---

## Part 1: Tenant Configuration System

### 1.1 Create Tenant Config Types

**File:** `shared/config/tenant-types.ts`

```typescript
/**
 * Tenant Configuration Types
 * 
 * Defines the shape of tenant-specific configuration.
 * Each demo tenant (AAR, PSO, VLP) has its own config.
 */

export interface TenantConfig {
  // Identity
  tenant_id: string;
  tenant_name: string;
  tenant_description: string;
  
  // Branding (optional)
  branding?: {
    primary_color?: string;
    logo_url?: string;
    welcome_message?: string;
  };
  
  // Feature flags - which pillar features are enabled
  features: {
    content: ContentFeatures;
    insights: InsightsFeatures;
    operations: OperationsFeatures;
    outcomes: OutcomesFeatures;
  };
  
  // Sample data configuration
  sample_data?: {
    files?: Array<{
      name: string;
      description: string;
      type: string;
      url?: string; // Pre-loaded sample file URL
    }>;
  };
  
  // Agent configuration
  agents?: {
    guide_agent_prompt_context?: string;
    liaison_agent_prompt_context?: string;
  };
}

export interface ContentFeatures {
  enabled: boolean;
  file_types: string[]; // Which file types to highlight
  upload_guidance?: string; // Tenant-specific upload instructions
  show_mainframe_parser?: boolean;
  show_edi_parser?: boolean;
}

export interface InsightsFeatures {
  enabled: boolean;
  tabs: {
    data_quality: boolean;
    data_interpretation: boolean;
    your_data_mash: boolean;
    business_analysis: boolean;
    relationship_mapping: boolean;
  };
  // Demo-specific sections
  show_aar_analysis?: boolean;
  show_pso_viewer?: boolean;
  show_vlp_extraction?: boolean;
  // Custom analysis options
  analysis_presets?: Array<{
    name: string;
    description: string;
    analysis_type: string;
    options: Record<string, any>;
  }>;
}

export interface OperationsFeatures {
  enabled: boolean;
  show_sop_generator: boolean;
  show_workflow_builder: boolean;
  show_coexistence_analysis: boolean;
  // Demo-specific templates
  sop_templates?: string[];
  workflow_templates?: string[];
}

export interface OutcomesFeatures {
  enabled: boolean;
  show_roadmap_generator: boolean;
  show_poc_generator: boolean;
  show_blueprint_generator: boolean;
  show_synthesis: boolean;
}

export type TenantId = 'base' | 'aar' | 'pso' | 'vlp';
```

### 1.2 Create Tenant Configurations

**File:** `shared/config/tenants/base.ts`

```typescript
import { TenantConfig } from '../tenant-types';

export const baseTenantConfig: TenantConfig = {
  tenant_id: 'base',
  tenant_name: 'SymphAIny Platform',
  tenant_description: 'Full platform experience - all features enabled',
  
  branding: {
    welcome_message: 'Welcome to SymphAIny - the Intent-Driven Enterprise Operating System',
  },
  
  features: {
    content: {
      enabled: true,
      file_types: ['csv', 'excel', 'pdf', 'word', 'json', 'xml', 'mainframe', 'edi'],
      upload_guidance: 'Upload any file type to begin your data journey.',
      show_mainframe_parser: true,
      show_edi_parser: true,
    },
    insights: {
      enabled: true,
      tabs: {
        data_quality: true,
        data_interpretation: true,
        your_data_mash: true,
        business_analysis: true,
        relationship_mapping: true,
      },
      // Base tenant shows all demo sections (for internal testing)
      show_aar_analysis: true,
      show_pso_viewer: true,
      show_vlp_extraction: true,
    },
    operations: {
      enabled: true,
      show_sop_generator: true,
      show_workflow_builder: true,
      show_coexistence_analysis: true,
    },
    outcomes: {
      enabled: true,
      show_roadmap_generator: true,
      show_poc_generator: true,
      show_blueprint_generator: true,
      show_synthesis: true,
    },
  },
  
  agents: {
    guide_agent_prompt_context: 'You are helping a user explore the full SymphAIny platform capabilities.',
  },
};
```

**File:** `shared/config/tenants/aar.ts`

```typescript
import { TenantConfig } from '../tenant-types';

export const aarTenantConfig: TenantConfig = {
  tenant_id: 'aar',
  tenant_name: 'Navy AAR Analysis Demo',
  tenant_description: 'After Action Report analysis and insights extraction',
  
  branding: {
    primary_color: '#1e3a5f', // Navy blue
    welcome_message: 'Welcome to the Navy AAR Analysis Platform - Transform After Action Reports into actionable insights',
  },
  
  features: {
    content: {
      enabled: true,
      file_types: ['pdf', 'word', 'txt'],
      upload_guidance: 'Upload After Action Reports (PDF, Word, or text files) for analysis.',
      show_mainframe_parser: false,
      show_edi_parser: false,
    },
    insights: {
      enabled: true,
      tabs: {
        data_quality: true,
        data_interpretation: true,
        your_data_mash: true,
        business_analysis: true,
        relationship_mapping: false, // Not relevant for AAR
      },
      show_aar_analysis: true, // PRIMARY FEATURE
      show_pso_viewer: false,
      show_vlp_extraction: false,
      analysis_presets: [
        {
          name: 'Lessons Learned Extraction',
          description: 'Extract key lessons learned from AAR documents',
          analysis_type: 'unstructured',
          options: { focus: 'lessons_learned' },
        },
        {
          name: 'Risk Assessment',
          description: 'Identify risks and mitigation strategies',
          analysis_type: 'unstructured',
          options: { focus: 'risk_assessment' },
        },
        {
          name: 'Timeline Reconstruction',
          description: 'Build event timeline from AAR narrative',
          analysis_type: 'unstructured',
          options: { focus: 'timeline' },
        },
      ],
    },
    operations: {
      enabled: true,
      show_sop_generator: true,
      show_workflow_builder: false,
      show_coexistence_analysis: false,
      sop_templates: ['post_mission_debrief', 'incident_response', 'training_feedback'],
    },
    outcomes: {
      enabled: true,
      show_roadmap_generator: true,
      show_poc_generator: false,
      show_blueprint_generator: true,
      show_synthesis: true,
    },
  },
  
  sample_data: {
    files: [
      {
        name: 'Sample_AAR_Exercise_Alpha.pdf',
        description: 'Example After Action Report from training exercise',
        type: 'pdf',
      },
    ],
  },
  
  agents: {
    guide_agent_prompt_context: 'You are helping a Navy analyst extract insights from After Action Reports. Focus on lessons learned, risks, recommendations, and timeline events. Use military terminology appropriately.',
    liaison_agent_prompt_context: 'Specialize in military document analysis, particularly After Action Reports. Help identify operational improvements and training recommendations.',
  },
};
```

**File:** `shared/config/tenants/pso.ts`

```typescript
import { TenantConfig } from '../tenant-types';

export const psoTenantConfig: TenantConfig = {
  tenant_id: 'pso',
  tenant_name: 'Permit & Service Order Processing Demo',
  tenant_description: 'Energy and utility permit data extraction and processing',
  
  branding: {
    primary_color: '#2d5a27', // Utility green
    welcome_message: 'Welcome to PSO Processing - Transform permit data into structured insights',
  },
  
  features: {
    content: {
      enabled: true,
      file_types: ['csv', 'excel', 'pdf', 'xml'],
      upload_guidance: 'Upload permit files, service orders, or utility data extracts.',
      show_mainframe_parser: false,
      show_edi_parser: true, // Utilities often use EDI
    },
    insights: {
      enabled: true,
      tabs: {
        data_quality: true,
        data_interpretation: true,
        your_data_mash: true,
        business_analysis: true,
        relationship_mapping: true, // Useful for permit relationships
      },
      show_aar_analysis: false,
      show_pso_viewer: true, // PRIMARY FEATURE
      show_vlp_extraction: false,
      analysis_presets: [
        {
          name: 'Permit Field Extraction',
          description: 'Extract standard permit fields (dates, addresses, status)',
          analysis_type: 'structured',
          options: { schema: 'permit_standard' },
        },
        {
          name: 'Service Order Mapping',
          description: 'Map service orders to customer accounts',
          analysis_type: 'structured',
          options: { schema: 'service_order' },
        },
        {
          name: 'Compliance Check',
          description: 'Verify permit data against regulatory requirements',
          analysis_type: 'structured',
          options: { focus: 'compliance' },
        },
      ],
    },
    operations: {
      enabled: true,
      show_sop_generator: true,
      show_workflow_builder: true,
      show_coexistence_analysis: true,
      sop_templates: ['permit_processing', 'service_order_workflow', 'compliance_review'],
      workflow_templates: ['permit_approval', 'service_activation', 'meter_installation'],
    },
    outcomes: {
      enabled: true,
      show_roadmap_generator: true,
      show_poc_generator: true,
      show_blueprint_generator: true,
      show_synthesis: true,
    },
  },
  
  sample_data: {
    files: [
      {
        name: 'Sample_Permits_Q4_2024.csv',
        description: 'Sample permit data extract',
        type: 'csv',
      },
      {
        name: 'Service_Orders_Extract.xlsx',
        description: 'Sample service order data',
        type: 'excel',
      },
    ],
  },
  
  agents: {
    guide_agent_prompt_context: 'You are helping a utility company analyst process permit and service order data. Focus on data quality, field mapping, and regulatory compliance.',
    liaison_agent_prompt_context: 'Specialize in utility industry data patterns, permit processing workflows, and service order management.',
  },
};
```

**File:** `shared/config/tenants/vlp.ts`

```typescript
import { TenantConfig } from '../tenant-types';

export const vlpTenantConfig: TenantConfig = {
  tenant_id: 'vlp',
  tenant_name: 'Variable Life Policy Processing Demo',
  tenant_description: 'Life insurance policy data extraction and migration',
  
  branding: {
    primary_color: '#4a1c6b', // Insurance purple
    welcome_message: 'Welcome to VLP Processing - Modernize your policy administration',
  },
  
  features: {
    content: {
      enabled: true,
      file_types: ['mainframe', 'csv', 'excel', 'pdf'],
      upload_guidance: 'Upload policy data files, mainframe extracts, or policy documents.',
      show_mainframe_parser: true, // PRIMARY - insurance on mainframe
      show_edi_parser: false,
    },
    insights: {
      enabled: true,
      tabs: {
        data_quality: true,
        data_interpretation: true,
        your_data_mash: true,
        business_analysis: true,
        relationship_mapping: true, // Policy-holder relationships
      },
      show_aar_analysis: false,
      show_pso_viewer: false,
      show_vlp_extraction: true, // PRIMARY FEATURE
      analysis_presets: [
        {
          name: 'Policy Field Extraction',
          description: 'Extract standard policy fields (policy number, holder, coverage)',
          analysis_type: 'structured',
          options: { schema: 'life_policy_standard' },
        },
        {
          name: 'COBOL Copybook Mapping',
          description: 'Map mainframe fields using copybook definitions',
          analysis_type: 'structured',
          options: { parser: 'mainframe', use_copybook: true },
        },
        {
          name: 'Migration Readiness',
          description: 'Assess data quality for migration to modern systems',
          analysis_type: 'structured',
          options: { focus: 'migration_readiness' },
        },
      ],
    },
    operations: {
      enabled: true,
      show_sop_generator: true,
      show_workflow_builder: true,
      show_coexistence_analysis: true, // KEY - legacy/modern coexistence
      sop_templates: ['policy_migration', 'data_validation', 'coexistence_operation'],
      workflow_templates: ['policy_conversion', 'batch_migration', 'validation_workflow'],
    },
    outcomes: {
      enabled: true,
      show_roadmap_generator: true,
      show_poc_generator: true,
      show_blueprint_generator: true, // KEY - coexistence blueprint
      show_synthesis: true,
    },
  },
  
  sample_data: {
    files: [
      {
        name: 'Sample_Policy_Extract.dat',
        description: 'Sample mainframe policy data extract',
        type: 'mainframe',
      },
      {
        name: 'Policy_Copybook.cpy',
        description: 'COBOL copybook for policy layout',
        type: 'text',
      },
    ],
  },
  
  agents: {
    guide_agent_prompt_context: 'You are helping an insurance company modernize their variable life policy administration. Focus on mainframe data extraction, legacy system coexistence, and migration planning.',
    liaison_agent_prompt_context: 'Specialize in life insurance data patterns, mainframe to modern migration, and policy administration workflows. Understand ACORD standards and common policy data structures.',
  },
};
```

**File:** `shared/config/tenants/index.ts`

```typescript
import { TenantConfig, TenantId } from '../tenant-types';
import { baseTenantConfig } from './base';
import { aarTenantConfig } from './aar';
import { psoTenantConfig } from './pso';
import { vlpTenantConfig } from './vlp';

export const TENANT_CONFIGS: Record<TenantId, TenantConfig> = {
  base: baseTenantConfig,
  aar: aarTenantConfig,
  pso: psoTenantConfig,
  vlp: vlpTenantConfig,
};

export function getTenantConfig(tenantId: string): TenantConfig {
  const config = TENANT_CONFIGS[tenantId as TenantId];
  if (!config) {
    console.warn(`Unknown tenant: ${tenantId}, falling back to base`);
    return baseTenantConfig;
  }
  return config;
}

export function getAvailableTenants(): Array<{ id: TenantId; name: string; description: string }> {
  return Object.entries(TENANT_CONFIGS).map(([id, config]) => ({
    id: id as TenantId,
    name: config.tenant_name,
    description: config.tenant_description,
  }));
}

export { TenantConfig, TenantId };
```

---

## Part 2: Tenant Context Provider

**File:** `shared/contexts/TenantContext.tsx`

```typescript
"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { TenantConfig, TenantId, getTenantConfig, getAvailableTenants } from '@/shared/config/tenants';

interface TenantContextType {
  // Current tenant
  currentTenant: TenantConfig;
  tenantId: TenantId;
  
  // Tenant switching
  setTenant: (tenantId: TenantId) => void;
  availableTenants: Array<{ id: TenantId; name: string; description: string }>;
  
  // Feature checks (convenience methods)
  hasFeature: (pillar: string, feature: string) => boolean;
  isTabEnabled: (pillar: string, tab: string) => boolean;
}

const TenantContext = createContext<TenantContextType | undefined>(undefined);

export const useTenant = (): TenantContextType => {
  const context = useContext(TenantContext);
  if (!context) {
    throw new Error('useTenant must be used within TenantProvider');
  }
  return context;
};

interface TenantProviderProps {
  children: React.ReactNode;
  initialTenantId?: TenantId;
}

export const TenantProvider: React.FC<TenantProviderProps> = ({
  children,
  initialTenantId = 'base',
}) => {
  const [tenantId, setTenantIdState] = useState<TenantId>(initialTenantId);
  const [currentTenant, setCurrentTenant] = useState<TenantConfig>(getTenantConfig(initialTenantId));

  // Load tenant from session storage on mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const storedTenantId = sessionStorage.getItem('tenant_id') as TenantId;
      if (storedTenantId && storedTenantId !== tenantId) {
        setTenantIdState(storedTenantId);
        setCurrentTenant(getTenantConfig(storedTenantId));
      }
    }
  }, []);

  const setTenant = useCallback((newTenantId: TenantId) => {
    setTenantIdState(newTenantId);
    setCurrentTenant(getTenantConfig(newTenantId));
    
    // Persist to session storage
    if (typeof window !== 'undefined') {
      sessionStorage.setItem('tenant_id', newTenantId);
    }
  }, []);

  const hasFeature = useCallback((pillar: string, feature: string): boolean => {
    const pillarConfig = currentTenant.features[pillar as keyof typeof currentTenant.features];
    if (!pillarConfig || !pillarConfig.enabled) return false;
    return pillarConfig[feature as keyof typeof pillarConfig] === true;
  }, [currentTenant]);

  const isTabEnabled = useCallback((pillar: string, tab: string): boolean => {
    const pillarConfig = currentTenant.features[pillar as keyof typeof currentTenant.features];
    if (!pillarConfig || !pillarConfig.enabled) return false;
    
    if ('tabs' in pillarConfig && pillarConfig.tabs) {
      return pillarConfig.tabs[tab as keyof typeof pillarConfig.tabs] === true;
    }
    return true;
  }, [currentTenant]);

  const value: TenantContextType = {
    currentTenant,
    tenantId,
    setTenant,
    availableTenants: getAvailableTenants(),
    hasFeature,
    isTabEnabled,
  };

  return (
    <TenantContext.Provider value={value}>
      {children}
    </TenantContext.Provider>
  );
};
```

---

## Part 3: Update Login Page

**File:** `app/(public)/login/page.tsx` — FULL REPLACEMENT

```typescript
"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { LoginForm, RegisterForm } from "@/components/auth";
import { useAuth } from "@/shared/auth/AuthProvider";
import { useTenant } from "@/shared/contexts/TenantContext";
import { TenantId } from "@/shared/config/tenant-types";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";

export default function AuthPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "register">("login");
  const { login, register } = useAuth();
  const { setTenant, availableTenants, tenantId } = useTenant();

  const handleTenantChange = (value: string) => {
    setTenant(value as TenantId);
  };

  const handleAuthSuccess = async (user: any, token: string) => {
    console.log("Auth successful:", { user, token, tenant: tenantId });
    router.push("/");
  };

  const handleAuthError = (error: string) => {
    console.error("Auth error:", error);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">SymphAIny Platform</CardTitle>
          <CardDescription>
            Select your demo environment and sign in
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Tenant Selector */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">
              Demo Environment
            </label>
            <Select value={tenantId} onValueChange={handleTenantChange}>
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Select demo environment" />
              </SelectTrigger>
              <SelectContent>
                {availableTenants.map((tenant) => (
                  <SelectItem key={tenant.id} value={tenant.id}>
                    <div className="flex flex-col">
                      <span className="font-medium">{tenant.name}</span>
                      <span className="text-xs text-gray-500">{tenant.description}</span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Divider */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-white px-2 text-gray-500">
                {mode === "login" ? "Sign in to continue" : "Create account"}
              </span>
            </div>
          </div>

          {/* Auth Form */}
          {mode === "register" ? (
            <RegisterForm
              onRegisterSuccess={handleAuthSuccess}
              onRegisterError={handleAuthError}
              onSwitchToLogin={() => setMode("login")}
            />
          ) : (
            <LoginForm
              onLoginSuccess={handleAuthSuccess}
              onLoginError={handleAuthError}
              onSwitchToRegister={() => setMode("register")}
            />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
```

---

## Part 4: Update Pillar Pages

### 4.1 Insights Pillar — Conditional Demo Sections

**File:** `app/(protected)/pillars/insights/page.tsx` — KEY CHANGES

Add these imports at the top:
```typescript
import { useTenant } from "@/shared/contexts/TenantContext";
```

Add this inside the component:
```typescript
const { currentTenant, isTabEnabled, hasFeature } = useTenant();
const insightsFeatures = currentTenant.features.insights;
```

Update the Tabs component to conditionally render:
```typescript
<Tabs defaultValue="data-quality" className="space-y-6">
  <TabsList className="grid w-full" style={{ 
    gridTemplateColumns: `repeat(${
      [
        insightsFeatures.tabs.data_quality,
        insightsFeatures.tabs.data_interpretation,
        insightsFeatures.tabs.your_data_mash,
        insightsFeatures.tabs.business_analysis,
        insightsFeatures.tabs.relationship_mapping,
      ].filter(Boolean).length
    }, 1fr)` 
  }}>
    {insightsFeatures.tabs.data_quality && (
      <TabsTrigger value="data-quality">Data Quality</TabsTrigger>
    )}
    {insightsFeatures.tabs.data_interpretation && (
      <TabsTrigger value="data-interpretation">Data Interpretation</TabsTrigger>
    )}
    {insightsFeatures.tabs.your_data_mash && (
      <TabsTrigger value="your-data-mash">
        Your Data Mash
        <span className="ml-2 px-2 py-0.5 text-xs bg-blue-100 text-blue-800 rounded-full">Lineage</span>
      </TabsTrigger>
    )}
    {insightsFeatures.tabs.business_analysis && (
      <TabsTrigger value="business-analysis">Business Analysis</TabsTrigger>
    )}
    {insightsFeatures.tabs.relationship_mapping && (
      <TabsTrigger value="relationship-mapping">Relationships</TabsTrigger>
    )}
  </TabsList>

  {/* Tab Contents - only render if enabled */}
  {insightsFeatures.tabs.data_quality && (
    <TabsContent value="data-quality">
      {/* Existing DataQualitySection */}
    </TabsContent>
  )}
  
  {/* ... other tabs ... */}
  
  {/* Business Analysis Tab - with demo-specific sections */}
  {insightsFeatures.tabs.business_analysis && (
    <TabsContent value="business-analysis">
      <Card>
        <CardHeader>
          <CardTitle>Business Analysis</CardTitle>
          <CardDescription>
            {currentTenant.tenant_id === 'aar' 
              ? 'Analyze After Action Reports for lessons learned, risks, and recommendations.'
              : currentTenant.tenant_id === 'pso'
              ? 'Analyze permit and service order data for compliance and optimization.'
              : currentTenant.tenant_id === 'vlp'
              ? 'Analyze policy data for migration readiness and data quality.'
              : 'Generate actionable business insights from your data.'
            }
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Demo-specific analysis sections */}
          {insightsFeatures.show_aar_analysis && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Target className="h-5 w-5 text-blue-600" />
                AAR Analysis
              </h3>
              <AARAnalysisSection aarAnalysis={aarAnalysisData} />
            </div>
          )}
          
          {insightsFeatures.show_pso_viewer && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <FileText className="h-5 w-5 text-green-600" />
                Permit Processing
              </h3>
              <PermitProcessingSection />
              <PSOViewer />
            </div>
          )}
          
          {insightsFeatures.show_vlp_extraction && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Database className="h-5 w-5 text-purple-600" />
                Policy Data Extraction
              </h3>
              {/* VLP-specific component - may need to create */}
              <VLPExtractionSection />
            </div>
          )}
          
          {/* Standard business analysis - always shown */}
          <BusinessAnalysisSection 
            onAnalysisComplete={handleBusinessAnalysisComplete}
            presets={insightsFeatures.analysis_presets}
          />
        </CardContent>
      </Card>
    </TabsContent>
  )}
</Tabs>
```

### 4.2 Content Pillar — Tenant-Specific Upload Guidance

**File:** `app/(protected)/pillars/content/page.tsx` — KEY CHANGES

Add tenant context:
```typescript
import { useTenant } from "@/shared/contexts/TenantContext";

// Inside component:
const { currentTenant } = useTenant();
const contentFeatures = currentTenant.features.content;
```

Update header description:
```typescript
<p className="text-lead text-gray-600">
  {contentFeatures.upload_guidance || 'Upload and manage your content files.'}
</p>
```

Conditionally show parsers:
```typescript
{/* Mainframe parser section - only for VLP and base */}
{contentFeatures.show_mainframe_parser && (
  <Card>
    <CardHeader>
      <CardTitle>Mainframe Data Processing</CardTitle>
      <CardDescription>
        Upload mainframe data files with optional COBOL copybook for field mapping.
      </CardDescription>
    </CardHeader>
    <CardContent>
      {/* Mainframe upload component */}
    </CardContent>
  </Card>
)}

{/* EDI parser section - only for PSO and base */}
{contentFeatures.show_edi_parser && (
  <Card>
    <CardHeader>
      <CardTitle>EDI Processing</CardTitle>
      <CardDescription>
        Process EDI transactions from trading partners.
      </CardDescription>
    </CardHeader>
    <CardContent>
      {/* EDI upload component */}
    </CardContent>
  </Card>
)}
```

### 4.3 Operations Pillar — Tenant-Specific Templates

**File:** `app/(protected)/pillars/journey/page.tsx` — KEY CHANGES

```typescript
import { useTenant } from "@/shared/contexts/TenantContext";

// Inside component:
const { currentTenant } = useTenant();
const operationsFeatures = currentTenant.features.operations;

// Conditionally render sections:
{operationsFeatures.show_sop_generator && (
  <SOPGeneratorSection templates={operationsFeatures.sop_templates} />
)}

{operationsFeatures.show_workflow_builder && (
  <WorkflowBuilderSection templates={operationsFeatures.workflow_templates} />
)}

{operationsFeatures.show_coexistence_analysis && (
  <CoexistenceAnalysisSection />
)}
```

### 4.4 Outcomes Pillar — Tenant-Specific Generators

**File:** `app/(protected)/pillars/business-outcomes/page.tsx` — KEY CHANGES

```typescript
import { useTenant } from "@/shared/contexts/TenantContext";

// Inside component:
const { currentTenant } = useTenant();
const outcomesFeatures = currentTenant.features.outcomes;

// Conditionally render:
{outcomesFeatures.show_roadmap_generator && <RoadmapGenerator />}
{outcomesFeatures.show_poc_generator && <POCGenerator />}
{outcomesFeatures.show_blueprint_generator && <BlueprintGenerator />}
{outcomesFeatures.show_synthesis && <SynthesisSection />}
```

---

## Part 5: Update Welcome Journey (Coexistence Landing)

**File:** `components/landing/WelcomeJourney.tsx` — KEY CHANGES

```typescript
import { useTenant } from "@/shared/contexts/TenantContext";

// Inside component:
const { currentTenant } = useTenant();

// Update welcome message:
<h1 className="text-3xl font-bold text-gray-800">
  {currentTenant.branding?.welcome_message || 'Welcome to SymphAIny'}
</h1>

// Update description based on tenant:
<p className="text-gray-600">
  {currentTenant.tenant_id === 'aar' 
    ? 'Upload your After Action Reports to extract lessons learned and actionable insights.'
    : currentTenant.tenant_id === 'pso'
    ? 'Upload permit and service order data for processing and compliance analysis.'
    : currentTenant.tenant_id === 'vlp'
    ? 'Upload policy data to begin your modernization journey.'
    : 'Upload any file to begin your data journey with AI-powered analysis.'
  }
</p>
```

---

## Part 6: Update Control Tower

**File:** `app/(protected)/admin/page.tsx` — KEY CHANGES

```typescript
import { useTenant } from "@/shared/contexts/TenantContext";

// Inside component:
const { currentTenant, tenantId } = useTenant();

// Add tenant indicator in header:
<div className="mb-6 flex items-center justify-between">
  <div>
    <h1 className="text-3xl font-bold mb-2">Control Tower</h1>
    <p className="text-muted-foreground">
      Platform monitoring and administration
    </p>
  </div>
  <div className="flex items-center gap-2 px-4 py-2 bg-blue-50 border border-blue-200 rounded-lg">
    <span className="text-sm font-medium">Current Tenant:</span>
    <span className="text-sm text-blue-700">{currentTenant.tenant_name}</span>
  </div>
</div>
```

**File:** `app/(protected)/admin/components/ControlRoomView.tsx` — KEY CHANGES

Add tenant filtering to metrics:
```typescript
import { useTenant } from "@/shared/contexts/TenantContext";

// Inside component:
const { tenantId } = useTenant();

// Pass tenantId to health/stats components:
<SystemHealthCard tenantId={tenantId} />
<RealmHealthCard tenantId={tenantId} />
<ExecutionMetricsCard tenantId={tenantId} />
```

---

## Part 7: Wire TenantProvider into App

**File:** `app/(protected)/layout.tsx` — UPDATE

```typescript
import { TenantProvider } from "@/shared/contexts/TenantContext";

export default function ProtectedLayout({ children }: { children: React.ReactNode }) {
  return (
    <TenantProvider>
      {/* existing providers */}
      {children}
    </TenantProvider>
  );
}
```

**File:** `app/(public)/layout.tsx` — UPDATE

```typescript
import { TenantProvider } from "@/shared/contexts/TenantContext";

export default function PublicLayout({ children }: { children: React.ReactNode }) {
  return (
    <TenantProvider>
      {children}
    </TenantProvider>
  );
}
```

---

## Part 8: Create VLP Extraction Component (New)

**File:** `app/(protected)/pillars/insights/components/VLPExtractionSection.tsx`

```typescript
/**
 * VLP Extraction Section
 * 
 * Policy data extraction for Variable Life Policy demo.
 * Shows extracted fields, data quality, and migration readiness.
 */

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Database, FileText, CheckCircle, AlertTriangle } from 'lucide-react';

interface PolicyField {
  name: string;
  value: string | null;
  confidence: number;
  source: 'mainframe' | 'document' | 'inferred';
  issues?: string[];
}

interface VLPExtractionSectionProps {
  onExtractionComplete?: (result: any) => void;
}

export function VLPExtractionSection({ onExtractionComplete }: VLPExtractionSectionProps) {
  const [extractedFields, setExtractedFields] = useState<PolicyField[]>([]);
  const [migrationReadiness, setMigrationReadiness] = useState<number>(0);
  const [isProcessing, setIsProcessing] = useState(false);

  // Standard VLP fields
  const standardFields = [
    'Policy Number',
    'Policy Holder Name',
    'Policy Holder SSN',
    'Issue Date',
    'Effective Date',
    'Face Amount',
    'Premium Amount',
    'Payment Frequency',
    'Beneficiary Name',
    'Beneficiary Relationship',
    'Agent Code',
    'Product Code',
    'Status Code',
  ];

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return 'bg-green-100 text-green-800';
    if (confidence >= 0.7) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  return (
    <div className="space-y-6">
      {/* Migration Readiness Score */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5 text-purple-600" />
            Migration Readiness Assessment
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Overall Readiness</span>
              <span className="text-2xl font-bold text-purple-600">
                {migrationReadiness}%
              </span>
            </div>
            <Progress value={migrationReadiness} className="h-3" />
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div className="text-center p-3 bg-green-50 rounded-lg">
                <div className="font-semibold text-green-700">Data Completeness</div>
                <div className="text-2xl font-bold text-green-600">87%</div>
              </div>
              <div className="text-center p-3 bg-yellow-50 rounded-lg">
                <div className="font-semibold text-yellow-700">Schema Compliance</div>
                <div className="text-2xl font-bold text-yellow-600">72%</div>
              </div>
              <div className="text-center p-3 bg-blue-50 rounded-lg">
                <div className="font-semibold text-blue-700">Data Quality</div>
                <div className="text-2xl font-bold text-blue-600">91%</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Extracted Fields */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-purple-600" />
            Extracted Policy Fields
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {standardFields.map((field) => {
              const extracted = extractedFields.find(f => f.name === field);
              return (
                <div key={field} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    {extracted ? (
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    ) : (
                      <AlertTriangle className="h-4 w-4 text-yellow-500" />
                    )}
                    <span className="font-medium">{field}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    {extracted ? (
                      <>
                        <span className="text-sm text-gray-600">{extracted.value || '—'}</span>
                        <Badge className={getConfidenceColor(extracted.confidence)}>
                          {Math.round(extracted.confidence * 100)}%
                        </Badge>
                      </>
                    ) : (
                      <Badge variant="outline">Pending</Badge>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
```

---

## Part 9: Testing Checklist

### Manual Testing Steps

1. **Login Flow**
   - [ ] Navigate to `/login`
   - [ ] Verify tenant selector is visible
   - [ ] Select each tenant (base, aar, pso, vlp) and verify selection persists
   - [ ] Login and verify redirect to home page

2. **Content Pillar**
   - [ ] Base tenant: All file types shown, mainframe + EDI visible
   - [ ] AAR tenant: Only PDF/Word/TXT shown, no mainframe/EDI
   - [ ] PSO tenant: CSV/Excel/PDF/XML shown, EDI visible, no mainframe
   - [ ] VLP tenant: Mainframe shown prominently, CSV/Excel/PDF

3. **Insights Pillar**
   - [ ] Base tenant: All tabs visible, all demo sections visible
   - [ ] AAR tenant: AARAnalysisSection visible, PSO/VLP hidden
   - [ ] PSO tenant: PSOViewer visible, AAR/VLP hidden
   - [ ] VLP tenant: VLPExtractionSection visible, AAR/PSO hidden

4. **Operations Pillar**
   - [ ] Verify SOP templates are tenant-specific
   - [ ] Verify workflow templates are tenant-specific
   - [ ] Verify coexistence analysis is visible/hidden per tenant

5. **Outcomes Pillar**
   - [ ] Verify generators are visible/hidden per tenant config

6. **Control Tower**
   - [ ] Verify tenant indicator shows current tenant
   - [ ] Verify metrics are filtered by tenant (when backend supports)

7. **Welcome Journey**
   - [ ] Verify welcome message matches tenant config
   - [ ] Verify description is tenant-appropriate

---

## Summary: What Changes Per Tenant

| Component | Base | AAR | PSO | VLP |
|-----------|------|-----|-----|-----|
| **Content: File Types** | All | PDF, Word, TXT | CSV, Excel, PDF, XML | Mainframe, CSV, Excel, PDF |
| **Content: Mainframe Parser** | ✅ | ❌ | ❌ | ✅ |
| **Content: EDI Parser** | ✅ | ❌ | ✅ | ❌ |
| **Insights: All Tabs** | ✅ | Most | All | All |
| **Insights: AAR Section** | ✅ | ✅ | ❌ | ❌ |
| **Insights: PSO Viewer** | ✅ | ❌ | ✅ | ❌ |
| **Insights: VLP Extraction** | ✅ | ❌ | ❌ | ✅ |
| **Operations: All Features** | ✅ | Limited | ✅ | ✅ |
| **Outcomes: All Features** | ✅ | Limited | ✅ | ✅ |
| **Welcome Message** | Generic | AAR-specific | PSO-specific | VLP-specific |
| **Agent Context** | Generic | Military/AAR | Utility/Permit | Insurance/Policy |

---

## Files to Create (New)

1. `shared/config/tenant-types.ts`
2. `shared/config/tenants/base.ts`
3. `shared/config/tenants/aar.ts`
4. `shared/config/tenants/pso.ts`
5. `shared/config/tenants/vlp.ts`
6. `shared/config/tenants/index.ts`
7. `shared/contexts/TenantContext.tsx`
8. `app/(protected)/pillars/insights/components/VLPExtractionSection.tsx`

## Files to Modify

1. `app/(public)/login/page.tsx` — Add tenant selector
2. `app/(protected)/layout.tsx` — Add TenantProvider
3. `app/(public)/layout.tsx` — Add TenantProvider
4. `app/(protected)/pillars/insights/page.tsx` — Conditional demo sections
5. `app/(protected)/pillars/content/page.tsx` — Conditional parsers
6. `app/(protected)/pillars/journey/page.tsx` — Conditional features
7. `app/(protected)/pillars/business-outcomes/page.tsx` — Conditional generators
8. `components/landing/WelcomeJourney.tsx` — Tenant-aware welcome
9. `app/(protected)/admin/page.tsx` — Tenant indicator
10. `app/(protected)/admin/components/ControlRoomView.tsx` — Tenant filtering

---

## Definition of Done

- [ ] All 4 tenants selectable from login
- [ ] Each tenant shows only relevant features
- [ ] Demo-specific sections (AAR, PSO, VLP) only appear in correct tenant
- [ ] Welcome message is tenant-appropriate
- [ ] Control Tower shows current tenant
- [ ] No TypeScript errors
- [ ] No console errors
- [ ] Manual testing checklist complete
