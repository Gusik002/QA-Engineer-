#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
COLLECTION="$ROOT_DIR/postman/collections/restful-booker.postman_collection.json"
ENV="$ROOT_DIR/postman/environments/restful-booker.postman_environment.json"
REPORT_DIR="$ROOT_DIR/postman/reports/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$REPORT_DIR"

if ! command -v newman >/dev/null 2>&1; then
  echo "Installing newman and reporters..."
  npm install -g newman newman-reporter-html newman-reporter-junitfull
fi

newman run "$COLLECTION" \
  -e "$ENV" \
  --reporters cli,junit,html \
  --reporter-junit-export "$REPORT_DIR/newman-results.xml" \
  --reporter-html-export "$REPORT_DIR/newman-results.html" \
  --timeout-request 60000

echo "Reports written to: $REPORT_DIR"
