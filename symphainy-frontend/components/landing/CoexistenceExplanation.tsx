"use client";

import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CoexistenceDiagram } from "./CoexistenceDiagram";
import { ArrowRight, Link2, Shield, GitBranch } from "lucide-react";
import { useRouter } from "next/navigation";

/**
 * ✅ PHASE 3.1: Coexistence Explanation Component
 * 
 * Explains the Coexistence Fabric concept:
 * - What coexistence means
 * - How the platform coordinates boundary-crossing work
 * - Key concepts: boundary-crossing, coordination, governance
 * - Links to Journey pillar for coexistence analysis
 */
export function CoexistenceExplanation() {
  const router = useRouter();

  return (
    <Card className="border-2 border-blue-200 bg-gradient-to-br from-white to-blue-50/30">
      <CardHeader>
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-100 rounded-lg">
            <GitBranch className="h-6 w-6 text-blue-600" />
          </div>
          <div>
            <CardTitle className="text-2xl">What is Coexistence?</CardTitle>
            <CardDescription className="mt-1">
              Understanding how the Symphainy platform coordinates boundary-crossing work
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Explanation Text */}
        <div className="space-y-4">
          <p className="text-gray-700 leading-relaxed">
            The <strong>Coexistence Fabric</strong> is Symphainy's approach to coordinating work that spans
            multiple systems, tools, and people. Instead of replacing existing systems, the platform enables
            them to <strong>coexist</strong> and work together seamlessly.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <Link2 className="h-5 w-5 text-blue-600" />
                <h4 className="font-semibold text-gray-800">Boundary-Crossing</h4>
              </div>
              <p className="text-sm text-gray-600">
                Workflows that span legacy systems, modern tools, and human teams require coordination
                across boundaries.
              </p>
            </div>

            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <GitBranch className="h-5 w-5 text-green-600" />
                <h4 className="font-semibold text-gray-800">Coordination</h4>
              </div>
              <p className="text-sm text-gray-600">
                The platform orchestrates work across systems, translating between formats, validating
                operations, and ensuring consistency.
              </p>
            </div>

            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <Shield className="h-5 w-5 text-purple-600" />
                <h4 className="font-semibold text-gray-800">Governance</h4>
              </div>
              <p className="text-sm text-gray-600">
                Policy enforcement, data boundaries, and compliance are managed centrally while respecting
                system autonomy.
              </p>
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-semibold text-blue-900 mb-2">Example: SOP ↔ Workflow Coexistence</h4>
            <p className="text-sm text-blue-800">
              A Standard Operating Procedure (SOP) defines how work <em>should</em> be done. A workflow
              defines how work <em>is</em> done in practice. The platform analyzes how these coexist,
              identifying gaps, overlaps, and opportunities for alignment.
            </p>
          </div>
        </div>

        {/* Visual Diagram */}
        <div>
          <CoexistenceDiagram />
        </div>

        {/* Call to Action */}
        <div className="flex items-center justify-between pt-4 border-t border-gray-200">
          <div>
            <p className="text-sm text-gray-600">
              Ready to analyze coexistence in your organization?
            </p>
          </div>
          <Button
            onClick={() => router.push("/pillars/journey")}
            variant="default"
            className="bg-blue-600 hover:bg-blue-700"
          >
            Analyze Coexistence
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
