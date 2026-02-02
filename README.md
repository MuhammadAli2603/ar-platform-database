# 🎯 AR Platform - 3D Model Viewer & QR System

<div align="center">

![AR Platform](https://img.shields.io/badge/AR-Platform-blueviolet?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-Database-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)
![WebXR](https://img.shields.io/badge/WebXR-AR%20Ready-FF6B6B?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**A modern AR platform for viewing 3D models in augmented reality through QR codes**

[Features](#-features) • [Demo](#-demo) • [Installation](#-installation) • [Usage](#-usage) • [Documentation](#-documentation)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Demo](#-demo)
- [Technology Stack](#-technology-stack)
- [Database Schema](#-database-schema)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Reference](#-api-reference)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)

---

## 🌟 Overview

AR Platform is a full-stack web application that enables users to view 3D models in augmented reality through QR codes. Built for restaurants, retail stores, museums, and any business wanting to showcase products in AR, it provides a seamless experience from model upload to AR visualization.

### Key Highlights

- 📱 **Mobile-First AR Experience** - View 3D models in your physical space using your phone camera
- 🔄 **Automated QR Generation** - Instantly create QR codes for any uploaded model
- 📊 **Analytics Dashboard** - Track views, AR activations, and user engagement
- ☁️ **Cloud Storage** - Secure model hosting with Supabase Storage
- 🎨 **Modern UI** - Responsive design that works on any device
- 🚀 **Production Ready** - Deploy to Vercel with HTTPS support

---

## ✨ Features

### Core Functionality

| Feature | Description | Status |
|---------|-------------|--------|
| 🎭 **3D Model Upload** | Support for GLB/GLTF files up to 5MB | ✅ Complete |
| 📸 **QR Code Generation** | High-quality QR codes with custom branding | ✅ Complete |
| 🥽 **AR Viewer** | WebXR-based AR experience (iOS & Android) | ✅ Complete |
| 📊 **Analytics** | Real-time tracking of views and interactions | ✅ Complete |
| 🔐 **Row Level Security** | Secure multi-tenant data isolation | ✅ Complete |
| 🔄 **Batch Upload** | Upload multiple models at once | ✅ Complete |

### Technical Features

- ✅ File validation with magic byte verification
- ✅ Automatic retry with exponential backoff
- ✅ Rollback on failure (transactional uploads)
- ✅ CORS-enabled storage for cross-origin access
- ✅ Responsive design (320px - 1920px+)
- ✅ Progressive Web App (PWA) ready
- ✅ SEO optimized with meta tags

---

## 🎬 Demo

### QR Code → AR Experience

```
1. Upload Model     2. Generate QR      3. Scan with Phone    4. View in AR
   [duck.glb]    →    [QR Code]      →    [📱 Camera]      →   [🦆 in Space]
```

### Live Example

**Try it yourself:**
1. Scan this QR code with your phone
2. Wait for the 3D model to load
3. Tap "View in Your Space"
4. Point your camera at a flat surface
5. See the model in augmented reality!

---

## 🛠️ Technology Stack

### Backend

| Technology | Purpose | Version |
|------------|---------|---------|
| **Python** | Core backend logic | 3.11+ |
| **Supabase** | Database & storage | Latest |
| **PostgreSQL** | Relational database | 14+ |
| **python-dotenv** | Environment management | 1.0+ |

### Frontend

| Technology | Purpose | Version |
|------------|---------|---------|
| **HTML5** | Structure | - |
| **CSS3** | Styling | - |
| **JavaScript (ES6+)** | Interactivity | - |
| **Model-Viewer** | 3D rendering | 3.3.0 |
| **WebXR** | AR capabilities | - |

### DevOps & Tools

| Tool | Purpose |
|------|---------|
| **Vercel** | Frontend hosting |
| **Git** | Version control |
| **QRCode** | QR generation |
| **Pillow** | Image processing |

---

## 🗄️ Database Schema

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     AR PLATFORM DATABASE                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐         ┌──────────┐         ┌──────────┐   │
│  │ CLIENTS  │────────>│  MODELS  │<────────│ ANALYTICS│   │
│  └──────────┘         └──────────┘         └──────────┘   │
│       │                    │                     │          │
│       │                    │                     │          │
│   client_id            model_id             event_type     │
│   company_name         product_name         timestamp      │
│   contact_info         public_url           device_type    │
│                        category                             │
│                        price                                │
└─────────────────────────────────────────────────────────────┘
```

### Entity Relationship Diagram

```sql
clients (1) ─────< (N) models
models (1) ─────< (N) analytics
```

---

## 📊 Table Descriptions

### 1. `clients` Table

Stores information about businesses/organizations using the platform.

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| `client_id` | VARCHAR(50) | Unique client identifier | PRIMARY KEY |
| `company_name` | VARCHAR(255) | Business name | NOT NULL |
| `contact_email` | VARCHAR(255) | Contact email | UNIQUE |
| `contact_phone` | VARCHAR(20) | Contact number | - |
| `website_url` | TEXT | Company website | - |
| `address` | TEXT | Physical address | - |
| `is_active` | BOOLEAN | Active status | DEFAULT true |
| `subscription_tier` | VARCHAR(50) | Plan tier | DEFAULT 'free' |
| `created_at` | TIMESTAMPTZ | Creation time | DEFAULT NOW() |
| `updated_at` | TIMESTAMPTZ | Last update | DEFAULT NOW() |

**Example:**
```sql
INSERT INTO clients (client_id, company_name, contact_email)
VALUES ('REST_001', 'Downtown Cafe', 'contact@downtown.cafe');
```

### 2. `models` Table

Stores 3D model metadata and references to storage.

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| `id` | BIGSERIAL | Auto-increment ID | PRIMARY KEY |
| `model_id` | VARCHAR(100) | Unique model code | UNIQUE, NOT NULL |
| `product_name` | VARCHAR(255) | Display name | NOT NULL |
| `category` | VARCHAR(100) | Product category | NOT NULL |
| `subcategory` | VARCHAR(100) | Subcategory | - |
| `price` | DECIMAL(10,2) | Product price | - |
| `currency` | VARCHAR(3) | Currency code | DEFAULT 'USD' |
| `description` | TEXT | Product details | - |
| `client_id` | VARCHAR(50) | Owner client | FK → clients |
| `public_url` | TEXT | CDN URL | NOT NULL |
| `storage_path` | TEXT | Storage location | NOT NULL |
| `file_size_bytes` | BIGINT | File size | - |
| `file_size_mb` | DECIMAL(10,2) | Size in MB | - |
| `polygon_count` | INTEGER | Mesh complexity | - |
| `texture_resolution` | VARCHAR(50) | Texture size | - |
| `file_format` | VARCHAR(10) | Format (GLB/GLTF) | DEFAULT 'GLB' |
| `tags` | TEXT[] | Search tags | - |
| `is_active` | BOOLEAN | Visible status | DEFAULT true |
| `created_at` | TIMESTAMPTZ | Upload time | DEFAULT NOW() |
| `updated_at` | TIMESTAMPTZ | Last modified | DEFAULT NOW() |
| `uploaded_by` | VARCHAR(100) | Uploader ID | - |

**Example:**
```sql
INSERT INTO models (model_id, product_name, category, client_id, public_url, storage_path)
VALUES (
    'BURGER_001',
    'Classic Burger',
    'food',
    'REST_001',
    'https://cdn.example.com/models/burger.glb',
    'food/burger.glb'
);
```

### 3. `analytics` Table

Tracks user interactions and engagement metrics.

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| `id` | BIGSERIAL | Auto-increment ID | PRIMARY KEY |
| `model_id` | VARCHAR(100) | Related model | FK → models |
| `event_type` | VARCHAR(50) | Event category | NOT NULL |
| `event_timestamp` | TIMESTAMPTZ | When occurred | DEFAULT NOW() |
| `user_agent` | TEXT | Browser info | - |
| `device_type` | VARCHAR(50) | Device category | - |
| `os_name` | VARCHAR(50) | Operating system | - |
| `browser_name` | VARCHAR(50) | Browser name | - |
| `ip_address` | VARCHAR(45) | User IP | - |
| `country` | VARCHAR(100) | Geographic location | - |
| `session_id` | VARCHAR(100) | Session identifier | - |
| `referrer_url` | TEXT | Traffic source | - |

**Event Types:**
- `qr_scanned` - QR code was scanned
- `view` - Model page was viewed
- `ar_activated` - AR mode was launched
- `ar_placement` - Model placed in space
- `screenshot` - AR screenshot taken
- `share` - Model link shared

**Example:**
```sql
INSERT INTO analytics (model_id, event_type, device_type, os_name)
VALUES ('BURGER_001', 'ar_activated', 'mobile', 'iOS');
```

---

## 🚀 Installation

### Prerequisites

- Python 3.11 or higher
- Node.js 18+ (for Vercel deployment)
- Supabase account (free tier works)
- Git

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/ar-platform.git
cd ar-platform
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt:**
```txt
supabase==2.5.0
python-dotenv==1.0.0
qrcode[pil]==7.4.2
Pillow==10.2.0
```

### 3. Set Up Supabase

#### Create a New Project

1. Go to [supabase.com](https://supabase.com)
2. Click "New Project"
3. Fill in project details
4. Wait for setup to complete (~2 minutes)

#### Create Database Tables

1. Open SQL Editor in Supabase Dashboard
2. Copy and paste `config/db_schema.sql`
3. Click "Run" to execute

#### Create Storage Bucket

1. Go to Storage section
2. Create new bucket: `ar-models`
3. Set as **Public bucket**
4. Disable RLS (or configure policies)

### 4. Configure Environment

Create `.env` file in project root:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# Storage Configuration
STORAGE_BUCKET=ar-models

# AR Viewer Base URL
BASE_AR_VIEWER_URL=http://localhost:8000/ar_viewer

# Environment
ENVIRONMENT=development

# Logging
LOG_LEVEL=INFO
```

**Get your keys from:**
- Supabase Dashboard → Settings → API
- Copy `anon` key and `service_role` key

### 5. Test Connection

```bash
python scripts/test_connection.py
```

Expected output:
```
✅ Environment variables loaded
✅ Supabase client created successfully
✅ All required tables exist
✅ Storage bucket 'ar-models' is accessible
✅ Database write operation successful
```

---

## 📖 Usage

### Upload a 3D Model

#### Single Upload

```bash
python scripts/upload_model.py \
  models/burger.glb \
  BURGER_001 \
  "Classic Burger" \
  food \
  RESTAURANT_001 \
  --price 8.99 \
  --description "Delicious beef burger with cheese"
```

**Output:**
```
✅ SUCCESS!
Model ID: BURGER_001
Public URL: https://your-project.supabase.co/storage/v1/object/public/ar-models/food/burger.glb
File Size: 2.3MB
Upload Time: 3.2s
```

#### Batch Upload

Create `metadata.json`:
```json
[
  {
    "filename": "burger.glb",
    "model_id": "BURGER_001",
    "product_name": "Classic Burger",
    "category": "food",
    "price": 8.99,
    "client_id": "REST_001"
  },
  {
    "filename": "pizza.glb",
    "model_id": "PIZZA_001",
    "product_name": "Margherita Pizza",
    "category": "food",
    "price": 12.99,
    "client_id": "REST_001"
  }
]
```

Run batch upload:
```bash
python scripts/batch_upload.py \
  --dir models/ \
  --metadata models/metadata.json
```

### Generate QR Code

```bash
python scripts/generate_qr.py BURGER_001
```

**Output:**
```
✅ QR code generated: qr_codes/BURGER_001_qr.png
URL: http://localhost:8000/ar_viewer/?model=BURGER_001
```

**With custom URL:**
```bash
python scripts/generate_qr.py BURGER_001 \
  --base-url https://your-domain.vercel.app
```

### Start Local Server

```bash
python start_server.py
```

Opens browser at: `http://localhost:8000/ar_viewer/?model=BURGER_001`

### Deploy to Production

```bash
cd ar_viewer/
vercel deploy --prod
```

**Then regenerate QR with production URL:**
```bash
python scripts/generate_qr.py BURGER_001 \
  --base-url https://your-domain.vercel.app
```

---

## 🔌 API Reference

### Database Queries

#### Fetch Model by ID

```python
from config import get_supabase_client

client = get_supabase_client()
result = client.table('models').select('*').eq('model_id', 'BURGER_001').execute()
model = result.data[0]

print(f"Product: {model['product_name']}")
print(f"Price: ${model['price']}")
print(f"URL: {model['public_url']}")
```

#### Get Analytics for Model

```python
result = client.table('analytics') \
    .select('*') \
    .eq('model_id', 'BURGER_001') \
    .order('event_timestamp', desc=True) \
    .limit(100) \
    .execute()

for event in result.data:
    print(f"{event['event_type']} - {event['device_type']} - {event['event_timestamp']}")
```

#### Get Client's Models

```python
result = client.table('models') \
    .select('*') \
    .eq('client_id', 'REST_001') \
    .eq('is_active', True) \
    .execute()

print(f"Total models: {len(result.data)}")
```

### REST API (Supabase)

#### Get Model

```bash
curl https://your-project.supabase.co/rest/v1/models?model_id=eq.BURGER_001 \
  -H "apikey: YOUR_ANON_KEY" \
  -H "Authorization: Bearer YOUR_ANON_KEY"
```

#### Track Analytics

```bash
curl -X POST https://your-project.supabase.co/rest/v1/analytics \
  -H "apikey: YOUR_ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "BURGER_001",
    "event_type": "view",
    "device_type": "mobile",
    "os_name": "iOS"
  }'
```

---

## 📁 Project Structure

```
ar-platform/
├── 📂 ar_viewer/              # Frontend AR viewer
│   ├── index.html             # Main AR viewer page
│   ├── fetch_models.js        # Model loading logic
│   ├── styles.css             # Responsive styles
│   └── vercel.json            # Deployment config
│
├── 📂 config/                 # Configuration files
│   ├── __init__.py            # Config management
│   └── db_schema.sql          # Database schema
│
├── 📂 scripts/                # Python scripts
│   ├── upload_model.py        # Single upload
│   ├── batch_upload.py        # Batch upload
│   ├── generate_qr.py         # QR generation
│   ├── validate_glb.py        # File validation
│   └── test_connection.py     # Connection test
│
├── 📂 models/                 # 3D models storage
│   ├── burger.glb
│   ├── pizza.glb
│   └── metadata_template.json
│
├── 📂 qr_codes/               # Generated QR codes
│   ├── BURGER_001_qr.png
│   └── PIZZA_001_qr.png
│
├── 📂 tests/                  # Unit tests
│   └── test_validator.py
│
├── 📂 docs/                   # Documentation
│   ├── SETUP.md
│   └── API.md
│
├── .env                       # Environment variables (git-ignored)
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
├── requirements.txt           # Python dependencies
├── start_server.py            # Local dev server
└── README.md                  # This file
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

### Development Workflow

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/ar-platform.git
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make your changes**
   - Write clean, documented code
   - Follow PEP 8 style guide
   - Add tests for new features

4. **Test your changes**
   ```bash
   pytest tests/ -v
   python scripts/test_connection.py
   ```

5. **Commit with clear messages**
   ```bash
   git commit -m "Add: Amazing new feature"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```

7. **Open a Pull Request**
   - Describe your changes
   - Reference any related issues
   - Wait for review

### Code Style

- **Python:** Follow PEP 8
- **JavaScript:** Use ES6+ features
- **SQL:** Uppercase keywords, snake_case names
- **Comments:** Explain "why", not "what"

### Commit Message Format

```
Type: Brief description

- Detailed point 1
- Detailed point 2

Fixes #123
```

**Types:** `Add`, `Fix`, `Update`, `Remove`, `Refactor`, `Docs`

---

## 🐛 Troubleshooting

### Common Issues

#### Upload fails with "403 Unauthorized"

**Solution:** Add Service Role Key to `.env`

```bash
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

#### Model not loading in AR viewer

**Checklist:**
- ✅ Model uploaded successfully?
- ✅ Public URL accessible?
- ✅ Using HTTPS (required for AR)?
- ✅ Browser supports WebXR?

#### QR code doesn't work on mobile

**Solution:** Deploy to production (HTTPS required)
```bash
vercel deploy --prod
```

#### Database connection fails

**Check:**
1. Supabase credentials in `.env`
2. Project is not paused (free tier)
3. Tables exist (run `db_schema.sql`)

---

## 📝 License

This project is licensed under the MIT License - see below for details.

```
MIT License

Copyright (c) 2026 AR Platform Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 Acknowledgments

### Technologies

- **[Model-Viewer](https://modelviewer.dev/)** - Google's web component for 3D models
- **[Supabase](https://supabase.com)** - Open-source Firebase alternative
- **[Vercel](https://vercel.com)** - Frontend deployment platform
- **[Python](https://python.org)** - Programming language

### Inspiration

This project was inspired by the need for accessible AR experiences in retail and hospitality. Special thanks to the open-source community for making AR technology accessible to everyone.

### 3D Models

Sample models sourced from:
- [Khronos glTF Sample Models](https://github.com/KhronosGroup/glTF-Sample-Models)
- [Sketchfab](https://sketchfab.com/) (CC-licensed models)

---

## 📞 Support

### Get Help

- 🐛 [Report a Bug](https://github.com/yourusername/ar-platform/issues)
- 💡 [Request a Feature](https://github.com/yourusername/ar-platform/issues)
- 💬 [Join Discussions](https://github.com/yourusername/ar-platform/discussions)

### FAQ

**Q: Does this work on iOS?**
A: Yes! iOS 12+ supports AR Quick Look for viewing models in AR.

**Q: What file formats are supported?**
A: GLB (recommended) and GLTF with embedded assets.

**Q: Can I use this commercially?**
A: Yes, under MIT License. Modify and use freely.

**Q: What's the model size limit?**
A: 5MB by default (configurable in `config/__init__.py`).

**Q: Is there a hosting cost?**
A: Supabase and Vercel free tiers should cover small projects.

---

## 🗺️ Roadmap

### Version 2.0 (Planned)

- [ ] Admin dashboard with analytics
- [ ] Multi-language support
- [ ] Custom branding per client
- [ ] Video texture support
- [ ] Animation playback
- [ ] Social sharing features
- [ ] Offline model caching
- [ ] Payment integration
- [ ] White-label solution

### Version 3.0 (Future)

- [ ] AR Cloud anchors
- [ ] Multi-user AR experiences
- [ ] AI-powered model optimization
- [ ] Voice commands in AR
- [ ] Gesture recognition

---

<div align="center">

**Made with ❤️ and Python**

*A personal project exploring AR technology and web development*

[⬆ Back to Top](#-ar-platform---3d-model-viewer--qr-system)

</div>
