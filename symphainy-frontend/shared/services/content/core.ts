/**
 * Content Service Core
 * Core content service functionality for file management and processing
 */

import { getGlobalConfig } from '../../config';
import { 
  SimpleFileData, 
  ParseFileRequest, 
  ParseFileResponse,
  AnalyzeFileRequest,
  AnalyzeFileResponse,
  FilePreviewData,
  FileAnalysisData,
  ContentSessionStatus,
  ContentSessionUpdate
} from './types';

const config = getGlobalConfig();
const API_BASE = `${config.getSection('api').baseURL}/api/content`;

// Helper to create standardized authenticated headers
const getAuthHeaders = (token: string, sessionToken?: string) => {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  
  if (sessionToken) {
    headers["X-Session-Token"] = sessionToken;
  }
  
  return headers;
};

export class ContentService {
  private token: string;

  constructor(token: string) {
    this.token = token;
  }

  async listContentFiles(sessionToken?: string, userId?: string): Promise<SimpleFileData[]> {
    const params = new URLSearchParams();
    if (userId) params.append('user_id', userId);
    if (sessionToken) params.append('session_token', sessionToken);
    
    const res = await fetch(`${API_BASE}/files?${params.toString()}`, {
      headers: getAuthHeaders(this.token, sessionToken),
    });
    
    if (!res.ok) {
      throw new Error(`Failed to fetch files: ${res.status} ${res.statusText}`);
    }
    
    const response = await res.json();
    
    if (response.status === 'success' && response.data && response.data.files) {
      return response.data.files;
    }
    
    if (Array.isArray(response)) {
      return response;
    }
    
    throw new Error('Invalid response format from content API');
  }

  async parseFile(request: ParseFileRequest): Promise<ParseFileResponse> {
    const res = await fetch(`${API_BASE}/parse`, {
      method: 'POST',
      headers: getAuthHeaders(this.token, request.session_token),
      body: JSON.stringify(request),
    });
    
    if (!res.ok) {
      throw new Error(`Failed to parse file: ${res.status} ${res.statusText}`);
    }
    
    const response = await res.json();
    
    if (response.status === 'success' && response.data) {
      return response.data;
    }
    
    return response;
  }

  async getFilePreview(fileId: string, sessionToken?: string, userId?: string): Promise<FilePreviewData> {
    const params = new URLSearchParams();
    if (userId) params.append('user_id', userId);
    if (sessionToken) params.append('session_token', sessionToken);
    
    const res = await fetch(`${API_BASE}/files/${fileId}/preview?${params.toString()}`, {
      headers: getAuthHeaders(this.token, sessionToken),
    });
    
    if (!res.ok) {
      throw new Error(`Failed to get file preview: ${res.status} ${res.statusText}`);
    }
    
    const response = await res.json();
    
    if (response.status === 'success' && response.data) {
      return response.data;
    }
    
    return response;
  }

  async analyzeFile(request: AnalyzeFileRequest): Promise<AnalyzeFileResponse> {
    const res = await fetch(`${API_BASE}/analyze`, {
      method: 'POST',
      headers: getAuthHeaders(this.token, request.session_token),
      body: JSON.stringify(request),
    });
    
    if (!res.ok) {
      throw new Error(`Failed to analyze file: ${res.status} ${res.statusText}`);
    }
    
    const response = await res.json();
    
    if (response.status === 'success' && response.data) {
      return response.data;
    }
    
    return response;
  }

  async getFileAnalysis(fileId: string, sessionToken?: string, userId?: string): Promise<FileAnalysisData> {
    const params = new URLSearchParams();
    if (userId) params.append('user_id', userId);
    if (sessionToken) params.append('session_token', sessionToken);
    
    const res = await fetch(`${API_BASE}/files/${fileId}/analysis?${params.toString()}`, {
      headers: getAuthHeaders(this.token, sessionToken),
    });
    
    if (!res.ok) {
      throw new Error(`Failed to get file analysis: ${res.status} ${res.statusText}`);
    }
    
    const response = await res.json();
    
    if (response.status === 'success' && response.data) {
      return response.data;
    }
    
    return response;
  }

  async getContentSessionStatus(sessionToken: string): Promise<ContentSessionStatus> {
    const res = await fetch(`${API_BASE}/session/status`, {
      headers: getAuthHeaders(this.token, sessionToken),
    });
    
    if (!res.ok) {
      throw new Error(`Failed to get session status: ${res.status} ${res.statusText}`);
    }
    
    const response = await res.json();
    
    if (response.status === 'success' && response.data) {
      return response.data;
    }
    
    return response;
  }

  async updateContentSession(sessionToken: string, updates: ContentSessionUpdate): Promise<any> {
    const res = await fetch(`${API_BASE}/session/update`, {
      method: 'POST',
      headers: getAuthHeaders(this.token, sessionToken),
      body: JSON.stringify(updates),
    });
    
    if (!res.ok) {
      throw new Error(`Failed to update session: ${res.status} ${res.statusText}`);
    }
    
    const response = await res.json();
    
    if (response.status === 'success' && response.data) {
      return response.data;
    }
    
    return response;
  }
} 