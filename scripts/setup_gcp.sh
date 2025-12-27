#!/bin/bash

# setup_gcp.sh
# Simple setup script for Google Cloud Resources
# Usage: ./setup_gcp.sh <PROJECT_ID> <REGION>

set -e

PROJECT_ID=$1
REGION=${2:-"us-central1"}

if [ -z "$PROJECT_ID" ]; then
    echo "Usage: ./setup_gcp.sh <PROJECT_ID> [REGION]"
    exit 1
fi

echo "Setting up Google Cloud Project: $PROJECT_ID in $REGION"

# Set project
gcloud config set project "$PROJECT_ID"

# Enable required APIs
echo "Enabling APIs..."
gcloud services enable run.googleapis.com \
    cloudbuild.googleapis.com \
    aiplatform.googleapis.com \
    firestore.googleapis.com \
    artifactregistry.googleapis.com

# Create Firestore Database (Native mode)
echo "Checking/Creating Firestore..."
if ! gcloud firestore databases list --format="value(name)" | grep -q "(default)"; then
    gcloud firestore databases create --location="$REGION" --type=firestore-native
    echo "Firestore created."
else
    echo "Firestore already exists."
fi

# Create Storage Bucket
BUCKET_NAME="${PROJECT_ID}-animations"
echo "Checking/Creating Storage Bucket: $BUCKET_NAME..."
if ! gcloud storage buckets list gs://$BUCKET_NAME --format="value(name)" > /dev/null 2>&1; then
    gcloud storage buckets create gs://$BUCKET_NAME --location="$REGION"
    # Make objects publicly readable (for simple HTTP polling)
    gcloud storage buckets add-iam-policy-binding gs://$BUCKET_NAME \
    --member=allUsers --role=roles/storage.objectViewer
    echo "Bucket created and made public."
else
    echo "Bucket already exists."
fi

echo "Setup complete!"
echo "Next steps:"
echo "1. Deploy webapp: gcloud run deploy xmas-lights-web --source ./webapp --region $REGION --allow-unauthenticated"
