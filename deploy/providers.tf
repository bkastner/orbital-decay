provider "aws" {
  region = "us-west-2"
  default_tags {
    tags = {
      ManagedBy = "terraform"
      Project   = "orbital-decay"
    }
  }
}