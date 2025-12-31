#!/bin/bash

# scripts/deploy_webapp.sh
# Deployment script for the Xmas Lights Webapp on Cloud Run
# Usage: ./scripts/deploy_webapp.sh <PROJECT_ID> <REGION>

set -e

PROJECT_ID=$1
REGION=${2:-"us-central1"}
WEBAPP_PASSWORD=${3:-"admin"}
SERVICE_NAME="xmas-lights-web"
SERVICE_ACCOUNT_NAME="xmas-lights-sa"

if [ -z "$PROJECT_ID" ]; then
    echo "Usage: ./scripts/deploy_webapp.sh <PROJECT_ID> [REGION] [PASSWORD]"
    exit 1
fi

echo "Deploying to Project: $PROJECT_ID in $REGION"

# 1. Create a Dedicated Service Account
echo "Configuring Service Account..."
if ! gcloud iam service-accounts describe "${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" --project="$PROJECT_ID" > /dev/null 2>&1; then
    gcloud iam service-accounts create "$SERVICE_ACCOUNT_NAME" \
        --display-name="Xmas Lights Webapp Service Account" \
        --project="$PROJECT_ID"
    echo "Service Account created."
else
    echo "Service Account already exists."
fi

SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# 2. Grant Permissions to the Service Account
echo "Granting IAM roles..."
# Allow access to Vertex AI (Gemini)
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/aiplatform.user" > /dev/null

# Allow access to Firestore (Datastore User)
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/datastore.user" > /dev/null

# Allow access to Cloud Storage (Object Admin for the specific bucket)
# Note: For simplicity we grant it on the project, but bucket-level is stricter.
BUCKET_NAME="${PROJECT_ID}-animations"
gcloud storage buckets add-iam-policy-binding "gs://${BUCKET_NAME}" \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/storage.objectAdmin" > /dev/null

echo "Permissions granted."

# 3. Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
    --source ./webapp \
    --project "$PROJECT_ID" \
    --region "$REGION" \
    --service-account "$SERVICE_ACCOUNT_EMAIL" \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_REGION=us-central1,WEBAPP_PASSWORD=$WEBAPP_PASSWORD" \
    --allow-unauthenticated

echo "--------------------------------------------------------"
echo "Deployment Complete!"
echo "Service URL:"
gcloud run services describe "$SERVICE_NAME" --platform managed --region "$REGION" --format 'value(status.url)'
echo "--------------------------------------------------------"
