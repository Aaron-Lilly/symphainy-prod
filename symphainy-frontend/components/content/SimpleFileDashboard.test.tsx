import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import SimpleFileDashboard from './SimpleFileDashboard';
import { listContentFiles } from '@/lib/api/content';

// Mock the API call
jest.mock('@/lib/api/content', () => ({
  listContentFiles: jest.fn(),
}));

// Mock the global session
jest.mock('@/shared/agui/GlobalSessionProvider', () => ({
  useGlobalSession: () => ({
    guideSessionToken: 'mock-token',
  }),
}));

// Mock toast
jest.mock('sonner', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

describe('SimpleFileDashboard', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders without crashing', () => {
    render(<SimpleFileDashboard />);
    expect(screen.getByText(/Files/)).toBeInTheDocument();
  });

  it('shows loading state initially', () => {
    render(<SimpleFileDashboard />);
    expect(screen.getByText(/Files/)).toBeInTheDocument();
    expect(screen.getByText('Refresh')).toBeInTheDocument();
  });

  it('displays files when API call succeeds', async () => {
    const mockFiles = [
      {
        id: '1',
        user_id: 'user1',
        ui_name: 'test.pdf',
        file_type: 'PDF',
        mime_type: 'application/pdf',
        original_path: '/uploads/test.pdf',
        status: 'uploaded',
        metadata: { size: 12345 },
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      }
    ];

    (listContentFiles as jest.Mock).mockResolvedValue(mockFiles);

    render(<SimpleFileDashboard />);

    await waitFor(() => {
      expect(screen.getByText('test.pdf')).toBeInTheDocument();
    });

    expect(screen.getByText('PDF')).toBeInTheDocument();
    expect(screen.getByText('uploaded')).toBeInTheDocument();
  });
}); 