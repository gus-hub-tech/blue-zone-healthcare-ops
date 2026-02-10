# Local Development Guide

Complete guide for setting up and running Blue Zone Healthcare Ops locally.

## Prerequisites

- Python 3.9+
- Node.js 14+
- PostgreSQL 13+ (or Docker)
- Git

---

## Quick Start (5 minutes)

```bash
# 1. Clone repository
git clone <repo-url>
cd blue-zone-healthcare-ops

# 2. Start PostgreSQL
docker run --name local-postgres \
  -e POSTGRES_PASSWORD=devpass \
  -e POSTGRES_DB=audit_logs \
  -e POSTGRES_USER=adminuser \
  -p 5432:5432 -d postgres:15

# 3. Setup backend
cd app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Configure environment
export DATABASE_URL="postgresql://adminuser:devpass@localhost:5432/audit_logs"

# 5. Initialize database
python -c "from database import init_db; init_db()"

# 6. Run backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 7. Run frontend (new terminal)
cd frontend
npm install
npm start
```

**Access:**
- Backend API: http://localhost:8000/docs
- Frontend: http://localhost:3000

---

## Backend Setup

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
cd app
pip install -r requirements.txt
```

### 3. Setup Database

#### Option 1: Docker (Recommended)

```bash
docker run --name local-postgres \
  -e POSTGRES_PASSWORD=devpass \
  -e POSTGRES_DB=audit_logs \
  -e POSTGRES_USER=adminuser \
  -p 5432:5432 -d postgres:15
```

#### Option 2: Local PostgreSQL

```bash
# Access PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE audit_logs;
CREATE USER adminuser WITH PASSWORD 'devpass';
GRANT ALL PRIVILEGES ON DATABASE audit_logs TO adminuser;
\q
```

### 4. Configure Environment

```bash
# Set DATABASE_URL
export DATABASE_URL="postgresql://adminuser:devpass@localhost:5432/audit_logs"

# Or create .env file in app/ directory
cat > app/.env << EOF
DATABASE_URL=postgresql://adminuser:devpass@localhost:5432/audit_logs
DEBUG=True
LOG_LEVEL=INFO
SECRET_KEY=dev-secret-key-change-in-production
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
EOF
```

### 5. Initialize Database

```bash
python -c "from database import init_db; init_db()"
```

### 6. Run Application

```bash
# Development mode (auto-reload)
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure API URL (Optional)

Create `frontend/src/config.js`:

```javascript
export const API_URL = "http://localhost:8000";
```

### 3. Run Development Server

```bash
npm start
```

The frontend will open at http://localhost:3000

### 4. Build for Production

```bash
npm run build
```

---

## Running Tests

### Backend Tests

```bash
# All tests
pytest app/tests -v

# Unit tests only
pytest app/tests/unit -v

# Property-based tests
pytest app/tests/properties -v

# Integration tests
pytest app/tests/integration -v

# With coverage
pytest app/tests --cov=app --cov-report=html

# Specific test file
pytest app/tests/unit/test_patient_service.py -v
```

### Frontend Tests

```bash
cd frontend
npm test
```

---

## Development Workflow

### 1. Start Development Environment

```bash
# Terminal 1: Backend
cd app
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Frontend
cd frontend
npm start

# Terminal 3: Database (if using Docker)
docker start local-postgres
```

### 2. Access Services

- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Frontend**: http://localhost:3000
- **Health Check**: http://localhost:8000/health/

### 3. Database Management

```bash
# Connect to database
psql postgresql://adminuser:devpass@localhost:5432/audit_logs

# View tables
\dt

# Query data
SELECT * FROM patients LIMIT 10;

# Exit
\q
```

---

## Troubleshooting

### Database Connection Errors

**Problem**: App fails to connect to database

**Solution**:
```bash
# Check DATABASE_URL format
export DATABASE_URL="postgresql://user:password@host:5432/dbname"

# URL-encode special characters in password
# < becomes %3C, > becomes %3E, & becomes %26

# Test connection
psql $DATABASE_URL
```

### Import Errors

**Problem**: `ModuleNotFoundError` when running app

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r app/requirements.txt

# Run from project root
python -m uvicorn app.main:app
```

### Port Already in Use

**Problem**: Port 8000 or 3000 already in use

**Solution**:
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

### Frontend Can't Connect to Backend

**Problem**: Frontend shows connection errors

**Solution**:
```bash
# Check backend is running
curl http://localhost:8000/health/

# Update frontend API URL in src/config.js
export const API_URL = "http://localhost:8000";

# Check CORS settings in backend
```

### React Scripts Permission Denied

**Problem**: `npm start` fails with permission error

**Solution**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Database Initialization Fails

**Problem**: `init_db()` fails with errors

**Solution**:
```bash
# Drop and recreate database
psql -U adminuser -d postgres
DROP DATABASE audit_logs;
CREATE DATABASE audit_logs;
\q

# Reinitialize
python -c "from database import init_db; init_db()"
```

---

## Environment Variables

Create `.env` file in `app/` directory:

```bash
# Database
DATABASE_URL=postgresql://adminuser:devpass@localhost:5432/audit_logs

# Application
DEBUG=True
LOG_LEVEL=INFO
SECRET_KEY=dev-secret-key-change-in-production

# Database Pool
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
```

---

## Helper Scripts

### Start Application

```bash
./scripts/start_app.sh
```

### Run Tests

```bash
./scripts/run_tests.sh
```

---

## Next Steps

- Review [API Documentation](http://localhost:8000/docs)
- Check [Application Features](../README.md#application-features)
- Run tests to verify setup
- Start developing!
