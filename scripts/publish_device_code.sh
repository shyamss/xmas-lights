#!/bin/bash

# scripts/publish_device_code.sh
# Packages the controller code and uploads it to the GCS bucket
# so the device can download it via the install script.
# Usage: ./scripts/publish_device_code.sh <PROJECT_ID>

set -e

PROJECT_ID=$1

if [ -z "$PROJECT_ID" ]; then
    echo "Usage: ./scripts/publish_device_code.sh <PROJECT_ID>"
    exit 1
fi

BUCKET_NAME="${PROJECT_ID}-animations"
TEMP_DIR=$(mktemp -d)

echo "Packaging controller code..."

# Create the tarball. We include the 'controller' directory itself.
# This ensures when extracted it creates a nice subfolder.
tar -czf "$TEMP_DIR/controller.tar.gz" controller

# Upload tarball
echo "Uploading controller.tar.gz to gs://${BUCKET_NAME}..."
gcloud storage cp "$TEMP_DIR/controller.tar.gz" "gs://${BUCKET_NAME}/controller.tar.gz"

# Upload install script (bootstrap)
echo "Uploading install.sh to gs://${BUCKET_NAME}..."
gcloud storage cp "controller/install.sh" "gs://${BUCKET_NAME}/install.sh"

# Make them public
echo "Setting public access..."
gcloud storage objects update "gs://${BUCKET_NAME}/controller.tar.gz" --add-acl-grant=entity=AllUsers,role=READER
gcloud storage objects update "gs://${BUCKET_NAME}/install.sh" --add-acl-grant=entity=AllUsers,role=READER

# Cleanup
rm -rf "$TEMP_DIR"
