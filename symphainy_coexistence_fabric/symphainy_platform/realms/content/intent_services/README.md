# Content Realm Intent Services

This directory contains the intent services for the Content Realm. These services implement atomic platform capabilities following the Intent Contract pattern.

## Architecture

Each intent service:
- Extends `BaseIntentService`
- Implements a specific Intent Contract (see `docs/intent_contracts/`)
- Is stateless and atomic
- Reports telemetry via Nurse SDK
- Registers artifacts via State Surface
- Uses Public Works abstractions for all infrastructure access

## Services

### IngestFileService
- **Intent:** `ingest_file`
- **Contract:** `journey_content_file_upload_materialization/intent_ingest_file.md`
- **Role:** Uploads files to the platform (Working Material)

### SaveMaterializationService
- **Intent:** `save_materialization`
- **Contract:** `journey_content_file_upload_materialization/intent_save_materialization.md`
- **Role:** Transitions files to Records of Fact and triggers parsing

## Usage

Intent services are executed by the Runtime Execution Engine:

```python
# Runtime executes intent
result = await intent_service.execute(context, params)
```

## Adding New Services

1. Create a new class extending `BaseIntentService`
2. Implement `execute()` method following the Intent Contract
3. Register the service in `__init__.py`
4. Ensure all infrastructure access goes through Public Works
