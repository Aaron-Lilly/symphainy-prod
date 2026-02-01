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
