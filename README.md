# Blue Zone Healthcare Ops

## Project Description

A HIPAA-aligned 2-tier AWS infrastructure provisioned with Terraform, featuring an encrypted RDS PostgreSQL database and an isolated EC2 application server running a FastAPI audit logging application. Utilizes AWS Secrets Manager for secure credential management and S3 for remote state storage. The application provides RESTful API endpoints for patient record access logging, ensuring compliance with healthcare audit requirements.

## Architecture

The infrastructure follows a 2-tier architecture: a public-facing application tier and a private database tier within a secure VPC. This ensures isolation, high availability, and HIPAA compliance.

### Components
- **VPC**: Private virtual network (CIDR: 10.0.0.0/16) with DNS support.
- **Public Subnet**: Hosts the EC2 instance (t3.micro, Ubuntu 24.04) with public IP.
- **Private Subnets**: Host the encrypted, multi-AZ RDS PostgreSQL (db.t3.micro) across af-south-1a and af-south-1b.
- **Security Groups**:
  - App Server SG: Allows SSH (port 22) and HTTP (port 8000) from anywhere (restrict in production).
  - Database SG: Allows PostgreSQL (port 5432) from App Server SG only.
- **Internet Gateway & Route Tables**: Enable internet access for the public subnet.
- **Secrets Manager**: Stores DB credentials securely.
- **S3 Backend**: Encrypted remote state storage in af-south-1.

| Layer      | Component                | Healthcare Compliance Feature |
|------------|--------------------------|-------------------------------|
| Automation | GitHub Actions           | Automated audit trail of changes. |
| Compute    | AWS EC2 (t3.micro)      | Least privilege in public subnet. |
| Database   | Amazon RDS (PostgreSQL) | Encrypted, multi-AZ for availability. |
| State      | S3 Remote Backend       | Versioned, encrypted state. |
| Secrets    | AWS Secrets Manager     | Secure credential management. |

### Architecture Diagram
```
Internet
    |
Internet Gateway
    |
+---------------------------------+
| Public Subnet (10.0.101.0/24)  |
|  +-------------------+          |
|  | EC2 Instance      |          |
|  | (t3.micro)        |          |
|  +-------------------+          |
+---------------------------------+
          |
          | (via Security Group)
          |
+---------------------------------+
| Private Subnets                 |
| (10.0.102.0/24, 10.0.103.0/24) |
|  +-------------------+          |
|  | RDS PostgreSQL    |          |
|  | Multi-AZ          |          |
|  +-------------------+          |
+---------------------------------+
          |
          | (Credentials)
          |
AWS Secrets Manager
          |
          | (State)
          |
S3 Bucket (healthcare-ops-state)
```

## Prerequisites

### Infrastructure Prerequisites
- AWS CLI configured with permissions for EC2, RDS, VPC, Secrets Manager, S3.
- Terraform v1.0+ installed.
- S3 bucket `healthcare-ops-state` in af-south-1 (create manually if needed).

### Application Prerequisites
- Python 3.8+ installed on the EC2 instance.
- pip for package management.
- Git for cloning the application repository.

## Usage

1. Navigate to `terraform/` directory.
2. Run `terraform init` to initialize.
3. Run `terraform plan` to review changes.
4. Run `terraform apply` to deploy.

After deployment, the FastAPI app will be accessible at the EC2 instance's public IP on port 8000.

## CI/CD

Optional: Automated deployment via GitHub Actions on pushes/PRs to `main` (init, validate, plan). Apply manually.

**Setup**: Add `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` to repo secrets.

## Outputs

After deployment:
- `vpc_id`: VPC ID.
- `public_subnet_id`: Public subnet ID.
- `db_endpoint`: PostgreSQL endpoint.
- `db_arn`: Database ARN.

## Security Notes

- DB password is randomly generated and stored in Secrets Manager.
- Restrict SSH access in production.
- Rotate secrets and review IAM permissions regularly.

## Application

### Database Schema

The application uses a PostgreSQL database with the following schema for audit logging:

- **patient_audit_logs** table:
  - `id`: SERIAL PRIMARY KEY
  - `doctor_id`: VARCHAR(100) NOT NULL
  - `patient_id`: VARCHAR(100) NOT NULL
  - `action`: VARCHAR(50) NOT NULL (e.g., 'ACCESS', 'MODIFY')
  - `timestamp`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

### Application Setup

1. SSH into the EC2 instance: `ssh -i key.pem ubuntu@<ec2-public-ip>`
2. Install Python and pip if not already installed: `sudo apt update && sudo apt install -y python3 python3-pip`
3. Clone the repository: `git clone <repository-url> && cd <repo-directory>/app`
4. Install dependencies: `pip3 install -r requirements.txt` (assuming requirements.txt exists with fastapi, uvicorn, sqlalchemy, psycopg2-binary, python-dotenv, pydantic)
5. Set environment variables:
   ```bash
   export DATABASE_URL="postgresql://adminuser:<password>@<db_endpoint>/audit_logs"
   ```
   Obtain the password from AWS Secrets Manager.
6. Run the application: `uvicorn main:app --host 0.0.0.0 --port 8000`

### API Endpoints

- **POST /log-access**: Logs patient access events.
  - Request Body (JSON):
    ```json
    {
      "doctor_id": "string",
      "patient_id": "string",
      "action": "string"
    }
    ```
  - Response: Success message or error.

The application provides a RESTful API for logging patient record access, ensuring compliance with HIPAA audit requirements.

## Troubleshooting

### Common Issues and Solutions

#### ImportError: attempted relative import with no known parent package
**Problem**: When running `uvicorn main:app`, you get an import error for relative imports.

**Solution**: The import in `main.py` needs to be absolute. Change:
```python
from . import models
```
To:
```python
import models
```

#### Database Connection Errors
**Problem**: App fails to start with database-related errors.

**Solution**: 
1. Ensure DATABASE_URL is set correctly with URL-encoded password (special characters like `< > & ? %` need encoding).
2. Example encoding: `<` becomes `%3C`, `>` becomes `%3E`, `&` becomes `%26`, etc.
3. Verify credentials from AWS Secrets Manager are correct.

#### Site Can't Be Reached in Browser
**Problem**: Browser shows "site can't be reached" when accessing `http://<ec2-ip>:8000/docs`.

**Solution**:
1. Confirm the app is running on EC2 (check for startup messages in SSH terminal).
2. Verify the correct EC2 public IP from `terraform output`.
3. Ensure port 8000 is accessible (check EC2 security group).
4. App must run on EC2 instance, not locally, as it connects to AWS RDS.

#### AWS CLI Permission Errors
**Problem**: `aws secretsmanager get-secret-value` fails with permission errors.

**Solution**: Configure AWS CLI credentials on EC2:
```bash
aws configure
```
Enter your access key, secret key, region (af-south-1), and output format.

#### Requirements Installation Issues
**Problem**: `pip3 install -r requirements.txt` fails with "No such file or directory".

**Solution**: Ensure you're in the correct directory (`blue-zone-healthcare-ops/app`) and the file exists. Pull latest changes from GitHub if needed.

### Step-by-Step Deployment Guide

1. **Get Terraform outputs**:
   ```bash
   terraform output
   ```
   Note the `ec2_public_ip` and `db_endpoint`.

2. **SSH into EC2**:
   ```bash
   ssh -i <key-pair>.pem ubuntu@<ec2_public_ip>
   ```

3. **Install dependencies**:
   ```bash
   sudo apt update && sudo apt install -y python3 python3-pip git
   ```

4. **Clone and setup app**:
   ```bash
   git clone <repo-url>
   cd <repo>/app
   pip3 install -r requirements.txt
   ```

5. **Get database password**:
   ```bash
   aws secretsmanager get-secret-value --secret-id <secret-name> --query SecretString --output text
   ```

6. **Set environment**:
   ```bash
   export DATABASE_URL="postgresql://adminuser:<encoded-password>@<db_endpoint>/audit_logs"
   ```

7. **Run the app**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

8. **Access in browser**:
   Go to `http://<ec2_public_ip>:8000/docs`

## Database Connection

1. SSH into EC2: `ssh -i key.pem ubuntu@ec2-public-ip`
2. Install PostgreSQL client: `sudo apt-get update && sudo apt-get install -y postgresql`
3. Get credentials: `aws secretsmanager get-secret-value --secret-id <secret-name> --query SecretString --output text`
4. Connect: `psql -h <db_endpoint> -U adminuser -d audit_logs`
5. Create table
```bash
CREATE TABLE patient_records (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    dob DATE,
    diagnosis TEXT,
    treatment_plan TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
6. Insert data
```bash
INSERT INTO patient_audit_logs (doctor_id, patient_id, action, timestamp) VALUES ('DR_SMITH_99', 'PATIENT_X_001', 'ACCESS', CURRENT_TIMESTAMP);
```

7. View record
```bash
SELECT * FROM patient_audit_logs;
```
8. Verify final state
```bash
SELECT * FROM patient_audit_logs;
```
9. Exit database
```bash
\q
```
