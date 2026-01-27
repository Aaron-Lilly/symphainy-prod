#!/bin/bash
# Upload Flow Log Analysis Script
# Deep dive into logs for each system boundary

set -e

echo "=========================================="
echo "Upload Flow Log Analysis"
echo "=========================================="
echo ""

# Find containers
BACKEND_CONTAINER=$(docker ps --format '{{.Names}}' | grep -i "backend\|runtime\|api" | head -1)
FRONTEND_CONTAINER=$(docker ps --format '{{.Names}}' | grep -i "frontend\|next" | head -1)
TRAEFIK_CONTAINER=$(docker ps --format '{{.Names}}' | grep -i "traefik" | head -1)

if [ -z "$BACKEND_CONTAINER" ]; then
    echo "Error: Backend container not found"
    exit 1
fi

# Function to analyze boundary
analyze_boundary() {
    local boundary_name=$1
    local container=$2
    local patterns=("${@:3}")
    
    echo "=========================================="
    echo "Boundary: $boundary_name"
    echo "Container: $container"
    echo "=========================================="
    echo ""
    
    if [ -z "$container" ]; then
        echo "Container not found, skipping..."
        echo ""
        return
    fi
    
    for pattern in "${patterns[@]}"; do
        echo "Pattern: $pattern"
        echo "---"
        docker logs "$container" --tail 200 2>&1 | grep -i "$pattern" | tail -10
        echo ""
    done
    
    echo "Recent errors:"
    echo "---"
    docker logs "$container" --tail 100 2>&1 | grep -i "error\|exception\|failed\|traceback" | tail -10
    echo ""
    echo ""
}

# Boundary 1-2: Traefik/Frontend
analyze_boundary "Browser → Traefik → Frontend" "$TRAEFIK_CONTAINER" \
    "upload" "intent" "POST" "GET"

analyze_boundary "Frontend Container" "$FRONTEND_CONTAINER" \
    "upload" "intent" "submit" "error"

# Boundary 3-5: Backend/Auth/Runtime
analyze_boundary "Backend API → Auth → Runtime" "$BACKEND_CONTAINER" \
    "/api/intent/submit" "intent.*received" "execution.*started" \
    "auth" "session" "tenant"

# Boundary 6-7: Data Steward/Policy
analyze_boundary "Runtime → Data Steward → Policy Store" "$BACKEND_CONTAINER" \
    "data.*steward" "boundary.*contract" "materialization.*policy" \
    "policy.*retrieved" "policy.*store"

# Boundary 8-9: Ingestion/Storage
analyze_boundary "Content Realm → Ingestion → Storage" "$BACKEND_CONTAINER" \
    "ingest_file" "ingestion.*abstraction" "gcs" "supabase" \
    "file.*uploaded" "file.*storage"

# Boundary 10-11: Materialization
analyze_boundary "Save Materialization → Authorization → Registration" "$BACKEND_CONTAINER" \
    "save_materialization" "materialization.*authorized" \
    "materialization.*registered" "register.*materialization"

# Summary
echo "=========================================="
echo "Summary: Recent Activity"
echo "=========================================="
echo ""
echo "Last 20 lines from backend:"
docker logs "$BACKEND_CONTAINER" --tail 20
echo ""
