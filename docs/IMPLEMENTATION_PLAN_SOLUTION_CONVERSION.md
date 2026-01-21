# Implementation Plan: Solution Conversion Features

**Date:** January 19, 2026  
**Status:** 📋 Planning  
**Priority:** High

---

## Overview

Move `create_solution_from_blueprint` from Journey Realm to Outcomes Realm and add frontend UI to allow users to convert:
1. Coexistence Blueprints → Platform Solutions
2. Roadmaps → Platform Solutions  
3. POC Proposals → Platform Solutions

Each conversion option should be available as a separate, selectable action.

---

## Current State

### Backend
- ✅ `create_solution` intent exists in Outcomes Realm (handles "roadmap" and "poc" sources)
- ✅ `SolutionSynthesisService.create_solution_from_artifact` already supports "blueprint" source
- ❌ `create_solution_from_blueprint` intent is in Journey Realm (needs to move)
- ❌ `create_solution` doesn't handle "blueprint" source yet

### Frontend
- ✅ Blueprint display component exists (`ProcessBlueprint.tsx`)
- ❌ No UI for converting blueprints to solutions
- ❌ No UI for converting roadmaps to solutions
- ❌ No UI for converting POC proposals to solutions

---

## Implementation Plan

### Phase 1: Backend - Move Blueprint Solution Creation to Outcomes Realm

#### Step 1.1: Update Outcomes Realm Intent Declaration
**File:** `symphainy_platform/realms/outcomes/outcomes_realm.py`

**Changes:**
- Add `create_solution_from_blueprint` to `declare_intents()` method
- This makes the intent available to the Runtime

**Code:**
```python
def declare_intents(self) -> List[str]:
    return [
        "synthesize_outcome",
        "generate_roadmap",
        "create_poc",
        "create_solution",
        "create_solution_from_blueprint"  # NEW
    ]
```

#### Step 1.2: Update Outcomes Orchestrator
**File:** `symphainy_platform/realms/outcomes/orchestrators/outcomes_orchestrator.py`

**Changes:**
- Add handler for `create_solution_from_blueprint` in `handle_intent()` method
- Implement `_handle_create_solution_from_blueprint()` method
- Optionally extend `_handle_create_solution()` to also handle "blueprint" source

**Option A: Extend existing `create_solution` (Recommended)**
- Modify `_handle_create_solution()` to accept "blueprint" as a `solution_source`
- This unifies all solution creation under one intent

**Option B: Add separate handler**
- Add `_handle_create_solution_from_blueprint()` method
- Keep separate intent for blueprint conversion

**Recommendation:** Option A (extend `create_solution`) - simpler, more consistent

**Code (Option A):**
```python
async def _handle_create_solution(
    self,
    intent: Intent,
    context: ExecutionContext
) -> Dict[str, Any]:
    """
    Handle create_solution intent - create platform solution from roadmap/POC/blueprint.
    
    Uses Solution SDK to create and register solutions.
    """
    # Get solution source (roadmap, poc, or blueprint)
    solution_source = intent.parameters.get("solution_source")  # "roadmap", "poc", or "blueprint"
    source_id = intent.parameters.get("source_id")  # roadmap_id, proposal_id, or blueprint_id
    
    if not solution_source or not source_id:
        raise ValueError("solution_source and source_id are required for create_solution intent")
    
    if solution_source not in ["roadmap", "poc", "blueprint"]:
        raise ValueError(f"Invalid solution_source: {solution_source}. Must be 'roadmap', 'poc', or 'blueprint'")
    
    # Read source artifact from State Surface
    # For blueprint, try blueprint-specific reference format
    if solution_source == "blueprint":
        source_reference = f"blueprint:{context.tenant_id}:{context.session_id}:{source_id}"
    else:
        source_reference = f"{solution_source}:{context.tenant_id}:{context.session_id}:{source_id}"
    
    source_data = await context.state_surface.get_file(source_reference)
    
    if not source_data:
        # Try to get from execution state
        execution_state = await context.state_surface.get_execution_state(
            source_id,
            context.tenant_id
        )
        if execution_state:
            source_data = execution_state.get("artifacts", {}).get(solution_source) or execution_state.get("artifacts", {}).get("blueprint")
    
    if not source_data:
        raise ValueError(f"Source {solution_source} with id {source_id} not found")
    
    # Create solution via SolutionSynthesisService
    solution_result = await self.solution_synthesis_service.create_solution_from_artifact(
        solution_source=solution_source,
        source_id=source_id,
        source_data=source_data,
        tenant_id=context.tenant_id,
        context=context
    )
    
    return {
        "artifacts": {
            "solution": solution_result,
            "solution_id": solution_result.get("solution_id")
        },
        "events": [
            {
                "type": "solution_created",
                "solution_id": solution_result.get("solution_id"),
                "source": solution_source,
                "source_id": source_id,
                "session_id": context.session_id
            }
        ]
    }
```

#### Step 1.3: Remove from Journey Realm
**File:** `symphainy_platform/realms/journey/journey_realm.py`

**Changes:**
- Remove `create_solution_from_blueprint` from `declare_intents()`

**File:** `symphainy_platform/realms/journey/orchestrators/journey_orchestrator.py`

**Changes:**
- Remove `_handle_create_solution_from_blueprint()` method
- Remove handler from `handle_intent()` method

#### Step 1.4: Update Tests
**File:** `tests/integration/capabilities/phase2/journey_realm/coexistence/test_create_solution_from_blueprint.py`

**Changes:**
- Update test to use Outcomes Realm intent
- Move test to Outcomes Realm test directory (or update import paths)
- Update intent type from `create_solution_from_blueprint` to `create_solution` with `solution_source: "blueprint"`

---

### Phase 2: Frontend - Add Solution Conversion UI

#### Step 2.1: Create Solution Conversion Component
**File:** `frontend/components/outcomes/SolutionConversion.tsx` (NEW)

**Purpose:** Reusable component for converting artifacts to platform solutions

**Props:**
```typescript
interface SolutionConversionProps {
  sourceType: "blueprint" | "roadmap" | "poc";
  sourceId: string;
  sourceName?: string;
  onSuccess?: (solutionId: string) => void;
  onError?: (error: string) => void;
}
```

**Features:**
- Button to trigger conversion
- Loading state during conversion
- Success/error messaging
- Optional preview of solution details

**Implementation:**
```typescript
'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, CheckCircle2, XCircle } from 'lucide-react';
import { submitIntent } from '@/lib/api/outcomes';

export function SolutionConversion({
  sourceType,
  sourceId,
  sourceName,
  onSuccess,
  onError
}: SolutionConversionProps) {
  const [isConverting, setIsConverting] = useState(false);
  const [result, setResult] = useState<{ success: boolean; solutionId?: string; error?: string } | null>(null);

  const handleConvert = async () => {
    setIsConverting(true);
    setResult(null);

    try {
      const response = await submitIntent({
        intent_type: 'create_solution',
        parameters: {
          solution_source: sourceType,
          source_id: sourceId
        }
      });

      if (response.execution_id) {
        // Poll for completion
        const solutionId = await pollExecution(response.execution_id);
        setResult({ success: true, solutionId });
        onSuccess?.(solutionId);
      } else {
        throw new Error('Failed to start conversion');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      setResult({ success: false, error: errorMessage });
      onError?.(errorMessage);
    } finally {
      setIsConverting(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Convert to Platform Solution</CardTitle>
        <CardDescription>
          Create a platform solution from this {sourceType}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {!result && (
          <Button
            onClick={handleConvert}
            disabled={isConverting}
            className="w-full"
          >
            {isConverting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Converting...
              </>
            ) : (
              `Convert ${sourceName || sourceType} to Solution`
            )}
          </Button>
        )}
        
        {result?.success && (
          <div className="flex items-center gap-2 text-green-600">
            <CheckCircle2 className="h-5 w-5" />
            <span>Solution created successfully! ID: {result.solutionId}</span>
          </div>
        )}
        
        {result?.error && (
          <div className="flex items-center gap-2 text-red-600">
            <XCircle className="h-5 w-5" />
            <span>Error: {result.error}</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
```

#### Step 2.2: Add to Blueprint Display
**File:** `frontend/components/operations/ProcessBlueprint.tsx`

**Changes:**
- Import `SolutionConversion` component
- Add section after blueprint display
- Pass blueprint ID and metadata to conversion component

**Location:** Add after blueprint visualization/display section

**Code:**
```typescript
import { SolutionConversion } from '@/components/outcomes/SolutionConversion';

// In component render, after blueprint display:
{blueprintId && (
  <div className="mt-6">
    <SolutionConversion
      sourceType="blueprint"
      sourceId={blueprintId}
      sourceName={blueprintName}
      onSuccess={(solutionId) => {
        // Handle success - maybe navigate to solution view
        console.log('Solution created:', solutionId);
      }}
      onError={(error) => {
        // Handle error
        console.error('Conversion error:', error);
      }}
    />
  </div>
)}
```

#### Step 2.3: Add to Roadmap Display
**File:** `frontend/app/pillars/outcomes/page.tsx` or roadmap-specific component

**Changes:**
- Find where roadmap is displayed
- Add `SolutionConversion` component with `sourceType="roadmap"`
- Pass roadmap ID

**Location:** After roadmap visualization/display section

#### Step 2.4: Add to POC Display
**File:** `frontend/app/pillars/outcomes/page.tsx` or POC-specific component

**Changes:**
- Find where POC proposal is displayed
- Add `SolutionConversion` component with `sourceType="poc"`
- Pass POC proposal ID

**Location:** After POC proposal display section

#### Step 2.5: Create Outcomes API Helper
**File:** `frontend/lib/api/outcomes.ts` (NEW or update existing)

**Purpose:** API functions for Outcomes Realm intents

**Code:**
```typescript
import { API_BASE_URL } from '@/lib/config';

export interface SubmitIntentRequest {
  intent_type: string;
  parameters: Record<string, any>;
  session_id?: string;
}

export interface SubmitIntentResponse {
  execution_id: string;
  status: string;
}

export async function submitIntent(
  request: SubmitIntentRequest,
  token?: string
): Promise<SubmitIntentResponse> {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}/api/intent/submit`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      intent_type: request.intent_type,
      tenant_id: 'default', // Get from context
      session_id: request.session_id || generateSessionId(),
      solution_id: 'default',
      parameters: request.parameters,
      metadata: {}
    })
  });

  if (!response.ok) {
    throw new Error(`Intent submission failed: ${response.statusText}`);
  }

  return response.json();
}

export async function pollExecution(
  executionId: string,
  timeout: number = 60000
): Promise<string> {
  const startTime = Date.now();
  const pollInterval = 1000; // 1 second

  while (Date.now() - startTime < timeout) {
    const response = await fetch(
      `${API_BASE_URL}/api/execution/${executionId}/status?include_artifacts=true`
    );

    if (!response.ok) {
      throw new Error(`Execution status check failed: ${response.statusText}`);
    }

    const status = await response.json();

    if (status.status === 'completed') {
      // Extract solution_id from artifacts
      const solutionId = status.artifacts?.solution?.solution_id || 
                         status.artifacts?.solution_id;
      if (solutionId) {
        return solutionId;
      }
      throw new Error('Solution ID not found in execution result');
    }

    if (status.status === 'failed') {
      throw new Error(status.error || 'Execution failed');
    }

    // Wait before next poll
    await new Promise(resolve => setTimeout(resolve, pollInterval));
  }

  throw new Error('Execution timeout');
}

function generateSessionId(): string {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}
```

---

### Phase 3: Testing & Validation

#### Step 3.1: Update Backend Tests
- Move `test_create_solution_from_blueprint.py` to Outcomes Realm test directory
- Update to use `create_solution` intent with `solution_source: "blueprint"`
- Test all three source types: blueprint, roadmap, poc

#### Step 3.2: Create Frontend Tests
- Test SolutionConversion component
- Test integration with blueprint display
- Test integration with roadmap display
- Test integration with POC display

#### Step 3.3: End-to-End Testing
- Test full flow: Create blueprint → Convert to solution
- Test full flow: Generate roadmap → Convert to solution
- Test full flow: Create POC → Convert to solution
- Verify solution is created and registered correctly

---

## File Changes Summary

### Backend Files to Modify
1. ✅ `symphainy_platform/realms/outcomes/outcomes_realm.py` - Add intent declaration
2. ✅ `symphainy_platform/realms/outcomes/orchestrators/outcomes_orchestrator.py` - Extend `create_solution` handler
3. ✅ `symphainy_platform/realms/journey/journey_realm.py` - Remove intent declaration
4. ✅ `symphainy_platform/realms/journey/orchestrators/journey_orchestrator.py` - Remove handler

### Backend Files to Create/Update
5. ✅ `tests/integration/capabilities/phase2/outcomes/test_create_solution_from_blueprint.py` - Move/update test

### Frontend Files to Create
6. ✅ `frontend/components/outcomes/SolutionConversion.tsx` - NEW component
7. ✅ `frontend/lib/api/outcomes.ts` - NEW or update API helper

### Frontend Files to Modify
8. ✅ `frontend/components/operations/ProcessBlueprint.tsx` - Add conversion UI
9. ✅ `frontend/app/pillars/outcomes/page.tsx` - Add roadmap/POC conversion UI (or separate components)

---

## Implementation Order

1. **Backend Phase 1** (Steps 1.1-1.3) - Move intent to Outcomes Realm
2. **Backend Phase 1** (Step 1.4) - Update tests
3. **Frontend Phase 2** (Step 2.5) - Create API helper
4. **Frontend Phase 2** (Step 2.1) - Create SolutionConversion component
5. **Frontend Phase 2** (Steps 2.2-2.4) - Integrate into displays
6. **Phase 3** - Testing & validation

---

## Success Criteria

- ✅ `create_solution_from_blueprint` removed from Journey Realm (if it exists)
- ✅ `create_solution` in Outcomes Realm handles "blueprint", "roadmap", and "poc" sources
- ✅ Frontend displays conversion option for blueprints (after blueprint display)
- ✅ Frontend displays conversion option for roadmaps (after roadmap display)
- ✅ Frontend displays conversion option for POC proposals (after POC display)
- ✅ Each conversion is a separate, selectable action (user can choose which to convert)
- ✅ All tests pass
- ✅ End-to-end flows work correctly
- ✅ Solution is created and registered successfully for all three source types

---

## Notes

- **Session State Persistence:** The known issue with multi-turn conversations can be deferred for holistic agent testing as discussed
- **Backward Compatibility:** Existing `create_solution` calls with "roadmap" and "poc" sources should continue to work
- **Error Handling:** Ensure proper error messages if source artifacts are not found
- **Loading States:** Provide clear feedback during conversion process
- **Solution Display:** Consider adding navigation to view created solutions

---

**Last Updated:** January 19, 2026
