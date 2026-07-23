terraform {
  required_version = ">= 1.10"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 6.0" }
  }
  backend "s3" {
    bucket       = "orbital-decay-tfstate-864144288881"
    key          = "orbital-decay/deploy.tfstate"
    region       = "us-west-2"
    encrypt      = true
    use_lockfile = true
  }
}