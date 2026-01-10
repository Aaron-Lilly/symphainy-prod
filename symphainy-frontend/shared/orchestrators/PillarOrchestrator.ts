/**
 * Pillar Orchestrator Base Class
 * 
 * Provides pillar-level orchestration that works WITH the beautiful service layer.
 * Each pillar gets its own orchestrator that manages pillar-specific operations
 * while leveraging the centralized service layer for common functionality.
 */

// ============================================
// Base Pillar Orchestrator
// ============================================

export abstract class PillarOrchestrator {
  protected sessionToken: string;
  protected pillarName: string;

  constructor(sessionToken: string, pillarName: string) {
    this.sessionToken = sessionToken;
    this.pillarName = pillarName;
  }

  // Abstract methods that each pillar must implement
  abstract initialize(): Promise<void>;
  abstract getPillarData(): Promise<any>;
  abstract processPillarOperation(operation: string, data: any): Promise<any>;
  abstract cleanup(): Promise<void>;

  // Common orchestration methods
  protected async logPillarActivity(activity: string, data?: any) {
    console.log(`[${this.pillarName}] ${activity}`, data);
  }

  protected async handlePillarError(error: any, operation: string) {
    console.error(`[${this.pillarName}] Error in ${operation}:`, error);
    throw new Error(`${this.pillarName} ${operation} failed: ${error.message}`);
  }
}

// ============================================
// Content Pillar Orchestrator
// ============================================

export class ContentPillarOrchestrator extends PillarOrchestrator {
  private contentService: any;

  constructor(sessionToken: string) {
    super(sessionToken, 'Content');
  }

  async initialize(): Promise<void> {
    await this.logPillarActivity('Initializing Content Pillar');
    // Initialize content-specific services
    const { ContentService } = await import('@/shared/services/content');
    this.contentService = new ContentService(this.sessionToken);
  }

  async getPillarData(): Promise<any> {
    await this.logPillarActivity('Getting Content Pillar Data');
    try {
      const files = await this.contentService.listContentFiles(this.sessionToken);
      return { files, pillar: 'content' };
    } catch (error) {
      await this.handlePillarError(error, 'getPillarData');
    }
  }

  async processPillarOperation(operation: string, data: any): Promise<any> {
    await this.logPillarActivity(`Processing Content Operation: ${operation}`, data);
    
    switch (operation) {
      case 'uploadFile':
        return await this.contentService.uploadFile(data);
      case 'processFile':
        return await this.contentService.processFile(data.fileId);
      case 'getFileMetadata':
        return await this.contentService.getFileMetadata(data.fileId);
      default:
        throw new Error(`Unknown Content operation: ${operation}`);
    }
  }

  async cleanup(): Promise<void> {
    await this.logPillarActivity('Cleaning up Content Pillar');
    // Cleanup content-specific resources
  }
}

// ============================================
// Insights Pillar Orchestrator
// ============================================

export class InsightsPillarOrchestrator extends PillarOrchestrator {
  private insightsService: any;

  constructor(sessionToken: string) {
    super(sessionToken, 'Insights');
  }

  async initialize(): Promise<void> {
    await this.logPillarActivity('Initializing Insights Pillar');
    const { InsightsService } = await import('@/shared/services/insights');
    this.insightsService = new InsightsService(this.sessionToken);
  }

  async getPillarData(): Promise<any> {
    await this.logPillarActivity('Getting Insights Pillar Data');
    try {
      const insights = await this.insightsService.getBusinessAnalysis(
        '', // fileUrl
        'session_123', // sessionId
        JSON.stringify({ include_recommendations: true }),
        this.sessionToken
      );
      return { insights, pillar: 'insights' };
    } catch (error) {
      await this.handlePillarError(error, 'getPillarData');
    }
  }

  async processPillarOperation(operation: string, data: any): Promise<any> {
    await this.logPillarActivity(`Processing Insights Operation: ${operation}`, data);
    
    switch (operation) {
      case 'generateInsights':
        return await this.insightsService.getBusinessAnalysis(
          data.fileUrl,
          data.sessionId,
          JSON.stringify(data.options),
          this.sessionToken
        );
      case 'getVARKAnalysis':
        return await this.insightsService.getVARKAnalysis(data);
      default:
        throw new Error(`Unknown Insights operation: ${operation}`);
    }
  }

  async cleanup(): Promise<void> {
    await this.logPillarActivity('Cleaning up Insights Pillar');
  }
}

// ============================================
// Operations Pillar Orchestrator
// ============================================

export class OperationsPillarOrchestrator extends PillarOrchestrator {
  private operationsSolutionService: any;
  private authToken: string | null = null;

  constructor(sessionToken: string) {
    super(sessionToken, 'Operations');
    // Get auth token from localStorage if available
    if (typeof window !== 'undefined') {
      this.authToken = localStorage.getItem('auth_token') || null;
    }
  }

  async initialize(): Promise<void> {
    await this.logPillarActivity('Initializing Operations Pillar');
    const { OperationsSolutionService } = await import('@/shared/services/operations/solution-service');
    // Create service instance with auth token
    this.operationsSolutionService = new OperationsSolutionService(this.authToken || undefined);
  }

  async getPillarData(): Promise<any> {
    await this.logPillarActivity('Getting Operations Pillar Data');
    try {
      // Query data mash for workflow/SOP files
      const { listParsedFilesWithEmbeddings } = await import('@/lib/api/content');
      const parsedFilesResponse = await listParsedFilesWithEmbeddings(this.authToken || undefined);
      
      // Filter for workflow/SOP files based on parsing_type or content_type
      const operationFiles = (parsedFilesResponse.parsed_files || []).filter((file: any) => {
        const parsingType = file.parsing_type || file.content_type || '';
        const formatType = file.format_type || '';
        // Check if file is marked as workflow or sop, or has workflow/SOP format
        return parsingType === 'workflow' || 
               parsingType === 'sop' || 
               formatType?.toLowerCase().includes('workflow') ||
               formatType?.toLowerCase().includes('sop') ||
               file.name?.toLowerCase().match(/\.(bpmn|drawio|xml|json)$/i) || // Workflow formats
               file.name?.toLowerCase().match(/\.(docx|pdf|txt|md)$/i); // SOP formats
      });
      
      // Convert to elements format expected by frontend
      const elements: Record<string, any> = {};
      operationFiles.forEach((file: any) => {
        elements[file.file_id || file.id] = {
          uuid: file.file_id || file.id,
          ui_name: file.name,
          file_type: file.format_type || 'document',
          parsing_type: file.parsing_type || file.content_type,
          ...file
        };
      });
      
      return { elements, pillar: 'operations' };
    } catch (error) {
      await this.logPillarActivity('Error getting operations files, returning empty', error);
      // Return empty elements on error to allow page to load
      return { elements: {}, pillar: 'operations' };
    }
  }

  async processPillarOperation(operation: string, data: any): Promise<any> {
    await this.logPillarActivity(`Processing Operations Operation: ${operation}`, data);
    
    // Get user ID from localStorage if available
    const userData = typeof window !== 'undefined' ? localStorage.getItem('user_data') : null;
    const userId = userData ? JSON.parse(userData)?.id : undefined;
    
    switch (operation) {
      case 'analyzeCoexistence':
        return await this.operationsSolutionService.analyzeCoexistence({
          sessionToken: this.sessionToken,
          sopFileUuid: data.sopFileUuid,
          workflowFileUuid: data.workflowFileUuid,
          sopContent: data.sopContent,
          workflowContent: data.workflowContent,
          currentState: data.currentState,
          targetState: data.targetState,
          analysisOptions: data.analysisOptions,
          userId: userId,
          sessionId: this.sessionToken
        });
      case 'generateWorkflow':
        return await this.operationsSolutionService.generateWorkflowFromSop({
          sopFileUuid: data.sopFileUuid,
          sessionToken: this.sessionToken,
          sopContent: data.sopContent,
          workflowOptions: data.workflowOptions,
          userId: userId,
          sessionId: this.sessionToken
        });
      case 'generateSOP':
        return await this.operationsSolutionService.generateSopFromWorkflow({
          workflowFileUuid: data.workflowFileUuid,
          sessionToken: this.sessionToken,
          workflowContent: data.workflowContent,
          sopOptions: data.sopOptions,
          userId: userId,
          sessionId: this.sessionToken
        });
      default:
        throw new Error(`Unknown Operations operation: ${operation}`);
    }
  }

  async cleanup(): Promise<void> {
    await this.logPillarActivity('Cleaning up Operations Pillar');
  }
}

// ============================================
// Experience Pillar Orchestrator
// ============================================

export class ExperiencePillarOrchestrator extends PillarOrchestrator {
  private experienceService: any;

  constructor(sessionToken: string) {
    super(sessionToken, 'Experience');
  }

  async initialize(): Promise<void> {
    await this.logPillarActivity('Initializing Experience Pillar');
    const { ExperienceService } = await import('@/shared/services/experience');
    // ExperienceService is a static class, no constructor needed
  }

  async getPillarData(): Promise<any> {
    await this.logPillarActivity('Getting Experience Pillar Data');
    try {
      const session = await this.experienceService.createExperienceSession(this.sessionToken);
      return { session, pillar: 'experience' };
    } catch (error) {
      await this.handlePillarError(error, 'getPillarData');
    }
  }

  async processPillarOperation(operation: string, data: any): Promise<any> {
    await this.logPillarActivity(`Processing Experience Operation: ${operation}`, data);
    
    switch (operation) {
      case 'createSession':
        return await this.experienceService.createExperienceSession(data.sessionToken);
      case 'getCrossPillarData':
        return await this.experienceService.getCrossPillarData(data);
      case 'generateOutputs':
        return await this.experienceService.generateExperienceOutputs(data);
      default:
        throw new Error(`Unknown Experience operation: ${operation}`);
    }
  }

  async cleanup(): Promise<void> {
    await this.logPillarActivity('Cleaning up Experience Pillar');
  }
}

// ============================================
// Pillar Orchestrator Factory
// ============================================

export class PillarOrchestratorFactory {
  static createOrchestrator(pillarName: string, sessionToken: string): PillarOrchestrator {
    switch (pillarName.toLowerCase()) {
      case 'content':
        return new ContentPillarOrchestrator(sessionToken);
      case 'insights':
        return new InsightsPillarOrchestrator(sessionToken);
      case 'operations':
        return new OperationsPillarOrchestrator(sessionToken);
      case 'experience':
      case 'business-outcomes':
        return new ExperiencePillarOrchestrator(sessionToken);
      default:
        throw new Error(`Unknown pillar: ${pillarName}`);
    }
  }
}
