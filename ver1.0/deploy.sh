#!/bin/bash
# deploy.sh

# Configuration
PROJECT_ID="your-gcp-project"
REGION="asia-south1"
SERVICE_NAME="nifty-ai-recommender"

# Build and push container
echo "Building container..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --memory 2Gi \
  --timeout 300 \
  --concurrency 100 \
  --set-env-vars "GCP_PROJECT_ID=$PROJECT_ID" \
  --set-secrets "KITE_API_KEY=kite-api-key:latest" \
  --set-secrets "KITE_API_SECRET=kite-api-secret:latest" \
  --set-secrets "KITE_ACCESS_TOKEN=kite-access-token:latest" \
  --set-secrets "TELEGRAM_TOKEN=telegram-token:latest" \
  --set-secrets "TELEGRAM_CHAT_ID=telegram-chat-id:latest"

echo "Deployment complete!"