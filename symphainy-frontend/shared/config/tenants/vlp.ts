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
