terraform {
  backend "s3" {
    bucket         = "healthcare-ops-state" # Tells terraform to store its memory in this s3 bucket
    key            = "state/terraform.tfstate"
    region         = "af-south-1"
    encrypt        = true  # Encryption is mandatory for healthcare state files
  }
}