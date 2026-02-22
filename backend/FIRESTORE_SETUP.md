# Firestore Setup Guide for Aviato

This guide walks you through setting up Firestore for Aviato's intelligent caching system.

## 📋 Prerequisites

- Google/Gmail account
- Firebase/Google Cloud Console access
- Terminal access for CLI commands

---

## 🚀 Quick Start (5 minutes)

### Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **"Add project"**
3. Enter project name: `aviato` (or `aviato-prod`)
4. **Disable** Google Analytics (not needed)
5. Click **"Create Project"**
6. Wait for project creation (~30 seconds)

### Step 2: Enable Firestore Database

1. In the left sidebar: **Build** → **Firestore Database**
2. Click **"Create database"**
3. **Choose mode**:
   - For production: Select **"Start in production mode"**
   - For testing: Select **"Start in test mode"** (allows all access for 30 days)
4. **Select location** (IMPORTANT: cannot change later):
   - `us-central1 (Iowa)` - Best for US-based users
   - `us-east1 (South Carolina)` - Alternative US location
   - `europe-west1 (Belgium)` - Best for EU users
   - `asia-south1 (Mumbai)` - Best for Asia users
5. Click **"Enable"**
6. Wait for database creation (~1 minute)

### Step 3: Get Project ID

1. Click the **⚙️ gear icon** next to "Project Overview"
2. Select **"Project settings"**
3. Copy the **"Project ID"** (e.g., `aviato-12345`)
   - You'll need this for the `.env` file

---

## 🔑 Authentication Setup

Choose **ONE** of the following methods:

### Method A: Service Account Key (Recommended for Production/Deployment)

**Best for**: Cloud deployments (Vercel, Railway, Cloud Run, etc.)

1. **Generate Service Account Key**:
   - Firebase Console → ⚙️ Settings → **Service accounts** tab
   - Click **"Generate new private key"**
   - Click **"Generate key"** in the popup
   - A JSON file downloads (e.g., `aviato-firebase-adminsdk-xxxxx.json`)

2. **Save the credentials file**:
   ```bash
   # Move to backend directory
   mv ~/Downloads/aviato-firebase-adminsdk-*.json \
      /Users/chandan/myspace/ai-shark/backend/firebase-credentials.json

   # Secure the file (Mac/Linux)
   chmod 600 /Users/chandan/myspace/ai-shark/backend/firebase-credentials.json
   ```

3. **Add to .gitignore** (if not already):
   ```bash
   echo "firebase-credentials.json" >> .gitignore
   ```

4. **Update `.env`**:
   ```bash
   USE_FIRESTORE=true
   GCP_PROJECT_ID=your-actual-project-id  # From Step 3 above
   GOOGLE_APPLICATION_CREDENTIALS=/Users/chandan/myspace/ai-shark/backend/firebase-credentials.json
   ```

### Method B: Application Default Credentials (Recommended for Local Development)

**Best for**: Local development on your machine

1. **Install Google Cloud SDK** (if not installed):
   ```bash
   # Mac (using Homebrew)
   brew install google-cloud-sdk

   # Or download from: https://cloud.google.com/sdk/docs/install
   ```

2. **Authenticate**:
   ```bash
   # Login to your Google account
   gcloud auth application-default login

   # This opens a browser - sign in with the same account used for Firebase
   ```

3. **Set default project**:
   ```bash
   gcloud config set project YOUR_PROJECT_ID

   # Verify it's set correctly
   gcloud config get-value project
   ```

4. **Update `.env`**:
   ```bash
   USE_FIRESTORE=true
   GCP_PROJECT_ID=your-actual-project-id  # From Step 3 above
   # No GOOGLE_APPLICATION_CREDENTIALS needed - uses ADC automatically
   ```

---

## 🔒 Security Rules (Optional but Recommended)

### For Backend-Only Access (No Frontend)

Since Aviato uses Firestore only from the backend, use these rules:

1. Go to **Firestore Database** → **Rules** tab
2. Replace with:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Allow all access - backend only, no public clients
    match /{document=**} {
      allow read, write: if true;
    }
  }
}
```

3. Click **"Publish"**

### For Production (Restrict to Service Account Only)

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Only authenticated backend (service account)
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
```

---

## ✅ Verify Setup

### 1. Check Environment Variables

```bash
cd /Users/chandan/myspace/ai-shark/backend

# View current settings (without exposing secrets)
grep -E "USE_FIRESTORE|GCP_PROJECT_ID|GOOGLE_APPLICATION_CREDENTIALS" .env
```

Expected output:
```
USE_FIRESTORE=true
GCP_PROJECT_ID=aviato-12345
GOOGLE_APPLICATION_CREDENTIALS=/path/to/firebase-credentials.json  # Or blank for ADC
```

### 2. Test Connection

Start your backend:
```bash
cd /Users/chandan/myspace/ai-shark/backend
python -m src.api.main
```

Look for these log messages:
```
✅ Firestore client initialized for project: aviato-12345
🔥 Firestore caching enabled
```

If you see these, you're good! ✅

### 3. Test via API

```bash
# Check cache status for a company (will return "exists: false" if new)
curl "http://localhost:8000/api/v1/cache/status?website=https://example.com"

# Expected response:
# {"exists": false}
```

---

## 📁 Final `.env` Configuration

Here's what your `.env` should look like:

### Option A: Using Service Account Key
```bash
# =============================================================================
# FIRESTORE CONFIGURATION
# =============================================================================

USE_FIRESTORE=true
GCP_PROJECT_ID=aviato-12345  # Replace with YOUR project ID
GOOGLE_APPLICATION_CREDENTIALS=/Users/chandan/myspace/ai-shark/backend/firebase-credentials.json
FIRESTORE_DATABASE_ID=(default)
```

### Option B: Using Application Default Credentials
```bash
# =============================================================================
# FIRESTORE CONFIGURATION
# =============================================================================

USE_FIRESTORE=true
GCP_PROJECT_ID=aviato-12345  # Replace with YOUR project ID
# GOOGLE_APPLICATION_CREDENTIALS not needed - uses gcloud auth
FIRESTORE_DATABASE_ID=(default)
```

---

## 🧪 Testing the Integration

### 1. Upload a Pitch Deck

```bash
# Upload pitch deck
curl -X POST http://localhost:8000/api/v1/documents/pitch-deck \
  -F "file=@/path/to/pitchdeck.pdf"

# Response: {"job_id": "xxx-xxx-xxx"}
```

### 2. Check Firestore Console

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Navigate to **Firestore Database** → **Data**
3. You should see a new collection: `companies`
4. Inside: A document with company data and subcollections

### 3. Run Analysis

```bash
# Run business analysis
curl -X POST http://localhost:8000/api/v1/analysis/run-agents \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "company_name_from_upload",
    "selected_agents": ["business", "market"]
  }'
```

### 4. Check Cache Hit

Run the same analysis again:
```bash
# Second run - should use cache
curl -X POST http://localhost:8000/api/v1/analysis/run-agents \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "company_name_from_upload",
    "selected_agents": ["business", "market"]
  }'
```

Look for in logs:
```
📦 Cache hit: 2 agents
🔄 Need to run: 0 agents
```

---

## 🐛 Troubleshooting

### Error: "Failed to initialize Firestore"

**Cause**: Authentication issue

**Solutions**:
1. Verify `GCP_PROJECT_ID` matches your Firebase project ID
2. Check `GOOGLE_APPLICATION_CREDENTIALS` path is correct
3. Ensure JSON key file has correct permissions (`chmod 600`)
4. For ADC: Run `gcloud auth application-default login` again

### Error: "Permission denied" or "PERMISSION_DENIED"

**Cause**: Firestore security rules too restrictive

**Solutions**:
1. Go to Firestore → Rules
2. Temporarily use permissive rules (see Security Rules section above)
3. Ensure service account has `Cloud Datastore User` role

### Error: "Project not found"

**Cause**: Wrong project ID

**Solutions**:
1. Verify project ID in Firebase Console → Settings
2. Ensure no typos in `.env` file
3. Check `gcloud config get-value project` matches

### System falls back to file-based storage

**Check**:
1. Is `USE_FIRESTORE=true` in `.env`?
2. Are there any error messages in logs?
3. Try setting `USE_FIRESTORE=false`, restart, then `USE_FIRESTORE=true` again

---

## 🌐 Deployment (Production)

### Vercel / Netlify / Railway

1. Upload `firebase-credentials.json` to your deployment platform
2. Set environment variables in platform dashboard:
   ```
   USE_FIRESTORE=true
   GCP_PROJECT_ID=aviato-12345
   GOOGLE_APPLICATION_CREDENTIALS=/path/in/deployment/firebase-credentials.json
   ```

### Google Cloud Run / App Engine

1. No credentials file needed - uses automatic service account
2. Just set:
   ```
   USE_FIRESTORE=true
   GCP_PROJECT_ID=aviato-12345
   ```

### Docker

Add to `Dockerfile`:
```dockerfile
# Copy credentials file
COPY firebase-credentials.json /app/firebase-credentials.json

# Set environment variables
ENV USE_FIRESTORE=true
ENV GCP_PROJECT_ID=aviato-12345
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/firebase-credentials.json
```

---

## 📊 Monitoring Usage

### View Data in Firestore Console

1. Go to **Firestore Database** → **Data**
2. Browse collections:
   - `companies` - All analyzed companies
   - `jobs` - Processing jobs

### Check Usage & Billing

1. Go to **Firestore Database** → **Usage** tab
2. Monitor:
   - Document reads/writes
   - Storage used
   - Network bandwidth

**Free tier limits**:
- 50K reads/day
- 20K writes/day
- 1 GB storage

For Aviato, typical usage:
- 1 company = ~10 writes (initial)
- Cache hit = 4-8 reads (vs 0 LLM calls 🎉)
- 100 companies = ~100MB storage

---

## 🎯 Next Steps

1. ✅ Complete Firestore setup (this guide)
2. 🧪 Test with a sample pitch deck
3. 📊 Monitor cache hit rates in logs
4. 🚀 Deploy to production
5. 💰 Set up billing alerts in GCP Console (recommended)

---

## 📚 Additional Resources

- [Firebase Documentation](https://firebase.google.com/docs/firestore)
- [Firestore Pricing](https://firebase.google.com/pricing)
- [Security Rules Guide](https://firebase.google.com/docs/firestore/security/get-started)
- [Google Cloud SDK](https://cloud.google.com/sdk/docs)

---

## 🆘 Need Help?

- Check the logs: Look for Firestore-related messages
- Test with `USE_FIRESTORE=false` to verify rest of the system works
- Firebase Console → Support → Contact Support
