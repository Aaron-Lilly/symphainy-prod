/**
 * Extended Smart City Integration for Session Management
 * Additional methods for Smart City session integration
 */

import { SmartCitySessionIntegration } from './smart_city_integration';

export class ExtendedSmartCitySessionIntegration extends SmartCitySessionIntegration {
  // Smart City enhanced pillar state management
  async setSmartCityPillarState(pillar: string, state: any): Promise<void> {
    const sessionToken = this.getSessionToken();
    if (!sessionToken) {
      throw new Error('No active session');
    }

    try {
      // Update local state
      await this.setPillarState(pillar, state);
      
      // Store in Archive
      const archive = this.getArchive();
      const sessionData = await archive.retrieveSession(sessionToken);
      sessionData.pillarStates = {
        ...sessionData.pillarStates,
        [pillar]: state
      };
      await archive.updateSession(sessionToken, sessionData);
      
      // Route session via Traffic Cop if needed
      const trafficCop = this.getTrafficCop();
      await trafficCop.routeSession(sessionToken, pillar);
    } catch (error) {
      console.error('Failed to set Smart City pillar state:', error);
      throw error;
    }
  }

  // Smart City enhanced session reset
  async resetSmartCitySession(): Promise<void> {
    const sessionToken = this.getSessionToken();
    if (sessionToken) {
      try {
        // Delete from Archive
        const archive = this.getArchive();
        await archive.deleteSession(sessionToken);
      } catch (error) {
        console.error('Failed to delete session from Archive:', error);
      }
    }
    
    // Reset local state
    await this.resetAllState();
  }

  // Get Smart City session status
  async getSmartCitySessionStatus(): Promise<string> {
    const sessionToken = this.getSessionToken();
    if (!sessionToken) {
      return 'no_session';
    }
    
    try {
      const conductor = this.getConductor();
      return await conductor.getSessionStatus(sessionToken);
    } catch (error) {
      console.error('Failed to get Smart City session status:', error);
      return 'error';
    }
  }
} 