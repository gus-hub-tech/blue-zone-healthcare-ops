data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

resource "aws_instance" "app_server" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.healthcare_public_subnet.id
  vpc_security_group_ids = [aws_security_group.app-server_sg.id]

  user_data = <<-EOF
    #!/bin/bash
    sudo apt update -y
    sudo apt install git python3-pip -y
    pip3 install fastapi uvicorn sqlalchemy psycopg2-binary

    export DB_URL="postgresql://adminuser:${random_password.db_password.result}@${aws_db_instance.patient_db.endpoint}/audit_logs"

    uvicorn app.main:app --host 0.0.0.0 --port 8000
  EOF

  tags = {
    Name = "blue-zone"
  }
}
