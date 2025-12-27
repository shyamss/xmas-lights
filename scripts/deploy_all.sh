#!/bin/bash

# scripts/deploy_all.sh
# Comprehensive deployment script for Xmas Lights project.
# Sets up GCP resources, deploys the webapp, and publishes device code.
# Usage: ./scripts/deploy_all.sh <PROJECT_ID> [REGION]

set -e

PROJECT_ID=$1
REGION=${2:-"us-central1"}

if [ -z "$PROJECT_ID" ]; then
    echo "Usage: ./scripts/deploy_all.sh <PROJECT_ID> [REGION]"
    exit 1
fi

echo "--- Starting Full Deployment for Project: $PROJECT_ID in Region: $REGION ---"

echo "Step 1/3: Setting up Google Cloud Project resources (idempotent)..."
./scripts/setup_gcp.sh "$PROJECT_ID" "$REGION"

echo ""
echo "Step 2/3: Deploying Web Application to Cloud Run..."
./scripts/deploy_webapp.sh "$PROJECT_ID" "$REGION"

echo ""
echo "Step 3/3: Publishing Device Controller Code to GCS..."
./scripts/publish_device_code.sh "$PROJECT_ID"

echo ""
echo "--- Deployment Complete! ---"
echo ""
echo "To install/update the Xmas Lights Controller on your device (Orange Pi/Raspberry Pi), run this command on the device:"
echo ""
echo "    curl -sL https://storage.googleapis.com/${PROJECT_ID}-animations/install.sh | sudo bash -s ${PROJECT_ID}"
echo ""