#!/usr/bin/env bash
# Thin wrapper — all logic lives in bootstrap.py (§78 "One Core" principle).
set -euo pipefail
SCRIPT_DIR="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PYTHON_BIN="python3"
command -v "$PYTHON_BIN" >/dev/null 2>&1 || PYTHON_BIN="python"

exec "$PYTHON_BIN" "$SCRIPT_DIR/bootstrap.py" "$@"
