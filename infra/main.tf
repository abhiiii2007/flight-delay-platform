terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.57"
    }
  }
}

provider "aws" { region = var.aws_region }

resource "aws_vpc" "main" {
  cidr_block           = "10.40.0.0/16"
  enable_dns_hostnames = true
  tags                 = { Name = "${var.project_name}-vpc" }
}

data "aws_availability_zones" "available" { state = "available" }

resource "aws_subnet" "database" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.40.${count.index + 1}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  tags              = { Name = "${var.project_name}-db-${count.index + 1}" }
}

resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-database"
  subnet_ids = aws_subnet.database[*].id
}

resource "aws_security_group" "database" {
  name   = "${var.project_name}-database"
  vpc_id = aws_vpc.main.id
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_s3_bucket" "data" {
  bucket_prefix = "${var.project_name}-data-"
}

resource "aws_s3_bucket_versioning" "data" {
  bucket = aws_s3_bucket.data.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data" {
  bucket = aws_s3_bucket.data.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "data" {
  bucket                  = aws_s3_bucket.data.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_db_instance" "postgres" {
  identifier                   = "${var.project_name}-postgres"
  engine                       = "postgres"
  engine_version               = "16"
  instance_class               = "db.t4g.micro"
  allocated_storage            = 20
  storage_encrypted            = true
  db_name                      = "flightpulse"
  username                     = var.db_username
  manage_master_user_password  = true
  db_subnet_group_name         = aws_db_subnet_group.main.name
  vpc_security_group_ids       = [aws_security_group.database.id]
  publicly_accessible          = false
  backup_retention_period      = 1
  skip_final_snapshot          = true
  deletion_protection          = false
}

resource "aws_budgets_budget" "monthly" {
  name         = "${var.project_name}-monthly-limit"
  budget_type  = "COST"
  limit_amount = "15"
  limit_unit   = "USD"
  time_unit    = "MONTHLY"
}

output "data_bucket" {
  value = aws_s3_bucket.data.id
}

output "database_endpoint" {
  value = aws_db_instance.postgres.address
}

output "database_secret_arn" {
  value     = aws_db_instance.postgres.master_user_secret[0].secret_arn
  sensitive = true
}
