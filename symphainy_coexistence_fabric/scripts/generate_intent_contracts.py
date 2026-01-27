#!/usr/bin/env python3
"""
Generate Intent Contract Templates from Journey Contracts

This script extracts intents from journey contracts and generates intent contract templates.
"""

import os
import re
from pathlib import Path
from typing import List, Dict

def extract_intents_from_journey(journey_file: Path) -> List[Dict[str, str]]:
    """Extract intent information from a journey contract."""
    intents = []
    
    with open(journey_file, 'r') as f:
        content = f.read()
    
    # Find "Intents in Journey" section
    intents_section_match = re.search(
        r'### Intents in Journey\n(.*?)(?=\n##|\n---|$)',
        content,
        re.DOTALL
    )
    
    if not intents_section_match:
        return intents
    
    intents_section = intents_section_match.group(1)
    
    # Extract intent lines (format: "1. `intent_name` - Description")
    intent_pattern = r'\d+\.\s+`([^`]+)`\s+-\s+(.+?)(?=\n|$)'
    matches = re.finditer(intent_pattern, intents_section)
    
    for match in matches:
        intent_name = match.group(1)
        description = match.group(2).strip()
        intents.append({
            'name': intent_name,
            'description': description
        })
    
    return intents

def generate_intent_contract_template(intent_name: str, journey_name: str, journey_id: str, realm: str) -> str:
    """Generate intent contract template."""
    template = f'''# Intent Contract: {intent_name}

**Intent:** {intent_name}  
**Intent Type:** `{intent_name}`  
**Journey:** {journey_name} (`{journey_id}`)  
**Realm:** {realm}  
**Status:** IN PROGRESS  
**Priority:** PRIORITY 1

---

## 1. Intent Overview

### Purpose
[Describe the purpose of this intent based on journey contract]

### Intent Flow
```
[Describe the flow for this intent]
```

### Expected Observable Artifacts
- [List expected artifacts]

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `parameter_name` | `type` | Description | Validation rules |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `parameter_name` | `type` | Description | Default value |

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `metadata_key` | `type` | Description | Runtime |

---

## 3. Intent Returns

### Success Response

```json
{{
  "artifacts": {{
    "artifact_type": {{
      "result_type": "artifact",
      "semantic_payload": {{
        // Artifact data
      }},
      "renderings": {{}}
    }}
  }},
  "events": [
    {{
      "type": "event_type",
      // Event data
    }}
  ]
}}
```

### Error Response

```json
{{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "execution_id": "exec_abc123"
}}
```

---

## 4. Artifact Registration

### State Surface Registration
- **Artifact ID:** [How artifact_id is generated]
- **Artifact Type:** `"artifact_type"`
- **Lifecycle State:** `"PENDING"` or `"READY"`
- **Produced By:** `{{ intent: "{intent_name}", execution_id: "<execution_id>" }}`
- **Semantic Descriptor:** [Descriptor details]
- **Parent Artifacts:** [List of parent artifact IDs]
- **Materializations:** [List of materializations]

### Artifact Index Registration
- Indexed in Supabase `artifact_index` table
- Includes: [List of indexed fields]

---

## 5. Idempotency

### Idempotency Key
```
idempotency_key = hash([key components])
```

### Scope
- [Describe scope: per tenant, per session, per artifact, etc.]

### Behavior
- [Describe idempotent behavior]

---

## 6. Implementation Details

### Handler Location
[Path to handler implementation]

### Key Implementation Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Dependencies
- **Public Works:** [Abstractions needed]
- **State Surface:** [Methods needed]
- **Runtime:** [Context requirements]

---

## 7. Frontend Integration

### Frontend Usage
```typescript
// [Frontend code example]
```

### Expected Frontend Behavior
1. [Behavior 1]
2. [Behavior 2]

---

## 8. Error Handling

### Validation Errors
- [Error type] -> [Error response]

### Runtime Errors
- [Error type] -> [Error response]

### Error Response Format
```json
{{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "execution_id": "exec_abc123",
  "intent_type": "{intent_name}"
}}
```

---

## 9. Testing & Validation

### Happy Path
1. [Step 1]
2. [Step 2]

### Boundary Violations
- [Violation type] -> [Expected behavior]

### Failure Scenarios
- [Failure type] -> [Expected behavior]

---

## 10. Contract Compliance

### Required Artifacts
- `artifact_type` - Required

### Required Events
- `event_type` - Required

### Lifecycle State
- [Lifecycle state requirements]

---

**Last Updated:** [Date]  
**Owner:** [Realm] Solution Team  
**Status:** IN PROGRESS
'''
    return template

def main():
    """Main function to generate intent contract templates."""
    base_dir = Path(__file__).parent.parent
    journey_contracts_dir = base_dir / 'docs' / 'journey_contracts'
    intent_contracts_dir = base_dir / 'docs' / 'intent_contracts'
    
    # Map journey IDs to realm names
    journey_to_realm = {
        'journey_content_': 'Content Realm',
        'journey_insights_': 'Insights Realm',
        'journey_journey_': 'Journey Realm',
        'journey_solution_': 'Solution Realm',
        'journey_security_': 'Security Solution',
        'journey_coexistence_': 'Coexistence Solution',
        'journey_control_tower_': 'Control Tower Solution',
    }
    
    # Process each journey contract
    for journey_file in journey_contracts_dir.rglob('journey_*.md'):
        journey_name = journey_file.stem
        journey_id = journey_name
        
        # Determine realm
        realm = 'Unknown Realm'
        for prefix, realm_name in journey_to_realm.items():
            if journey_id.startswith(prefix):
                realm = realm_name
                break
        
        # Extract intents
        intents = extract_intents_from_journey(journey_file)
        
        if not intents:
            print(f"⚠️  No intents found in {journey_file}")
            continue
        
        # Create intent contracts directory for this journey
        intent_dir = intent_contracts_dir / journey_id
        intent_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate intent contract for each intent
        for intent in intents:
            intent_name = intent['name']
            intent_file = intent_dir / f'intent_{intent_name}.md'
            
            # Skip if already exists
            if intent_file.exists():
                print(f"⏭️  Skipping {intent_file} (already exists)")
                continue
            
            # Generate template
            template = generate_intent_contract_template(
                intent_name,
                journey_name.replace('_', ' ').title(),
                journey_id,
                realm
            )
            
            # Write template
            with open(intent_file, 'w') as f:
                f.write(template)
            
            print(f"✅ Created {intent_file}")

if __name__ == '__main__':
    main()
