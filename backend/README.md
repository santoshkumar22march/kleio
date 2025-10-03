# Kleio.ai Backend

FastAPI backend for Kleio.ai - AI-powered household inventory management system.

## 🏗️ Architecture

**Option 1: Firebase Auth + PostgreSQL (Implemented)**

```
Frontend (React) → Firebase Auth → FastAPI (Token Verification) → PostgreSQL (Data)
                                        ↓
                                   Gemini AI (Recipes, Photos)
```

- ✅ Firebase handles ALL authentication (OAuth, passwords, sessions)
- ✅ PostgreSQL stores ALL application data (inventory, patterns, predictions)
- ✅ FastAPI verifies tokens and manages business logic
- ✅ No password storage, no session management in backend
- ✅ Single source of truth for data

**See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed architecture documentation.**

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.11+
- PostgreSQL database (Neon recommended)
- Firebase project with service account key
- Google Gemini API key

### 2. Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate

# Install uv (faster pip alternative)
pip install uv

# Install dependencies
uv pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in the backend directory:

```env
# Database
DATABASE_URL=postgresql://user:pass@host:5432/kleio_db

# Firebase
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_PATH=./serviceAccountKey.json

# Google AI
GEMINI_API_KEY=your_gemini_api_key

# App Settings
ENVIRONMENT=development
DEBUG=True
CORS_ORIGINS=http://localhost:5173
```

### 4. Firebase Setup

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select your project
3. Go to Project Settings → Service Accounts
4. Click "Generate new private key"
5. Save the downloaded JSON file as `serviceAccountKey.json` in the backend directory

### 5. Run the Server

```bash
# Development mode (with auto-reload)
uvicorn main:app --reload --port 8000

# Or using Python
python main.py
```

The API will be available at:
- **API:** http://localhost:8000
- **Docs:** http://localhost:8000/docs (Swagger UI)
- **Health Check:** http://localhost:8000/health

## 📁 Project Structure

```
backend/
├── main.py                 # FastAPI application
├── config.py               # Configuration settings
├── database.py             # Database connection
├── requirements.txt        # Dependencies
├── .env                    # Environment variables (create this)
├── .env.example           # Environment template
├── serviceAccountKey.json # Firebase key (don't commit!)
│
├── models/                # SQLAlchemy models
│   ├── user.py
│   ├── inventory.py
│   └── consumption_log.py
│
├── schemas/               # Pydantic schemas
│   ├── user.py
│   └── inventory.py
│
├── crud/                  # CRUD operations
│   ├── user.py
│   └── inventory.py
│
├── routers/               # API endpoints
│   ├── health.py
│   ├── users.py
│   └── inventory.py
│
└── utils/                 # Utility functions
    └── auth.py            # Firebase authentication
```

## 🔌 API Endpoints

### Health Check
- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed health with DB status

### Users
- `POST /api/users/profile` - Create/update user profile
- `GET /api/users/profile` - Get user profile
- `PATCH /api/users/profile` - Update profile
- `GET /api/users/me` - Get current user info

### Inventory
- `POST /api/inventory/add` - Add single item
- `POST /api/inventory/bulk-add` - Add multiple items
- `GET /api/inventory/list` - List items (with filters)
- `GET /api/inventory/{id}` - Get specific item
- `PATCH /api/inventory/{id}/update` - Update item
- `DELETE /api/inventory/{id}` - Delete item
- `POST /api/inventory/{id}/mark-used` - Mark as consumed
- `GET /api/inventory/categories` - Get categories list
- `GET /api/inventory/units` - Get units list
- `GET /api/inventory/common-items` - Get autocomplete suggestions

## 🔐 Authentication

All protected endpoints require a Firebase ID token in the Authorization header:

```
Authorization: Bearer <firebase_id_token>
```

### Testing with Postman

1. Get a Firebase ID token from your frontend app
2. Add to request headers:
   ```
   Authorization: Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6...
   ```

## 🗄️ Database Models

### Users
```python
firebase_uid          # Primary key
phone_number          # Optional
household_size        # Integer
location_city         # String
language_preference   # en, hi, ta
dietary_preferences   # JSON
region                # north, south, east, west, all
```

### Inventory
```python
id                    # Auto-increment primary key
firebase_uid          # Foreign key to users
item_name             # String
category              # String
quantity              # Decimal
unit                  # String
added_date            # Date
expiry_date           # Date (optional)
status                # active, consumed, expired, discarded
photo_url             # String (optional)
```

### Consumption Log
```python
id                    # Auto-increment primary key
firebase_uid          # Foreign key to users
item_name             # String
quantity_consumed     # Decimal
consumed_date         # Date
added_date            # Date
days_lasted           # Integer (calculated)
```

## 🧪 Testing

```bash
# Install test dependencies (already in requirements.txt)
uv pip install pytest pytest-asyncio httpx

# Run tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```


### Environment Variables for Production

```env
DATABASE_URL=postgresql://...  # From Neon
FIREBASE_PROJECT_ID=...
FIREBASE_PRIVATE_KEY_PATH=./serviceAccountKey.json
GEMINI_API_KEY=...
ENVIRONMENT=production
DEBUG=False
CORS_ORIGINS=https://your-frontend-domain.com
```



### Common Issues

**Import errors:**
```bash
# Make sure you're in the backend directory
cd backend
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux
```

**Database connection fails:**
- Check DATABASE_URL in .env
- Verify PostgreSQL is running
- Test connection: `psql "postgresql://..."`

**Firebase auth fails:**
- Verify serviceAccountKey.json exists
- Check file path in .env
- Ensure Firebase project ID is correct

## 🔧 Next Steps

- [ ] Add AI endpoints (photo detection, recipe generation)
- [ ] Implement shopping list generation
- [ ] Add festival calendar features
- [ ] Set up background jobs for pattern analysis
- [ ] Add comprehensive tests
- [ ] Set up CI/CD pipeline

## 📚 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org)
- [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)
- [Pydantic Validation](https://docs.pydantic.dev)

---


