/**
 * PSO Viewer Component
 * 
 * Displays Permit Semantic Object details
 * Shows permit metadata, obligations, legal citations, and source provenance
 */

"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  FileText, 
  AlertCircle, 
  Loader2,
  Calendar,
  Building2,
  Scale,
  ListChecks,
  ExternalLink
} from 'lucide-react';
import { InsightsService } from '@/shared/services/insights/core';
import { PermitSemanticObject, Obligation } from '@/shared/services/insights/types';
// ✅ PHASE 4: Session-First - Use SessionBoundary for session state
import { useSessionBoundary } from '@/shared/state/SessionBoundaryProvider';
import { toast } from 'sonner';

interface PSOViewerProps {
  psoId: string;
  onClose?: () => void;
}

export function PSOViewer({ psoId, onClose }: PSOViewerProps) {
  // ✅ PHASE 4: Session-First - Use SessionBoundary for session state
  const { state: sessionState } = useSessionBoundary();
  const { submitIntent, getExecutionStatus } = usePlatformState();
  const [pso, setPso] = useState<PermitSemanticObject | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPSO();
  }, [psoId]);

  // ✅ PHASE 4: Migrate to artifact retrieval (PSO stored as artifact)
  // Note: PSO retrieval may need to use artifact retrieval API or a specific intent
  // For now, using artifact retrieval pattern - may need to be updated when PSO intent is available
  const loadPSO = async () => {
    try {
      setLoading(true);
      setError(null);
      
      if (!sessionState.sessionId || !sessionState.tenantId) {
        throw new Error("Session required to load PSO");
      }

      // TODO: PSO retrieval - need to determine if this should be:
      // 1. Artifact retrieval (if PSOs are stored as artifacts)
      // 2. Specific intent (if PSO retrieval intent exists)
      // 3. Direct API call (if PSOs are not yet in intent-based flow)
      
      // Submit intent (will work when backend implements `get_pso` intent)
      // TODO: Backend needs to implement `get_pso` intent or use artifact retrieval
      const executionId = await submitIntent(
        'get_pso', // New intent needed - see PHASE_4_MIGRATION_GAPS.md
        {
          pso_id: psoId
        }
      );

      // Wait for execution to complete
      const maxAttempts = 10;
      let attempts = 0;
      let psoData: any = null;

      while (attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 500));
        
        const status = await getExecutionStatus(executionId);
        
        if (status?.status === "completed") {
          // Extract PSO from execution artifacts
          const psoArtifact = status.artifacts?.pso;
          if (psoArtifact?.semantic_payload) {
            psoData = psoArtifact.semantic_payload;
          }
          break;
        } else if (status?.status === "failed") {
          throw new Error(status.error || "Failed to load PSO");
        }
        
        attempts++;
      }

      if (!psoData) {
        throw new Error("PSO not found in execution result");
      }

      setPso(psoData);
    } catch (err: any) {
      setError(err.message || 'Failed to load PSO');
      toast.error('Failed to load PSO', {
        description: err.message || 'PSO retrieval needs migration to intent-based API'
      });
    } finally {
      setLoading(false);
    }
  };

  const getObligationTypeColor = (type: string) => {
    switch (type) {
      case 'reporting':
        return 'bg-blue-100 text-blue-800';
      case 'threshold':
        return 'bg-orange-100 text-orange-800';
      case 'notification':
        return 'bg-purple-100 text-purple-800';
      case 'operational':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center p-8">
          <Loader2 className="h-6 w-6 animate-spin mr-2" />
          <span>Loading PSO...</span>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center p-8">
          <AlertCircle className="h-6 w-6 text-destructive mr-2" />
          <span className="text-destructive">{error}</span>
        </CardContent>
      </Card>
    );
  }

  if (!pso) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center p-8">
          <span>PSO not found</span>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Permit Semantic Object
            </CardTitle>
            <CardDescription>
              {pso.permit_id} • {pso.pso_id}
            </CardDescription>
          </div>
          {onClose && (
            <Button variant="ghost" size="sm" onClick={onClose}>
              Close
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="obligations">Obligations</TabsTrigger>
            <TabsTrigger value="citations">Citations</TabsTrigger>
            <TabsTrigger value="provenance">Provenance</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-muted-foreground">Permit Type</Label>
                <Badge className="mt-1">{pso.permit_type}</Badge>
              </div>
              <div>
                <Label className="text-muted-foreground">Jurisdiction</Label>
                <p className="mt-1">{pso.jurisdiction}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Issuing Authority</Label>
                <p className="mt-1">{pso.issuing_authority}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Obligations Count</Label>
                <p className="mt-1">{pso.obligations.length}</p>
              </div>
              {pso.effective_period.start && (
                <div>
                  <Label className="text-muted-foreground flex items-center gap-1">
                    <Calendar className="h-3 w-3" />
                    Effective Period
                  </Label>
                  <p className="mt-1 text-sm">
                    {pso.effective_period.start}
                    {pso.effective_period.end && ` - ${pso.effective_period.end}`}
                  </p>
                </div>
              )}
              {pso.covered_entities.length > 0 && (
                <div>
                  <Label className="text-muted-foreground flex items-center gap-1">
                    <Building2 className="h-3 w-3" />
                    Covered Entities
                  </Label>
                  <div className="mt-1 flex flex-wrap gap-1">
                    {pso.covered_entities.map((entity, i) => (
                      <Badge key={i} variant="outline">{entity}</Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </TabsContent>

          {/* Obligations Tab */}
          <TabsContent value="obligations" className="space-y-4">
            {pso.obligations.length === 0 ? (
              <p className="text-muted-foreground">No obligations found</p>
            ) : (
              <div className="space-y-3">
                {pso.obligations.map((obligation) => (
                  <Card key={obligation.obligation_id}>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-base">{obligation.action}</CardTitle>
                        <Badge className={getObligationTypeColor(obligation.obligation_type)}>
                          {obligation.obligation_type}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      {obligation.trigger && (
                        <div>
                          <Label className="text-muted-foreground">Trigger</Label>
                          <p className="text-sm">{obligation.trigger}</p>
                        </div>
                      )}
                      {obligation.condition && (
                        <div>
                          <Label className="text-muted-foreground">Condition</Label>
                          <p className="text-sm">{obligation.condition}</p>
                        </div>
                      )}
                      {obligation.metric && (
                        <div>
                          <Label className="text-muted-foreground">Metric</Label>
                          <p className="text-sm">
                            {obligation.metric}
                            {obligation.threshold && ` (${obligation.threshold}${obligation.unit ? ` ${obligation.unit}` : ''})`}
                          </p>
                        </div>
                      )}
                      {obligation.frequency && (
                        <div>
                          <Label className="text-muted-foreground">Frequency</Label>
                          <p className="text-sm">{obligation.frequency}</p>
                        </div>
                      )}
                      {obligation.deadline && (
                        <div>
                          <Label className="text-muted-foreground">Deadline</Label>
                          <p className="text-sm">{obligation.deadline}</p>
                        </div>
                      )}
                      {obligation.enforcement_reference && (
                        <div>
                          <Label className="text-muted-foreground">Enforcement Reference</Label>
                          <p className="text-sm font-mono">{obligation.enforcement_reference}</p>
                        </div>
                      )}
                      <div className="flex items-center gap-2 pt-2">
                        <Label className="text-muted-foreground">Confidence</Label>
                        <Badge variant="outline">{(obligation.confidence * 100).toFixed(0)}%</Badge>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>

          {/* Citations Tab */}
          <TabsContent value="citations" className="space-y-4">
            {pso.legal_citations.length === 0 ? (
              <p className="text-muted-foreground">No legal citations found</p>
            ) : (
              <div className="space-y-2">
                {pso.legal_citations.map((citation, i) => (
                  <div key={i} className="flex items-center gap-2 p-3 border rounded-lg">
                    <Scale className="h-4 w-4 text-muted-foreground" />
                    <span className="font-mono text-sm">{citation}</span>
                  </div>
                ))}
              </div>
            )}
          </TabsContent>

          {/* Provenance Tab */}
          <TabsContent value="provenance" className="space-y-4">
            {pso.source_provenance ? (
              <div className="space-y-3">
                <div>
                  <Label className="text-muted-foreground">Document ID</Label>
                  <p className="font-mono text-sm">{pso.source_provenance.document_id}</p>
                </div>
                {pso.source_provenance.page_numbers.length > 0 && (
                  <div>
                    <Label className="text-muted-foreground">Page Numbers</Label>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {pso.source_provenance.page_numbers.map((page, i) => (
                        <Badge key={i} variant="outline">{page}</Badge>
                      ))}
                    </div>
                  </div>
                )}
                {pso.source_provenance.section_reference && (
                  <div>
                    <Label className="text-muted-foreground">Section Reference</Label>
                    <p className="text-sm">{pso.source_provenance.section_reference}</p>
                  </div>
                )}
                <div>
                  <Label className="text-muted-foreground">Extraction Method</Label>
                  <p className="text-sm">{pso.source_provenance.extraction_method}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Confidence</Label>
                  <Badge variant="outline">{(pso.source_provenance.confidence * 100).toFixed(0)}%</Badge>
                </div>
                <div>
                  <Label className="text-muted-foreground">Extracted At</Label>
                  <p className="text-sm">{new Date(pso.source_provenance.timestamp).toLocaleString()}</p>
                </div>
              </div>
            ) : (
              <p className="text-muted-foreground">No provenance information available</p>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}

