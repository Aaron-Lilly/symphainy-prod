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
