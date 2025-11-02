# Setup Instructions

## 1. Prerequisites
- GCP Account with billing enabled
- Kite Connect API credentials
- Telegram Bot token
- Python 3.10+

## 2. GCP Setup
```bash
# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable aiplatform.googleapis.com

# Create service account
gcloud iam service-accounts create nifty-ai-sa \
  --display-name="Nifty AI Service Account"

# Grant permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:nifty-ai-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

## 3. Secrets Setup
```bash  
# Store secrets in Secret Manager
echo -n "your-api-key" | gcloud secrets create kite-api-key --data-file=-
echo -n "your-api-secret" | gcloud secrets create kite-api-secret --data-file=-
echo -n "your-access-token" | gcloud secrets create kite-access-token --data-file=-
echo -n "your-telegram-token" | gcloud secrets create telegram-token --data-file=-
echo -n "your-chat-id" | gcloud secrets create telegram-chat-id --data-file=-

## 4. Local Development
```bash
# Clone repository
git clone <your-repo-url>
cd Niftica

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env .env

# Edit .env with your credentials
nano .env

# Run locally
python app.py


## 5. Vertex AI Setup
```bash
# Create Vertex AI endpoint (optional - can use direct model)
gcloud ai endpoints create \
  --region=asia-south1 \
  --display-name="Niftica"

# Note the endpoint ID for configuration

## 6. Firestore Setup
```bash
# Create Firestore database
gcloud firestore databases create \
  --location=asia-south1 \
  --type=firestore-native

# Create indexes (create firestore.indexes.json first)
gcloud firestore indexes composite create \
  --collection-group=recommendation_feedback \
  --query-scope=COLLECTION \
  --field-config field-path=timestamp,order=DESCENDING \
  --field-config field-path=verified,order=ASCENDING

## 7. Telegram Webhook Setup
```bash
# Set webhook URL after deployment
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-service-url.run.app/telegram-webhook"}'


## 8. Cloud Scheduler Setup (for periodic tasks)
```bash
# Create a scheduled job for market hours check
gcloud scheduler jobs create http market-hours-check \
  --schedule="*/5 9-16 * * MON-FRI" \
  --uri="https://your-service-url.run.app/health" \
  --http-method=GET \
  --time-zone="Asia/Kolkata"



### **15. Additional Configuration Files**

```json
// firestore.indexes.json
{
  "indexes": [
    {
      "collectionGroup": "recommendation_feedback",
      "queryScope": "COLLECTION",
      "fields": [
        {"fieldPath": "timestamp", "order": "DESCENDING"},
        {"fieldPath": "verified", "order": "ASCENDING"}
      ]
    },
    {
      "collectionGroup": "recommendation_feedback",
      "queryScope": "COLLECTION", 
      "fields": [
        {"fieldPath": "symbol", "order": "ASCENDING"},
        {"fieldPath": "timestamp", "order": "DESCENDING"}
      ]
    }
  ],
  "fieldOverrides": []
}  

