# AR Platform Setup Guide

## Prerequisites

- Python 3.9+ (tested with Python 3.13)
- Supabase account (free tier)
- Git
- Text editor (VS Code recommended)

---

## Step 1: Supabase Setup

### 1.1 Create Supabase Project

1. Go to https://supabase.com/dashboard
2. Click "New Project"
3. Fill in:
   - Name: `ar-platform` (or your choice)
   - Database Password: (save this - you'll need it)
   - Region: Choose closest to you
4. Wait 1-2 minutes for project to be created

### 1.2 Get API Credentials

1. In your project dashboard, go to **Settings** > **API**
2. Copy these values:
   - **Project URL** (e.g., `https://xxxxxxxxxxxxx.supabase.co`)
   - **anon/public key** (long JWT token starting with `eyJ...`)

### 1.3 Create Database Tables

1. In your project dashboard, go to **SQL Editor**
2. Click "New Query"
3. Copy the entire contents of `config/db_schema.sql`
4. Paste into the SQL editor
5. Click "Run" or press Ctrl+Enter
6. Verify tables created: Go to **Table Editor** > should see `models`, `clients`, `analytics`

### 1.4 Create Storage Bucket

1. In your project dashboard, go to **Storage**
2. Click "Create Bucket"
3. Name: `ar-models`
4. **IMPORTANT:** Make it **Public**
5. Click "Create Bucket"

---

## Step 2: Local Environment Setup

### 2.1 Clone Repository

```bash
cd /path/to/your/projects
git clone <your-repo-url>
cd ar-viewer
```

### 2.2 Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2.3 Install Dependencies

```bash
pip install -r requirements.txt
```

### 2.4 Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your Supabase credentials:
   ```env
   SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
   SUPABASE_KEY=eyJhbGc...your_long_jwt_token
   STORAGE_BUCKET=ar-models
   BASE_AR_VIEWER_URL=http://localhost:8000/ar_viewer
   ENVIRONMENT=development
   LOG_LEVEL=INFO
   ```

### 2.5 Test Connection

```bash
python scripts/test_connection.py
```

Expected output:
```
============================================================
AR PLATFORM - SUPABASE CONNECTION TEST
============================================================

Testing environment variables...
✅ Environment variables loaded
   - Supabase URL: https://xxx...
   - Storage Bucket: ar-models
   - AR Viewer URL: http://localhost:8000/ar_viewer

Testing Supabase connection...
✅ Supabase client created successfully

Testing database tables...
✅ Table 'models' exists
✅ Table 'clients' exists
✅ Table 'analytics' exists
✅ All required tables exist

Testing storage bucket...
✅ Storage bucket 'ar-models' is accessible
   - Files in bucket: 0

Testing database write operation...
✅ Database write operation successful
   - Test client created/updated: TEST_CLIENT

============================================================
RESULTS: 5/5 tests passed
============================================================
✅ All tests passed! Your Supabase setup is ready.
```

---

## Step 3: Get Test GLB Files

### Option 1: Download Free Models (Recommended)

1. Go to https://sketchfab.com/
2. Search for "food 3D models" with filter "Downloadable"
3. Download 3-5 models in GLB format
4. Place in `models/` directory

### Option 2: Use Sample Models

```bash
# Create a models directory
mkdir -p models

# Download sample burger model (example)
curl -L "https://github.com/KhronosGroup/glTF-Sample-Models/raw/master/2.0/Burger/glTF-Binary/Burger.glb" -o models/burger.glb
```

---

## Step 4: Verify Installation

Run the complete setup verification:

```bash
# Test Supabase connection
python scripts/test_connection.py

# Upload a test model (after Task 1.3 is complete)
python scripts/upload_model.py

# Generate QR code (after Task 2.1 is complete)
python scripts/generate_qr.py
```

---

## Troubleshooting

### "getaddrinfo failed" error
- Check your internet connection
- Verify Supabase URL is correct
- Ensure Supabase project is not paused

### "Table 'models' not found"
- Run `config/db_schema.sql` in Supabase SQL Editor
- Verify tables exist in Table Editor

### "Storage bucket not found"
- Create `ar-models` bucket in Supabase Storage
- Make sure it's set to **Public**

### Import errors
- Activate virtual environment: `venv\Scripts\activate`
- Reinstall dependencies: `pip install -r requirements.txt`

---

## Next Steps

After successful setup:
1. Upload test models (Module 5)
2. Generate QR codes (Module 6)
3. Deploy AR viewer to Vercel
4. Test on mobile devices

---

## Support

For issues:
1. Check Supabase dashboard for error logs
2. Check `logs/` directory for application logs
3. Review documentation in `docs/`
4. Contact: muhammad.ali@codecelix.com
