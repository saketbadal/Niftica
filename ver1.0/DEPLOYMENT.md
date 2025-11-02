# 📋 Deployment Guide

## Prerequisites Checklist

- [ ] GCP Account with billing enabled
- [ ] gcloud CLI installed and authenticated
- [ ] Kite Connect API credentials
- [ ] Telegram Bot token
- [ ] Python 3.10+ installed locally

## Step-by-Step Deployment

### 1. GCP Project Setup

```bash
# Set your project ID
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  firestore.googleapis.com \
  aiplatform.googleapis.com \
  cloudscheduler.googleapis.com





2. Service Account Setup
bash
# Create service account
gcloud iam service-accounts create nifty-ai-sa \
  --display-name="Nifty AI Service Account"

# Grant necessary roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:nifty-ai-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.developer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:nifty-ai-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:nifty-ai-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/datastore.user"
3. Secrets Configuration
bash
# Create secrets
echo -n "your-kite-api-key" | gcloud secrets create kite-api-key --data-file=-
echo -n "your-kite-api-secret" | gcloud secrets create kite-api-secret --data-file=-
echo -n "your-kite-access-token" | gcloud secrets create kite-access-token --data-file=-
echo -n "your-telegram-token" | gcloud secrets create telegram-token --data-file=-
echo -n "your-chat-id" | gcloud secrets create telegram-chat-id --data-file=-


# Grant access to service account
for secret in kite-api-key kite-api-secret kite-access-token telegram-token telegram-chat-id; do
  gcloud secrets add-iam-policy-binding $secret \
    --member="serviceAccount:nifty-ai-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
done
4. Firestore Setup
bash
# Create Firestore database
gcloud firestore databases create \
  --location=asia-south1 \
  --type=firestore-native

# Deploy indexes
gcloud firestore indexes composite create \
  --collection-group=recommendation_feedback \
  --field-config=field-path=timestamp,order=descending \
  --field-config=field-path=verified,order=ascending

# Run setup script
python scripts/setup_firestore.py
5. Build and Deploy
bash
# Build container
gcloud builds submit --tag gcr.io/$PROJECT_ID/nifty-ai-recommender

# Deploy to Cloud Run
gcloud run deploy nifty-ai-recommender \
  --image gcr.io/$PROJECT_ID/nifty-ai-recommender \
  --platform managed \
  --region asia-south1 \
  --memory 2Gi \
  --timeout 300 \
  --concurrency 100 \
  --service-account nifty-ai-sa@$PROJECT_ID.iam.gserviceaccount.com \
  --set-env-vars GCP_PROJECT_ID=$PROJECT_ID,VERTEX_LOCATION=asia-south1 \
  --update-secrets KITE_API_KEY=kite-api-key:latest \
  --update-secrets KITE_API_SECRET=kite-api-secret:latest \
  --update-secrets KITE_ACCESS_TOKEN=kite-access-token:latest \
  --update-secrets TELEGRAM_TOKEN=telegram-token:latest \
  --update-secrets TELEGRAM_CHAT_ID=telegram-chat-id:latest

# Get service URL
SERVICE_URL=$(gcloud run services describe nifty-ai-recommender --region asia-south1 --format 'value(status.url)')
echo "Service deployed at: $SERVICE_URL"
6. Configure Telegram Webhook
bash
# Set webhook
curl -X POST "https://api.telegram.org/bot$(gcloud secrets versions access latest --secret=telegram-token)/setWebhook" \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"$SERVICE_URL/telegram-webhook\"}"
7. Set Up Cloud Scheduler (Optional)
bash
# Create health check job
gcloud scheduler jobs create http health-check \
  --schedule="*/5 9-16 * * MON-FRI" \
  --uri="$SERVICE_URL/health" \
  --http-method=GET \
  --location=asia-south1 \
  --time-zone="Asia/Kolkata"

# Create EOD summary job
gcloud scheduler jobs create http eod-summary \
  --schedule="30 15 * * MON-FRI" \
  --uri="$SERVICE_URL/eod-summary" \
  --http-method=POST \
  --location=asia-south1 \
  --time-zone="Asia/Kolkata"
Post-Deployment Verification
1. Health Check
bash
curl $SERVICE_URL/health
2. Telegram Bot Test
Send /help to your bot

3. Monitor Logs
bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=nifty-ai-recommender" \
  --limit 50 \
  --format json
Troubleshooting
Common Issues
Kite Authentication Failed

Verify access token is valid
Check if token needs refresh
Ensure API credentials are correct
Telegram Webhook Not Working

Verify bot token is correct
Check webhook URL is accessible
Ensure authorized users list is configured
Vertex AI Errors

Verify API is enabled
Check service account permissions
Ensure region is correct (asia-south1)
Memory Issues

Increase Cloud Run memory allocation
Check for memory leaks in code
Monitor memory usage in Cloud Console
Debug Commands
bash
# View recent logs
gcloud run services logs read nifty-ai-recommender --limit=100

# Check service status
gcloud run services describe nifty-ai-recommender --region asia-south1

# Update environment variable
gcloud run services update nifty-ai-recommender \
  --update-env-vars KEY=VALUE \
  --region asia-south1

# Force new deployment
gcloud run deploy nifty-ai-recommender \
  --image gcr.io/$PROJECT_ID/nifty-ai-recommender \
  --region asia-south1 \
  --force
Monitoring Setup
1. Create Uptime Check
bash
gcloud monitoring uptime-checks create nifty-ai-health \
  --display-name="Nifty AI Health Check" \
  --resource-type="URL" \
  --monitored-url="$SERVICE_URL/health" \
  --check-interval="5m"
2. Create Alerts
bash
# Alert for service downtime
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="Nifty AI Service Down" \
  --condition="uptime-health-check" \
  --uptime-check="nifty-ai-health" \
  --duration="5m"
Maintenance
Daily Tasks
Check error logs
Verify recommendation accuracy
Monitor API quotas
Weekly Tasks
Review performance metrics
Clean up old logs
Update system configuration if needed
Monthly Tasks
Archive old recommendation data
Review and optimize Firestore indexes
Update dependencies
Rollback Procedure
If issues occur after deployment:

bash
# List revisions
gcloud run revisions list --service nifty-ai-recommender --region asia-south1

# Rollback to previous revision
gcloud run services update-traffic nifty-ai-recommender \
  --to-revisions=PREVIOUS_REVISION_NAME=100 \
  --region asia-south1
Security Checklist
 All secrets stored in Secret Manager
 Service account has minimum required permissions
 Telegram webhook uses HTTPS
 Authorized users list is configured
 No hardcoded credentials in code
 Cloud Run service is not publicly accessible (if required)
 Regular security updates applied
Cost Optimization
Cloud Run: Set appropriate concurrency and memory limits
Firestore: Monitor read/write operations
Vertex AI: Use caching for repeated queries
Cloud Storage: Set lifecycle policies for old data
Support
For issues:

Check logs in Cloud Console
Run health check script
Review error recovery procedures
Contact support team
