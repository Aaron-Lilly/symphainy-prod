'use client';

import React, { useState } from 'react';
import SmartCityChat from '../../shared/components/SmartCityChat';
import { AgentType, PillarType } from '../../shared/types/smart-city-api';

export default function SmartCityTestPage() {
  const [sessionToken] = useState('test-session-' + Date.now());
  const [currentAgent, setCurrentAgent] = useState<AgentType | null>(null);
  const [currentPillar, setCurrentPillar] = useState<PillarType | null>(null);

  const handleMessage = (response: any) => {
    console.log('Smart City Chat Response:', response);
  };

  const handleAgentChange = (agent: AgentType) => {
    console.log('Agent changed to:', agent);
    setCurrentAgent(agent);
  };

  const handlePillarChange = (pillar: PillarType) => {
    console.log('Pillar changed to:', pillar);
    setCurrentPillar(pillar);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Smart City Chat Test
          </h1>
          <p className="text-gray-600">
            Testing the Smart City chat system integration
          </p>
          <div className="mt-4 p-4 bg-white rounded-lg border">
            <h2 className="text-lg font-semibold mb-2">Session Info</h2>
            <p><strong>Session Token:</strong> {sessionToken}</p>
            <p><strong>Current Agent:</strong> {currentAgent || 'None'}</p>
            <p><strong>Current Pillar:</strong> {currentPillar || 'None'}</p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <SmartCityChat
            sessionToken={sessionToken}
            onMessage={handleMessage}
            onAgentChange={handleAgentChange}
            onPillarChange={handlePillarChange}
            className="h-96"
          />
        </div>

        <div className="mt-6 p-4 bg-white rounded-lg border">
          <h2 className="text-lg font-semibold mb-2">Test Instructions</h2>
          <ul className="list-disc list-inside space-y-1 text-gray-600">
            <li>Try saying "hello" to start a conversation</li>
            <li>Ask "list my files" to test Content Specialist</li>
            <li>Ask "analyze the trends in this data" to test Insights Specialist</li>
            <li>Ask "create a workflow" to test Operations Specialist</li>
            <li>Ask "create a strategic plan" to test Experience Specialist</li>
            <li>Ask "analyze file completely" to test workflow orchestration</li>
          </ul>
        </div>
      </div>
    </div>
  );
} 