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
