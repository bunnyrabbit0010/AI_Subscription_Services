provider "aws" {
  region = "us-east-2"  
}

variable "availability_zones" {
  default = ["us-east-2a", "us-east-2b", "us-east-2c"]
}

resource "aws_vpc" "dev_subs_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "dev-subs-vpc"
    Project     = "subscription_services"
    Environment = "development"
 
  }
}

resource "aws_subnet" "dev_subs_private_subnet" {
  count             = length(var.availability_zones)
  vpc_id            = aws_vpc.dev_subs_vpc.id
  cidr_block        = cidrsubnet(aws_vpc.dev_subs_vpc.cidr_block, 8, count.index)
  availability_zone = var.availability_zones[count.index]

  tags = {
    Name = "dev-subs-private-subnet-${var.availability_zones[count.index]}"
    Project     = "subscription_services"
    Environment = "development"
  }
}

resource "aws_route_table" "dev_subs_private_rt" {
  vpc_id = aws_vpc.dev_subs_vpc.id

  tags = {
    Name = "dev-subs-private-rt"
    Project     = "subscription_services"
    Environment = "development"
 
  }
}

resource "aws_route_table_association" "dev_subs_private_rta" {
  count          = length(aws_subnet.dev_subs_private_subnet)
  subnet_id      = aws_subnet.dev_subs_private_subnet[count.index].id
  route_table_id = aws_route_table.dev_subs_private_rt.id
}


resource "aws_docdb_subnet_group" "dev_subs_subnet_group" {
  name       = "dev-subs-docdb-subnet-group"
  subnet_ids = aws_subnet.dev_subs_private_subnet[*].id

  tags = {
    Name = "dev-subs-docdb-subnet-group"
    Project     = "subscription_services"
    Environment = "development"
  }
}

resource "aws_docdb_cluster" "dev_subs_cluster" {
  cluster_identifier      = "dev-subs-docdb-cluster"
  engine                  = "docdb"
  master_username         = "devsubsuser"
  master_password         = "DevSubsPassword123!"   
  preferred_backup_window = "04:00-05:00"
  skip_final_snapshot     = true


  # Use minimal storage for development
  storage_encrypted = false

  # Disable automatic backups to reduce costs
  backup_retention_period = 1

  # Use a small volume size
  storage_type = "standard"

  # Use a custom subnet group
  db_subnet_group_name = aws_docdb_subnet_group.dev_subs_subnet_group.name

  tags = {
    Project     = "subscription_services"
    Environment = "development"
  }
}


resource "aws_docdb_cluster_instance" "dev_subs_instances" {
  count              = 1
  identifier         = "dev-subs-docdb-instance-${count.index}"
  cluster_identifier = aws_docdb_cluster.dev_subs_cluster.id
  instance_class     = "db.t3.medium"

  # Disable performance insights to reduce costs
  enable_performance_insights = false

  tags = {
    Project     = "subscription_services"
    Environment = "development"
  }
}

output "dev_subs_docdb_endpoint" {
  value = aws_docdb_cluster.dev_subs_cluster.endpoint
}

output "dev_subs_docdb_port" {
  value = aws_docdb_cluster.dev_subs_cluster.port
}

resource "aws_dynamodb_table" "subscription_table" {
  name           = "subscription_table"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "title"

  attribute {
    name = "title"
    type = "S"
  }

  attribute {
    name = "main_category"
    type = "S"
  }

  global_secondary_index {
    name               = "MainCategoryIndex"
    hash_key           = "main_category"
    projection_type    = "ALL"
  }

  tags = {
    Project     = "subscription_services"
    Environment = "development"  }
}
