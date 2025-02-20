provider "aws" {
  region = "us-east-2"  
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
