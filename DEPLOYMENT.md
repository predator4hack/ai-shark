# Deployment Guide

This guide covers deploying Aviato with the backend on Google Cloud Run and the frontend on Vercel.

## Architecture Overview

```text
┌─────────────────────────────────────────────────────────┐
│                    Vercel (Frontend)                     │
│                  React + Vite + TypeScript               │
│                  https://your-app.vercel.app             │
└─────────────────────────────────────────────────────────┘
                           │
                           │ HTTPS API Calls
                           ▼
┌─────────────────────────────────────────────────────────┐
│              Google Cloud Run (Backend)                  │
│                    FastAPI + Python                      │
│         https://aviato-backend-xxx.run.app               │
└─────────────────────────────────────────────────────────┘
                           │
                ┌──────────┴──────────┐
                ▼                     ▼
    ┌──────────────────┐  ┌──────────────────┐
    │  Google Cloud    │  │  Google Gemini   │
    │    Storage       │  │      LLM API     │
    └──────────────────┘  └──────────────────┘
```

## Prerequisites

- Google Cloud account with billing enabled
- Vercel account (free tier works)
- Google Gemini API key
- gcloud CLI installed
- Vercel CLI installed (`npm i -g vercel`)

## Part 1: Backend Deployment (Google Cloud Run)

### 1. Set up Google Cloud Project

```bash
# Set your project ID
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable storage.googleapis.com
```

### 2. Create Google Cloud Storage Bucket

```bash
gcloud storage buckets create gs://aviato-outputs \
  --location=us-central1 \
  --uniform-bucket-level-access

# Set CORS for file access
echo '[
  {
    "origin": ["*"],
    "method": ["GET", "HEAD"],
    "responseHeader": ["Content-Type"],
    "maxAgeSeconds": 3600
  }
]' > cors.json

gcloud storage buckets update gs://aviato-outputs --cors-file=cors.json
rm cors.json
```

### 3. Set up Secrets

```bash
# Store Google API key in Secret Manager
echo -n "your-google-api-key-here" | gcloud secrets create google-api-key --data-file=-

# Grant Cloud Run access to the secret
gcloud secrets add-iam-policy-binding google-api-key \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### 4. Deploy Backend to Cloud Run

```bash
cd backend

gcloud run deploy aviato-backend \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars USE_GCS=true,GCS_BUCKET_NAME=aviato-outputs,GEMINI_MODEL=gemini-2.5-flash \
  --set-secrets GOOGLE_API_KEY=google-api-key:latest \
  --memory 2Gi \
  --cpu 2 \
  --timeout 600 \
  --max-instances 10 \
  --min-instances 0
```

### 5. Get Backend URL

```bash
export BACKEND_URL=$(gcloud run services describe aviato-backend \
  --region us-central1 \
  --format='value(status.url)')

echo "Backend URL: $BACKEND_URL"
```

## Part 2: Frontend Deployment (Vercel)

### 1. Configure Frontend Environment

```bash
cd frontend

# Create production environment file
cat > .env.production << EOF
VITE_API_URL=${BACKEND_URL}/api
EOF
```

### 2. Deploy to Vercel

```bash
# Login to Vercel (first time only)
vercel login

# Deploy to production
vercel --prod
```

### 3. Set Environment Variables in Vercel Dashboard

Alternatively, set environment variables through the Vercel dashboard:

1. Go to your project settings on [vercel.com](https://vercel.com)
2. Navigate to Settings > Environment Variables
3. Add:
   - Key: `VITE_API_URL`
   - Value: `https://your-backend-url.run.app/api`
   - Environment: Production

4. Redeploy: `vercel --prod`

## Part 3: Testing the Deployment

### Test Backend

```bash
# Health check
curl $BACKEND_URL/health

# API documentation
open $BACKEND_URL/docs
```

### Test Frontend

```bash
# Open your Vercel deployment
vercel --prod
```

### End-to-End Test

1. Open your Vercel frontend URL
2. Upload a test pitch deck
3. Verify processing completes
4. Check that files are stored in GCS
5. Download the generated analysis

## Environment Variables Reference

### Backend (.env)

```env
# Required
GOOGLE_API_KEY=your_google_api_key
GCS_BUCKET_NAME=aviato-outputs
USE_GCS=true

# Optional
GEMINI_MODEL=gemini-2.5-flash
API_PORT=8080
MAX_FILE_SIZE_MB=100
USE_MOCK_LLM=false
```

### Frontend (.env.production)

```env
# Required
VITE_API_URL=https://your-backend-url.run.app/api
```

## Monitoring and Maintenance

### View Backend Logs

```bash
gcloud run services logs read aviato-backend \
  --region us-central1 \
  --limit 50
```

### View Frontend Logs

Check logs in the Vercel dashboard or use:

```bash
vercel logs
```

### Update Backend

```bash
cd backend
gcloud run deploy aviato-backend --source .
```

### Update Frontend

```bash
cd frontend
vercel --prod
```

## Cost Estimation

### Google Cloud Run (Backend)
- **Free tier**: 2 million requests/month, 360,000 GB-seconds
- **After free tier**: ~$0.00002 per request
- **Estimated monthly cost**: $10-50 for moderate usage

### Google Cloud Storage
- **Storage**: $0.020 per GB/month
- **Network egress**: $0.12 per GB
- **Estimated monthly cost**: $5-20 for moderate usage

### Vercel (Frontend)
- **Free tier**: 100 GB bandwidth, unlimited deployments
- **Pro tier**: $20/month (optional, for more bandwidth)

### Total Estimated Monthly Cost
- **Development/Testing**: $0-10 (within free tiers)
- **Production (moderate usage)**: $20-70

## Troubleshooting

### Backend Not Starting

Check logs:
```bash
gcloud run services logs read aviato-backend --region us-central1
```

Common issues:
- Missing secret access permissions
- Invalid GCS bucket name
- Memory/CPU limits too low

### Frontend Can't Connect to Backend

1. Verify CORS settings on Cloud Run
2. Check VITE_API_URL is correct in Vercel
3. Ensure backend is allowing unauthenticated requests
4. Check Cloud Run service is not in error state

### File Upload Failures

1. Verify GCS bucket exists and has correct permissions
2. Check Cloud Run service account has Storage Object Admin role
3. Verify CORS configuration on GCS bucket
4. Check file size limits (default: 100MB)

## Rollback

### Rollback Backend

```bash
# List revisions
gcloud run revisions list --service aviato-backend --region us-central1

# Rollback to specific revision
gcloud run services update-traffic aviato-backend \
  --to-revisions REVISION_NAME=100 \
  --region us-central1
```

### Rollback Frontend

```bash
# List deployments
vercel ls

# Rollback in Vercel dashboard or redeploy a previous commit
git checkout <previous-commit>
vercel --prod
```

## Security Best Practices

1. **Never commit .env files** with real credentials
2. **Use Secret Manager** for sensitive data
3. **Enable VPC** for production backends (optional)
4. **Set up Cloud Armor** for DDoS protection (optional)
5. **Use custom domains** with HTTPS
6. **Enable Cloud Audit Logs** for compliance
7. **Set up budget alerts** in Google Cloud Console

## Next Steps

- Set up custom domain on Vercel
- Configure CDN and caching
- Set up monitoring with Google Cloud Monitoring
- Implement CI/CD with GitHub Actions
- Configure staging environment
