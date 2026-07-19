# Read the current account ID and region from AWS rather than hardcoding.
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  account_id           = data.aws_caller_identity.current.account_id
  region               = data.aws_region.current.region
  frontend_bucket_name = "orbital-decay-frontend-864144288881-us-west-2-an"
}
