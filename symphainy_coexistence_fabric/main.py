#!/usr/bin/env python3
"""
Symphainy Platform - Main Entry Point (Local Development)

For containerized deployment, use runtime_main.py instead.

This file can optionally call runtime_main.main() for local development,
or can be used as a lightweight entry point for other services.

Version: 2.0 (Breaking Changes - No Backwards Compatibility)
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# For local development, use runtime_main
# For containerized deployment, Dockerfile uses runtime_main.py directly
if __name__ == "__main__":
    from runtime_main import main
    main()
