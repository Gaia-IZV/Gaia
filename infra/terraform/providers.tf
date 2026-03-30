terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.31.0"
    }
    null = {
      source  = "hashicorp/null"
      version = ">= 3.2.2"
    }
  }
}

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Application = "Gaia"
      Owner       = "Erik Tortajada"
    }
  }
}
