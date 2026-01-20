# Blue Zone Healthcare Ops

## Project Description

A HIPAA-aligned 2-tier AWS infrastructure provisioned with Terraform, featuring an encrypted RDS PostgreSQL database and an isolated EC2 application server running a FastAPI app. Utilizes AWS Secrets Manager for secure credential management and S3 for remote state storage.

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

- AWS CLI configured with permissions for EC2, RDS, VPC, Secrets Manager, S3.
- Terraform v1.0+ installed.
- S3 bucket `healthcare-ops-state` in af-south-1 (create manually if needed).

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
INSERT INTO access_logs (doctor_id, patient_id) VALUES ('DR_SMITH_99', 'PATIENT_X_001');
```

7. View record
```bash
SELECT * FROM access_logs;
```
8. Verify final state
```bash
SELECT * FROM access_logs;
```
9. Exit database
```bash
\q
```

The "Software" Path (The Application)
Right now, you have an empty server. Let’s give it a purpose.

The Task: Write a tiny Python API (using Flask or FastAPI) that sits on the EC2.

The Goal: Instead of typing SQL commands, you can send a "Patient Log" via a simple web request.

Why: This demonstrates a "Full Stack" DevOps mentality—you aren't just building the pipes; you know how the water (data) flows through them.

1. The Database Schema (Medical Standard)
In healthcare, an audit log must follow a strict trail. We’ll create a table that tracks Who accessed Which record and When.
