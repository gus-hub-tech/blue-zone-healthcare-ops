# Blue Zone Healthcare Ops

A HIPAA-aligned hospital management system with 2-tier AWS infrastructure, featuring encrypted RDS PostgreSQL, EC2 application server, and a comprehensive FastAPI backend with React frontend.

## Table of Contents
- [Overview](#overview)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Local Development](#local-development)
- [AWS Deployment](#aws-deployment)
- [Application Features](#application-features)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

---

## Overview

### What is Blue Zone Healthcare Ops?

A complete hospital management system providing:
- **Patient Management**: Registration, records, and status tracking
- **Appointment Scheduling**: Double-booking prevention with availability tracking
- **Medical Records**: Version history and access control
- **Staff Management**: Credentials, availability, and department assignments
- **Prescription Management**: Medication validation and tracking
- **Billing & Payments**: Automated charge calculation and payment processing
- **Inventory Management**: Stock tracking with expiration monitoring
- **Access Control**: JWT authentication with role-based permissions
- **Audit Logging**: Complete audit trail for HIPAA compliance

### Technology Stack

**Backend:**
- FastAPI (Python 3.9+)
- SQLAlchemy ORM
- PostgreSQL
- JWT Authentication
- Pydantic validation

**Frontend:**
- React
- Axios for API calls
- Material-UI components

**Infrastructure:**
- AWS EC2 (t3.micro)
- AWS RDS PostgreSQL (Multi-AZ)
- AWS Secrets Manager
- S3 (Terraform state)
- Terraform IaC

---

## Quick Start

### Local Development (5 minutes)

```bash
# 1. Clone repository
git clone <repo-url>
cd blue-zone-healthcare-ops

# 2. Start PostgreSQL (choose one)
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

## Getting Started

- **Local Development**: See [Local Development Guide](docs/LOCAL_DEVELOPMENT.md)
- **AWS Deployment**: See [AWS Deployment Guide](docs/AWS_DEPLOYMENT.md)
- **API Documentation**: http://localhost:8000/docs (when running)

---

## Architecture

### Infrastructure Overview

```
Internet
    |
Internet Gateway
    |
+---------------------------------+
| Public Subnet (10.0.101.0/24)  |
|  +-------------------+          |
|  | EC2 Instance      |          |
|  | FastAPI + React   |          |
|  +-------------------+          |
+---------------------------------+
          |
          | (Security Group)
          |
+---------------------------------+
| Private Subnets                 |
| (10.0.102.0/24, 10.0.103.0/24) |
|  +-------------------+          |
|  | RDS PostgreSQL    |          |
|  | Multi-AZ Encrypted|          |
|  +-------------------+          |
+---------------------------------+
          |
    AWS Secrets Manager
          |
    S3 (Terraform State)
```

### Application Architecture

```
app/
├── models/          # SQLAlchemy ORM models
├── services/        # Business logic layer
├── routes/          # API endpoints
├── middleware/      # Logging, error handling
├── tests/           # Unit, integration, property tests
├── main.py          # FastAPI application
├── config.py        # Configuration
└── database.py      # Database setup

frontend/
├── src/
│   ├── components/  # React components
│   ├── App.js       # Main application
│   └── index.js     # Entry point
└── public/
```

### Detailed Project Structure

```
blue-zone-healthcare-ops/
├── app/                          # Main application code
│   ├── middleware/               # FastAPI middleware
│   │   ├── __init__.py
│   │   ├── logging.py           # Request/response logging
│   │   └── error_handler.py     # Exception handling
│   ├── models/                   # SQLAlchemy database models
│   │   ├── __init__.py
│   │   ├── patient.py           # Patient model
│   │   ├── medical_record.py    # Medical records
│   │   ├── appointment.py       # Appointments
│   │   ├── staff.py             # Staff management
│   │   ├── prescription.py      # Prescriptions
│   │   ├── billing.py           # Billing records
│   │   ├── inventory.py         # Inventory items
│   │   ├── department.py        # Departments
│   │   ├── access_control.py    # Users and roles
│   │   └── audit.py             # Audit logs
│   ├── routes/                   # API route handlers
│   │   ├── __init__.py
│   │   ├── health.py            # Health check endpoints
│   │   ├── patients.py          # Patient endpoints
│   │   ├── appointments.py      # Appointment endpoints
│   │   ├── medical_records.py   # Medical record endpoints
│   │   ├── staff.py             # Staff endpoints
│   │   ├── prescriptions.py     # Prescription endpoints
│   │   ├── billing.py           # Billing endpoints
│   │   ├── inventory.py         # Inventory endpoints
│   │   └── departments.py       # Department endpoints
│   ├── services/                 # Business logic layer
│   │   ├── __init__.py
│   │   ├── patient_service.py
│   │   ├── medical_record_service.py
│   │   ├── appointment_service.py
│   │   ├── staff_service.py
│   │   ├── prescription_service.py
│   │   ├── billing_service.py
│   │   ├── inventory_service.py
│   │   ├── department_service.py
│   │   └── access_control_service.py
│   ├── tests/                    # Application tests
│   │   ├── integration/          # Integration tests
│   │   ├── properties/           # Property-based tests (Hypothesis)
│   │   ├── unit/                 # Unit tests
│   │   ├── __init__.py
│   │   ├── conftest.py          # Pytest fixtures
│   │   └── test_health.py       # Health check tests
│   ├── __init__.py
│   ├── config.py                 # Application configuration
│   ├── database.py               # Database connection setup
│   ├── exceptions.py             # Custom exceptions
│   ├── main.py                   # Main FastAPI application
│   ├── models.py                 # Legacy models (simple setup)
│   ├── simple_main.py            # Simplified app version
│   └── requirements.txt          # Python dependencies
│
├── docs/                         # Documentation
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── PROPERTY_TESTS_SUMMARY.md
│   ├── SETUP.md
│   └── TASK_12_COMPLETION_SUMMARY.md
│
├── frontend/                     # React frontend application
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/           # React components
│   │   │   ├── AppointmentDashboard.js
│   │   │   ├── BillingDashboard.js
│   │   │   ├── DepartmentsDashboard.js
│   │   │   ├── InventoryDashboard.js
│   │   │   ├── MedicalRecordsDashboard.js
│   │   │   ├── PatientDashboard.js
│   │   │   ├── PrescriptionsDashboard.js
│   │   │   └── StaffDashboard.js
│   │   ├── App.css
│   │   ├── App.js               # Main application
│   │   └── index.js             # Entry point
│   ├── package.json
│   └── README.md
│
├── images/                       # Architecture diagrams
│   ├── database.png
│   ├── rds-ha.png
│   ├── resource-map.tf.png
│   └── secret-manager.png
│
├── scripts/                      # Utility scripts
│   ├── run.sh                    # Run application
│   ├── run_tests.sh              # Run test suite
│   └── start_app.sh              # Start application
│
├── terraform/                    # Infrastructure as Code
│   ├── backend.tf                # S3 backend configuration
│   ├── database.tf               # RDS PostgreSQL setup
│   ├── main.tf                   # Main infrastructure
│   ├── network.tf                # VPC, subnets, routing
│   ├── output.tf                 # Terraform outputs
│   ├── provider.tf               # AWS provider config
│   └── security.tf               # Security groups
│
├── tests/                        # Root-level test utilities
│   ├── run_pbt_tests.py          # Property-based test runner
│   └── test_single.py            # Single test runner
│
├── .gitignore                    # Git ignore rules
├── pytest.ini                    # Pytest configuration
└── README.md                     # Project documentation
```

### AWS Components

| Component | Type | Purpose |
|-----------|------|---------|
| VPC | 10.0.0.0/16 | Isolated network |
| EC2 | t3.micro | Application server |
| RDS | db.t3.micro | PostgreSQL database |
| Secrets Manager | - | Credential storage |
| S3 | - | Terraform state |
| Security Groups | - | Network access control |

---

## Local Development

For detailed local setup instructions, see [Local Development Guide](docs/LOCAL_DEVELOPMENT.md).

**Quick Start:**
```bash
docker run --name local-postgres -e POSTGRES_PASSWORD=devpass -e POSTGRES_DB=audit_logs -e POSTGRES_USER=adminuser -p 5432:5432 -d postgres:15
cd app && pip install -r requirements.txt
export DATABASE_URL="postgresql://adminuser:devpass@localhost:5432/audit_logs"
python -c "from database import init_db; init_db()"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## AWS Deployment

For detailed AWS deployment instructions, see [AWS Deployment Guide](docs/AWS_DEPLOYMENT.md).

**Quick Deploy:**
```bash
cd terraform
terraform init
terraform apply
```

---

## Application Features

### 1. Patient Management
- Register new patients with demographic information
- Update patient records
- Track patient status (Active, Inactive, Deceased)
- Search and filter patients
- Audit trail for all patient access

**API Endpoints:**
- `POST /patients` - Register patient
- `GET /patients/{id}` - Get patient details
- `PUT /patients/{id}` - Update patient
- `GET /patients` - List patients
- `PATCH /patients/{id}/status` - Update status

### 2. Medical Records
- Create and manage medical records
- Add diagnoses, treatments, clinical notes
- Version history tracking
- Access control and audit logging

**API Endpoints:**
- `GET /medical-records/patient/{id}` - Get medical record
- `POST /medical-records/patient/{id}/diagnoses` - Add diagnosis
- `POST /medical-records/patient/{id}/treatments` - Add treatment
- `POST /medical-records/patient/{id}/notes` - Add note
- `GET /medical-records/patient/{id}/history` - Get history

### 3. Appointment Scheduling
- Schedule appointments with double-booking prevention
- Check doctor availability
- Cancel appointments
- View patient appointment history

**API Endpoints:**
- `POST /appointments` - Schedule appointment
- `GET /appointments/{id}` - Get appointment
- `DELETE /appointments/{id}` - Cancel appointment
- `GET /appointments/doctor/{id}/available-slots` - Available slots
- `GET /appointments/patient/{id}/appointments` - Patient appointments

### 4. Staff Management
- Add and manage staff members
- Track credentials and certifications
- Manage availability schedules
- Department assignments

**API Endpoints:**
- `POST /staff` - Add staff
- `GET /staff/{id}` - Get staff details
- `PUT /staff/{id}` - Update staff
- `PATCH /staff/{id}/department` - Assign department
- `GET /staff/{id}/availability` - Get availability

### 5. Prescription Management
- Create prescriptions with medication validation
- Track prescription status
- View patient prescription history

**API Endpoints:**
- `POST /prescriptions` - Create prescription
- `GET /prescriptions/{id}` - Get prescription
- `GET /prescriptions/patient/{id}/prescriptions` - Patient prescriptions
- `PATCH /prescriptions/{id}/status` - Update status

### 6. Billing & Payments
- Create billing records
- Calculate charges automatically
- Process payments
- Track account balances
- Finalize billing records (immutable)

**API Endpoints:**
- `POST /billing` - Create billing record
- `GET /billing/{id}` - Get billing record
- `POST /billing/payments` - Process payment
- `GET /billing/patient/{id}/balance` - Get balance
- `PATCH /billing/{id}/finalize` - Finalize billing

### 7. Inventory Management
- Track medical supplies and medications
- Monitor stock levels
- Handle expiration dates
- Record consumption transactions

**API Endpoints:**
- `POST /inventory` - Add item
- `GET /inventory/{id}` - Get item
- `PATCH /inventory/{id}/consume` - Consume inventory
- `GET /inventory/low-stock` - Low stock items
- `GET /inventory/expired` - Expired items

### 8. Department Management
- Create and manage departments
- Assign staff to departments
- Track department metrics

**API Endpoints:**
- `POST /departments` - Create department
- `GET /departments/{id}` - Get department
- `GET /departments/{id}/staff` - Department staff
- `GET /departments/{id}/metrics` - Department metrics

### 9. Access Control & Security
- JWT-based authentication
- Role-based access control (RBAC)
- Access logging for audit trails
- Password hashing with bcrypt

---

## API Documentation

### Interactive Documentation

Once running, access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Health Check Endpoints

```bash
# Basic health check
curl http://localhost:8000/health/

# Database health check
curl http://localhost:8000/health/db
```

### Authentication

```bash
# Login (get JWT token)
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'

# Use token in requests
curl http://localhost:8000/patients \
  -H "Authorization: Bearer <token>"
```

---

## Testing

### Test Structure

```
app/tests/
├── unit/              # Unit tests for services
├── properties/        # Property-based tests (Hypothesis)
├── integration/       # End-to-end workflow tests
├── conftest.py        # Pytest fixtures
└── test_health.py     # Health check tests
```

### Running Tests

```bash
# All tests
pytest app/tests -v

# Specific test file
pytest app/tests/unit/test_patient_service.py -v

# With coverage report
pytest app/tests --cov=app --cov-report=html

# Property-based tests only
pytest app/tests/properties -v
```

### Test Coverage

The test suite includes:
- **Unit Tests**: Individual component testing
- **Property-Based Tests**: Hypothesis-driven testing with 50+ iterations
- **Integration Tests**: Complete workflow validation

**Key Properties Tested:**
- Patient registration idempotence
- Appointment double-booking prevention
- Medical record version history
- Billing calculation consistency
- Inventory consumption tracking
- Access control enforcement

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

### AWS Deployment Issues

**Problem**: Can't access EC2 application

**Solution**:
1. Verify security group allows port 8000
2. Check EC2 public IP is correct
3. Ensure app is running on EC2 (not locally)
4. Test with: `curl http://<ec2-ip>:8000/health/`

**Problem**: Database connection fails on EC2

**Solution**:
```bash
# Get DB password from Secrets Manager
aws secretsmanager get-secret-value \
  --secret-id <secret-name> \
  --query SecretString \
  --output text

# Test database connection
psql -h <db-endpoint> -U adminuser -d audit_logs
```

### React Scripts Permission Denied

**Problem**: `npm start` fails with permission error

**Solution**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

## Configuration

### Environment Variables

Create `.env` file in `app/` directory:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/audit_logs

# Application
DEBUG=True
LOG_LEVEL=INFO
SECRET_KEY=your-secret-key-here

# Database Pool
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
```

### AWS Configuration

Terraform variables in `terraform/terraform.tfvars`:

```hcl
aws_region = "af-south-1"
vpc_cidr = "10.0.0.0/16"
db_instance_class = "db.t3.micro"
ec2_instance_type = "t3.micro"
```

---

## Security Notes

- Database password randomly generated and stored in Secrets Manager
- All RDS data encrypted at rest
- Multi-AZ deployment for high availability
- Security groups restrict access (SSH from specific IPs in production)
- JWT tokens for API authentication
- RBAC for authorization
- Complete audit trail for HIPAA compliance
- Regular secret rotation recommended

---

## CI/CD

GitHub Actions workflow in `.github/workflows/terraform.yml`:
- Runs on push/PR to `main`
- Terraform init, validate, plan
- Manual approval for apply

**Setup**:
1. Add AWS credentials to GitHub secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`

---

## Additional Documentation

- [Local Development Guide](docs/LOCAL_DEVELOPMENT.md)
- [AWS Deployment Guide](docs/AWS_DEPLOYMENT.md)
- [Implementation Details](docs/IMPLEMENTATION_SUMMARY.md)
- [Property-Based Tests](docs/PROPERTY_TESTS_SUMMARY.md)
- [Task Completion](docs/TASK_12_COMPLETION_SUMMARY.md)

---

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review API documentation at `/docs`
3. Check application logs
4. Open GitHub issue

---

**Built with ❤️ for healthcare compliance and efficiency**
