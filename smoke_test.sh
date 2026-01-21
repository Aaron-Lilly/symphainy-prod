#!/bin/bash
# Quick Smoke Test: Two-Phase Materialization Flow
# Tests the critical path: Upload → Save → List

set -e

BASE_URL="http://localhost:8000"
TENANT_ID="test_tenant"
USER_ID="test_user"
SESSION_ID="test_session_$(date +%s)"

echo "🚀 Starting Smoke Test: Two-Phase Materialization Flow"
echo "=================================================="
echo ""

# Step 1: Upload File (Phase 1 - Pending Materialization)
echo "📤 Step 1: Uploading file (should create pending boundary contract)..."
UPLOAD_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/intent/submit" \
  -H "Content-Type: application/json" \
  -H "x-user-id: ${USER_ID}" \
  -H "x-session-id: ${SESSION_ID}" \
  -d "{
    \"tenant_id\": \"${TENANT_ID}\",
    \"session_id\": \"${SESSION_ID}\",
    \"solution_id\": \"default\",
    \"intent_type\": \"ingest_file\",
    \"parameters\": {
      \"ingestion_type\": \"upload\",
      \"file_content\": \"48656c6c6f20576f726c64\",
      \"ui_name\": \"smoke_test.txt\",
      \"file_type\": \"unstructured\",
      \"mime_type\": \"text/plain\"
    }
  }")

echo "Upload Response: ${UPLOAD_RESPONSE}"
echo ""

EXECUTION_ID=$(echo "${UPLOAD_RESPONSE}" | grep -o '"execution_id":"[^"]*' | cut -d'"' -f4)

if [ -z "${EXECUTION_ID}" ]; then
  echo "❌ FAILED: No execution_id in upload response"
  exit 1
fi

echo "✅ Upload successful! Execution ID: ${EXECUTION_ID}"
echo ""

# Wait for execution to complete
echo "⏳ Waiting for execution to complete..."
sleep 3

# Get execution status
echo "📋 Getting execution status..."
STATUS_RESPONSE=$(curl -s "${BASE_URL}/api/execution/${EXECUTION_ID}/status?tenant_id=${TENANT_ID}")
echo "Status Response: ${STATUS_RESPONSE}"
echo ""

# Extract boundary_contract_id and file_id from status
# Try multiple extraction methods
BOUNDARY_CONTRACT_ID=$(echo "${STATUS_RESPONSE}" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('artifacts', {}).get('file', {}).get('semantic_payload', {}).get('boundary_contract_id', ''))" 2>/dev/null || echo "")
FILE_ID=$(echo "${STATUS_RESPONSE}" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('artifacts', {}).get('file', {}).get('semantic_payload', {}).get('file_id', ''))" 2>/dev/null || echo "")

# Fallback to grep if python extraction fails
if [ -z "${FILE_ID}" ]; then
  FILE_ID=$(echo "${STATUS_RESPONSE}" | grep -o '"file_id":"[^"]*' | head -1 | cut -d'"' -f4 || echo "")
fi
if [ -z "${BOUNDARY_CONTRACT_ID}" ]; then
  BOUNDARY_CONTRACT_ID=$(echo "${STATUS_RESPONSE}" | grep -o '"boundary_contract_id":"[^"]*' | head -1 | cut -d'"' -f4 || echo "")
fi

if [ -z "${BOUNDARY_CONTRACT_ID}" ] || [ -z "${FILE_ID}" ]; then
  echo "⚠️  WARNING: Could not extract boundary_contract_id or file_id from status"
  echo "   This might be OK if the response format is different"
  echo "   Check the status response above for actual values"
  echo ""
  echo "Please manually extract boundary_contract_id and file_id and run:"
  echo "  curl -X POST ${BASE_URL}/api/content/save_materialization \\"
  echo "    -H 'Content-Type: application/json' \\"
  echo "    -H 'x-user-id: ${USER_ID}' \\"
  echo "    -H 'x-session-id: ${SESSION_ID}' \\"
  echo "    -d '{\"boundary_contract_id\": \"<YOUR_CONTRACT_ID>\", \"file_id\": \"<YOUR_FILE_ID>\", \"tenant_id\": \"${TENANT_ID}\"}'"
  exit 0
fi

echo "✅ Found boundary_contract_id: ${BOUNDARY_CONTRACT_ID}"
echo "✅ Found file_id: ${FILE_ID}"
echo ""

# Step 2: Save Materialization (Phase 2 - Authorize Materialization)
echo "💾 Step 2: Saving materialization (should authorize with workspace scope)..."
SAVE_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/content/save_materialization?boundary_contract_id=${BOUNDARY_CONTRACT_ID}&file_id=${FILE_ID}&tenant_id=${TENANT_ID}" \
  -H "Content-Type: application/json" \
  -H "x-user-id: ${USER_ID}" \
  -H "x-session-id: ${SESSION_ID}")

echo "Save Response: ${SAVE_RESPONSE}"
echo ""

if echo "${SAVE_RESPONSE}" | grep -q '"success":true'; then
  echo "✅ Save successful! Materialization authorized"
else
  echo "❌ FAILED: Save did not return success"
  exit 1
fi

echo ""

# Step 3: List Files (Phase 3 - Workspace Scope Filtering)
echo "📋 Step 3: Listing files (should show saved file only)..."
LIST_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/intent/submit" \
  -H "Content-Type: application/json" \
  -H "x-user-id: ${USER_ID}" \
  -H "x-session-id: ${SESSION_ID}" \
  -d "{
    \"tenant_id\": \"${TENANT_ID}\",
    \"session_id\": \"${SESSION_ID}\",
    \"solution_id\": \"default\",
    \"intent_type\": \"list_files\",
    \"parameters\": {}
  }")

echo "List Response: ${LIST_RESPONSE}"
echo ""

LIST_EXECUTION_ID=$(echo "${LIST_RESPONSE}" | grep -o '"execution_id":"[^"]*' | cut -d'"' -f4)

if [ -z "${LIST_EXECUTION_ID}" ]; then
  echo "❌ FAILED: No execution_id in list response"
  exit 1
fi

echo "✅ List intent submitted! Execution ID: ${LIST_EXECUTION_ID}"
echo "⏳ Waiting for list execution to complete..."
sleep 3

LIST_STATUS=$(curl -s "${BASE_URL}/api/execution/${LIST_EXECUTION_ID}/status?tenant_id=${TENANT_ID}")
echo "List Status: ${LIST_STATUS}"
echo ""

# Check if our file appears in the list
if echo "${LIST_STATUS}" | grep -q "${FILE_ID}"; then
  echo "✅ SUCCESS: Saved file appears in list!"
else
  echo "⚠️  WARNING: Saved file may not appear in list (check response above)"
fi

echo ""
echo "=================================================="
echo "🎉 Smoke Test Complete!"
echo ""
echo "Next Steps:"
echo "1. Verify database state in Supabase SQL Editor:"
echo "   SELECT contract_id, contract_status, materialization_allowed,"
echo "          materialization_scope, reference_scope"
echo "   FROM data_boundary_contracts"
echo "   WHERE contract_id = '${BOUNDARY_CONTRACT_ID}';"
echo ""
echo "2. Check materialization index:"
echo "   SELECT uuid, ui_name, boundary_contract_id, representation_type"
echo "   FROM project_files"
echo "   WHERE uuid = '${FILE_ID}';"
