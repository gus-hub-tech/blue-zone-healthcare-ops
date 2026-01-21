data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }

  owners = ["099720109477"] # Canonical
}

resource "aws_instance" "app_server" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.healthcare_public_subnet.id
  vpc_security_group_ids = [aws_security_group.app-server_sg.id]

  provisioner "remote-exec" {
    inline = [
      "git clone https://github.com/gus-hub-tech/blue-zone-healthcare-ops.git"
    ]
  }

  user_data = <<-EOF
    #!/bin/bash
    sudo apt update -y
    sudo apt install git -y
    sudo apt install python3-pip -y
    pip3 install fastapi uvicorn sqlalchemy psycopg2-binary
    
    # Note: DB credentials should be retrieved dynamically in the app from AWS Secrets Manager
    # Example DB URL (replace with actual password retrieval)
    export DB_URL="postgresql://adminuser:${random_password.db_password.result}@${aws_db_instance.patient_db.endpoint}/audit_logs"
    
    # Start the app (assuming app code is present)
    uvicorn app.main:app --host 0.0.0.0 --port 8000
  EOF

  tags = {
    Name = "blue-zone"
  }
}