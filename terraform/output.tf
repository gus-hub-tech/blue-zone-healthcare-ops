output "vpc_id" {
  value       = aws_vpc.healthcare_vpc.id
  description = "The ID of the VPC"
}

output "public_subnet_id" {
  value       = aws_subnet.healthcare_public_subnet.id
  description = "The ID of the public subnet"
}

output "db_endpoint" {
  value       = aws_db_instance.patient_db.endpoint
  description = "The endpoint of the PostgreSQL database"
}

output "db_arn" {
  value       = aws_db_instance.patient_db.arn
  description = "The ARN of the PostgreSQL database"
}
