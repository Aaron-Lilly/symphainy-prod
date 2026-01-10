/**
 * Agent Router
 * 
 * Routes WebSocket messages to appropriate agents and manages
 * agent-specific operations and state.
 */

// WebSocketManager will be dynamically imported to avoid SSR issues

// ============================================
// Agent Router Types
// ============================================

export interface AgentContext {
  sessionToken: string;
  currentPillar?: string;
  fileContext?: any;
  userContext?: any;
}

export interface AgentOperation {
  type: string;
  data: any;
  context: AgentContext;
}

// ============================================
// Base Agent Manager
// ============================================

export abstract class BaseAgentManager {
  protected webSocketManager: any;
  protected agentType: string;
  protected context: AgentContext;

  constructor(webSocketManager: any, agentType: string, context: AgentContext) {
    this.webSocketManager = webSocketManager;
    this.agentType = agentType;
    this.context = context;
  }

  abstract processMessage(message: string, additionalContext?: any): Promise<any>;
  abstract processOperation(operation: AgentOperation): Promise<any>;
}

// ============================================
// Guide Agent Manager
// ============================================

export class GuideAgentManager extends BaseAgentManager {
  constructor(webSocketManager: any, context: AgentContext) {
    super(webSocketManager, 'guide', context);
  }

  async processMessage(message: string, additionalContext?: any): Promise<any> {
    return this.webSocketManager.sendToGuideAgent(
      message,
      this.context.currentPillar,
      { ...this.context.fileContext, ...additionalContext }
    );
  }

  async processOperation(operation: AgentOperation): Promise<any> {
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
  constructor(webSocketManager: any, context: AgentContext) {
    super(webSocketManager, 'content', context);
  }

  async processMessage(message: string, additionalContext?: any): Promise<any> {
    return this.webSocketManager.sendToContentAgent(
      message,
      { ...this.context.fileContext, ...additionalContext }
    );
  }

  async processOperation(operation: AgentOperation): Promise<any> {
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
  constructor(webSocketManager: any, context: AgentContext) {
    super(webSocketManager, 'insights', context);
  }

  async processMessage(message: string, additionalContext?: any): Promise<any> {
    return this.webSocketManager.sendToInsightsAgent(
      message,
      { ...this.context.fileContext, ...additionalContext }
    );
  }

  async processOperation(operation: AgentOperation): Promise<any> {
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
  constructor(webSocketManager: any, context: AgentContext) {
    super(webSocketManager, 'operations', context);
  }

  async processMessage(message: string, additionalContext?: any): Promise<any> {
    return this.webSocketManager.sendToOperationsAgent(
      message,
      { ...this.context.fileContext, ...additionalContext }
    );
  }

  async processOperation(operation: AgentOperation): Promise<any> {
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
  constructor(webSocketManager: any, context: AgentContext) {
    super(webSocketManager, 'business-outcomes', context);
  }

  async processMessage(message: string, additionalContext?: any): Promise<any> {
    return this.webSocketManager.sendToExperienceAgent(
      message,
      { ...this.context.fileContext, ...additionalContext }
    );
  }

  async processOperation(operation: AgentOperation): Promise<any> {
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

export class AgentRouter {
  private webSocketManager: any;
  private context: AgentContext;
  private agents: Map<string, BaseAgentManager> = new Map();

  constructor(webSocketManager: any, context: AgentContext) {
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

  getAgent(agentType: string): BaseAgentManager {
    const agent = this.agents.get(agentType);
    if (!agent) {
      throw new Error(`Unknown agent type: ${agentType}`);
    }
    return agent;
  }

  async routeMessage(agentType: string, message: string, additionalContext?: any): Promise<any> {
    const agent = this.getAgent(agentType);
    return agent.processMessage(message, additionalContext);
  }

  async routeOperation(agentType: string, operation: AgentOperation): Promise<any> {
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
  static async createRouter(sessionToken: string, currentPillar?: string, fileContext?: any): Promise<AgentRouter> {
    // WebSocketManager will be dynamically imported
    const { WebSocketManager } = await import('./WebSocketManager');
    const webSocketManager = new WebSocketManager();
    const context: AgentContext = {
      sessionToken,
      currentPillar,
      fileContext
    };
    return new AgentRouter(webSocketManager, context);
  }
}
