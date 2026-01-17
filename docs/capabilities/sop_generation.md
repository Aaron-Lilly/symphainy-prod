# SOP Generation

**Realm:** Journey  
**Status:** ✅ Complete  
**Last Updated:** January 2026

---

## Overview

The SOP Generation capability creates Standard Operating Procedures (SOPs) from interactive conversations or existing workflows, enabling process documentation and standardization.

---

## Intents

### 1. `generate_sop`

Generates an SOP from an existing workflow.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workflow_id` | string | Yes | Identifier for existing workflow |
| `chat_mode` | boolean | No | If true, uses chat-based generation instead |

#### Response

```json
{
  "artifacts": {
    "sop": {
      "sop_id": "sop_123",
      "workflow_id": "workflow_456",
      "title": "Insurance Policy Processing SOP",
      "sections": [
        {
          "section": "Overview",
          "content": "This SOP describes the process for processing insurance policies..."
        },
        {
          "section": "Steps",
          "content": "1. Validate policy data\n2. Extract key information..."
        }
      ],
      "metadata": {
        "created_date": "2026-01-15T10:00:00Z",
        "version": "1.0"
      }
    },
    "workflow_id": "workflow_456",
    "sop_visual": {
      "image_base64": "...",
      "storage_path": "sops/sop_123.png"
    }
  },
  "events": [
    {
      "type": "sop_generated",
      "workflow_id": "workflow_456"
    }
  ]
}
```

---

### 2. `generate_sop_from_chat`

Generates an SOP from an interactive chat conversation with the Journey Liaison Agent.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session_id` | string | No | Existing chat session ID (if continuing) |
| `initial_requirements` | string | No | Initial requirements for new chat session |

#### Response (New Chat Session)

```json
{
  "artifacts": {
    "chat_session": {
      "session_id": "chat_session_789",
      "status": "active",
      "initial_requirements": "Create SOP for insurance policy processing"
    },
    "status": "chat_active"
  },
  "events": [
    {
      "type": "sop_chat_started",
      "session_id": "chat_session_789"
    }
  ]
}
```

#### Response (SOP Generated)

```json
{
  "artifacts": {
    "sop": {
      "sop_id": "sop_123",
      "title": "Insurance Policy Processing SOP",
      "sections": [...],
      "source": "chat"
    },
    "session_id": "chat_session_789",
    "source": "chat",
    "sop_visual": {
      "image_base64": "...",
      "storage_path": "sops/sop_123.png"
    }
  },
  "events": [
    {
      "type": "sop_generated_from_chat",
      "sop_id": "sop_123",
      "session_id": "chat_session_789"
    }
  ]
}
```

---

### 3. `sop_chat_message`

Processes a chat message in an active SOP generation session.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session_id` | string | Yes | Chat session identifier |
| `message` | string | Yes | User message |

#### Response

```json
{
  "artifacts": {
    "chat_response": {
      "message": "I understand. Let me add a validation step for policy numbers...",
      "session_id": "chat_session_789",
      "status": "active"
    },
    "session_id": "chat_session_789"
  },
  "events": [
    {
      "type": "sop_chat_message_processed",
      "session_id": "chat_session_789"
    }
  ]
}
```

---

## Use Cases

### 1. Interactive SOP Creation
**Scenario:** Creating SOPs through natural conversation.

**Use Case:** Use `generate_sop_from_chat` to:
- Describe process requirements in natural language
- Refine SOP through conversation
- Generate complete SOP with visualizations

**Business Value:** Makes SOP creation accessible to non-technical users.

---

### 2. Workflow Documentation
**Scenario:** Documenting existing workflows as SOPs.

**Use Case:** Use `generate_sop` to:
- Convert workflows to human-readable SOPs
- Generate visual documentation
- Standardize process documentation

**Business Value:** Ensures workflows are properly documented.

---

### 3. Process Standardization
**Scenario:** Standardizing processes across teams.

**Use Case:** Use chat-based SOP generation to:
- Capture process knowledge from experts
- Refine processes through discussion
- Generate standardized documentation

**Business Value:** Ensures consistent process execution.

---

## Technical Details

### Chat-Based Generation

The chat-based SOP generation uses the Journey Liaison Agent:
- Initiates conversation with user requirements
- Asks clarifying questions
- Refines SOP iteratively
- Generates final SOP when complete

### SOP Visualization

Automatically generates visual SOP diagrams:
- Shows process flow
- Includes annotations and notes
- Stores as base64 image and file path

---

## Related Capabilities

- [Workflow Creation](workflow_creation.md) - Create workflows from SOPs
- [Visual Generation](visual_generation.md) - Generate SOP visualizations
- [Coexistence Analysis](coexistence_analysis.md) - Analyze SOP interactions

---

## API Examples

### Generate SOP from Workflow

```python
intent = Intent(
    intent_type="generate_sop",
    parameters={
        "workflow_id": "workflow_456"
    }
)

result = await runtime.execute(intent, context)
sop_id = result.artifacts["sop"]["sop_id"]
```

### Start Chat-Based SOP Generation

```python
intent = Intent(
    intent_type="generate_sop_from_chat",
    parameters={
        "initial_requirements": "Create SOP for insurance policy processing with validation steps"
    }
)

result = await runtime.execute(intent, context)
session_id = result.artifacts["chat_session"]["session_id"]
```

### Continue Chat Conversation

```python
intent = Intent(
    intent_type="sop_chat_message",
    parameters={
        "session_id": "chat_session_789",
        "message": "Add a step to validate policy numbers before processing"
    }
)

result = await runtime.execute(intent, context)
response = result.artifacts["chat_response"]["message"]
```

---

**See Also:**
- [Journey Realm Overview](../architecture/north_star.md#23-domain-services-formerly-realms)
- [API Contracts](../execution/api_contracts_frontend_integration.md)
