# AWS Deployment Guide

Complete guide for deploying Blue Zone Healthcare Ops to AWS infrastructure.

## Prerequisites

- AWS CLI configured with credentials
- Terraform v1.0+
- S3 bucket `healthcare-ops-state` in af-south-1
- AWS permissions: EC2, RDS, VPC, Secrets Manager, S3
- SSH key pair for EC2 access

---

## Infrastructure Deployment

### 1. Prepare Terraform Backend

```bash
# Create S3 bucket for Terraform state (if not exists)
aws s3 mb s3://healthcare-ops-state --region af-south-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket healthcare-ops-state \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket healthcare-ops-state \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'
```

### 2. Configure Terraform Variables

Create `terraform/terraform.tfvars`:

```hcl
aws_region = "af-south-1"
vpc_cidr = "10.0.0.0/16"
db_instance_class = "db.t3.micro"
ec2_instance_type = "t3.micro"
db_name = "audit_logs"
db_username = "adminuser"
```

### 3. Deploy Infrastructure

```bash
# Navigate to terraform directory
cd terraform

# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Review planned changes
terraform plan

# Deploy infrastructure
terraform apply

# Note the outputs
terraform output
```

### 4. Save Outputs

```bash
# Save important outputs
terraform output ec2_public_ip > ../ec2_ip.txt
terraform output db_endpoint > ../db_endpoint.txt
terraform output db_secret_name > ../db_secret.txt
```

---

## Application Deployment

### 1. Connect to EC2 Instance

```bash
# Get EC2 public IP
EC2_IP=$(terraform output -raw ec2_public_ip)

# SSH into EC2
ssh -i <your-key-pair>.pem ubuntu@$EC2_IP
```

### 2. Install System Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python, Node.js, and Git
sudo apt install -y python3 python3-pip python3-venv git nodejs npm

# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

### 3. Configure AWS CLI

```bash
# Configure AWS credentials
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Default region: af-south-1
# Default output format: json
```

### 4. Clone Repository

```bash
# Clone the repository
git clone <your-repo-url>
cd blue-zone-healthcare-ops
```

### 5. Setup Backend

```bash
# Navigate to app directory
cd app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 6. Configure Database Connection

```bash
# Get database endpoint
DB_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name healthcare-ops \
  --query 'Stacks[0].Outputs[?OutputKey==`DBEndpoint`].OutputValue' \
  --output text)

# Get database password from Secrets Manager
DB_SECRET_NAME=$(aws cloudformation describe-stacks \
  --stack-name healthcare-ops \
  --query 'Stacks[0].Outputs[?OutputKey==`DBSecretName`].OutputValue' \
  --output text)

DB_PASSWORD=$(aws secretsmanager get-secret-value \
  --secret-id $DB_SECRET_NAME \
  --query SecretString \
  --output text | jq -r .password)

# Set environment variable
export DATABASE_URL="postgresql://adminuser:${DB_PASSWORD}@${DB_ENDPOINT}/audit_logs"

# Or create .env file
cat > .env << EOF
DATABASE_URL=postgresql://adminuser:${DB_PASSWORD}@${DB_ENDPOINT}/audit_logs
DEBUG=False
LOG_LEVEL=INFO
SECRET_KEY=$(openssl rand -hex 32)
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600
EOF
```

### 7. Initialize Database

```bash
# Initialize database tables
python -c "from database import init_db; init_db()"
```

### 8. Run Backend Application

#### Option 1: Direct Run (Testing)

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### Option 2: Systemd Service (Production)

```bash
# Create systemd service file
sudo tee /etc/systemd/system/healthcare-api.service > /dev/null << EOF
[Unit]
Description=Healthcare API Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/blue-zone-healthcare-ops/app
Environment="PATH=/home/ubuntu/blue-zone-healthcare-ops/app/venv/bin"
EnvironmentFile=/home/ubuntu/blue-zone-healthcare-ops/app/.env
ExecStart=/home/ubuntu/blue-zone-healthcare-ops/app/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable healthcare-api
sudo systemctl start healthcare-api

# Check status
sudo systemctl status healthcare-api
```

### 9. Setup Frontend

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install

# Build for production
npm run build

# Install serve (static file server)
sudo npm install -g serve

# Serve frontend
serve -s build -l 3000
```

#### Option: Setup Nginx for Frontend

```bash
# Install Nginx
sudo apt install -y nginx

# Create Nginx configuration
sudo tee /etc/nginx/sites-available/healthcare-frontend > /dev/null << EOF
server {
    listen 80;
    server_name _;

    root /home/ubuntu/blue-zone-healthcare-ops/frontend/build;
    index index.html;

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/healthcare-frontend /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Test and restart Nginx
sudo nginx -t
sudo systemctl restart nginx
```

---

## Verification

### 1. Test Backend

```bash
# From your local machine
curl http://<ec2-public-ip>:8000/health/

# Expected response: {"status": "healthy"}
```

### 2. Test Database Connection

```bash
curl http://<ec2-public-ip>:8000/health/db

# Expected response: {"status": "healthy", "database": "connected"}
```

### 3. Access API Documentation

Open in browser: `http://<ec2-public-ip>:8000/docs`

### 4. Access Frontend

Open in browser: `http://<ec2-public-ip>` (if using Nginx)

---

## Security Configuration

### 1. Update Security Groups

```bash
# Restrict SSH access to your IP
aws ec2 authorize-security-group-ingress \
  --group-id <app-server-sg-id> \
  --protocol tcp \
  --port 22 \
  --cidr <your-ip>/32

# Remove open SSH access
aws ec2 revoke-security-group-ingress \
  --group-id <app-server-sg-id> \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0
```

### 2. Enable HTTPS (Optional)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

### 3. Rotate Secrets

```bash
# Generate new database password
NEW_PASSWORD=$(openssl rand -base64 32)

# Update in Secrets Manager
aws secretsmanager update-secret \
  --secret-id <secret-name> \
  --secret-string "{\"password\":\"$NEW_PASSWORD\"}"

# Update RDS password
aws rds modify-db-instance \
  --db-instance-identifier <db-instance-id> \
  --master-user-password "$NEW_PASSWORD" \
  --apply-immediately
```

---

## Monitoring and Logs

### 1. View Application Logs

```bash
# Systemd service logs
sudo journalctl -u healthcare-api -f

# Application logs
tail -f /home/ubuntu/blue-zone-healthcare-ops/app/logs/app.log
```

### 2. View Nginx Logs

```bash
# Access logs
sudo tail -f /var/log/nginx/access.log

# Error logs
sudo tail -f /var/log/nginx/error.log
```

### 3. Database Logs

```bash
# View RDS logs via AWS CLI
aws rds describe-db-log-files \
  --db-instance-identifier <db-instance-id>

# Download log file
aws rds download-db-log-file-portion \
  --db-instance-identifier <db-instance-id> \
  --log-file-name <log-file-name>
```

---

## Backup and Recovery

### 1. Database Backups

```bash
# Create manual snapshot
aws rds create-db-snapshot \
  --db-instance-identifier <db-instance-id> \
  --db-snapshot-identifier healthcare-backup-$(date +%Y%m%d)

# List snapshots
aws rds describe-db-snapshots \
  --db-instance-identifier <db-instance-id>
```

### 2. Application Backups

```bash
# Backup application code
tar -czf healthcare-app-backup-$(date +%Y%m%d).tar.gz \
  /home/ubuntu/blue-zone-healthcare-ops

# Upload to S3
aws s3 cp healthcare-app-backup-$(date +%Y%m%d).tar.gz \
  s3://healthcare-ops-backups/
```

---

## Scaling and Updates

### 1. Update Application

```bash
# SSH into EC2
ssh -i <key-pair>.pem ubuntu@<ec2-ip>

# Pull latest changes
cd blue-zone-healthcare-ops
git pull origin main

# Update backend
cd app
source venv/bin/activate
pip install -r requirements.txt

# Restart service
sudo systemctl restart healthcare-api

# Update frontend
cd ../frontend
npm install
npm run build
sudo systemctl restart nginx
```

### 2. Scale Database

```bash
# Modify instance class
aws rds modify-db-instance \
  --db-instance-identifier <db-instance-id> \
  --db-instance-class db.t3.small \
  --apply-immediately
```

### 3. Scale EC2

```bash
# Stop instance
aws ec2 stop-instances --instance-ids <instance-id>

# Change instance type
aws ec2 modify-instance-attribute \
  --instance-id <instance-id> \
  --instance-type t3.small

# Start instance
aws ec2 start-instances --instance-ids <instance-id>
```

---

## Troubleshooting

### Can't Access EC2 Application

1. Verify security group allows port 8000
2. Check EC2 public IP is correct
3. Ensure app is running: `sudo systemctl status healthcare-api`
4. Test with: `curl http://<ec2-ip>:8000/health/`

### Database Connection Fails

```bash
# Get DB password from Secrets Manager
aws secretsmanager get-secret-value \
  --secret-id <secret-name> \
  --query SecretString \
  --output text

# Test database connection
psql -h <db-endpoint> -U adminuser -d audit_logs
```

### Application Won't Start

```bash
# Check logs
sudo journalctl -u healthcare-api -n 50

# Check environment variables
sudo systemctl show healthcare-api | grep Environment

# Restart service
sudo systemctl restart healthcare-api
```

---

## Cleanup

### Destroy Infrastructure

```bash
# Navigate to terraform directory
cd terraform

# Destroy all resources
terraform destroy

# Confirm with 'yes'
```

### Manual Cleanup

```bash
# Delete S3 bucket
aws s3 rb s3://healthcare-ops-state --force

# Delete secrets
aws secretsmanager delete-secret \
  --secret-id <secret-name> \
  --force-delete-without-recovery
```

---

## CI/CD Integration

See [CI/CD Documentation](../README.md#cicd) for GitHub Actions setup.

---

## Support

For deployment issues:
1. Check [Troubleshooting](#troubleshooting) section
2. Review CloudWatch logs
3. Check Terraform state
4. Open GitHub issue
