/**
 * Smart City Integration for Session Management
 * Integrates with Traffic Cop, Archive, and Conductor components
 */

import { SessionManager, SessionState } from './core';

// Smart City component interfaces (to be imported from backend types)
export interface TrafficCop {
  createSession(sessionData: any): Promise<string>;
  validateSession(sessionToken: string): Promise<boolean>;
  routeSession(sessionToken: string, destination: string): Promise<void>;
}

export interface Archive {
  storeSession(sessionToken: string, sessionData: any): Promise<void>;
  retrieveSession(sessionToken: string): Promise<any>;
  updateSession(sessionToken: string, sessionData: any): Promise<void>;
  deleteSession(sessionToken: string): Promise<void>;
}

export interface Conductor {
  orchestrateSession(sessionToken: string, workflow: string): Promise<void>;
  getSessionStatus(sessionToken: string): Promise<string>;
}

export class SmartCitySessionIntegration {
  private sessionManager: SessionManager;
  private trafficCop: TrafficCop;
  private archive: Archive;
  private conductor: Conductor;

  constructor(
    sessionManager: SessionManager,
    trafficCop: TrafficCop,
    archive: Archive,
    conductor: Conductor
  ) {
    this.sessionManager = sessionManager;
    this.trafficCop = trafficCop;
    this.archive = archive;
    this.conductor = conductor;
  }

  // Smart City enhanced session creation
  async createSmartCitySession(sessionData: any): Promise<string> {
    try {
      // Create session via Traffic Cop
      const sessionToken = await this.trafficCop.createSession(sessionData);
      
      // Store session data in Archive
      await this.archive.storeSession(sessionToken, sessionData);
      
      // Update local session manager
      await this.sessionManager.setGuideSessionToken(sessionToken);
      
      // Orchestrate session via Conductor
      await this.conductor.orchestrateSession(sessionToken, 'default');
      
      return sessionToken;
    } catch (error) {
      console.error('Failed to create Smart City session:', error);
      throw error;
    }
  }

  // Smart City enhanced session validation
  async validateSmartCitySession(sessionToken: string): Promise<boolean> {
    try {
      const isValid = await this.trafficCop.validateSession(sessionToken);
      if (isValid) {
        // Retrieve and sync session data from Archive
        const sessionData = await this.archive.retrieveSession(sessionToken);
        await this.sessionManager.setGuideSessionToken(sessionToken);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Failed to validate Smart City session:', error);
      return false;
    }
  }

  // Public method to get session token
  getSessionToken(): string | null {
    return this.sessionManager.getState().guideSessionToken;
  }

  // Public method to set pillar state
  async setPillarState(pillar: string, state: any): Promise<void> {
    await this.sessionManager.setPillarState(pillar, state);
  }

  // Public method to reset all state
  async resetAllState(): Promise<void> {
    await this.sessionManager.resetAllState();
  }

  // Public method to access archive
  getArchive(): Archive {
    return this.archive;
  }

  // Public method to access traffic cop
  getTrafficCop(): TrafficCop {
    return this.trafficCop;
  }

  // Public method to access conductor
  getConductor(): Conductor {
    return this.conductor;
  }
} 