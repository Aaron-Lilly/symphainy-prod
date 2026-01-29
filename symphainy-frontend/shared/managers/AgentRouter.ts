/**
 * Agent Router
 * 
 * Routes WebSocket messages to appropriate agents and manages
 * agent-specific operations and state.
 */

// WebSocketManager will be dynamically imported to avoid SSR issues

// ============================================
// WebSocket Manager Interface
// ============================================

/**
 * WebSocket Manager interface for agent communication
 */
export interface IWebSocketManager {
  connect(sessionToken?: string): Promise<void>;
  disconnect(): void;
  sendMessage(message: string): void;
  isConnected(): boolean;
  onConnectionChange(callback: (connected: boolean) => void): () => void;
  sendToGuideAgent?(message: string, pillar?: string, context?: Record<string, unknown>): Promise<AgentResponse>;
  sendToContentAgent?(message: string, context?: Record<string, unknown>): Promise<AgentResponse>;
  sendToInsightsAgent?(message: string, context?: Record<string, unknown>): Promise<AgentResponse>;
  sendToOperationsAgent?(message: string, context?: Record<string, unknown>): Promise<AgentResponse>;
  sendToExperienceAgent?(message: string, context?: Record<string, unknown>): Promise<AgentResponse>;
}

// ============================================
// Agent Router Types
// ============================================

/**
 * File context information for agent interactions
 */
export interface FileContext {
  fileId?: string;
  fileName?: string;
  fileType?: string;
  fileSize?: number;
  parseStatus?: string;
}

/**
 * User context information for agent interactions
 */
export interface UserContext {
  userId?: string;
  preferences?: Record<string, unknown>;
  history?: string[];
}

/**
 * Agent context containing session and contextual information
 */
export interface AgentContext {
  sessionToken: string;
  currentPillar?: string;
  fileContext?: FileContext;
  userContext?: UserContext;
}

/**
 * Agent response structure
 */
export interface AgentResponse {
  type: string;
  content: string;
  metadata?: Record<string, unknown>;
  artifacts?: string[];
  suggested_actions?: string[];
}

/**
 * Operation data for different agent operations
 */
export interface OperationData {
  query?: string;
  topic?: string;
  pillar?: string;
  fileName?: string;
  fileId?: string;
  contentType?: string;
  dataType?: string;
  chartType?: string;
  process?: string;
  workflowType?: string;
  processId?: string;
  goal?: string;
  timeline?: string;
  metrics?: string;
}

/**
 * Agent operation request
 */
export interface AgentOperation {
  type: string;
  data: OperationData;
  context: AgentContext;
}

// ============================================
// Base Agent Manager
// ============================================

/**
 * Additional context for message processing
 */
export interface AdditionalMessageContext {
  conversationId?: string;
  priority?: 'low' | 'medium' | 'high';
  includeHistory?: boolean;
  customData?: Record<string, unknown>;
}

export abstract class BaseAgentManager {
  protected webSocketManager: IWebSocketManager;
  protected agentType: string;
  protected context: AgentContext;

  constructor(webSocketManager: IWebSocketManager, agentType: string, context: AgentContext) {
    this.webSocketManager = webSocketManager;
    this.agentType = agentType;
    this.context = context;
  }

  abstract processMessage(message: string, additionalContext?: AdditionalMessageContext): Promise<AgentResponse>;
  abstract processOperation(operation: AgentOperation): Promise<AgentResponse>;
}

// ============================================
// Guide Agent Manager
// ============================================

export class GuideAgentManager extends BaseAgentManager {
  constructor(webSocketManager: IWebSocketManager, context: AgentContext) {
    super(webSocketManager, 'guide', context);
  }

  async processMessage(message: string, additionalContext?: AdditionalMessageContext): Promise<AgentResponse> {
    if (!this.webSocketManager.sendToGuideAgent) {
      throw new Error('WebSocket manager does not support Guide Agent');
    }
    return this.webSocketManager.sendToGuideAgent(
      message,
      this.context.currentPillar,
      { ...this.context.fileContext, ...additionalContext }
    );
  }

  async processOperation(operation: AgentOperation): Promise<AgentResponse> {
    switch (operation.type) {
      case 'analyze_intent':
        return this.processMessage(`Analyze intent: ${operation.data.query}`);
      case 'route_to_pillar':
        return this.processMessage(`Route to ${operation.data.pillar} pillar`);
      case 'provide_guidance':
        return this.processMessage(`Provide guidance for: ${operation.data.topic}`);
      default:
        throw new Error(`Unknown Guide Agent operation: ${operation.type}`);
    }
  }
}

// ============================================
// Content Agent Manager
// ============================================

export class ContentAgentManager extends BaseAgentManager {
  constructor(webSocketManager: IWebSocketManager, context: AgentContext) {
    super(webSocketManager, 'content', context);
  }

  async processMessage(message: string, additionalContext?: AdditionalMessageContext): Promise<AgentResponse> {
    if (!this.webSocketManager.sendToContentAgent) {
      throw new Error('WebSocket manager does not support Content Agent');
    }
    return this.webSocketManager.sendToContentAgent(
      message,
      { ...this.context.fileContext, ...additionalContext }
    );
  }

  async processOperation(operation: AgentOperation): Promise<AgentResponse> {
    switch (operation.type) {
      case 'upload_file':
        return this.processMessage(`Help with file upload: ${operation.data.fileName}`);
      case 'process_content':
        return this.processMessage(`Process content: ${operation.data.contentType}`);
      case 'extract_metadata':
        return this.processMessage(`Extract metadata from: ${operation.data.fileId}`);
      default:
        throw new Error(`Unknown Content Agent operation: ${operation.type}`);
    }
  }
}

// ============================================
// Insights Agent Manager
// ============================================

export class InsightsAgentManager extends BaseAgentManager {
  constructor(webSocketManager: IWebSocketManager, context: AgentContext) {
    super(webSocketManager, 'insights', context);
  }

  async processMessage(message: string, additionalContext?: AdditionalMessageContext): Promise<AgentResponse> {
    if (!this.webSocketManager.sendToInsightsAgent) {
      throw new Error('WebSocket manager does not support Insights Agent');
    }
    return this.webSocketManager.sendToInsightsAgent(
      message,
      { ...this.context.fileContext, ...additionalContext }
    );
  }

  async processOperation(operation: AgentOperation): Promise<AgentResponse> {
    switch (operation.type) {
      case 'analyze_data':
        return this.processMessage(`Analyze data: ${operation.data.dataType}`);
      case 'generate_insights':
        return this.processMessage(`Generate insights for: ${operation.data.topic}`);
      case 'create_visualization':
        return this.processMessage(`Create visualization: ${operation.data.chartType}`);
      default:
        throw new Error(`Unknown Insights Agent operation: ${operation.type}`);
    }
  }
}

// ============================================
// Operations Agent Manager
// ============================================

export class OperationsAgentManager extends BaseAgentManager {
  constructor(webSocketManager: IWebSocketManager, context: AgentContext) {
    super(webSocketManager, 'operations', context);
  }

  async processMessage(message: string, additionalContext?: AdditionalMessageContext): Promise<AgentResponse> {
    if (!this.webSocketManager.sendToOperationsAgent) {
      throw new Error('WebSocket manager does not support Operations Agent');
    }
    return this.webSocketManager.sendToOperationsAgent(
      message,
      { ...this.context.fileContext, ...additionalContext }
    );
  }

  async processOperation(operation: AgentOperation): Promise<AgentResponse> {
    switch (operation.type) {
      case 'generate_sop':
        return this.processMessage(`Generate SOP for: ${operation.data.process}`);
      case 'create_workflow':
        return this.processMessage(`Create workflow: ${operation.data.workflowType}`);
      case 'optimize_process':
        return this.processMessage(`Optimize process: ${operation.data.processId}`);
      default:
        throw new Error(`Unknown Operations Agent operation: ${operation.type}`);
    }
  }
}

// ============================================
// Experience Agent Manager
// ============================================

export class ExperienceAgentManager extends BaseAgentManager {
  constructor(webSocketManager: IWebSocketManager, context: AgentContext) {
    super(webSocketManager, 'business-outcomes', context);
  }

  async processMessage(message: string, additionalContext?: AdditionalMessageContext): Promise<AgentResponse> {
    if (!this.webSocketManager.sendToExperienceAgent) {
      throw new Error('WebSocket manager does not support Experience Agent');
    }
    return this.webSocketManager.sendToExperienceAgent(
      message,
      { ...this.context.fileContext, ...additionalContext }
    );
  }

  async processOperation(operation: AgentOperation): Promise<AgentResponse> {
    switch (operation.type) {
      case 'strategic_planning':
        return this.processMessage(`Strategic planning for: ${operation.data.goal}`);
      case 'generate_roadmap':
        return this.processMessage(`Generate roadmap: ${operation.data.timeline}`);
      case 'measure_outcomes':
        return this.processMessage(`Measure outcomes: ${operation.data.metrics}`);
      default:
        throw new Error(`Unknown Experience Agent operation: ${operation.type}`);
    }
  }
}

// ============================================
// Agent Router
// ============================================

export type AgentType = 'guide' | 'content' | 'insights' | 'operations' | 'experience';

export class AgentRouter {
  private webSocketManager: IWebSocketManager;
  private context: AgentContext;
  private agents: Map<AgentType, BaseAgentManager> = new Map();

  constructor(webSocketManager: IWebSocketManager, context: AgentContext) {
    this.webSocketManager = webSocketManager;
    this.context = context;
    this.initializeAgents();
  }

  private initializeAgents(): void {
    this.agents.set('guide', new GuideAgentManager(this.webSocketManager, this.context));
    this.agents.set('content', new ContentAgentManager(this.webSocketManager, this.context));
    this.agents.set('insights', new InsightsAgentManager(this.webSocketManager, this.context));
    this.agents.set('operations', new OperationsAgentManager(this.webSocketManager, this.context));
    this.agents.set('experience', new ExperienceAgentManager(this.webSocketManager, this.context));
  }

  getAgent(agentType: AgentType): BaseAgentManager {
    const agent = this.agents.get(agentType);
    if (!agent) {
      throw new Error(`Unknown agent type: ${agentType}`);
    }
    return agent;
  }

  async routeMessage(agentType: AgentType, message: string, additionalContext?: AdditionalMessageContext): Promise<AgentResponse> {
    const agent = this.getAgent(agentType);
    return agent.processMessage(message, additionalContext);
  }

  async routeOperation(agentType: AgentType, operation: AgentOperation): Promise<AgentResponse> {
    const agent = this.getAgent(agentType);
    return agent.processOperation(operation);
  }

  updateContext(newContext: Partial<AgentContext>): void {
    this.context = { ...this.context, ...newContext };
    // Reinitialize agents with new context
    this.initializeAgents();
  }

  isConnected(): boolean {
    return this.webSocketManager.isConnected();
  }

  onConnectionChange(handler: (connected: boolean) => void): () => void {
    return this.webSocketManager.onConnectionChange(handler);
  }
}

// ============================================
// Agent Router Factory
// ============================================

export class AgentRouterFactory {
  static async createRouter(sessionToken: string, currentPillar?: string, fileContext?: FileContext): Promise<AgentRouter> {
    // WebSocketManager will be dynamically imported
    const { WebSocketManager } = await import('./WebSocketManager');
    const webSocketManager = new WebSocketManager() as IWebSocketManager;
    const context: AgentContext = {
      sessionToken,
      currentPillar,
      fileContext
    };
    return new AgentRouter(webSocketManager, context);
  }
}
