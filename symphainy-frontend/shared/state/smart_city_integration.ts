/**
 * Smart City Integration for State Management
 * Integrates state management with Smart City components
 */

import { ApplicationStateManager } from './core';

// Smart City component interfaces
export interface TrafficCop {
  routeState(stateData: any, destination: string): Promise<void>;
  validateState(stateData: any): Promise<boolean>;
}

export interface Archive {
  storeState(stateId: string, stateData: any): Promise<void>;
  retrieveState(stateId: string): Promise<any>;
  updateState(stateId: string, stateData: any): Promise<void>;
  deleteState(stateId: string): Promise<void>;
}

export interface Conductor {
  orchestrateState(stateId: string, workflow: string): Promise<void>;
  getStateStatus(stateId: string): Promise<string>;
}

export class SmartCityStateIntegration {
  private stateManager: ApplicationStateManager;
  private trafficCop: TrafficCop;
  private archive: Archive;
  private conductor: Conductor;

  constructor(
    stateManager: ApplicationStateManager,
    trafficCop: TrafficCop,
    archive: Archive,
    conductor: Conductor
  ) {
    this.stateManager = stateManager;
    this.trafficCop = trafficCop;
    this.archive = archive;
    this.conductor = conductor;
  }

  // Smart City enhanced state persistence
  async persistStateToArchive(stateId: string): Promise<void> {
    try {
      const stateData = {
        mainChatbotState: this.stateManager.getMainChatbotState(),
        agentInfo: this.stateManager.getAgentInfo(),
        analysisResults: this.stateManager.getAnalysisResults(),
        timestamp: new Date().toISOString(),
      };

      await this.archive.storeState(stateId, stateData);
      console.log('State persisted to Archive:', stateId);
    } catch (error) {
      console.error('Failed to persist state to Archive:', error);
      throw error;
    }
  }

  // Smart City enhanced state retrieval
  async retrieveStateFromArchive(stateId: string): Promise<void> {
    try {
      const stateData = await this.archive.retrieveState(stateId);
      
      if (stateData.mainChatbotState !== undefined) {
        this.stateManager.setMainChatbotState(stateData.mainChatbotState);
      }
      
      if (stateData.agentInfo) {
        this.stateManager.setAgentInfo(stateData.agentInfo);
      }
      
      if (stateData.analysisResults) {
        Object.entries(stateData.analysisResults).forEach(([type, result]) => {
          this.stateManager.setAnalysisResult(type, result);
        });
      }
      
      console.log('State retrieved from Archive:', stateId);
    } catch (error) {
      console.error('Failed to retrieve state from Archive:', error);
      throw error;
    }
  }

  // Public methods to access state manager
  getMainChatbotState() {
    return this.stateManager.getMainChatbotState();
  }

  getAgentInfo() {
    return this.stateManager.getAgentInfo();
  }

  getAnalysisResults() {
    return this.stateManager.getAnalysisResults();
  }

  // Public methods to access other components
  getTrafficCop(): TrafficCop {
    return this.trafficCop;
  }

  getArchive(): Archive {
    return this.archive;
  }

  getConductor(): Conductor {
    return this.conductor;
  }
} 