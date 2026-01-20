# 1. Create the Security Group for the EC2 Server
resource "aws_security_group" "app-server_sg" {
  name   = "app-server-sg"
  vpc_id = aws_vpc.healthcare_vpc.id
  
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Allows SSH (Ideally limit this to your IP)
  }

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Allows HTTP access to FastAPI app
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 2. Create the Security Group for the Database
resource "aws_security_group" "database_sg" {
  name   = "database-sg"
  vpc_id = aws_vpc.healthcare_vpc.id
  
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app-server_sg.id]
  }

  tags = {
    Name = "database-sg"
  }
}