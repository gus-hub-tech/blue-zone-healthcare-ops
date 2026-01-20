# Generate a random password for the database
resource "random_password" "db_password" {
  length  = 16
  special = true
}

# Generate a random suffix for the secret name
resource "random_string" "secret_suffix" {
  length  = 8
  special = false
  upper   = false
}

# Create a secret in AWS Secrets Manager for the DB credentials
resource "aws_secretsmanager_secret" "db_secret" {
  name = "db-credentials-secret-${random_string.secret_suffix.result}"
}

# Create a version of the secret with the credentials
resource "aws_secretsmanager_secret_version" "db_secret_version" {
  secret_id = aws_secretsmanager_secret.db_secret.id
  secret_string = jsonencode({
    username = "adminuser"
    password = random_password.db_password.result
  })
}

# Data source to retrieve the secret value
data "aws_secretsmanager_secret_version" "db_secret" {
  secret_id = aws_secretsmanager_secret.db_secret.id
  depends_on = [aws_secretsmanager_secret_version.db_secret_version]
}

# 3. Create an Encrypted Database (Healthcare Standard)
resource "aws_db_instance" "patient_db" {
  allocated_storage      = 20
  engine                 = "postgres"
  engine_version         = "15"
  instance_class         = "db.t3.micro"
  db_name                = "audit_logs"
  username               = jsondecode(data.aws_secretsmanager_secret_version.db_secret.secret_string)["username"]
  password               = jsondecode(data.aws_secretsmanager_secret_version.db_secret.secret_string)["password"]
  db_subnet_group_name   = aws_db_subnet_group.db_subnet_group.name
  vpc_security_group_ids = [aws_security_group.database_sg.id]
  multi_az               = false
  
  storage_encrypted    = true   # Essential for Healthcare
  publicly_accessible  = false  # HIPAA requirement: DB must be private
  skip_final_snapshot  = true

  tags = { Name = "patient-db" }
}
