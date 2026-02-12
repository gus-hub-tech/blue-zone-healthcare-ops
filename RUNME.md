# Getting Started with Blue Zone Healthcare Ops

Complete guide to run and start the Blue Zone Healthcare Ops application.

## Installation & Setup

### Step 1: Get the Code

```bash
# Navigate to where you want the project
cd ~/Projects

# If you already have the code
cd blue-zone-healthcare-ops

# If cloning from Git
git clone <repository-url>
cd blue-zone-healthcare-ops
```

### Step 2: Start the Database

**What this does:** Creates a PostgreSQL database in a Docker container that stores all application data.

```bash
# Create and start PostgreSQL container
docker run --name local-postgres \
  -e POSTGRES_PASSWORD=devpass \
  -e POSTGRES_DB=audit_logs \
  -e POSTGRES_USER=adminuser \
  -p 5432:5432 \
  -d postgres:15
```

**Explanation:**
- `--name local-postgres` - Names the container for easy reference
- `-e POSTGRES_PASSWORD=devpass` - Sets the database password
- `-e POSTGRES_DB=audit_logs` - Creates a database named "audit_logs"
- `-e POSTGRES_USER=adminuser` - Creates a user named "adminuser"
- `-p 5432:5432` - Makes database accessible on port 5432
- `-d` - Runs in background (detached mode)
- `postgres:15` - Uses PostgreSQL version 15

**Verify it's running:**
```bash
docker ps | grep local-postgres
# You should see: local-postgres   postgres:15   Up X seconds
```

**If container already exists:**
```bash
docker start local-postgres
```

### Step 3: Setup Python Backend

**What this does:** Creates an isolated Python environment and installs all required packages.

```bash
# Navigate to app directory
cd app

# Create virtual environment (isolated Python installation)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
# Your prompt should now show: (venv)

# Install all Python packages
pip install -r requirements.txt
# This takes 1-2 minutes
```

**Explanation:**
- `venv` - Virtual environment keeps project dependencies isolated
- `source venv/bin/activate` - Activates the environment
- `pip install -r requirements.txt` - Installs FastAPI, SQLAlchemy, and other packages

**Verify installation:**
```bash
pip list | grep fastapi
# You should see: fastapi  0.104.1
```

### Step 4: Configure Database Connection

**What this does:** Tells the application how to connect to the database.

```bash
# Set environment variable (temporary - for this session only)
export DATABASE_URL="postgresql://adminuser:devpass@localhost:5432/audit_logs"

# Create .env file (permanent - survives restarts)
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

**Explanation:**
- `DATABASE_URL` - Connection string with username, password, host, port, and database name
- `.env` file - Stores configuration that persists between sessions
- `DEBUG=True` - Enables detailed error messages for development

**Verify configuration:**
```bash
echo $DATABASE_URL
# Should show: postgresql://adminuser:devpass@localhost:5432/audit_logs
```

### Step 5: Initialize Database Tables

**What this does:** Creates all the tables (patients, appointments, staff, etc.) in the database.

```bash
python -c "from database import init_db; init_db()"
```

**Expected output:**
```
Creating all database tables...
Database initialized successfully!
```

**Verify tables were created:**
```bash
docker exec -it local-postgres psql -U adminuser -d audit_logs -c "\dt"
```

**You should see tables like:**
- patients
- appointments
- medical_records
- staff
- prescriptions
- billing_records
- inventory_items
- departments

---

## Running the Application

### Start the Backend API

**What this does:** Starts the FastAPI web server that handles all API requests.

```bash
# Make sure you're in the app directory with venv activated
cd app
source venv/bin/activate

# Start the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Application startup complete.
```

**Explanation:**
- `uvicorn` - ASGI web server for Python
- `main:app` - Runs the `app` object from `main.py`
- `--host 0.0.0.0` - Makes server accessible from any network interface
- `--port 8000` - Runs on port 8000
- `--reload` - Auto-restarts when code changes (development mode)

**Keep this terminal open!** The server must stay running.

### Start the Frontend (Optional)

**What this does:** Starts the React web interface for the application.

**Open a NEW terminal** (keep backend running):

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js packages (first time only)
npm install

# Start development server
npm start
```

**Expected output:**
```
Compiled successfully!

You can now view hospital-management-frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.1.x:3000
```

**Your browser should automatically open to http://localhost:3000**

---

## Using the Application

### Access Points

Once running, you can access:

| Service | URL | Purpose |
|---------|-----|---------|
| **API Documentation** | http://localhost:8000/docs | Interactive API testing (Swagger UI) |
| **API Alternative Docs** | http://localhost:8000/redoc | Alternative API documentation |
| **Frontend** | http://localhost:3000 | Web interface (if running) |
| **Health Check** | http://localhost:8000/health/ | Verify backend is running |
| **Database Health** | http://localhost:8000/health/db | Verify database connection |

### Testing the API

**1. Open API Documentation:**
```
http://localhost:8000/docs
```

**2. Test Health Endpoint:**
```bash
curl http://localhost:8000/health/
# Response: {"status":"healthy"}
```

**3. Create a Patient (Example):**

Using curl:
```bash
curl -X POST http://localhost:8000/patients \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "date_of_birth": "1990-01-15",
    "contact_info": "john.doe@email.com",
    "insurance_id": "INS123456"
  }'
```

Using the Swagger UI:
1. Go to http://localhost:8000/docs
2. Click on `POST /patients`
3. Click "Try it out"
4. Fill in the patient data
5. Click "Execute"

**4. Retrieve the Patient:**
```bash
curl http://localhost:8000/patients/1
```

### Available API Endpoints

**Patients:**
- `POST /patients` - Register new patient
- `GET /patients/{id}` - Get patient details
- `PUT /patients/{id}` - Update patient
- `GET /patients` - List all patients

**Appointments:**
- `POST /appointments` - Schedule appointment
- `GET /appointments/{id}` - Get appointment details
- `DELETE /appointments/{id}` - Cancel appointment

**Medical Records:**
- `GET /medical-records/patient/{id}` - Get patient's medical record
- `POST /medical-records/patient/{id}/diagnoses` - Add diagnosis
- `POST /medical-records/patient/{id}/treatments` - Add treatment

**Staff:**
- `POST /staff` - Add staff member
- `GET /staff/{id}` - Get staff details
- `PUT /staff/{id}` - Update staff

**Prescriptions:**
- `POST /prescriptions` - Create prescription
- `GET /prescriptions/{id}` - Get prescription details

**Billing:**
- `POST /billing` - Create billing record
- `POST /billing/payments` - Process payment
- `GET /billing/patient/{id}/balance` - Get patient balance

**Inventory:**
- `POST /inventory` - Add inventory item
- `GET /inventory/low-stock` - Get low stock items
- `GET /inventory/expired` - Get expired items

**Departments:**
- `POST /departments` - Create department
- `GET /departments/{id}` - Get department details
- `GET /departments/{id}/staff` - Get department staff

---

## Stopping the Application

### Stop Backend
In the terminal running uvicorn:
```bash
Press Ctrl+C
```

### Stop Frontend
In the terminal running npm:
```bash
Press Ctrl+C
```

### Stop Database
```bash
docker stop local-postgres
```

### Stop Everything
```bash
# Stop all running processes (Ctrl+C in each terminal)
# Then stop database
docker stop local-postgres
```

**Note:** Stopping the database does NOT delete your data. It's preserved in the Docker container.

---

## Daily Development Workflow

### Starting Your Day

```bash
# 1. Start database (if not running)
docker start local-postgres

# 2. Navigate to project
cd ~/Projects/blue-zone-healthcare-ops/app

# 3. Activate virtual environment
source venv/bin/activate

# 4. Set database URL (if not using .env file)
export DATABASE_URL="postgresql://adminuser:devpass@localhost:5432/audit_logs"

# 5. Start backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 6. (Optional) Start frontend in new terminal
cd ../frontend
npm start
```

### During Development

**Backend changes:**
- Edit Python files in `app/`
- Server auto-reloads (because of `--reload` flag)
- Check terminal for errors

**Frontend changes:**
- Edit React files in `frontend/src/`
- Browser auto-refreshes
- Check browser console for errors

**Database changes:**
- Connect: `docker exec -it local-postgres psql -U adminuser -d audit_logs`
- View tables: `\dt`
- Query data: `SELECT * FROM patients;`
- Exit: `\q`

### Ending Your Day

```bash
# 1. Stop backend (Ctrl+C in backend terminal)
# 2. Stop frontend (Ctrl+C in frontend terminal)
# 3. Stop database (optional - can leave running)
docker stop local-postgres
```

---

## Common Issues & Solutions

### Issue 1: "Port 5432 already in use"

**Problem:** Another PostgreSQL instance is running

**Solution:**
```bash
# Find what's using port 5432
sudo lsof -i :5432

# If it's another Docker container
docker ps -a | grep postgres
docker stop <container-name>

# If it's a system PostgreSQL
sudo systemctl stop postgresql
```

### Issue 2: "Port 8000 already in use"

**Problem:** Backend is already running or another app is using port 8000

**Solution:**
```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### Issue 3: "ModuleNotFoundError"

**Problem:** Virtual environment not activated or packages not installed

**Solution:**
```bash
# Activate virtual environment
cd app
source venv/bin/activate

# Reinstall packages
pip install -r requirements.txt
```

### Issue 4: "Database connection failed"

**Problem:** Database not running or wrong connection string

**Solution:**
```bash
# Check if database is running
docker ps | grep local-postgres

# Start if not running
docker start local-postgres

# Verify connection string
echo $DATABASE_URL

# Test connection
docker exec -it local-postgres psql -U adminuser -d audit_logs -c "SELECT 1;"
```

### Issue 5: "No tables found"

**Problem:** Database not initialized

**Solution:**
```bash
cd app
source venv/bin/activate
python -c "from database import init_db; init_db()"
```

### Issue 6: "Frontend won't start"

**Problem:** Node modules not installed or corrupted

**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

### Issue 7: "Permission denied: react-scripts"

**Problem:** React scripts don't have execute permission

**Solution:**
```bash
cd frontend
chmod +x node_modules/.bin/react-scripts
npm start
```

---

## Running Tests

### Backend Tests

```bash
cd app
source venv/bin/activate

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/unit/test_patient_service.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

### Frontend Tests

```bash
cd frontend
npm test
```

---

## Next Steps

1. **Explore the API** - Open http://localhost:8000/docs and try different endpoints
2. **Read the Documentation** - Check `docs/LOCAL_DEVELOPMENT.md` for more details
3. **Run Tests** - Verify everything works with `pytest tests/ -v`
4. **Customize** - Start modifying the code for your needs
5. **Deploy** - When ready, see `docs/AWS_DEPLOYMENT.md` for cloud deployment

---

## Quick Reference

### Essential Commands

```bash
# Start database
docker start local-postgres

# Activate Python environment
source app/venv/bin/activate

# Start backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Start frontend
npm start

# Run tests
pytest tests/ -v

# Stop database
docker stop local-postgres
```

### Important URLs

- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:3000
- Health Check: http://localhost:8000/health/

### Project Structure

```
blue-zone-healthcare-ops/
├── app/              # Backend (Python/FastAPI)
├── frontend/         # Frontend (React)
├── docs/             # Documentation
├── terraform/        # AWS Infrastructure
└── tests/            # Test utilities
```

---

## Getting Help

1. **Check Troubleshooting** - See [Common Issues](#common-issues--solutions)
2. **Review Logs** - Check terminal output for error messages
3. **Test Health** - Run `curl http://localhost:8000/health/`
4. **Read Docs** - See `docs/` folder for detailed guides
5. **Open Issue** - Create a GitHub issue with error details

---

**You're all set! Start the application and begin developing! 🚀**
