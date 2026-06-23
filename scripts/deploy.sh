#!/bin/bash
PROJECT_ID="sbi-lifepulse"
REGION="asia-south1"
SERVICE_NAME="lifepulse-api"

echo "🚀 Deploying SBI LifePulse to Cloud Run..."

# Build container via Cloud Builds
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME ./backend

# Deploy on Cloud Run
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=$GEMINI_API_KEY,GCP_PROJECT=$PROJECT_ID

echo "✅ Deployed successfully"
echo "To deploy frontend: firebase deploy --only hosting"
