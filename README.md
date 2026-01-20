# Blue Zone Healthcare Ops

## Project Description

A HIPAA-aligned 2-tier AWS infrastructure provisioned with Terraform, featuring an encrypted RDS PostgreSQL database and an isolated EC2 application server. Utilizes AWS Secrets Manager for secure credential management and S3 for remote state storage.

## Architecture

- **VPC**: Private virtual network (CIDR: 10.0.0.0/16) with DNS support enabled.
- **Public Subnet**: Hosts the EC2 instance (t3.micro, Ubuntu 24.04) for application hosting, with public IP assignment.
- **Private Subnet**: Hosts the encrypted, multi-AZ RDS PostgreSQL instance (db.t3.micro) across two availability zones (af-south-1a and af-south-1b) for high availability.
- **Security Groups**:
  - App Server SG: Allows SSH (port 22) from anywhere (restrict to specific IPs in production).
  - Database SG: Allows PostgreSQL traffic (port 5432) only from the App Server SG.
- **Internet Gateway and Route Tables**: Provides internet access for the public subnet.
- **Secrets Manager**: Securely stores DB username and password.
- **S3 Backend**: Remote Terraform state storage with encryption in `af-south-1`.

## Components

| Layer      | Component                | Healthcare Compliance Feature |
|------------|--------------------------|-------------------------------|
| Automation | GitHub Actions           | Automated audit trail of infrastructure changes. |
| Compute    | AWS EC2 (t3.micro)      | Hosted in Public Subnet with least privilege access. |
| Database   | Amazon RDS (PostgreSQL) | Encrypted at rest, multi-AZ deployment for high availability. |
| State      | S3 Remote Backend       | Versioned and encrypted infrastructure state. |
| Secrets    | AWS Secrets Manager     | Secure credential storage and retrieval. |

## Prerequisites

- AWS CLI configured with permissions for EC2, RDS, VPC, Secrets Manager, and S3.
- Terraform v1.0+ installed.
- S3 bucket `healthcare-state-bucket` exists in region `af-south-1` (create manually if needed).

## Usage

1. Navigate to the `terraform/` directory.
2. Run `terraform init` to download providers and initialize the backend.
3. Run `terraform plan` to review the infrastructure changes.
4. Run `terraform apply` to deploy the resources.

## CI/CD

Automated deployment via GitHub Actions. The workflow runs on pushes and pull requests to the `main` branch, performing Terraform init, validate, and plan. Apply is manual to ensure review.

**Setup**: Add `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` to GitHub repository secrets.

## Outputs

After deployment, Terraform provides:
- `vpc_id`: ID of the created VPC.
- `public_subnet_id`: ID of the public subnet.
- `db_endpoint`: Endpoint for connecting to the PostgreSQL database.
- `db_arn`: ARN of the database instance.

## Security Notes

- DB password is randomly generated and stored in AWS Secrets Manager.
- Ensure SSH access is restricted in production environments.
- Regularly rotate secrets and review IAM permissions.

# Installing & PostgreSQL client
To interact with the PostgreSQL database, you need to install the PostgreSQL client on yourEC2 instance.
1. Connect to your EC2 instance via SSH:
   ```bash
   ssh -i /path/to/your-key.pem ubuntu@your-ec2-public-ip
   ```
2. Update the package list:   sudo apt-get update
      sudo apt-get update
   
3. Install the PostgreSQL client:   sudo apt-get install -y postgresql
   sudo apt-get install -y postgresql

# Test Connectivity
To test connectivity to the PostgreSQL database from your EC2 instance, follow these steps:
1. Connect to your EC2 instance via SSH:
   ssh -i /path/to/your-key.pem ubuntu@your-ec2-public-ip
2. Retrieve the database credentials from AWS Secrets Manager:
   ```bash
    aws secretsmanager get-secret-value --secret-id your-secret-name --query 'SecretString' --output text
   
