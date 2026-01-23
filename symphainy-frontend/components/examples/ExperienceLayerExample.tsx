/**
 * Experience Layer Example Component
 * 
 * Demonstrates how to use the new unified Experience Layer Client
 * to replace fragmented API calls with clean, production-ready code.
 */

"use client";

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/shared/auth/AuthProvider';
import { useGuideAgent } from '@/shared/agui/GuideAgentProvider';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
// import { Label } from '@/components/ui/label'; // Component doesn't exist

export const ExperienceLayerExample: React.FC = () => {
  // ============================================================================
  // HOOKS - Clean, unified API access
  // ============================================================================
  
  const { user, isAuthenticated, login, logout } = useAuth();
  const guideAgent = useGuideAgent();

  // ============================================================================
  // STATE
  // ============================================================================
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [files, setFiles] = useState<any[]>([]);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [guidance, setGuidance] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // ============================================================================
  // AUTHENTICATION METHODS
  // ============================================================================

  const handleLogin = async () => {
    if (!email || !password) {
      setError('Please enter email and password');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await login(email, password);
      // Login successful - AuthProvider handles state updates
    } catch (err) {
      setError('Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    setLoading(true);
    try {
      await logout();
      setFiles([]);
      setAnalysisResult(null);
      setGuidance(null);
    } finally {
      setLoading(false);
    }
  };

  // ============================================================================
  // CONTENT PILLAR METHODS
  // ============================================================================

  const handleFileUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Use the unified content pillar client
      // TODO: Replace with proper file upload API call
      const response = { 
        success: true, 
        file_id: `file_${Date.now()}`,
        message: 'File uploaded successfully'
      };

      if (response.success) {
        console.log('✅ File uploaded successfully:', response.file_id);
        await fetchFiles(); // Refresh file list
      } else {
        setError('Upload failed');
      }
    } catch (err) {
      setError('Upload failed');
    } finally {
      setLoading(false);
    }
  };

  const fetchFiles = async () => {
    try {
      // TODO: Replace with proper file listing API call
      const response = { success: true, files: [] };
      if (response.success) {
        setFiles(response.files || []);
      }
    } catch (err) {
      console.error('Failed to fetch files:', err);
    }
  };

  const handleFileParse = async (fileId: string) => {
    setLoading(true);
    setError(null);

    try {
      // TODO: Replace with proper file parsing API call
      const response = { 
        success: true, 
        parsed_data: {
          content: 'Sample parsed content',
          metadata: { format: 'json_structured' }
        }
      };

      if (response.success) {
        console.log('✅ File parsed successfully:', response.parsed_data);
      } else {
        setError('Parsing failed');
      }
    } catch (err) {
      setError('Parsing failed');
    } finally {
      setLoading(false);
    }
  };

  // ============================================================================
  // INSIGHTS PILLAR METHODS
  // ============================================================================

  const handleAnalyzeFiles = async () => {
    if (files.length === 0) {
      setError('No files to analyze');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const fileIds = files.map(f => f.file_id || f.id);
      // TODO: Replace with proper business data analysis API call
      const response = { 
        success: true, 
        analysis: {
          insights: ['Sample insight 1', 'Sample insight 2'],
          visualizations: ['chart1', 'chart2'],
          recommendations: ['Recommendation 1', 'Recommendation 2']
        }
      };

      if (response.success) {
        setAnalysisResult(response.analysis);
        console.log('✅ Analysis completed:', response.analysis);
      } else {
        setError('Analysis failed');
      }
    } catch (err) {
      setError('Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  // ============================================================================
  // GUIDE AGENT METHODS
  // ============================================================================

  const handleGetGuidance = async () => {
    setLoading(true);
    setError(null);

    try {
      // TODO: Replace with proper guide agent API call
      const response = { 
        success: true, 
        guidance: {
          message: 'Sample guidance for data analysis',
          next_steps: ['Step 1', 'Step 2'],
          recommendations: ['Recommendation 1', 'Recommendation 2']
        }
      };

      if (response.success) {
        setGuidance(response.guidance);
        console.log('✅ Guidance received:', response.guidance);
      } else {
        setError('Guidance request failed');
      }
    } catch (err) {
      setError('Guidance request failed');
    } finally {
      setLoading(false);
    }
  };

  // ============================================================================
  // EFFECTS
  // ============================================================================

  useEffect(() => {
    if (isAuthenticated) {
      fetchFiles();
    }
  }, [isAuthenticated]);

  // ============================================================================
  // RENDER
  // ============================================================================

  if (!isAuthenticated) {
    return (
      <div className="max-w-md mx-auto mt-8">
        <Card>
          <CardHeader>
            <CardTitle>Experience Layer Example</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="text-sm font-medium text-gray-700">Email</div>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email"
              />
            </div>
            <div>
              <div className="text-sm font-medium text-gray-700">Password</div>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
              />
            </div>
            {error && (
              <div className="text-red-600 text-sm">{error}</div>
            )}
            <Button 
              onClick={handleLogin} 
              disabled={loading}
              className="w-full"
            >
              {loading ? 'Logging in...' : 'Login'}
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Experience Layer Example</CardTitle>
          <div className="flex justify-between items-center">
            <div>
              Welcome, {user?.name} ({user?.email})
            </div>
            <Button onClick={handleLogout} variant="outline">
              Logout
            </Button>
          </div>
        </CardHeader>
      </Card>

      {/* File Upload Section */}
      <Card>
        <CardHeader>
          <CardTitle>Content Pillar - File Upload</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <div className="text-sm font-medium text-gray-700">Select File</div>
            <Input
              id="file"
              type="file"
              onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
              accept=".pdf,.doc,.docx,.txt,.csv"
            />
          </div>
          <Button 
            onClick={handleFileUpload} 
            disabled={!selectedFile || loading}
          >
            {loading ? 'Uploading...' : 'Upload File'}
          </Button>
        </CardContent>
      </Card>

      {/* Files List */}
      <Card>
        <CardHeader>
          <CardTitle>Your Files ({files.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {files.length === 0 ? (
            <p className="text-gray-500">No files uploaded yet</p>
          ) : (
            <div className="space-y-2">
              {files.map((file, index) => (
                <div key={index} className="flex justify-between items-center p-2 border rounded">
                  <div>
                    <div className="font-medium">{file.filename || file.ui_name}</div>
                    <div className="text-sm text-gray-500">
                      {file.file_type} • {file.file_size} bytes
                    </div>
                  </div>
                  <Button 
                    size="sm" 
                    onClick={() => handleFileParse(file.file_id || file.id)}
                    disabled={loading}
                  >
                    Parse
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Insights Section */}
      <Card>
        <CardHeader>
          <CardTitle>Insights Pillar - Analysis</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Button 
            onClick={handleAnalyzeFiles} 
            disabled={files.length === 0 || loading}
          >
            {loading ? 'Analyzing...' : 'Analyze Files'}
          </Button>
          {analysisResult && (
            <div className="p-4 bg-green-50 border border-green-200 rounded">
              <h4 className="font-medium text-green-800">Analysis Complete</h4>
              <p className="text-green-700">
                Confidence Score: {analysisResult.confidence_score}
              </p>
              <p className="text-green-700">
                Insights: {analysisResult.insights?.length || 0} found
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Guide Agent Section */}
      <Card>
        <CardHeader>
          <CardTitle>Guide Agent - Guidance</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Button 
            onClick={handleGetGuidance} 
            disabled={loading}
          >
            {loading ? 'Getting Guidance...' : 'Get Guidance'}
          </Button>
          {guidance && (
            <div className="p-4 bg-blue-50 border border-blue-200 rounded">
              <h4 className="font-medium text-blue-800">Guidance Received</h4>
              <div className="text-blue-700">
                <p><strong>Intent:</strong> {guidance.intent_analysis}</p>
                <p><strong>Recommended Actions:</strong></p>
                <ul className="list-disc list-inside ml-4">
                  {guidance.recommended_actions?.map((action: string, index: number) => (
                    <li key={index}>{action}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Error Display */}
      {error && (
        <Card>
          <CardContent className="p-4">
            <div className="text-red-600">{error}</div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default ExperienceLayerExample;
