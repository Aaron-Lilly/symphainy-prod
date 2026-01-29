#!/bin/bash
# Wait for services to be ready before running tests
#
# Usage: ./scripts/wait-for-services.sh [--all|--infra|--runtime|--e2e]
#   --all     Wait for all services (infrastructure + runtime + frontend)
#   --infra   Wait for infrastructure services only (default)
#   --runtime Wait for infrastructure + runtime
#   --e2e     Wait for all services including frontend
#
# Exit codes:
#   0 - All services are healthy
#   1 - Timeout waiting for services

set -e

# Configuration
MAX_RETRIES=${MAX_RETRIES:-60}  # 60 * 5s = 5 minutes max wait
RETRY_INTERVAL=${RETRY_INTERVAL:-5}

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Service endpoints (using test ports)
REDIS_HOST=${TEST_REDIS_HOST:-localhost}
REDIS_PORT=${TEST_REDIS_PORT:-6380}

ARANGO_HOST=${TEST_ARANGO_HOST:-localhost}
ARANGO_PORT=${TEST_ARANGO_PORT:-8530}

CONSUL_HOST=${TEST_CONSUL_HOST:-localhost}
CONSUL_PORT=${TEST_CONSUL_PORT:-8501}

MEILISEARCH_HOST=${TEST_MEILISEARCH_HOST:-localhost}
MEILISEARCH_PORT=${TEST_MEILISEARCH_PORT:-7701}

GCS_EMULATOR_HOST=${TEST_GCS_EMULATOR_HOST:-localhost}
GCS_EMULATOR_PORT=${TEST_GCS_EMULATOR_PORT:-9023}

RUNTIME_HOST=${TEST_RUNTIME_HOST:-localhost}
RUNTIME_PORT=${TEST_RUNTIME_PORT:-8100}

FRONTEND_HOST=${TEST_FRONTEND_HOST:-localhost}
FRONTEND_PORT=${TEST_FRONTEND_PORT:-3100}

# Check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Wait for a TCP port to be available
wait_for_port() {
    local host=$1
    local port=$2
    local service=$3
    local retries=0
    
    echo -n "  Waiting for $service ($host:$port)..."
    
    while [ $retries -lt $MAX_RETRIES ]; do
        if command_exists nc; then
            if nc -z "$host" "$port" 2>/dev/null; then
                echo -e " ${GREEN}OK${NC}"
                return 0
            fi
        elif command_exists bash; then
            if bash -c "echo > /dev/tcp/$host/$port" 2>/dev/null; then
                echo -e " ${GREEN}OK${NC}"
                return 0
            fi
        else
            # Fallback to curl for HTTP services
            if curl -s "http://$host:$port" > /dev/null 2>&1; then
                echo -e " ${GREEN}OK${NC}"
                return 0
            fi
        fi
        
        retries=$((retries + 1))
        sleep $RETRY_INTERVAL
        echo -n "."
    done
    
    echo -e " ${RED}TIMEOUT${NC}"
    return 1
}

# Wait for HTTP endpoint to return success
wait_for_http() {
    local url=$1
    local service=$2
    local retries=0
    
    echo -n "  Waiting for $service ($url)..."
    
    while [ $retries -lt $MAX_RETRIES ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            echo -e " ${GREEN}OK${NC}"
            return 0
        fi
        
        retries=$((retries + 1))
        sleep $RETRY_INTERVAL
        echo -n "."
    done
    
    echo -e " ${RED}TIMEOUT${NC}"
    return 1
}

# Wait for Redis using redis-cli if available
wait_for_redis() {
    local host=$1
    local port=$2
    local retries=0
    
    echo -n "  Waiting for Redis ($host:$port)..."
    
    while [ $retries -lt $MAX_RETRIES ]; do
        if command_exists redis-cli; then
            if redis-cli -h "$host" -p "$port" ping 2>/dev/null | grep -q "PONG"; then
                echo -e " ${GREEN}OK${NC}"
                return 0
            fi
        else
            # Fallback to port check
            if command_exists nc; then
                if nc -z "$host" "$port" 2>/dev/null; then
                    echo -e " ${GREEN}OK${NC}"
                    return 0
                fi
            fi
        fi
        
        retries=$((retries + 1))
        sleep $RETRY_INTERVAL
        echo -n "."
    done
    
    echo -e " ${RED}TIMEOUT${NC}"
    return 1
}

# Wait for infrastructure services
wait_for_infrastructure() {
    echo -e "${YELLOW}Waiting for infrastructure services...${NC}"
    
    local failed=0
    
    wait_for_redis "$REDIS_HOST" "$REDIS_PORT" || failed=1
    wait_for_http "http://$ARANGO_HOST:$ARANGO_PORT/_api/version" "ArangoDB" || failed=1
    wait_for_http "http://$CONSUL_HOST:$CONSUL_PORT/v1/status/leader" "Consul" || failed=1
    wait_for_http "http://$MEILISEARCH_HOST:$MEILISEARCH_PORT/health" "Meilisearch" || failed=1
    wait_for_http "http://$GCS_EMULATOR_HOST:$GCS_EMULATOR_PORT/storage/v1/b" "GCS Emulator" || failed=1
    
    return $failed
}

# Wait for runtime service
wait_for_runtime() {
    echo -e "${YELLOW}Waiting for runtime service...${NC}"
    
    wait_for_http "http://$RUNTIME_HOST:$RUNTIME_PORT/health" "Runtime Backend"
    return $?
}

# Wait for frontend service
wait_for_frontend() {
    echo -e "${YELLOW}Waiting for frontend service...${NC}"
    
    # Frontend may take longer to start
    local old_max=$MAX_RETRIES
    MAX_RETRIES=$((MAX_RETRIES * 2))
    
    wait_for_http "http://$FRONTEND_HOST:$FRONTEND_PORT" "Frontend"
    local result=$?
    
    MAX_RETRIES=$old_max
    return $result
}

# Print usage
usage() {
    echo "Usage: $0 [--all|--infra|--runtime|--e2e]"
    echo ""
    echo "Options:"
    echo "  --all      Wait for all services"
    echo "  --infra    Wait for infrastructure only (default)"
    echo "  --runtime  Wait for infrastructure + runtime"
    echo "  --e2e      Wait for all services including frontend"
    echo ""
    echo "Environment variables:"
    echo "  MAX_RETRIES       Maximum number of retries (default: 60)"
    echo "  RETRY_INTERVAL    Seconds between retries (default: 5)"
    echo "  TEST_*_HOST/PORT  Service host/port overrides"
}

# Main
main() {
    local mode="infra"
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --all)
                mode="all"
                shift
                ;;
            --infra)
                mode="infra"
                shift
                ;;
            --runtime)
                mode="runtime"
                shift
                ;;
            --e2e)
                mode="e2e"
                shift
                ;;
            --help|-h)
                usage
                exit 0
                ;;
            *)
                echo -e "${RED}Unknown option: $1${NC}"
                usage
                exit 1
                ;;
        esac
    done
    
    echo ""
    echo "=============================================="
    echo "  Waiting for Test Services (mode: $mode)"
    echo "=============================================="
    echo ""
    
    local failed=0
    
    # Always wait for infrastructure
    wait_for_infrastructure || failed=1
    
    # Wait for runtime if requested
    if [[ "$mode" == "runtime" || "$mode" == "all" || "$mode" == "e2e" ]]; then
        wait_for_runtime || failed=1
    fi
    
    # Wait for frontend if requested
    if [[ "$mode" == "e2e" || "$mode" == "all" ]]; then
        wait_for_frontend || failed=1
    fi
    
    echo ""
    
    if [ $failed -eq 0 ]; then
        echo -e "${GREEN}All services are ready!${NC}"
        exit 0
    else
        echo -e "${RED}Some services failed to start${NC}"
        exit 1
    fi
}

main "$@"
