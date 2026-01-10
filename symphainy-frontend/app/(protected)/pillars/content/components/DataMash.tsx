'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Loader } from '@/components/ui/loader';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from 'sonner';
import { Brain, Database, Layers, Sparkles, RefreshCw, Wand2, Eye, BookOpen } from 'lucide-react';
import { listEmbeddings, previewEmbeddings, createEmbeddings, listParsedFilesWithEmbeddings, getMashContext, type EmbeddingFile, type SemanticLayerPreview } from '@/lib/api/content';
import { useGlobalSession } from '@/shared/agui/GlobalSessionProvider';
import { ContentAPIManager } from '@/shared/managers/ContentAPIManager';
import MashContextBanner from './MashContextBanner';
import CorrelationChain from './CorrelationChain';
import ThreeLayerPatternDiagram from './ThreeLayerPatternDiagram';

interface DataMashProps {
  selectedFile?: any;
}

export default function DataMash({ selectedFile: propSelectedFile }: DataMashProps) {
  const { getPillarState, guideSessionToken } = useGlobalSession();
  
  const [selectedFileUuid, setSelectedFileUuid] = useState<string | null>(null);
  const [selectedParsedFileId, setSelectedParsedFileId] = useState<string | null>(null);
  const [parsedFiles, setParsedFiles] = useState<any[]>([]);
  const [loadingParsedFiles, setLoadingParsedFiles] = useState(false);
  const [loading, setLoading] = useState(false);
  const [creatingEmbeddings, setCreatingEmbeddings] = useState(false);
  const [createEmbeddingsError, setCreateEmbeddingsError] = useState<string | null>(null);
  const [embeddingFiles, setEmbeddingFiles] = useState<EmbeddingFile[]>([]);
  const [selectedContentId, setSelectedContentId] = useState<string | null>(null);
  const [preview, setPreview] = useState<SemanticLayerPreview | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [parsedFilesWithEmbeddings, setParsedFilesWithEmbeddings] = useState<any[]>([]);
  const [loadingParsedFilesWithEmbeddings, setLoadingParsedFilesWithEmbeddings] = useState(false);
  const [selectedParsedFileWithEmbeddings, setSelectedParsedFileWithEmbeddings] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>('create');
  const [lastCreatedEmbedding, setLastCreatedEmbedding] = useState<{file_id?: string; parsed_file_id?: string; content_id?: string; workflow_id?: string} | null>(null);
  const [mashContext, setMashContext] = useState<any>(null);
  const [loadingMashContext, setLoadingMashContext] = useState(false);

  // Get files from all pillar states to find uploaded files
  const parsingState = getPillarState('parsing') || { files: [] };
  const dataState = getPillarState('data') || { files: [] };
  const contentState = getPillarState('content') || { files: [] };
  const insightsState = getPillarState('insights') || { files: [] };
  const operationsState = getPillarState('operations') || { files: [] };
  
  // Combine all files and deduplicate by UUID
  const allFiles = [
    ...(parsingState.files || []),
    ...(dataState.files || []),
    ...(contentState.files || []),
    ...(insightsState.files || []),
    ...(operationsState.files || [])
  ];
  
  const uniqueFilesMap = new Map();
  allFiles.forEach((file: any) => {
    if (!uniqueFilesMap.has(file.uuid)) {
      uniqueFilesMap.set(file.uuid, file);
    }
  });
  
  const availableFiles = Array.from(uniqueFilesMap.values()) as any[];

  // Use prop file if provided, otherwise use selected file from state
  const selectedFile = propSelectedFile || availableFiles.find((f: any) => f.uuid === selectedFileUuid);

  // Load parsed files on mount
  const loadParsedFiles = useCallback(async () => {
    if (!guideSessionToken) {
      setParsedFiles([]);
      return;
    }

    setLoadingParsedFiles(true);
    try {
      const apiManager = new ContentAPIManager(guideSessionToken);
      const parsedFilesList = await apiManager.listParsedFiles();
      setParsedFiles(parsedFilesList);
      
      // Auto-select first parsed file if available and none selected
      if (parsedFilesList.length > 0 && !selectedParsedFileId) {
        const firstFileId = parsedFilesList[0].parsed_file_id || parsedFilesList[0].id;
        setSelectedParsedFileId(firstFileId);
      }
    } catch (error) {
      console.error('[DataMash] Error loading parsed files:', error);
      setParsedFiles([]);
      toast.error('Failed to load parsed files');
    } finally {
      setLoadingParsedFiles(false);
    }
  }, [guideSessionToken, selectedParsedFileId]);

  useEffect(() => {
    loadParsedFiles();
  }, [loadParsedFiles]);

  // Listen for parse completion events to refresh parsed files list
  useEffect(() => {
    const handleParseComplete = () => {
      loadParsedFiles();
    };

    window.addEventListener('fileParsed', handleParseComplete);
    return () => {
      window.removeEventListener('fileParsed', handleParseComplete);
    };
  }, [loadParsedFiles]);

  // Auto-select the first file if none is selected and no prop file
  useEffect(() => {
    if (!propSelectedFile && availableFiles.length > 0 && !selectedFileUuid) {
      setSelectedFileUuid(availableFiles[0].uuid);
    }
  }, [availableFiles.length, selectedFileUuid, propSelectedFile]);

  // Load embeddings when file is selected
  useEffect(() => {
    if (selectedFile?.uuid) {
      loadEmbeddings(selectedFile.uuid);
    } else {
      setEmbeddingFiles([]);
      setSelectedContentId(null);
      setPreview(null);
    }
  }, [selectedFile?.uuid]);

  // Load preview when content_id is selected
  useEffect(() => {
    if (selectedContentId) {
      loadPreview(selectedContentId);
      loadMashContext({ content_id: selectedContentId });
    } else {
      setPreview(null);
      setMashContext(null);
    }
  }, [selectedContentId]);
  
  // Load mash context when file_id or parsed_file_id changes
  useEffect(() => {
    if (selectedFile?.uuid || selectedParsedFileId) {
      loadMashContext({
        file_id: selectedFile?.uuid,
        parsed_file_id: selectedParsedFileId || undefined
      });
    }
  }, [selectedFile?.uuid, selectedParsedFileId]);
  
  const loadMashContext = async (options: { content_id?: string; file_id?: string; parsed_file_id?: string }) => {
    setLoadingMashContext(true);
    try {
      const token = guideSessionToken || "debug-token";
      const result = await getMashContext(options, token);
      if (result.success && result.mash_context) {
        setMashContext(result.mash_context);
      } else {
        // If no mash context found, that's okay - use derived data
        setMashContext(null);
      }
    } catch (error) {
      console.error('[DataMash] Error loading mash context:', error);
      setMashContext(null);
    } finally {
      setLoadingMashContext(false);
    }
  };

  const loadEmbeddings = async (fileId: string) => {
    setLoading(true);
    try {
      const token = guideSessionToken || "debug-token";
      const result = await listEmbeddings(fileId, token);
      if (result.success) {
        setEmbeddingFiles(result.embeddings);
        // Auto-select first embedding if available
        if (result.embeddings.length > 0) {
          setSelectedContentId(result.embeddings[0].content_id);
        } else {
          setSelectedContentId(null);
        }
      } else {
        toast.error(result.error || "Failed to load embeddings");
        setEmbeddingFiles([]);
      }
    } catch (error) {
      toast.error(`Error loading embeddings: ${error instanceof Error ? error.message : 'Unknown error'}`);
      setEmbeddingFiles([]);
    } finally {
      setLoading(false);
    }
  };

  const loadPreview = async (contentId: string) => {
    setPreviewLoading(true);
    try {
      const token = guideSessionToken || "debug-token";
      const result = await previewEmbeddings(contentId, token);
      if (result.success) {
        setPreview(result);
      } else {
        toast.error(result.error || "Failed to load preview");
        setPreview(null);
      }
    } catch (error) {
      toast.error(`Error loading preview: ${error instanceof Error ? error.message : 'Unknown error'}`);
      setPreview(null);
    } finally {
      setPreviewLoading(false);
    }
  };

  const handleCreateEmbeddings = async () => {
    if (!selectedParsedFileId) {
      toast.error("Please select a parsed file first");
      return;
    }

    setCreatingEmbeddings(true);
    setCreateEmbeddingsError(null);
    
    try {
      const token = guideSessionToken || "debug-token";
      console.log('[DataMash] Creating embeddings for parsed_file_id:', selectedParsedFileId);
      const result = await createEmbeddings(selectedParsedFileId, token, selectedFile?.uuid);
      
      console.log('[DataMash] createEmbeddings result:', result);
      
      if (result.success) {
        // Check for edge case: success but no content_id
        if (!result.content_id) {
          const errorMsg = "Embedding creation succeeded but no content_id was returned. Please check logs.";
          console.error('[DataMash] Embedding creation succeeded but no content_id:', result);
          setCreateEmbeddingsError(errorMsg);
          toast.error(errorMsg);
          return;
        }
        
        // Success path: we have content_id
        const count = result.embeddings_count || 0;
        toast.success(`Successfully created ${count} embedding${count !== 1 ? 's' : ''}!`);
        
        // Store embedding info for mash context
        setLastCreatedEmbedding({
          file_id: result.file_id || selectedFile?.uuid,
          parsed_file_id: selectedParsedFileId,
          content_id: result.content_id,
          workflow_id: (result as any).workflow_id || undefined
        });
        
        // Switch to view tab to see the result
        setActiveTab('view');
        
        // Refresh embeddings list for the file (use file_id from result if available, otherwise selectedFile)
        const fileIdToUse = result.file_id || selectedFile?.uuid;
        if (fileIdToUse) {
          await loadEmbeddings(fileIdToUse);
        }
        
        // Refresh parsed files list in case metadata was updated
        await loadParsedFiles();
        
        // Refresh parsed files with embeddings list (this should now show the new embeddings)
        await loadParsedFilesWithEmbeddings();
      } else {
        // Failure path
        const errorMsg = result.error || "Failed to create embeddings";
        console.error('[DataMash] Embedding creation failed:', errorMsg, result);
        setCreateEmbeddingsError(errorMsg);
        toast.error(errorMsg);
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Unknown error';
      setCreateEmbeddingsError(errorMsg);
      toast.error(`Error creating embeddings: ${errorMsg}`);
    } finally {
      setCreatingEmbeddings(false);
    }
  };

  const loadParsedFilesWithEmbeddings = useCallback(async () => {
    if (!guideSessionToken) {
      setParsedFilesWithEmbeddings([]);
      return;
    }

    setLoadingParsedFilesWithEmbeddings(true);
    try {
      const token = guideSessionToken || "debug-token";
      const result = await listParsedFilesWithEmbeddings(token);
      if (result.success) {
        setParsedFilesWithEmbeddings(result.parsed_files);
        
        // Auto-select first parsed file if available and none selected
        if (result.parsed_files.length > 0 && !selectedParsedFileWithEmbeddings) {
          const firstFile = result.parsed_files[0];
          setSelectedParsedFileWithEmbeddings(firstFile.parsed_file_id || firstFile.id);
          // Auto-load preview if content_id is available
          if (firstFile.content_id) {
            setSelectedContentId(firstFile.content_id);
          }
        }
      } else {
        toast.error(result.error || "Failed to load parsed files with embeddings");
        setParsedFilesWithEmbeddings([]);
      }
    } catch (error) {
      console.error('[DataMash] Error loading parsed files with embeddings:', error);
      setParsedFilesWithEmbeddings([]);
      toast.error('Failed to load parsed files with embeddings');
    } finally {
      setLoadingParsedFilesWithEmbeddings(false);
    }
  }, [guideSessionToken, selectedParsedFileWithEmbeddings]);

  // Load parsed files with embeddings on mount
  useEffect(() => {
    loadParsedFilesWithEmbeddings();
  }, [loadParsedFilesWithEmbeddings]);

  // Determine current layer for diagram
  const currentLayer = preview ? 'semantic' : (selectedParsedFileId ? 'business' : 'infrastructure');
  
  // Use mash context from API if available, otherwise derive from state
  const mashContextData = mashContext?.mash || {
    source_count: 1, // Single-source mash
    execution_mode: 'virtual',
    lifecycle_state: preview ? 'active' : 'proposed',
    purpose: 'analytics'
  };
  
  // Use correlation IDs from mash context if available
  const correlationId = mashContext?.correlation_id;
  const workflowId = mashContext?.workflow_id || lastCreatedEmbedding?.workflow_id;
  
  // Use IDs from mash context if available, otherwise from state
  const fileId = mashContext?.file_id || lastCreatedEmbedding?.file_id || selectedFile?.uuid;
  const parsedFileId = mashContext?.parsed_file_id || lastCreatedEmbedding?.parsed_file_id || selectedParsedFileId;
  const contentId = mashContext?.content_id || lastCreatedEmbedding?.content_id || selectedContentId;
  
  return (
    <div className="space-y-6">
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="create" className="flex items-center gap-2">
            <Wand2 className="h-4 w-4" />
            Create Mash
          </TabsTrigger>
          <TabsTrigger value="view" className="flex items-center gap-2">
            <Eye className="h-4 w-4" />
            View Mash
          </TabsTrigger>
          <TabsTrigger value="how-it-works" className="flex items-center gap-2">
            <BookOpen className="h-4 w-4" />
            How It Works
          </TabsTrigger>
        </TabsList>
        
        {/* Create Tab - Existing embedding creation flow */}
        <TabsContent value="create" className="space-y-6">
          {/* Parsed File Selection - Step 1: Select parsed file to create embeddings from */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm flex items-center justify-between">
            <span>Step 1: Select Parsed File</span>
            <Button
              variant="ghost"
              size="sm"
              onClick={loadParsedFiles}
              disabled={loadingParsedFiles}
              title="Refresh parsed files list"
            >
              <RefreshCw className={`h-4 w-4 ${loadingParsedFiles ? 'animate-spin' : ''}`} />
            </Button>
          </CardTitle>
          <CardDescription>
            Choose a parsed file to create embeddings from
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {loadingParsedFiles ? (
            <div className="flex items-center justify-center py-4">
              <Loader />
            </div>
          ) : (
            <>
              <Select
                value={selectedParsedFileId || ''}
                onValueChange={(value) => {
                  setSelectedParsedFileId(value);
                  // Clear embeddings when selecting a new parsed file
                  setEmbeddingFiles([]);
                  setSelectedContentId(null);
                  setPreview(null);
                }}
                disabled={loadingParsedFiles || parsedFiles.length === 0}
              >
                <SelectTrigger className="w-full">
                  <SelectValue 
                    placeholder={parsedFiles.length > 0 ? "Choose a parsed file..." : "No parsed files available"} 
                  />
                </SelectTrigger>
                <SelectContent className="max-h-60 overflow-y-auto">
                  {parsedFiles.length > 0 ? (
                    parsedFiles.map((parsedFile) => (
                      <SelectItem 
                        key={parsedFile.parsed_file_id || parsedFile.id} 
                        value={parsedFile.parsed_file_id || parsedFile.id}
                      >
                        {/* ✅ UNIFIED PATTERN: Use ui_name directly from parsed_data_files table (no JOINs needed) */}
                        {parsedFile.ui_name || parsedFile.name || parsedFile.parsed_file_id || parsedFile.id}
                        {parsedFile.created_at && ` (${new Date(parsedFile.created_at).toLocaleDateString()})`}
                      </SelectItem>
                    ))
                  ) : (
                    <SelectItem value="no-files" disabled>No parsed files available</SelectItem>
                  )}
                </SelectContent>
              </Select>
              
              {parsedFiles.length === 0 && (
                <p className="text-sm text-gray-500 text-center py-2">
                  No parsed files available. Parse a file in the File Parsing section first.
                </p>
              )}
            </>
          )}
        </CardContent>
      </Card>

      {/* Create Embeddings Button - Step 2: Generate embeddings from selected parsed file */}
      {selectedParsedFileId && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Step 2: Create Embeddings</CardTitle>
            <CardDescription>
              Generate semantic embeddings from the selected parsed file
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button
              onClick={handleCreateEmbeddings}
              disabled={!selectedParsedFileId || creatingEmbeddings}
              className="w-full"
              size="lg"
            >
              {creatingEmbeddings ? (
                <>
                  <Loader className="mr-2 h-4 w-4 animate-spin" />
                  Creating Embeddings...
                </>
              ) : (
                <>
                  <Wand2 className="mr-2 h-4 w-4" />
                  Create Embeddings
                </>
              )}
            </Button>
            {selectedParsedFileId && (
              <p className="text-xs text-gray-500 mt-2 text-center">
                {/* ✅ UNIFIED PATTERN: Use ui_name directly from parsed_data_files table */}
                Selected: {parsedFiles.find(f => (f.parsed_file_id || f.id) === selectedParsedFileId)?.ui_name || 
                           parsedFiles.find(f => (f.parsed_file_id || f.id) === selectedParsedFileId)?.name || 
                           selectedParsedFileId}
              </p>
            )}
            {createEmbeddingsError && (
              <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="text-sm text-red-800 font-medium">Error creating embeddings</p>
                    <p className="text-xs text-red-600 mt-1 break-words">{createEmbeddingsError}</p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setCreateEmbeddingsError(null)}
                    className="ml-2 h-6 w-6 p-0 text-red-600 hover:text-red-800"
                  >
                    ×
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* View Embeddings by File - Shows only parsed files that have embeddings */}
      {!propSelectedFile && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm flex items-center justify-between">
              <span>View Embeddings by File</span>
              <Button
                variant="ghost"
                size="sm"
                onClick={loadParsedFilesWithEmbeddings}
                disabled={loadingParsedFilesWithEmbeddings}
                title="Refresh parsed files with embeddings"
              >
                <RefreshCw className={`h-4 w-4 ${loadingParsedFilesWithEmbeddings ? 'animate-spin' : ''}`} />
              </Button>
            </CardTitle>
            <CardDescription>
              Select a parsed file that has embeddings to view its semantic layer data
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {loadingParsedFilesWithEmbeddings ? (
              <div className="flex items-center justify-center py-4">
                <Loader />
              </div>
            ) : (
              <>
                <Select
                  value={selectedParsedFileWithEmbeddings || ''}
                  onValueChange={(value) => {
                    setSelectedParsedFileWithEmbeddings(value);
                    const selectedFile = parsedFilesWithEmbeddings.find(
                      f => (f.parsed_file_id || f.id) === value
                    );
                    if (selectedFile) {
                      // Set content_id if available
                      if (selectedFile.content_id) {
                        setSelectedContentId(selectedFile.content_id);
                      } else if (selectedFile.embeddings && selectedFile.embeddings.length > 0) {
                        setSelectedContentId(selectedFile.embeddings[0].content_id);
                      } else {
                        setSelectedContentId(null);
                      }
                      setPreview(null); // Clear preview until Generate Preview is clicked
                    }
                  }}
                  disabled={loadingParsedFilesWithEmbeddings || parsedFilesWithEmbeddings.length === 0}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue 
                      placeholder={parsedFilesWithEmbeddings.length > 0 ? "Choose a parsed file with embeddings..." : "No parsed files with embeddings available"} 
                    />
                  </SelectTrigger>
                  <SelectContent className="max-h-60 overflow-y-auto">
                    {parsedFilesWithEmbeddings.length > 0 ? (
                      parsedFilesWithEmbeddings.map((parsedFile) => (
                        <SelectItem 
                          key={parsedFile.parsed_file_id || parsedFile.id} 
                          value={parsedFile.parsed_file_id || parsedFile.id}
                        >
                          <div className="flex items-center justify-between w-full">
                            {/* ✅ UNIFIED PATTERN: Use ui_name directly from parsed_data_files table (no JOINs needed) */}
                            <span className="font-medium">{parsedFile.ui_name || parsedFile.name || parsedFile.parsed_file_id}</span>
                            <span className="text-xs text-muted-foreground ml-2">
                              {parsedFile.embeddings_count || 0} embedding{(parsedFile.embeddings_count || 0) !== 1 ? 's' : ''}
                            </span>
                          </div>
                        </SelectItem>
                      ))
                    ) : (
                      <SelectItem value="no-files" disabled>No parsed files with embeddings available</SelectItem>
                    )}
                  </SelectContent>
                </Select>
                
                {parsedFilesWithEmbeddings.length === 0 && (
                  <p className="text-sm text-gray-500 text-center py-2">
                    No parsed files with embeddings found. Create embeddings from a parsed file first.
                  </p>
                )}

                {/* Generate Preview Button */}
                {selectedParsedFileWithEmbeddings && (
                  <Button
                    onClick={async () => {
                      const selectedFile = parsedFilesWithEmbeddings.find(
                        f => (f.parsed_file_id || f.id) === selectedParsedFileWithEmbeddings
                      );
                      if (selectedFile?.content_id) {
                        setSelectedContentId(selectedFile.content_id);
                        await loadPreview(selectedFile.content_id);
                      } else {
                        toast.error("No content_id available for this parsed file");
                      }
                    }}
                    disabled={!selectedParsedFileWithEmbeddings || previewLoading}
                    className="w-full"
                    variant="outline"
                  >
                    {previewLoading ? (
                      <>
                        <Loader className="mr-2 h-4 w-4 animate-spin" />
                        Generating Preview...
                      </>
                    ) : (
                      <>
                        <Sparkles className="mr-2 h-4 w-4" />
                        Generate Preview
                      </>
                    )}
                  </Button>
                )}
              </>
            )}
          </CardContent>
        </Card>
      )}

      {/* Embeddings List */}
      {selectedFile && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="h-5 w-5" />
              Semantic Layer Files
            </CardTitle>
            <CardDescription>
              Embeddings and metadata extracted from parsed files
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <Loader />
              </div>
            ) : embeddingFiles.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Brain className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No semantic layer data found for this file.</p>
                <p className="text-sm mt-2">Parse the file first, then create embeddings to view the semantic layer.</p>
              </div>
            ) : (
              <div className="space-y-2">
                {embeddingFiles.map((file) => (
                  <div
                    key={file.content_id}
                    className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                      selectedContentId === file.content_id
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setSelectedContentId(file.content_id)}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-medium">Content ID: {file.content_id.slice(0, 8)}...</div>
                        <div className="text-sm text-gray-500">
                          {file.embeddings_count} embeddings • {file.columns.length} columns
                        </div>
                      </div>
                      {file.created_at && (
                        <Badge variant="outline">
                          {new Date(file.created_at).toLocaleDateString()}
                        </Badge>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Preview */}
      {selectedContentId && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Layers className="h-5 w-5" />
              Semantic Layer Preview
            </CardTitle>
            <CardDescription>
              Preview reconstructed from embeddings + metadata (not raw parsed data)
            </CardDescription>
          </CardHeader>
          <CardContent>
            {previewLoading ? (
              <div className="flex items-center justify-center py-8">
                <Loader />
              </div>
            ) : preview ? (
              <div className="space-y-6">
                {/* Structure Summary */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <div className="text-sm text-gray-500">Columns</div>
                    <div className="text-2xl font-bold">{preview.structure.column_count}</div>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <div className="text-sm text-gray-500">Rows</div>
                    <div className="text-2xl font-bold">{preview.structure.row_count?.toLocaleString() || 0}</div>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <div className="text-sm text-gray-500">Tables</div>
                    <div className="text-2xl font-bold">{preview.structure.table_count ?? 0}</div>
                  </div>
                </div>

                {/* Columns */}
                {preview.columns && preview.columns.length > 0 && (
                  <div className="space-y-4">
                    <h3 className="font-semibold">Columns & Semantic Meanings</h3>
                    {preview.columns.map((column, index) => (
                      <div key={index} className="p-4 border rounded-lg">
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <div className="font-medium">{column.column_name}</div>
                            <div className="text-sm text-gray-500">{column.data_type}</div>
                          </div>
                          {column.semantic_id && (
                            <Badge variant="outline">{column.semantic_id}</Badge>
                          )}
                        </div>
                        {column.semantic_meaning && (
                          <div className="mt-2 text-sm text-gray-700">
                            <strong>Semantic Meaning:</strong> {column.semantic_meaning}
                          </div>
                        )}
                        {column.sample_values && column.sample_values.length > 0 && (
                          <div className="mt-2">
                            <div className="text-sm text-gray-500 mb-1">Sample Values:</div>
                            <div className="flex flex-wrap gap-2">
                              {column.sample_values.slice(0, 5).map((value, i) => (
                                <Badge key={i} variant="secondary" className="text-xs">
                                  {String(value)}
                                </Badge>
                              ))}
                              {column.sample_values.length > 5 && (
                                <Badge variant="secondary" className="text-xs">
                                  +{column.sample_values.length - 5} more
                                </Badge>
                              )}
                            </div>
                          </div>
                        )}
                        {column.semantic_model_recommendation && (
                          <div className="mt-2 text-sm">
                            <strong>Confidence:</strong>{' '}
                            <span className={column.semantic_model_recommendation.confidence >= 0.7 ? 'text-green-600' : 'text-yellow-600'}>
                              {((column.semantic_model_recommendation.confidence || 0) * 100).toFixed(1)}%
                            </span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {/* Semantic Insights Summary */}
                {preview.structure.semantic_insights_summary && preview.structure.semantic_insights_summary.length > 0 && (
                  <div className="space-y-4">
                    <h3 className="font-semibold">Semantic Insights</h3>
                    <div className="space-y-2">
                      {preview.structure.semantic_insights_summary.map((insight, index) => (
                        <div key={index} className="p-3 bg-blue-50 rounded-lg text-sm">
                          {insight}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <p>No preview available</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

        </TabsContent>
        
        {/* View Tab - Enhanced preview with mash context */}
        <TabsContent value="view" className="space-y-6">
          {/* Mash Context Banner */}
          {loadingMashContext ? (
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-center py-4">
                  <Loader />
                </div>
              </CardContent>
            </Card>
          ) : (
            <>
              <MashContextBanner
                mash={mashContextData}
                file_id={fileId}
                parsed_file_id={parsedFileId}
                content_id={contentId}
              />
              
              {/* Correlation Chain */}
              <CorrelationChain
                file_id={fileId}
                parsed_file_id={parsedFileId}
                content_id={contentId}
                correlation_id={correlationId}
                workflow_id={workflowId}
              />
            </>
          )}
          
          {/* View Embeddings by File - Shows only parsed files that have embeddings */}
          {!propSelectedFile && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm flex items-center justify-between">
                  <span>View Embeddings by File</span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={loadParsedFilesWithEmbeddings}
                    disabled={loadingParsedFilesWithEmbeddings}
                    title="Refresh parsed files with embeddings"
                  >
                    <RefreshCw className={`h-4 w-4 ${loadingParsedFilesWithEmbeddings ? 'animate-spin' : ''}`} />
                  </Button>
                </CardTitle>
                <CardDescription>
                  Select a parsed file that has embeddings to view its semantic layer data
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {loadingParsedFilesWithEmbeddings ? (
                  <div className="flex items-center justify-center py-4">
                    <Loader />
                  </div>
                ) : (
                  <>
                    <Select
                      value={selectedParsedFileWithEmbeddings || ''}
                      onValueChange={(value) => {
                        setSelectedParsedFileWithEmbeddings(value);
                        const selectedFile = parsedFilesWithEmbeddings.find(
                          f => (f.parsed_file_id || f.id) === value
                        );
                        if (selectedFile) {
                          // Set content_id if available
                          if (selectedFile.content_id) {
                            setSelectedContentId(selectedFile.content_id);
                          } else if (selectedFile.embeddings && selectedFile.embeddings.length > 0) {
                            setSelectedContentId(selectedFile.embeddings[0].content_id);
                          } else {
                            setSelectedContentId(null);
                          }
                          setPreview(null); // Clear preview until Generate Preview is clicked
                        }
                      }}
                      disabled={loadingParsedFilesWithEmbeddings || parsedFilesWithEmbeddings.length === 0}
                    >
                      <SelectTrigger className="w-full">
                        <SelectValue 
                          placeholder={parsedFilesWithEmbeddings.length > 0 ? "Choose a parsed file with embeddings..." : "No parsed files with embeddings available"} 
                        />
                      </SelectTrigger>
                      <SelectContent className="max-h-60 overflow-y-auto">
                        {parsedFilesWithEmbeddings.length > 0 ? (
                          parsedFilesWithEmbeddings.map((parsedFile) => (
                            <SelectItem 
                              key={parsedFile.parsed_file_id || parsedFile.id} 
                              value={parsedFile.parsed_file_id || parsedFile.id}
                            >
                              <div className="flex items-center justify-between w-full">
                                <span className="font-medium">{parsedFile.ui_name || parsedFile.name || parsedFile.parsed_file_id}</span>
                                <span className="text-xs text-muted-foreground ml-2">
                                  {parsedFile.embeddings_count || 0} embedding{(parsedFile.embeddings_count || 0) !== 1 ? 's' : ''}
                                </span>
                              </div>
                            </SelectItem>
                          ))
                        ) : (
                          <SelectItem value="no-files" disabled>No parsed files with embeddings available</SelectItem>
                        )}
                      </SelectContent>
                    </Select>
                    
                    {parsedFilesWithEmbeddings.length === 0 && (
                      <p className="text-sm text-gray-500 text-center py-2">
                        No parsed files with embeddings found. Create embeddings from a parsed file first.
                      </p>
                    )}

                    {/* Generate Preview Button */}
                    {selectedParsedFileWithEmbeddings && (
                      <Button
                        onClick={async () => {
                          const selectedFile = parsedFilesWithEmbeddings.find(
                            f => (f.parsed_file_id || f.id) === selectedParsedFileWithEmbeddings
                          );
                          if (selectedFile?.content_id) {
                            setSelectedContentId(selectedFile.content_id);
                            await loadPreview(selectedFile.content_id);
                          } else {
                            toast.error("No content_id available for this parsed file");
                          }
                        }}
                        disabled={!selectedParsedFileWithEmbeddings || previewLoading}
                        className="w-full"
                        variant="outline"
                      >
                        {previewLoading ? (
                          <>
                            <Loader className="mr-2 h-4 w-4 animate-spin" />
                            Generating Preview...
                          </>
                        ) : (
                          <>
                            <Sparkles className="mr-2 h-4 w-4" />
                            Generate Preview
                          </>
                        )}
                      </Button>
                    )}
                  </>
                )}
              </CardContent>
            </Card>
          )}

          {/* Embeddings List */}
          {selectedFile && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Database className="h-5 w-5" />
                  Semantic Layer Files
                </CardTitle>
                <CardDescription>
                  Embeddings and metadata extracted from parsed files
                </CardDescription>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="flex items-center justify-center py-8">
                    <Loader />
                  </div>
                ) : embeddingFiles.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <Brain className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No semantic layer data found for this file.</p>
                    <p className="text-sm mt-2">Parse the file first, then create embeddings to view the semantic layer.</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {embeddingFiles.map((file) => (
                      <div
                        key={file.content_id}
                        className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                          selectedContentId === file.content_id
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                        onClick={() => setSelectedContentId(file.content_id)}
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="font-medium">Content ID: {file.content_id.slice(0, 8)}...</div>
                            <div className="text-sm text-gray-500">
                              {file.embeddings_count} embeddings • {file.columns.length} columns
                            </div>
                          </div>
                          {file.created_at && (
                            <Badge variant="outline">
                              {new Date(file.created_at).toLocaleDateString()}
                            </Badge>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Enhanced Preview with Mash Context */}
          {selectedContentId && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Layers className="h-5 w-5" />
                  Semantic Layer Preview
                </CardTitle>
                <CardDescription>
                  Preview reconstructed from embeddings + metadata (not raw parsed data)
                </CardDescription>
              </CardHeader>
              <CardContent>
                {previewLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <Loader />
                  </div>
                ) : preview ? (
                  <div className="space-y-6">
                    {/* Structure Summary */}
                    <div className="grid grid-cols-3 gap-4">
                      <div className="p-4 bg-gray-50 rounded-lg">
                        <div className="text-sm text-gray-500">Columns</div>
                        <div className="text-2xl font-bold">{preview.structure.column_count}</div>
                      </div>
                      <div className="p-4 bg-gray-50 rounded-lg">
                        <div className="text-sm text-gray-500">Rows</div>
                        <div className="text-2xl font-bold">{preview.structure.row_count?.toLocaleString() || 0}</div>
                      </div>
                      <div className="p-4 bg-gray-50 rounded-lg">
                        <div className="text-sm text-gray-500">Tables</div>
                        <div className="text-2xl font-bold">{preview.structure.table_count ?? 0}</div>
                      </div>
                    </div>

                    {/* Columns */}
                    {preview.columns && preview.columns.length > 0 && (
                      <div className="space-y-4">
                        <h3 className="font-semibold">Columns & Semantic Meanings</h3>
                        {preview.columns.map((column, index) => (
                          <div key={index} className="p-4 border rounded-lg">
                            <div className="flex items-start justify-between mb-2">
                              <div>
                                <div className="font-medium">{column.column_name}</div>
                                <div className="text-sm text-gray-500">{column.data_type}</div>
                              </div>
                              {column.semantic_id && (
                                <Badge variant="outline">{column.semantic_id}</Badge>
                              )}
                            </div>
                            {column.semantic_meaning && (
                              <div className="mt-2 text-sm text-gray-700">
                                <strong>Semantic Meaning:</strong> {column.semantic_meaning}
                              </div>
                            )}
                            {column.sample_values && column.sample_values.length > 0 && (
                              <div className="mt-2">
                                <div className="text-sm text-gray-500 mb-1">Sample Values:</div>
                                <div className="flex flex-wrap gap-2">
                                  {column.sample_values.slice(0, 5).map((value, i) => (
                                    <Badge key={i} variant="secondary" className="text-xs">
                                      {String(value)}
                                    </Badge>
                                  ))}
                                  {column.sample_values.length > 5 && (
                                    <Badge variant="secondary" className="text-xs">
                                      +{column.sample_values.length - 5} more
                                    </Badge>
                                  )}
                                </div>
                              </div>
                            )}
                            {column.semantic_model_recommendation && (
                              <div className="mt-2 text-sm">
                                <strong>Confidence:</strong>{' '}
                                <span className={column.semantic_model_recommendation.confidence >= 0.7 ? 'text-green-600' : 'text-yellow-600'}>
                                  {((column.semantic_model_recommendation.confidence || 0) * 100).toFixed(1)}%
                                </span>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Semantic Insights Summary */}
                    {preview.structure.semantic_insights_summary && preview.structure.semantic_insights_summary.length > 0 && (
                      <div className="space-y-4">
                        <h3 className="font-semibold">Semantic Insights</h3>
                        <div className="space-y-2">
                          {preview.structure.semantic_insights_summary.map((insight, index) => (
                            <div key={index} className="p-3 bg-blue-50 rounded-lg text-sm">
                              {insight}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <p>No preview available</p>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </TabsContent>
        
        {/* How It Works Tab - Process visualization */}
        <TabsContent value="how-it-works" className="space-y-6">
          <ThreeLayerPatternDiagram
            currentLayer={currentLayer}
            fileData={{
              file_id: fileId,
              parsed_file_id: parsedFileId,
              content_id: contentId
            }}
          />
          
          {/* Info Card */}
          <Card className="bg-blue-50 border-blue-200">
            <CardHeader>
              <CardTitle className="text-sm">About Data Mash</CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-gray-700">
              <p className="mb-2">
                <strong>Data Mash</strong> is an AI-assisted, virtual data composition layer that dynamically stitches together data from different sources without physically moving it.
              </p>
              <p className="mb-2">
                The <strong>3-Layer Pattern</strong>:
              </p>
              <ul className="list-disc list-inside space-y-1 ml-4">
                <li><strong>Layer 1 (Infrastructure):</strong> File parsing → stores parsed files</li>
                <li><strong>Layer 2 (Business Enablement):</strong> Embedding creation → extracts metadata FROM parsed files, creates embeddings</li>
                <li><strong>Layer 3 (Semantic Layer):</strong> Embeddings storage → stores embeddings + metadata in ArangoDB</li>
              </ul>
              <p className="mt-2">
                This preview is reconstructed from embeddings + metadata (not raw parsed data), demonstrating the power of the semantic layer.
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

