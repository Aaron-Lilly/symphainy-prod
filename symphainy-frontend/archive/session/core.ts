/**
 * Core Session Management
 * Handles session token and state management logic
 */

import { startGlobalSession } from "@/lib/api/global";

export interface SessionState {
  guideSessionToken: string | null;
  pillarStates: Record<string, any>;
}

export interface SessionActions {
  setGuideSessionToken: (token: string) => Promise<void>;
  getPillarState: (pillar: string) => any;
  setPillarState: (pillar: string, state: any) => Promise<void>;
  resetAllState: () => Promise<void>;
  startNewSession: () => Promise<string>;
}

export class SessionManager {
  private state: SessionState = {
    guideSessionToken: null,
    pillarStates: {},
  };

  private listeners: ((state: SessionState) => void)[] = [];

  // State management
  getState(): SessionState {
    return { ...this.state };
  }

  private setState(newState: Partial<SessionState>) {
    this.state = { ...this.state, ...newState };
    this.notifyListeners();
  }

  // Session token management
  async setGuideSessionToken(token: string): Promise<void> {
    this.setState({ guideSessionToken: token });
    // TODO: In future, persist to backend
  }

  async startNewSession(): Promise<string> {
    try {
      const res = await startGlobalSession();
      const token = res.session_token;
      this.setState({ guideSessionToken: token });
      return token;
    } catch (error) {
      console.error("Failed to start global session:", error);
      throw error;
    }
  }

  // Pillar state management
  getPillarState(pillar: string): any {
    return this.state.pillarStates[pillar] || null;
  }

  async setPillarState(pillar: string, state: any): Promise<void> {
    const newPillarStates = { ...this.state.pillarStates, [pillar]: state };
    this.setState({ pillarStates: newPillarStates });
    // TODO: In future, persist to backend
  }

  async resetAllState(): Promise<void> {
    this.setState({ guideSessionToken: null, pillarStates: {} });
    // TODO: In future, reset on backend
  }

  // Observer pattern
  subscribe(listener: (state: SessionState) => void): () => void {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  private notifyListeners(): void {
    this.listeners.forEach(listener => listener(this.getState()));
  }
} 