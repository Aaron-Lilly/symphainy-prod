'use client';

/**
 * Implementation Preparation Panel
 * 
 * Prepares business artifacts (POC Proposal, Roadmap) for SDLC execution.
 * Uses "suggest → validate" approach - analyzes artifacts and suggests configuration,
 * user validates/corrects (no technical knowledge required).
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader } from '@/components/ui/loader';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { CheckCircle2, XCircle, FileText, Rocket, ChevronRight, Sparkles } from 'lucide-react';
import type { AdminAPIManager } from '@/shared/managers/AdminAPIManager';

interface Artifact {
  id: string;
  type: 'roadmap' | 'poc_proposal' | 'blueprint';
  title: string;
  description: string;
  created_at: string;
}

interface SDLCConfigSuggestion {
  journey_type: {
    suggested: 'build' | 'modernize' | 'extend' | 'replatform';
    confidence: number;
    explanation: string;
  };
  capabilities: {
    compose: string[];
    create: string[];
  };
  deliverables: {
    source_code: boolean;
    tests: boolean;
    documentation: boolean;
    deployment_configs: boolean;
  };
  governance: {
    approvals: string[];
    environments: string[];
  };
  agent_team: {
    required: string[];
    realm_agents: string[];
  };
}

interface ImplementationPreparationPanelProps {
  adminAPIManager: AdminAPIManager;
}

export function ImplementationPreparationPanel({ adminAPIManager }: ImplementationPreparationPanelProps) {
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Artifacts from MVP journey
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [selectedArtifact, setSelectedArtifact] = useState<Artifact | null>(null);
  
  // SDLC Configuration
  const [suggestion, setSuggestion] = useState<SDLCConfigSuggestion | null>(null);
  const [validatedConfig, setValidatedConfig] = useState<SDLCConfigSuggestion | null>(null);
  const [currentStep, setCurrentStep] = useState<number>(1);
  const [launching, setLaunching] = useState(false);

  useEffect(() => {
    loadArtifacts();
  }, []);

  const loadArtifacts = async () => {
    setLoading(true);
    setError(null);

    try {
      // TODO: Replace with actual API call when backend is ready
      // const artifacts = await adminAPIManager.getJourneyArtifacts('mvp');
      
      // Mock data for now
      const mockArtifacts: Artifact[] = [
        {
          id: 'poc_001',
          type: 'poc_proposal',
          title: 'POC Proposal: Data Migration Platform',
          description: 'Proof of concept for migrating 350k policies from 8 legacy systems',
          created_at: new Date().toISOString(),
        },
        {
          id: 'roadmap_001',
          type: 'roadmap',
          title: 'Implementation Roadmap',
          description: 'Phased approach for platform implementation',
          created_at: new Date().toISOString(),
        },
        {
          id: 'blueprint_001',
          type: 'blueprint',
          title: 'Coexistence Blueprint',
          description: 'Workflow optimization and coexistence analysis',
          created_at: new Date().toISOString(),
        },
      ];

      setArtifacts(mockArtifacts);
      
      // Auto-select POC Proposal if available
      const pocProposal = mockArtifacts.find(a => a.type === 'poc_proposal');
      if (pocProposal) {
        setSelectedArtifact(pocProposal);
        analyzeArtifact(pocProposal);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load artifacts');
      console.error('Error loading artifacts:', err);
    } finally {
      setLoading(false);
    }
  };

  const analyzeArtifact = async (artifact: Artifact) => {
    setAnalyzing(true);
    setError(null);
    setSuggestion(null);
    setCurrentStep(1);

    try {
      // TODO: Replace with actual API call when backend is ready
      // const suggestion = await adminAPIManager.suggestSDLCConfig(artifact.id);
      
      // Mock analysis based on artifact type
      if (artifact.type === 'poc_proposal') {
        const mockSuggestion: SDLCConfigSuggestion = {
          journey_type: {
            suggested: 'build',
            confidence: 0.85,
            explanation: 'Based on your POC Proposal scope, this appears to be building new capabilities in your environment',
          },
          capabilities: {
            compose: ['Content processing', 'Insights generation'],
            create: ['Custom integration with legacy systems'],
          },
          deliverables: {
            source_code: true,
            tests: true,
            documentation: false,
            deployment_configs: true,
          },
          governance: {
            approvals: ['Code review', 'Security review'],
            environments: ['Development', 'Staging'],
          },
          agent_team: {
            required: ['Architecture', 'Builder', 'Validator', 'Promoter'],
            realm_agents: ['Content processing', 'Insights generation'],
          },
        };
        
        setSuggestion(mockSuggestion);
        setValidatedConfig({ ...mockSuggestion }); // Start with suggestion as validated
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze artifact');
      console.error('Error analyzing artifact:', err);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleValidateStep = (step: number, updates: Partial<SDLCConfigSuggestion>) => {
    if (!validatedConfig) return;
    
    const updated = { ...validatedConfig, ...updates };
    setValidatedConfig(updated);
    setCurrentStep(step + 1);
  };

  const handleLaunchJourney = async () => {
    if (!validatedConfig || !selectedArtifact) return;

    setLaunching(true);
    setError(null);

    try {
      // TODO: Replace with actual API call when backend is ready
      // await adminAPIManager.launchSDLCJourney({
      //   artifact_id: selectedArtifact.id,
      //   config: validatedConfig,
      // });
      
      // Mock success for now
      alert('SDLC Journey configuration saved! (Backend integration pending)');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to launch SDLC journey');
      console.error('Error launching SDLC journey:', err);
    } finally {
      setLaunching(false);
    }
  };

  const getJourneyTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      build: 'Build New',
      modernize: 'Modernize',
      extend: 'Extend',
      replatform: 'Replatform',
    };
    return labels[type] || type;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Artifacts Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Your MVP Journey Artifacts
          </CardTitle>
          <CardDescription>
            Select an artifact to prepare for implementation
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {artifacts.map((artifact) => (
              <Card
                key={artifact.id}
                className={`cursor-pointer transition-all hover:shadow-md ${
                  selectedArtifact?.id === artifact.id
                    ? 'ring-2 ring-primary'
                    : ''
                }`}
                onClick={() => {
                  setSelectedArtifact(artifact);
                  analyzeArtifact(artifact);
                }}
              >
                <CardContent className="p-4">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <h3 className="font-semibold text-sm mb-1">{artifact.title}</h3>
                      <p className="text-xs text-muted-foreground">{artifact.description}</p>
                    </div>
                    {artifact.type === 'poc_proposal' && (
                      <Badge variant="default" className="ml-2">
                        Recommended
                      </Badge>
                    )}
                  </div>
                  {selectedArtifact?.id === artifact.id && (
                    <div className="mt-3 flex items-center gap-2 text-xs text-primary">
                      <Sparkles className="h-3 w-3" />
                      <span>Analyzing...</span>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Analysis and Configuration */}
      {selectedArtifact && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Rocket className="h-5 w-5" />
              POC Implementation Preparation
            </CardTitle>
            <CardDescription>
              We've analyzed your {selectedArtifact.type === 'poc_proposal' ? 'POC Proposal' : 'artifact'} and prepared an implementation plan
            </CardDescription>
          </CardHeader>
          <CardContent>
            {analyzing ? (
              <div className="flex items-center justify-center py-12">
                <div className="text-center">
                  <Loader />
                  <p className="mt-4 text-sm text-muted-foreground">
                    Analyzing artifact and preparing suggestions...
                  </p>
                </div>
              </div>
            ) : suggestion ? (
              <div className="space-y-6">
                {/* Step 1: Journey Type */}
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-semibold">
                      1
                    </div>
                    <h3 className="text-lg font-semibold">Journey Type</h3>
                  </div>
                  <div className="ml-10 space-y-3">
                    <div className="p-4 bg-muted/50 rounded-lg">
                      <p className="text-sm mb-2">
                        <strong>Suggested:</strong> {getJourneyTypeLabel(suggestion.journey_type.suggested)} (in your environment)
                      </p>
                      <p className="text-xs text-muted-foreground mb-3">
                        {suggestion.journey_type.explanation}
                      </p>
                      <div className="flex items-center gap-2">
                        <Button
                          size="sm"
                          variant={validatedConfig?.journey_type.suggested === suggestion.journey_type.suggested ? 'default' : 'outline'}
                          onClick={() => handleValidateStep(1, { journey_type: suggestion.journey_type })}
                        >
                          <CheckCircle2 className="h-4 w-4 mr-2" />
                          Yes, that's correct
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            // TODO: Show clarification dialog
                            alert('Clarification dialog coming soon');
                          }}
                        >
                          <XCircle className="h-4 w-4 mr-2" />
                          No - Let me clarify
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>

                <Separator />

                {/* Step 2: Capabilities */}
                {currentStep >= 2 && (
                  <div className="space-y-4">
                    <div className="flex items-center gap-2">
                      <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-semibold">
                        2
                      </div>
                      <h3 className="text-lg font-semibold">Capabilities</h3>
                    </div>
                    <div className="ml-10 space-y-3">
                      <div className="p-4 bg-muted/50 rounded-lg">
                        <p className="text-sm mb-3">
                          <strong>We'll use:</strong>
                        </p>
                        <div className="space-y-2">
                          {suggestion.capabilities.compose.map((cap) => (
                            <div key={cap} className="flex items-center gap-2 text-sm">
                              <CheckCircle2 className="h-4 w-4 text-green-600" />
                              <span>{cap}</span>
                            </div>
                          ))}
                          {suggestion.capabilities.create.map((cap) => (
                            <div key={cap} className="flex items-center gap-2 text-sm">
                              <Sparkles className="h-4 w-4 text-blue-600" />
                              <span>{cap} (custom)</span>
                            </div>
                          ))}
                        </div>
                        <div className="mt-4 flex items-center gap-2">
                          <Button
                            size="sm"
                            onClick={() => handleValidateStep(2, { capabilities: suggestion.capabilities })}
                          >
                            <CheckCircle2 className="h-4 w-4 mr-2" />
                            Yes, that's correct
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => {
                              // TODO: Show add/remove dialog
                              alert('Add/remove capabilities dialog coming soon');
                            }}
                          >
                            Add/Remove
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {currentStep >= 2 && <Separator />}

                {/* Step 3: Deliverables */}
                {currentStep >= 3 && (
                  <div className="space-y-4">
                    <div className="flex items-center gap-2">
                      <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-semibold">
                        3
                      </div>
                      <h3 className="text-lg font-semibold">Deliverables</h3>
                    </div>
                    <div className="ml-10 space-y-3">
                      <div className="p-4 bg-muted/50 rounded-lg">
                        <p className="text-sm mb-3">
                          <strong>We'll create:</strong>
                        </p>
                        <div className="space-y-2">
                          {Object.entries(suggestion.deliverables).map(([key, value]) => (
                            <div key={key} className="flex items-center gap-2 text-sm">
                              {value ? (
                                <CheckCircle2 className="h-4 w-4 text-green-600" />
                              ) : (
                                <XCircle className="h-4 w-4 text-gray-400" />
                              )}
                              <span className="capitalize">{key.replace('_', ' ')}</span>
                            </div>
                          ))}
                        </div>
                        <div className="mt-4">
                          <Button
                            size="sm"
                            onClick={() => handleValidateStep(3, { deliverables: suggestion.deliverables })}
                          >
                            <CheckCircle2 className="h-4 w-4 mr-2" />
                            Looks good
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {currentStep >= 3 && <Separator />}

                {/* Step 4: Governance */}
                {currentStep >= 4 && (
                  <div className="space-y-4">
                    <div className="flex items-center gap-2">
                      <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-semibold">
                        4
                      </div>
                      <h3 className="text-lg font-semibold">Governance & Promotion</h3>
                    </div>
                    <div className="ml-10 space-y-3">
                      <div className="p-4 bg-muted/50 rounded-lg">
                        <div className="space-y-4">
                          <div>
                            <p className="text-sm font-medium mb-2">Approvals:</p>
                            <div className="space-y-1">
                              {suggestion.governance.approvals.map((approval) => (
                                <div key={approval} className="flex items-center gap-2 text-sm">
                                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                                  <span>{approval}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                          <div>
                            <p className="text-sm font-medium mb-2">Environments:</p>
                            <div className="space-y-1">
                              {suggestion.governance.environments.map((env) => (
                                <div key={env} className="flex items-center gap-2 text-sm">
                                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                                  <span>{env}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                        <div className="mt-4">
                          <Button
                            size="sm"
                            onClick={() => handleValidateStep(4, { governance: suggestion.governance })}
                          >
                            <CheckCircle2 className="h-4 w-4 mr-2" />
                            Works for us
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {currentStep >= 4 && <Separator />}

                {/* Step 5: Agent Team */}
                {currentStep >= 5 && (
                  <div className="space-y-4">
                    <div className="flex items-center gap-2">
                      <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-semibold">
                        5
                      </div>
                      <h3 className="text-lg font-semibold">Team (Auto-configured)</h3>
                    </div>
                    <div className="ml-10 space-y-3">
                      <div className="p-4 bg-muted/50 rounded-lg">
                        <p className="text-sm mb-3">
                          <strong>We'll use:</strong>
                        </p>
                        <div className="space-y-2">
                          {suggestion.agent_team.required.map((agent) => (
                            <div key={agent} className="flex items-center gap-2 text-sm">
                              <CheckCircle2 className="h-4 w-4 text-green-600" />
                              <span>{agent} agent</span>
                            </div>
                          ))}
                        </div>
                        <p className="text-xs text-muted-foreground mt-3">
                          This is automatically configured based on your POC scope.
                        </p>
                        <div className="mt-4">
                          <Button
                            size="sm"
                            onClick={() => handleValidateStep(5, { agent_team: suggestion.agent_team })}
                          >
                            <CheckCircle2 className="h-4 w-4 mr-2" />
                            No special requirements
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {currentStep >= 5 && <Separator />}

                {/* Step 6: Review & Launch */}
                {currentStep >= 6 && (
                  <div className="space-y-4">
                    <div className="flex items-center gap-2">
                      <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-semibold">
                        6
                      </div>
                      <h3 className="text-lg font-semibold">Review & Launch</h3>
                    </div>
                    <div className="ml-10 space-y-3">
                      <Card>
                        <CardHeader>
                          <CardTitle className="text-base">SDLC Journey Configuration Summary</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-3 text-sm">
                          <div>
                            <span className="font-medium">Journey Type:</span>{' '}
                            {getJourneyTypeLabel(validatedConfig?.journey_type.suggested || '')}
                          </div>
                          <div>
                            <span className="font-medium">Capabilities:</span>{' '}
                            {validatedConfig?.capabilities.compose.length || 0} existing,{' '}
                            {validatedConfig?.capabilities.create.length || 0} custom
                          </div>
                          <div>
                            <span className="font-medium">Deliverables:</span>{' '}
                            {Object.values(validatedConfig?.deliverables || {}).filter(Boolean).length} items
                          </div>
                          <div>
                            <span className="font-medium">Approvals:</span>{' '}
                            {validatedConfig?.governance.approvals.length || 0} required
                          </div>
                          <div>
                            <span className="font-medium">Environments:</span>{' '}
                            {validatedConfig?.governance.environments.join(', ')}
                          </div>
                        </CardContent>
                      </Card>
                      <div className="flex items-center gap-3">
                        <Button
                          onClick={handleLaunchJourney}
                          disabled={launching}
                          className="flex items-center gap-2"
                        >
                          {launching ? (
                            <>
                              <Loader className="h-4 w-4" />
                              Launching...
                            </>
                          ) : (
                            <>
                              <Rocket className="h-4 w-4" />
                              Launch SDLC Journey
                            </>
                          )}
                        </Button>
                        <Button variant="outline" onClick={() => {
                          // TODO: Save configuration
                          alert('Save configuration (coming soon)');
                        }}>
                          Save Configuration
                        </Button>
                      </div>
                    </div>
                  </div>
                )}

                {error && (
                  <Alert variant="destructive" className="mt-4">
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}
              </div>
            ) : (
              <Alert>
                <AlertDescription>
                  Select an artifact above to begin preparation
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
