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
