/**
 * Extended Smart City Integration for State Management
 * Additional methods for Smart City state integration
 */

import { SmartCityStateIntegration } from './smart_city_integration';

export class ExtendedSmartCityStateIntegration extends SmartCityStateIntegration {
  // Smart City enhanced state routing
  async routeStateToPillar(pillar: string): Promise<void> {
    try {
      const stateData = {
        mainChatbotState: this.getMainChatbotState(),
        agentInfo: this.getAgentInfo(),
        analysisResults: this.getAnalysisResults(),
      };

      const trafficCop = this.getTrafficCop();
      await trafficCop.routeState(stateData, pillar);
      console.log('State routed to pillar:', pillar);
    } catch (error) {
      console.error('Failed to route state to pillar:', error);
      throw error;
    }
  }

  // Smart City enhanced state validation
  async validateStateWithTrafficCop(): Promise<boolean> {
    try {
      const stateData = {
        mainChatbotState: this.getMainChatbotState(),
        agentInfo: this.getAgentInfo(),
        analysisResults: this.getAnalysisResults(),
      };

      const trafficCop = this.getTrafficCop();
      const isValid = await trafficCop.validateState(stateData);
      console.log('State validation result:', isValid);
      return isValid;
    } catch (error) {
      console.error('Failed to validate state with Traffic Cop:', error);
      return false;
    }
  }

  // Smart City enhanced state orchestration
  async orchestrateStateWorkflow(workflow: string): Promise<void> {
    try {
      const stateId = `state_${Date.now()}`;
      await this.persistStateToArchive(stateId);
      const conductor = this.getConductor();
      await conductor.orchestrateState(stateId, workflow);
      console.log('State orchestrated with workflow:', workflow);
    } catch (error) {
      console.error('Failed to orchestrate state workflow:', error);
      throw error;
    }
  }

  // Get Smart City state status
  async getSmartCityStateStatus(stateId: string): Promise<string> {
    try {
      const conductor = this.getConductor();
      return await conductor.getStateStatus(stateId);
    } catch (error) {
      console.error('Failed to get Smart City state status:', error);
      return 'error';
    }
  }
} 