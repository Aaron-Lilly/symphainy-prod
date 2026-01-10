/**
 * Test Data Setup for MVP 4-Pillar Journey
 * 
 * Provides test files and mock data for E2E testing of the complete MVP journey
 */

import { test as base } from '@playwright/test';
import fs from 'fs';
import path from 'path';

// ============================================
// Test Data Types
// ============================================

export interface TestFile {
  name: string;
  content: string;
  type: string;
  path: string;
}

export interface MockAnalysisResult {
  type: string;
  data: any;
  summary: string;
  visual?: any;
}

export interface MockWorkflowResult {
  workflow: any;
  sop: any;
  coexistenceBlueprint: any;
}

// ============================================
// Test Files Setup
// ============================================

export const testFiles: TestFile[] = [
  {
    name: 'sample.csv',
    content: `Name,Age,Email,Status
John Doe,30,john@example.com,Active
Jane Smith,25,jane@example.com,Inactive
Bob Johnson,35,bob@example.com,Active
Alice Brown,28,alice@example.com,Active
Charlie Wilson,42,charlie@example.com,Inactive`,
    type: 'text/csv',
    path: 'test-files/sample.csv'
  },
  {
    name: 'mainframe.bin',
    content: Buffer.from([0x01, 0x02, 0x03, 0x04, 0x05]).toString('base64'),
    type: 'application/octet-stream',
    path: 'test-files/mainframe.bin'
  },
  {
    name: 'copybook.cpy',
    content: `       01  CUSTOMER-RECORD.
           05  CUSTOMER-ID        PIC X(10).
           05  CUSTOMER-NAME      PIC X(50).
           05  CUSTOMER-ADDRESS   PIC X(100).
           05  CUSTOMER-PHONE     PIC X(15).
           05  CUSTOMER-EMAIL     PIC X(50).
           05  CUSTOMER-STATUS    PIC X(1).`,
    type: 'text/plain',
    path: 'test-files/copybook.cpy'
  },
  {
    name: 'large-dataset.csv',
    content: Array.from({ length: 1000 }, (_, i) => 
      `Customer${i},${20 + (i % 50)},customer${i}@example.com,${i % 2 === 0 ? 'Active' : 'Inactive'}`
    ).join('\n'),
    type: 'text/csv',
    path: 'test-files/large-dataset.csv'
  },
  {
    name: 'corrupted.csv',
    content: `Name,Age,Email,Status
John Doe,30,john@example.com,Active
Jane Smith,25,jane@example.com,Inactive
Bob Johnson,35,bob@example.com,Active
Alice Brown,28,alice@example.com,Active
Charlie Wilson,42,charlie@example.com,Inactive
Invalid,Row,With,Extra,Columns`,
    type: 'text/csv',
    path: 'test-files/corrupted.csv'
  }
];

// ============================================
// Mock Analysis Results
// ============================================

export const mockAnalysisResults: Record<string, MockAnalysisResult> = {
  anomaly: {
    type: 'anomaly-detection',
    data: {
      anomalies: [
        { field: 'Age', value: 42, reason: 'Outlier in age distribution' },
        { field: 'Status', value: 'Inactive', reason: 'Unusual status pattern' }
      ],
      summary: 'Found 2 anomalies in the dataset'
    },
    summary: 'Anomaly detection identified 2 potential data quality issues',
    visual: {
      type: 'scatter-plot',
      data: [
        { x: 'Age', y: 30, anomaly: false },
        { x: 'Age', y: 42, anomaly: true },
        { x: 'Age', y: 25, anomaly: false }
      ]
    }
  },
  eda: {
    type: 'eda-analysis',
    data: {
      statistics: {
        totalRecords: 5,
        ageRange: { min: 25, max: 42, mean: 32 },
        statusDistribution: { Active: 3, Inactive: 2 }
      },
      patterns: [
        'Age distribution shows normal spread',
        'Status is evenly distributed'
      ]
    },
    summary: 'Exploratory data analysis reveals normal data distribution patterns',
    visual: {
      type: 'bar-chart',
      data: [
        { category: 'Active', count: 3 },
        { category: 'Inactive', count: 2 }
      ]
    }
  },
  business: {
    type: 'business-analysis',
    data: {
      insights: [
        '60% of customers are active',
        'Average customer age is 32 years',
        'Customer base shows good diversity'
      ],
      recommendations: [
        'Focus retention efforts on inactive customers',
        'Consider age-based marketing strategies',
        'Monitor customer engagement patterns'
      ]
    },
    summary: 'Business analysis provides actionable insights for customer management',
    visual: {
      type: 'pie-chart',
      data: [
        { label: 'Active', value: 60 },
        { label: 'Inactive', value: 40 }
      ]
    }
  },
  visualization: {
    type: 'visualizations',
    data: {
      charts: [
        {
          type: 'bar-chart',
          title: 'Customer Status Distribution',
          data: [
            { status: 'Active', count: 3 },
            { status: 'Inactive', count: 2 }
          ]
        },
        {
          type: 'histogram',
          title: 'Age Distribution',
          data: [
            { range: '20-30', count: 2 },
            { range: '30-40', count: 2 },
            { range: '40-50', count: 1 }
          ]
        }
      ]
    },
    summary: 'Multiple visualizations created for data exploration',
    visual: {
      type: 'dashboard',
      charts: 2
    }
  }
};

// ============================================
// Mock Workflow Results
// ============================================

export const mockWorkflowResults: MockWorkflowResult = {
  workflow: {
    id: 'workflow-001',
    name: 'Customer Data Processing Workflow',
    steps: [
      {
        id: 'step-1',
        name: 'Data Validation',
        type: 'validation',
        description: 'Validate customer data format and completeness'
      },
      {
        id: 'step-2',
        name: 'Data Enrichment',
        type: 'enrichment',
        description: 'Enrich customer data with additional information'
      },
      {
        id: 'step-3',
        name: 'Status Update',
        type: 'update',
        description: 'Update customer status based on business rules'
      }
    ],
    visual: {
      type: 'flowchart',
      nodes: [
        { id: 'start', type: 'start', label: 'Start' },
        { id: 'validate', type: 'process', label: 'Validate Data' },
        { id: 'enrich', type: 'process', label: 'Enrich Data' },
        { id: 'update', type: 'process', label: 'Update Status' },
        { id: 'end', type: 'end', label: 'End' }
      ],
      edges: [
        { from: 'start', to: 'validate' },
        { from: 'validate', to: 'enrich' },
        { from: 'enrich', to: 'update' },
        { from: 'update', to: 'end' }
      ]
    }
  },
  sop: {
    id: 'sop-001',
    title: 'Customer Data Processing Standard Operating Procedure',
    version: '1.0',
    sections: [
      {
        title: 'Purpose',
        content: 'This SOP defines the standard process for processing customer data files.'
      },
      {
        title: 'Scope',
        content: 'Applies to all customer data processing activities.'
      },
      {
        title: 'Procedure',
        content: '1. Validate incoming data\n2. Enrich with additional information\n3. Update customer status\n4. Generate reports'
      }
    ]
  },
  coexistenceBlueprint: {
    id: 'blueprint-001',
    title: 'Customer Data Coexistence Blueprint',
    currentState: {
      description: 'Manual data processing with limited automation',
      challenges: [
        'Time-consuming manual validation',
        'Inconsistent data quality',
        'Limited scalability'
      ]
    },
    futureState: {
      description: 'Automated data processing with AI-powered insights',
      benefits: [
        'Reduced processing time by 80%',
        'Improved data quality',
        'Scalable architecture'
      ]
    },
    recommendations: [
      'Implement automated validation rules',
      'Deploy AI-powered data enrichment',
      'Establish real-time monitoring'
    ],
    roadmap: [
      {
        phase: 'Phase 1',
        duration: '3 months',
        activities: ['Setup infrastructure', 'Implement basic automation']
      },
      {
        phase: 'Phase 2',
        duration: '6 months',
        activities: ['Deploy AI components', 'Establish monitoring']
      },
      {
        phase: 'Phase 3',
        duration: '12 months',
        activities: ['Full automation', 'Continuous improvement']
      }
    ]
  }
};

// ============================================
// Mock Experience Results
// ============================================

export const mockExperienceResults = {
  roadmap: {
    title: 'Digital Transformation Roadmap',
    phases: [
      {
        name: 'Foundation Phase',
        duration: '3-6 months',
        objectives: [
          'Establish data governance framework',
          'Implement basic automation',
          'Train team on new processes'
        ],
        deliverables: [
          'Data governance policy',
          'Automated validation system',
          'Training materials'
        ]
      },
      {
        name: 'Enhancement Phase',
        duration: '6-12 months',
        objectives: [
          'Deploy AI-powered insights',
          'Implement advanced analytics',
          'Establish monitoring and alerting'
        ],
        deliverables: [
          'AI insights platform',
          'Advanced analytics dashboard',
          'Monitoring system'
        ]
      },
      {
        name: 'Optimization Phase',
        duration: '12-18 months',
        objectives: [
          'Full process automation',
          'Continuous improvement',
          'Scale to enterprise level'
        ],
        deliverables: [
          'Fully automated workflows',
          'Continuous improvement framework',
          'Enterprise-scale deployment'
        ]
      }
    ]
  },
  pocProposal: {
    title: 'Proof of Concept Proposal',
    executiveSummary: 'Proposed POC to demonstrate the value of automated customer data processing',
    objectives: [
      'Validate automated data processing capabilities',
      'Measure performance improvements',
      'Assess user adoption and satisfaction'
    ],
    scope: {
      included: [
        'Customer data file processing',
        'Automated validation and enrichment',
        'Basic reporting and analytics'
      ],
      excluded: [
        'Integration with legacy systems',
        'Advanced AI features',
        'Enterprise-wide deployment'
      ]
    },
    timeline: {
      duration: '3 months',
      milestones: [
        { week: 2, milestone: 'Environment setup and configuration' },
        { week: 6, milestone: 'Basic automation implementation' },
        { week: 10, milestone: 'Testing and validation' },
        { week: 12, milestone: 'POC completion and evaluation' }
      ]
    },
    successMetrics: [
      '50% reduction in processing time',
      '90% improvement in data quality',
      '80% user satisfaction score'
    ],
    budget: {
      estimatedCost: '$150,000',
      breakdown: [
        'Infrastructure: $50,000',
        'Development: $75,000',
        'Testing and validation: $25,000'
      ]
    }
  }
};

// ============================================
// Test Setup Utilities
// ============================================

export async function setupTestFiles(): Promise<void> {
  const testFilesDir = path.join(process.cwd(), 'test-files');
  
  // Create test-files directory if it doesn't exist
  if (!fs.existsSync(testFilesDir)) {
    fs.mkdirSync(testFilesDir, { recursive: true });
  }
  
  // Create test files
  for (const file of testFiles) {
    const filePath = path.join(testFilesDir, file.name);
    fs.writeFileSync(filePath, file.content);
  }
}

export async function cleanupTestFiles(): Promise<void> {
  const testFilesDir = path.join(process.cwd(), 'test-files');
  
  if (fs.existsSync(testFilesDir)) {
    fs.rmSync(testFilesDir, { recursive: true, force: true });
  }
}

// ============================================
// Test Data Exports
// ============================================

// Export test data for use in tests
// Note: Variables are already exported above

export { expect } from '@playwright/test'; 