resource "aws_vpc" "healthcare_vpc" {
  cidr_block = "10.0.0.0/16"

  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Terraform    = "true"
    Environment = "dev"
  }
}

resource "aws_subnet" "healthcare_public_subnet" {
  vpc_id                  = aws_vpc.healthcare_vpc.id
  cidr_block              = "10.0.101.0/24"
  map_public_ip_on_launch   = true

  tags = {
    Name = "healthcare-public-subnet"
  }
}

resource "aws_subnet" "healthcare_private_subnet_a" {
  vpc_id            = aws_vpc.healthcare_vpc.id
  cidr_block        = "10.0.102.0/24"
  availability_zone = "af-south-1a"

  tags = {
    Name = "healthcare-private-subnet-a"
  }
}

resource "aws_subnet" "healthcare_private_subnet_b" {
  vpc_id            = aws_vpc.healthcare_vpc.id
  cidr_block        = "10.0.103.0/24"
  availability_zone = "af-south-1b"

  tags = {
    Name = "healthcare-private-subnet-b"
  }
}

resource "aws_db_subnet_group" "db_subnet_group" {
  name       = "healthcare-db-subnet-group"
  subnet_ids = [aws_subnet.healthcare_private_subnet_a.id, aws_subnet.healthcare_private_subnet_b.id]

  tags = {
    Name = "healthcare-db-subnet-group"
  }
}

resource "aws_internet_gateway" "healthcare_igw" {
  vpc_id = aws_vpc.healthcare_vpc.id

  tags = {
    Name = "healthcare-igw"
  }
}

resource "aws_route_table" "healthcare_public_rt" {
  vpc_id = aws_vpc.healthcare_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.healthcare_igw.id
  }

  tags = {
    Name = "healthcare-public-route-table"
  }
}

resource "aws_route_table_association" "healthcare_public_association" {
  subnet_id      = aws_subnet.healthcare_public_subnet.id
  route_table_id = aws_route_table.healthcare_public_rt.id
}
