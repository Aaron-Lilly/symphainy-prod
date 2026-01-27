"use client";

import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { ArrowRight, ArrowLeft, Network, GitBranch } from "lucide-react";

/**
 * ✅ PHASE 3.1: Static Coexistence Diagram
 * 
 * Visual representation of the Coexistence Fabric concept:
 * - Shows how legacy systems, modern tools, and humans coexist
 * - Displays boundary-crossing coordination
 * - Illustrates platform governance
 */
export function CoexistenceDiagram() {
  return (
    <Card className="bg-gradient-to-br from-blue-50 to-purple-50 border-2 border-blue-200">
      <CardContent className="p-6">
        <div className="space-y-6">
          {/* Header */}
          <div className="text-center">
            <Network className="h-12 w-12 mx-auto mb-3 text-blue-600" />
            <h3 className="text-xl font-bold text-gray-800 mb-2">Coexistence Fabric</h3>
            <p className="text-sm text-gray-600">
              Coordinating boundary-crossing work across systems, tools, and people
            </p>
          </div>

          {/* Diagram */}
          <div className="relative">
            {/* Legacy Systems */}
            <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4 mb-4">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-semibold text-red-900">Legacy Systems</h4>
                  <p className="text-xs text-red-700 mt-1">Existing enterprise systems</p>
                </div>
                <div className="flex gap-2">
                  <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                  <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                  <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                </div>
              </div>
            </div>

            {/* Coordination Layer (Platform) */}
            <div className="bg-blue-100 border-2 border-blue-400 rounded-lg p-4 mb-4 relative">
              <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                <div className="bg-blue-600 text-white px-3 py-1 rounded-full text-xs font-semibold">
                  Symphainy Platform
                </div>
              </div>
              <div className="mt-4 text-center">
                <GitBranch className="h-8 w-8 mx-auto mb-2 text-blue-600" />
                <p className="text-sm text-blue-900 font-medium">
                  Boundary-Crossing Coordination
                </p>
                <p className="text-xs text-blue-700 mt-1">
                  Governance • Translation • Validation
                </p>
              </div>
              {/* Arrows showing coordination */}
              <div className="flex justify-center gap-4 mt-4">
                <ArrowRight className="h-4 w-4 text-blue-600" />
                <ArrowLeft className="h-4 w-4 text-blue-600" />
              </div>
            </div>

            {/* Modern Tools & Humans */}
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-green-50 border-2 border-green-300 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-semibold text-green-900">Modern Tools</h4>
                    <p className="text-xs text-green-700 mt-1">AI, automation, APIs</p>
                  </div>
                  <div className="flex gap-2">
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  </div>
                </div>
              </div>
              <div className="bg-purple-50 border-2 border-purple-300 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-semibold text-purple-900">People</h4>
                    <p className="text-xs text-purple-700 mt-1">Teams, stakeholders</p>
                  </div>
                  <div className="flex gap-2">
                    <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                    <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                  </div>
                </div>
              </div>
            </div>

            {/* Flow Indicators */}
            <div className="mt-4 text-center">
              <div className="flex items-center justify-center gap-2 text-xs text-gray-600">
                <ArrowRight className="h-3 w-3" />
                <span>Coordinated Workflows</span>
                <ArrowRight className="h-3 w-3" />
              </div>
            </div>
          </div>

          {/* Key Concepts */}
          <div className="grid grid-cols-3 gap-3 mt-6 pt-6 border-t border-blue-200">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">Boundary-Crossing</div>
              <p className="text-xs text-gray-600 mt-1">Workflows span systems</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">Coordination</div>
              <p className="text-xs text-gray-600 mt-1">Platform orchestrates</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">Governance</div>
              <p className="text-xs text-gray-600 mt-1">Policy & compliance</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
