/**
 * Test Experience Layer Page
 * 
 * A test page to demonstrate the new unified Experience Layer Client
 * and verify that it works correctly with the backend.
 */

"use client";

import React from 'react';
import { ProviderComposer } from '@/lib/contexts/ProviderComposer';
import ExperienceLayerExample from '@/components/examples/ExperienceLayerExample';

export default function TestExperienceLayerPage() {
  return (
    <ProviderComposer>
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto py-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Experience Layer Client Test
            </h1>
            <p className="text-gray-600">
              Testing the new unified API client that replaces fragmented API calls
            </p>
          </div>
          
          <ExperienceLayerExample />
        </div>
      </div>
    </ProviderComposer>
  );
}
