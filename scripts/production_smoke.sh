#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-http://localhost}"

echo "Checking health..."
curl -fsS "${BASE_URL}/health" >/dev/null

echo "Checking metrics..."
curl -fsS "${BASE_URL}/metrics" >/dev/null

echo "Checking root page..."
curl -fsS "${BASE_URL}/" >/dev/null

echo "Production smoke check passed for ${BASE_URL}"
