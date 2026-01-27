"use client";

import React, { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Download, FileText, Target, Map, Loader, CheckCircle2 } from "lucide-react";
import ReactMarkdown from "react-markdown";

interface Artifact {
  id: string;
  data: any;
  type: 'blueprint' | 'poc' | 'roadmap';
}

interface GeneratedArtifactsDisplayProps {
  artifacts: {
    blueprint?: Artifact;
    poc?: Artifact;
    roadmap?: Artifact;
  };
  onExport: (artifactType: string, artifactId: string, format: string) => Promise<void>;
  isOpen: boolean;
  onClose: () => void;
  onLoadArtifact?: (artifactType: 'blueprint' | 'poc' | 'roadmap', artifactId: string) => Promise<any>;
}

export default function GeneratedArtifactsDisplay({
  artifacts,
  onExport,
  isOpen,
  onClose,
  onLoadArtifact
}: GeneratedArtifactsDisplayProps) {
  const [exporting, setExporting] = useState<{ type: string; format: string } | null>(null);
  const [activeTab, setActiveTab] = useState<'blueprint' | 'poc' | 'roadmap'>('blueprint');
  const [loadedArtifacts, setLoadedArtifacts] = useState<typeof artifacts>(artifacts);
  const [loading, setLoading] = useState<string | null>(null);

  // Load artifact data when modal opens
  React.useEffect(() => {
    if (isOpen && onLoadArtifact) {
      const loadArtifacts = async () => {
        const updated: typeof artifacts = { ...artifacts };
        
        if (artifacts.blueprint && !artifacts.blueprint.data) {
          setLoading('blueprint');
          try {
            const data = await onLoadArtifact('blueprint', artifacts.blueprint.id);
            updated.blueprint = { ...artifacts.blueprint, data };
          } catch (error) {
            console.error("Failed to load blueprint:", error);
          } finally {
            setLoading(null);
          }
        }
        
        if (artifacts.poc && !artifacts.poc.data) {
          setLoading('poc');
          try {
            const data = await onLoadArtifact('poc', artifacts.poc.id);
            updated.poc = { ...artifacts.poc, data };
          } catch (error) {
            console.error("Failed to load POC:", error);
          } finally {
            setLoading(null);
          }
        }
        
        if (artifacts.roadmap && !artifacts.roadmap.data) {
          setLoading('roadmap');
          try {
            const data = await onLoadArtifact('roadmap', artifacts.roadmap.id);
            updated.roadmap = { ...artifacts.roadmap, data };
          } catch (error) {
            console.error("Failed to load roadmap:", error);
          } finally {
            setLoading(null);
          }
        }
        
        setLoadedArtifacts(updated);
      };
      
      loadArtifacts();
    } else if (isOpen) {
      // If no loader provided, use artifacts as-is
      setLoadedArtifacts(artifacts);
    }
  }, [isOpen, artifacts, onLoadArtifact]);

  // Update loaded artifacts when artifacts prop changes
  React.useEffect(() => {
    setLoadedArtifacts(artifacts);
  }, [artifacts]);

  const handleExport = async (artifactType: string, artifactId: string, format: string) => {
    setExporting({ type: artifactType, format });
    try {
      await onExport(artifactType, artifactId, format);
    } catch (error) {
      console.error("Export failed:", error);
    } finally {
      setExporting(null);
    }
  };

  const hasArtifacts = loadedArtifacts.blueprint || loadedArtifacts.poc || loadedArtifacts.roadmap;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Generated Artifacts</DialogTitle>
          <DialogDescription>
            Review and export your generated artifacts. Artifacts show lifecycle status and synthesis inputs from all pillars.
          </DialogDescription>
        </DialogHeader>

        {!hasArtifacts ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground">
              No artifacts generated yet. Use the generation options to create artifacts.
            </p>
          </div>
        ) : (
          <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as any)} className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="blueprint" disabled={!loadedArtifacts.blueprint}>
                Blueprint {loadedArtifacts.blueprint && <CheckCircle2 className="w-4 h-4 ml-2 text-green-600" />}
              </TabsTrigger>
              <TabsTrigger value="poc" disabled={!loadedArtifacts.poc}>
                POC {loadedArtifacts.poc && <CheckCircle2 className="w-4 h-4 ml-2 text-green-600" />}
              </TabsTrigger>
              <TabsTrigger value="roadmap" disabled={!loadedArtifacts.roadmap}>
                Roadmap {loadedArtifacts.roadmap && <CheckCircle2 className="w-4 h-4 ml-2 text-green-600" />}
              </TabsTrigger>
            </TabsList>

            {/* Blueprint Tab */}
            <TabsContent value="blueprint" className="space-y-4">
              {artifacts.blueprint ? (
                <>
                  {/* ✅ PHASE 2.3: Artifact Lifecycle and Metadata */}
                  {/* ✅ PHASE 5.3: Enhanced Lifecycle Display with Purpose, Scope, Owner */}
                  <div className="space-y-2 mb-4">
                    <div className="flex items-center gap-2">
                      <Badge className={artifacts.blueprint.status === 'active' ? 'bg-green-100 text-green-800' : artifacts.blueprint.status === 'draft' ? 'bg-gray-100 text-gray-800' : 'bg-gray-100 text-gray-600'}>
                        {artifacts.blueprint.status || 'active'}
                      </Badge>
                      {artifacts.blueprint.createdAt && (
                        <span className="text-xs text-gray-500">
                          Created: {new Date(artifacts.blueprint.createdAt).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                    {/* ✅ PHASE 5.3: Display purpose, scope, owner (testable guarantee: Visibility) */}
                    {(artifacts.blueprint.purpose || artifacts.blueprint.scope || artifacts.blueprint.owner) && (
                      <div className="text-xs text-gray-600 space-y-1">
                        {artifacts.blueprint.purpose && (
                          <div><span className="font-medium">Purpose:</span> {artifacts.blueprint.purpose}</div>
                        )}
                        {artifacts.blueprint.scope && (
                          <div><span className="font-medium">Scope:</span> {artifacts.blueprint.scope}</div>
                        )}
                        {artifacts.blueprint.owner && (
                          <div><span className="font-medium">Owner:</span> {artifacts.blueprint.owner}</div>
                        )}
                      </div>
                    )}
                  </div>
                  <div className="flex justify-between items-center">
                    <h3 className="text-lg font-semibold">Coexistence Blueprint</h3>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="outline" disabled={!!exporting}>
                          {exporting?.type === 'blueprint' ? (
                            <>
                              <Loader className="w-4 h-4 mr-2 animate-spin" />
                              Exporting...
                            </>
                          ) : (
                            <>
                              <Download className="w-4 h-4 mr-2" />
                              Export
                            </>
                          )}
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent>
                        <DropdownMenuItem
                          onClick={() => handleExport('blueprint', artifacts.blueprint!.id, 'json')}
                        >
                          Export as JSON
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onClick={() => handleExport('blueprint', artifacts.blueprint!.id, 'docx')}
                        >
                          Export as DOCX
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onClick={() => handleExport('blueprint', artifacts.blueprint!.id, 'yaml')}
                        >
                          Export as YAML
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>

                  <BlueprintContent blueprint={artifacts.blueprint.data} />
                </>
              ) : (
                <div className="text-center py-12 text-muted-foreground">
                  Blueprint not yet generated
                </div>
              )}
            </TabsContent>

            {/* POC Tab */}
            <TabsContent value="poc" className="space-y-4">
              {loadedArtifacts.poc ? (
                <>
                  {/* ✅ PHASE 2.3: Artifact Lifecycle and Metadata */}
                  {/* ✅ PHASE 5.3: Enhanced Lifecycle Display with Purpose, Scope, Owner */}
                  <div className="space-y-2 mb-4">
                    <div className="flex items-center gap-2">
                      <Badge className={loadedArtifacts.poc.status === 'active' ? 'bg-green-100 text-green-800' : loadedArtifacts.poc.status === 'draft' ? 'bg-gray-100 text-gray-800' : 'bg-gray-100 text-gray-600'}>
                        {loadedArtifacts.poc.status || 'draft'}
                      </Badge>
                      {loadedArtifacts.poc.createdAt && (
                        <span className="text-xs text-gray-500">
                          Created: {new Date(loadedArtifacts.poc.createdAt).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                    {/* ✅ PHASE 5.3: Display purpose, scope, owner (testable guarantee: Visibility) */}
                    {(loadedArtifacts.poc.purpose || loadedArtifacts.poc.scope || loadedArtifacts.poc.owner) && (
                      <div className="text-xs text-gray-600 space-y-1">
                        {loadedArtifacts.poc.purpose && (
                          <div><span className="font-medium">Purpose:</span> {loadedArtifacts.poc.purpose}</div>
                        )}
                        {loadedArtifacts.poc.scope && (
                          <div><span className="font-medium">Scope:</span> {loadedArtifacts.poc.scope}</div>
                        )}
                        {loadedArtifacts.poc.owner && (
                          <div><span className="font-medium">Owner:</span> {loadedArtifacts.poc.owner}</div>
                        )}
                      </div>
                    )}
                  </div>
                  <div className="flex justify-between items-center">
                    <h3 className="text-lg font-semibold">POC Proposal</h3>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="outline" disabled={!!exporting || loading === 'poc'}>
                          {loading === 'poc' ? (
                            <>
                              <Loader className="w-4 h-4 mr-2 animate-spin" />
                              Loading...
                            </>
                          ) : exporting?.type === 'poc' ? (
                            <>
                              <Loader className="w-4 h-4 mr-2 animate-spin" />
                              Exporting...
                            </>
                          ) : (
                            <>
                              <Download className="w-4 h-4 mr-2" />
                              Export
                            </>
                          )}
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent>
                        <DropdownMenuItem
                          onClick={() => handleExport('poc', loadedArtifacts.poc!.id, 'json')}
                        >
                          Export as JSON
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onClick={() => handleExport('poc', loadedArtifacts.poc!.id, 'docx')}
                        >
                          Export as DOCX
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onClick={() => handleExport('poc', loadedArtifacts.poc!.id, 'yaml')}
                        >
                          Export as YAML
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>

                  {loading === 'poc' ? (
                    <div className="text-center py-12">
                      <Loader className="w-8 h-8 mx-auto mb-2 animate-spin" />
                      <p className="text-sm text-muted-foreground">Loading POC proposal...</p>
                    </div>
                  ) : (
                    <POCContent poc={loadedArtifacts.poc.data} />
                  )}
                </>
              ) : (
                <div className="text-center py-12 text-muted-foreground">
                  POC proposal not yet generated
                </div>
              )}
            </TabsContent>

            {/* Roadmap Tab */}
            <TabsContent value="roadmap" className="space-y-4">
              {loadedArtifacts.roadmap ? (
                <>
                  {/* ✅ PHASE 2.3: Artifact Lifecycle and Metadata */}
                  {/* ✅ PHASE 5.3: Enhanced Lifecycle Display with Purpose, Scope, Owner */}
                  <div className="space-y-2 mb-4">
                    <div className="flex items-center gap-2">
                      <Badge className={loadedArtifacts.roadmap.status === 'active' ? 'bg-green-100 text-green-800' : loadedArtifacts.roadmap.status === 'draft' ? 'bg-gray-100 text-gray-800' : 'bg-gray-100 text-gray-600'}>
                        {loadedArtifacts.roadmap.status || 'active'}
                      </Badge>
                      {loadedArtifacts.roadmap.createdAt && (
                        <span className="text-xs text-gray-500">
                          Created: {new Date(loadedArtifacts.roadmap.createdAt).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                    {/* ✅ PHASE 5.3: Display purpose, scope, owner (testable guarantee: Visibility) */}
                    {(loadedArtifacts.roadmap.purpose || loadedArtifacts.roadmap.scope || loadedArtifacts.roadmap.owner) && (
                      <div className="text-xs text-gray-600 space-y-1">
                        {loadedArtifacts.roadmap.purpose && (
                          <div><span className="font-medium">Purpose:</span> {loadedArtifacts.roadmap.purpose}</div>
                        )}
                        {loadedArtifacts.roadmap.scope && (
                          <div><span className="font-medium">Scope:</span> {loadedArtifacts.roadmap.scope}</div>
                        )}
                        {loadedArtifacts.roadmap.owner && (
                          <div><span className="font-medium">Owner:</span> {loadedArtifacts.roadmap.owner}</div>
                        )}
                      </div>
                    )}
                  </div>
                  <div className="flex justify-between items-center">
                    <h3 className="text-lg font-semibold">Strategic Roadmap</h3>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="outline" disabled={!!exporting || loading === 'roadmap'}>
                          {loading === 'roadmap' ? (
                            <>
                              <Loader className="w-4 h-4 mr-2 animate-spin" />
                              Loading...
                            </>
                          ) : exporting?.type === 'roadmap' ? (
                            <>
                              <Loader className="w-4 h-4 mr-2 animate-spin" />
                              Exporting...
                            </>
                          ) : (
                            <>
                              <Download className="w-4 h-4 mr-2" />
                              Export
                            </>
                          )}
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent>
                        <DropdownMenuItem
                          onClick={() => handleExport('roadmap', loadedArtifacts.roadmap!.id, 'json')}
                        >
                          Export as JSON
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onClick={() => handleExport('roadmap', loadedArtifacts.roadmap!.id, 'docx')}
                        >
                          Export as DOCX
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onClick={() => handleExport('roadmap', loadedArtifacts.roadmap!.id, 'yaml')}
                        >
                          Export as YAML
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>

                  {loading === 'roadmap' ? (
                    <div className="text-center py-12">
                      <Loader className="w-8 h-8 mx-auto mb-2 animate-spin" />
                      <p className="text-sm text-muted-foreground">Loading roadmap...</p>
                    </div>
                  ) : (
                    <RoadmapContent roadmap={loadedArtifacts.roadmap.data} />
                  )}
                </>
              ) : (
                <div className="text-center py-12 text-muted-foreground">
                  Roadmap not yet generated
                </div>
              )}
            </TabsContent>
          </Tabs>
        )}
      </DialogContent>
    </Dialog>
  );
}

function BlueprintContent({ blueprint }: { blueprint: any }) {
  const currentState = blueprint?.current_state || {};
  const coexistenceState = blueprint?.coexistence_state || {};
  const roadmap = blueprint?.roadmap || {};
  const responsibilityMatrix = blueprint?.responsibility_matrix || {};

  return (
    <div className="space-y-6">
      {/* Current State */}
      <Card>
        <CardHeader>
          <CardTitle>Current State</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-700">{currentState.description || "N/A"}</p>
          {currentState.workflow_chart?.image_base64 && (
            <div className="mt-4">
              <img
                src={`data:image/png;base64,${currentState.workflow_chart.image_base64}`}
                alt="Current State Workflow"
                className="w-full rounded-lg border"
              />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Coexistence State */}
      <Card>
        <CardHeader>
          <CardTitle>Coexistence State</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-700">{coexistenceState.description || "N/A"}</p>
          {coexistenceState.workflow_chart?.image_base64 && (
            <div className="mt-4">
              <img
                src={`data:image/png;base64,${coexistenceState.workflow_chart.image_base64}`}
                alt="Coexistence State Workflow"
                className="w-full rounded-lg border"
              />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Transition Roadmap */}
      {roadmap.phases && roadmap.phases.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Transition Roadmap</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {roadmap.phases.map((phase: any, idx: number) => (
                <div key={idx} className="border-l-4 border-blue-500 pl-4">
                  <h4 className="font-semibold">Phase {phase.phase}: {phase.name}</h4>
                  <p className="text-sm text-gray-600">Duration: {phase.duration}</p>
                  <ul className="list-disc pl-5 mt-2 space-y-1">
                    {phase.objectives?.map((obj: string, objIdx: number) => (
                      <li key={objIdx} className="text-sm">{obj}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Responsibility Matrix */}
      {responsibilityMatrix.responsibilities && responsibilityMatrix.responsibilities.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Responsibility Matrix</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {responsibilityMatrix.responsibilities.map((resp: any, idx: number) => (
                <div key={idx} className="border rounded-lg p-4">
                  <h4 className="font-semibold mb-2">{resp.step}</h4>
                  {resp.human && resp.human.length > 0 && (
                    <div className="mb-2">
                      <Badge variant="outline" className="mr-2">Human</Badge>
                      <span className="text-sm">{resp.human.join(', ')}</span>
                    </div>
                  )}
                  {resp.ai_symphainy && resp.ai_symphainy.length > 0 && (
                    <div className="mb-2">
                      <Badge variant="outline" className="mr-2">AI/Symphainy</Badge>
                      <span className="text-sm">{resp.ai_symphainy.join(', ')}</span>
                    </div>
                  )}
                  {resp.external_systems && resp.external_systems.length > 0 && (
                    <div>
                      <Badge variant="outline" className="mr-2">External Systems</Badge>
                      <span className="text-sm">{resp.external_systems.join(', ')}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function POCContent({ poc }: { poc: any }) {
  const proposal = poc?.proposal || poc;

  return (
    <div className="space-y-6">
      {proposal.objectives && (
        <Card>
          <CardHeader>
            <CardTitle>Objectives</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="list-disc pl-5 space-y-2">
              {Array.isArray(proposal.objectives) ? (
                proposal.objectives.map((obj: any, idx: number) => (
                  <li key={idx} className="text-sm">
                    {typeof obj === 'string' ? obj : obj.description || JSON.stringify(obj)}
                  </li>
                ))
              ) : (
                <li className="text-sm">{JSON.stringify(proposal.objectives)}</li>
              )}
            </ul>
          </CardContent>
        </Card>
      )}

      {proposal.scope && (
        <Card>
          <CardHeader>
            <CardTitle>Scope</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="prose max-w-none text-sm">
              {typeof proposal.scope === 'string' ? (
                <ReactMarkdown>{proposal.scope}</ReactMarkdown>
              ) : (
                <pre className="whitespace-pre-wrap">{JSON.stringify(proposal.scope, null, 2)}</pre>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {proposal.timeline && (
        <Card>
          <CardHeader>
            <CardTitle>Timeline</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <p className="text-sm"><strong>Start:</strong> {proposal.timeline.start_date || 'N/A'}</p>
              <p className="text-sm"><strong>End:</strong> {proposal.timeline.end_date || 'N/A'}</p>
              <p className="text-sm"><strong>Duration:</strong> {proposal.timeline.duration || 'N/A'}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {proposal.resources && proposal.resources.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Resources</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="list-disc pl-5 space-y-2">
              {proposal.resources.map((resource: string, idx: number) => (
                <li key={idx} className="text-sm">{resource}</li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {proposal.success_criteria && (
        <Card>
          <CardHeader>
            <CardTitle>Success Criteria</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="list-disc pl-5 space-y-2">
              {Array.isArray(proposal.success_criteria) ? (
                proposal.success_criteria.map((criteria: any, idx: number) => (
                  <li key={idx} className="text-sm">
                    {typeof criteria === 'string' ? criteria : criteria.description || JSON.stringify(criteria)}
                  </li>
                ))
              ) : (
                <li className="text-sm">{JSON.stringify(proposal.success_criteria)}</li>
              )}
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function RoadmapContent({ roadmap }: { roadmap: any }) {
  const roadmapData = roadmap?.roadmap || roadmap;
  const strategicPlan = roadmap?.strategic_plan || {};

  return (
    <div className="space-y-6">
      {strategicPlan.overview && (
        <Card>
          <CardHeader>
            <CardTitle>Strategic Plan</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-700">{strategicPlan.overview}</p>
          </CardContent>
        </Card>
      )}

      {roadmapData.phases && roadmapData.phases.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Phases</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {roadmapData.phases.map((phase: any, idx: number) => (
                <div key={idx} className="border-l-4 border-purple-500 pl-4">
                  <h4 className="font-semibold">Phase {phase.phase}: {phase.name}</h4>
                  <p className="text-sm text-gray-600">Duration: {phase.duration}</p>
                  {phase.milestones && phase.milestones.length > 0 && (
                    <ul className="list-disc pl-5 mt-2 space-y-1">
                      {phase.milestones.map((milestone: string, mIdx: number) => (
                        <li key={mIdx} className="text-sm">{milestone}</li>
                      ))}
                    </ul>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {roadmapData.timeline && (
        <Card>
          <CardHeader>
            <CardTitle>Timeline</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <p className="text-sm"><strong>Start:</strong> {roadmapData.timeline.start_date || 'N/A'}</p>
              <p className="text-sm"><strong>End:</strong> {roadmapData.timeline.end_date || 'N/A'}</p>
              <p className="text-sm"><strong>Total Duration:</strong> {roadmapData.timeline.total_duration || 'N/A'}</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
