resource "aws_vpc" "healthcare_vpc" {
  cidr_block = "10.0.0.0/16"

  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Terraform    = "true"
    Environment = "dev"
  }
}

resource "aws_subnet" "public_subnet" {
  vpc_id                  = aws_vpc.healthcare_vpc.id
  cidr_block              = "10.0.101.0/24"
  map_public_ip_on_launch   = true

  tags = {
    Name = "public-subnet"
  }
}

resource "aws_subnet" "private_subnet" {
  vpc_id            = aws_vpc.healthcare_vpc.id
  cidr_block        = "10.0.102.0/24"
  availability_zone = "af-south-1a"

  tags = {
    Name = "private-subnet-a"
  }
}

resource "aws_subnet" "private_subnet_b" {
  vpc_id            = aws_vpc.healthcare_vpc.id
  cidr_block        = "10.0.103.0/24"
  availability_zone = "af-south-1b"

  tags = {
    Name = "private-subnet-b"
  }
}

resource "aws_db_subnet_group" "db_subnet_group" {
  name       = "db-subnet-group"
  subnet_ids = [aws_subnet.private_subnet.id, aws_subnet.private_subnet_b.id]

  tags = {
    Name = "db-subnet-group"
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.healthcare_vpc.id

  tags = {
    Name = "healthcare-igw"
  }
}

resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.healthcare_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "public-route-table"
  }
}

resource "aws_route_table_association" "public_association" {
  subnet_id      = aws_subnet.public_subnet.id
  route_table_id = aws_route_table.public_rt.id
}
