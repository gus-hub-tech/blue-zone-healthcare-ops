# Local Development Guide

Complete guide for setting up and running Blue Zone Healthcare Ops locally.

## Prerequisites

- Python 3.9+
- Node.js 14+
- Docker (for PostgreSQL)
- Git

### Check Prerequisites

```bash
# Check Docker
docker --version
# Expected: Docker version 20.x.x or higher

# Check Python
python3 --version
# Expected: Python 3.9.x or higher

# Check Node.js (optional, for frontend)
node --version
# Expected: v14.x.x or higher
```

**If Docker is not installed:**
- Ubuntu/Debian: `sudo apt install docker.io && sudo systemctl start docker`
- macOS: Download from https://www.docker.com/products/docker-desktop

**If Python is not installed:**
- Ubuntu/Debian: `sudo apt install python3 python3-pip python3-venv`
- macOS: `brew install python3`

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

## Detailed Backend Setup (Step-by-Step)

### Step 1: Navigate to Project Directory

```bash
cd /path/to/blue-zone-healthcare-ops
pwd
# Expected output: /path/to/blue-zone-healthcare-ops
```

### Step 2: Setup PostgreSQL Database with Docker

#### 2.1 Check if container already exists

```bash
docker ps -a | grep local-postgres
```

**If you see output:** Container exists, skip to step 2.3

**If no output:** Continue to step 2.2

#### 2.2 Create and start PostgreSQL container

```bash
docker run --name local-postgres \
  -e POSTGRES_PASSWORD=devpass \
  -e POSTGRES_DB=audit_logs \
  -e POSTGRES_USER=adminuser \
  -p 5432:5432 \
  -d postgres:15
```

**Expected output:** A long container ID like `a1b2c3d4e5f6...`

**What this does:**
- `--name local-postgres` - Names the container
- `-e POSTGRES_PASSWORD=devpass` - Sets password
- `-e POSTGRES_DB=audit_logs` - Creates database
- `-e POSTGRES_USER=adminuser` - Creates user
- `-p 5432:5432` - Maps port 5432
- `-d` - Runs in background
- `postgres:15` - Uses PostgreSQL version 15

#### 2.3 Verify container is running

```bash
docker ps | grep local-postgres
```

**Expected output:**
```
CONTAINER ID   IMAGE         STATUS         PORTS                    NAMES
a1b2c3d4e5f6   postgres:15   Up 2 seconds   0.0.0.0:5432->5432/tcp   local-postgres
```

**If container is not running:**
```bash
docker start local-postgres
docker ps | grep local-postgres
```

#### 2.4 Test database connection

```bash
docker exec -it local-postgres psql -U adminuser -d audit_logs -c "SELECT version();"
```

**Expected output:** PostgreSQL version information

**If error:** Wait 5 seconds and try again (database might still be starting)

### Step 3: Setup Python Virtual Environment

#### 3.1 Navigate to app directory

```bash
cd app
pwd
# Expected output: /path/to/blue-zone-healthcare-ops/app
```

#### 3.2 Create virtual environment

```bash
python3 -m venv venv
```

**Expected output:** No output (silent success)

**Verify it was created:**
```bash
ls -la venv
# Expected: You should see bin/, lib/, include/ directories
```

#### 3.3 Activate virtual environment

```bash
source venv/bin/activate
# Windows: venv\Scripts\activate
```

**Expected output:** Your prompt should change to show `(venv)` at the beginning:
```
(venv) user@computer:~/blue-zone-healthcare-ops/app$
```

#### 3.4 Verify virtual environment is active

```bash
which python
# Expected output: /path/to/blue-zone-healthcare-ops/app/venv/bin/python
```

### Step 4: Install Python Dependencies

#### 4.1 Install all required packages

```bash
pip install -r requirements.txt
```

**Expected output:** Lots of installation messages, ending with:
```
Successfully installed fastapi-0.104.1 uvicorn-0.24.0 sqlalchemy-2.0.23 ...
```

**This will take 1-2 minutes**

#### 4.2 Verify installations

```bash
pip list | grep -E "fastapi|uvicorn|sqlalchemy"
```

**Expected output:**
```
fastapi          0.104.1
sqlalchemy       2.0.23
uvicorn          0.24.0
```

### Step 5: Configure Database Connection

#### 5.1 Set DATABASE_URL environment variable

```bash
export DATABASE_URL="postgresql://adminuser:devpass@localhost:5432/audit_logs"
```

**Expected output:** No output (silent success)

#### 5.2 Verify environment variable is set

```bash
echo $DATABASE_URL
# Expected output: postgresql://adminuser:devpass@localhost:5432/audit_logs
```

#### 5.3 Create .env file (recommended)

```bash
cat > .env << 'EOF'
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

**Expected output:** No output (silent success)

#### 5.4 Verify .env file was created

```bash
cat .env
# Expected output: The contents of the .env file
```

### Step 6: Initialize Database Tables

#### 6.1 Run database initialization

```bash
python -c "from database import init_db; init_db()"
```

**Expected output:**
```
Creating all database tables...
Database initialized successfully!
```

**If you see errors:** Check that:
- Virtual environment is activated (you see `(venv)`)
- DATABASE_URL is set correctly
- PostgreSQL container is running

#### 6.2 Verify tables were created

```bash
docker exec -it local-postgres psql -U adminuser -d audit_logs -c "\dt"
```

**Expected output:** List of tables like:
```
                List of relations
 Schema |        Name         | Type  |   Owner
--------+---------------------+-------+-----------
 public | appointments        | table | adminuser
 public | patients            | table | adminuser
 public | staff               | table | adminuser
 ...
```

### Step 7: Run the Backend Application

#### 7.1 Start the FastAPI server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected output:**
```
INFO:     Will watch for changes in these directories: ['/path/to/app']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Keep this terminal open! The server is now running.**

### Step 8: Test the Application

#### 8.1 Open a NEW terminal (keep the server running)

Press `Ctrl+Shift+T` or open a new terminal window

#### 8.2 Test health endpoint

```bash
curl http://localhost:8000/health/
```

**Expected output:**
```json
{"status":"healthy"}
```

#### 8.3 Test database health endpoint

```bash
curl http://localhost:8000/health/db
```

**Expected output:**
```json
{"status":"healthy","database":"connected"}
```

#### 8.4 Open API documentation in browser

Open your web browser and go to:
```
http://localhost:8000/docs
```

**Expected result:** You should see the Swagger UI with all API endpoints

### Step 9: Verify Everything is Working

```bash
# Check Docker container
docker ps | grep local-postgres

# Check if port 8000 is in use (backend)
lsof -i :8000

# Check if port 5432 is in use (database)
lsof -i :5432
```

**All commands should show output**

### SUCCESS! 🎉

Your local development environment is now running!

**What's Running:**
- ✅ PostgreSQL database on port 5432 (Docker)
- ✅ FastAPI backend on port 8000
- ✅ All database tables created
- ✅ API documentation at http://localhost:8000/docs

### To Stop Everything:

```bash
# Stop backend (in the terminal running uvicorn)
Press Ctrl+C

# Stop database
docker stop local-postgres
```

### To Start Again Later:

```bash
# Start database
docker start local-postgres

# Start backend
cd /path/to/blue-zone-healthcare-ops/app
source venv/bin/activate
export DATABASE_URL="postgresql://adminuser:devpass@localhost:5432/audit_logs"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
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

**Ensure virtual environment is activated and you're in the app directory:**

```bash
cd /path/to/blue-zone-healthcare-ops/app
source venv/bin/activate
```

**Run tests:**

```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/unit -v

# Property-based tests
pytest tests/properties -v

# Integration tests
pytest tests/integration -v

# With coverage
pytest tests/ --cov=app --cov-report=html

# Specific test file
pytest tests/unit/test_patient_service.py -v
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
