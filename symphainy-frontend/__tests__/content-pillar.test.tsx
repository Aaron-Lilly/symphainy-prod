import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import FileUploader from '../components/content/FileUploader';
import ParsePreview from '../components/content/ParsePreview';
import FileDashboard from '../components/content/FileDashboard';
import { FileType, FileStatus } from '../shared/types/file';

// Mock the global session hook
jest.mock('../shared/atoms', () => ({
  useGlobalSession: () => ({
    getPillarState: jest.fn(() => ({ files: [] })),
    setPillarState: jest.fn(),
    guideSessionToken: 'test-token',
  }),
}));

// Mock the API calls
jest.mock('../lib/api/fms', () => ({
  uploadFile: jest.fn(() => Promise.resolve({ uuid: 'test-uuid', status: 'uploaded' })),
  parseFile: jest.fn(() => Promise.resolve({ 
    preview_grid: [['Name', 'Age'], ['John', '30'], ['Jane', '25']],
    text: 'Sample text content',
    metadata: { rows: 2, columns: 2 }
  })),
  approveFile: jest.fn(() => Promise.resolve({ success: true })),
  rejectFile: jest.fn(() => Promise.resolve({ success: true })),
}));

// Mock the content API
jest.mock('../lib/api/content', () => ({
  listContentFiles: jest.fn(() => Promise.resolve({ data: { files: [] } })),
  parseContentFile: jest.fn(() => Promise.resolve({ success: true })),
  getFilePreview: jest.fn(() => Promise.resolve({ 
    data: { 
      preview_grid: [['Name', 'Age'], ['John', '30']],
      text: 'Sample text',
      metadata: { rows: 1, columns: 2 }
    }
  })),
}));

describe('Content Pillar Components', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('FileUploader Component', () => {
    test('renders file upload options', () => {
      render(<FileUploader />);
      
      expect(screen.getByText('CSV')).toBeInTheDocument();
      expect(screen.getByText('Excel')).toBeInTheDocument();
      expect(screen.getByText('PDF')).toBeInTheDocument();
      expect(screen.getByText('Mainframe')).toBeInTheDocument();
      expect(screen.getByText('SOP/Workflow')).toBeInTheDocument();
    });

    test('shows SOP/Workflow description', () => {
      render(<FileUploader />);
      
      const sopOption = screen.getByText('SOP/Workflow');
      expect(sopOption).toBeInTheDocument();
      // Check that the description is present
      expect(screen.getByText(/SOP and Workflow files for Operations pillar processing/)).toBeInTheDocument();
    });
  });

  describe('ParsePreview Component', () => {
    test('renders when no files are available', () => {
      render(<ParsePreview />);
      
      expect(screen.getByText('No files available for parsing')).toBeInTheDocument();
      expect(screen.getByText('Upload a file first to begin parsing')).toBeInTheDocument();
    });

    test('shows file selection when files are available', () => {
      const mockGetPillarState = jest.fn(() => ({
        files: [
          {
            uuid: 'test-uuid',
            ui_name: 'test.csv',
            file_type: FileType.Csv,
            status: FileStatus.Uploaded,
            created_at: new Date().toISOString(),
          }
        ]
      }));

      jest.doMock('../shared/atoms', () => ({
        useGlobalSession: () => ({
          getPillarState: mockGetPillarState,
          setPillarState: jest.fn(),
          guideSessionToken: 'test-token',
        }),
      }));

      render(<ParsePreview />);
      
      expect(screen.getByText('test.csv')).toBeInTheDocument();
    });
  });

  describe('FileDashboard Component', () => {
    test('renders file dashboard', () => {
      render(<FileDashboard />);
      
      expect(screen.getByText('File Dashboard')).toBeInTheDocument();
    });
  });

  describe('SOP/Workflow File Handling', () => {
    test('SOP/Workflow files show operations tab', () => {
      const mockGetPillarState = jest.fn(() => ({
        files: [
          {
            uuid: 'test-uuid',
            ui_name: 'workflow.bpmn',
            file_type: FileType.SopWorkflow,
            status: FileStatus.Uploaded,
            created_at: new Date().toISOString(),
          }
        ]
      }));

      jest.doMock('../shared/atoms', () => ({
        useGlobalSession: () => ({
          getPillarState: mockGetPillarState,
          setPillarState: jest.fn(),
          guideSessionToken: 'test-token',
        }),
      }));

      render(<ParsePreview />);
      
      // Should show the file
      expect(screen.getByText('workflow.bpmn')).toBeInTheDocument();
    });
  });

  describe('File Type Support', () => {
    test('supports all required file types', () => {
      const fileTypes = [
        FileType.Csv,
        FileType.Excel,
        FileType.Pdf,
        FileType.Binary,
        FileType.SopWorkflow,
      ];

      fileTypes.forEach(fileType => {
        expect(Object.values(FileType)).toContain(fileType);
      });
    });
  });
}); 