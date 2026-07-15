resource "aws_s3_bucket" "frontend" {
  bucket        = "orbital-decay-frontend-864144288881-us-west-2-an"
  force_destroy = false
  lifecycle {
    prevent_destroy = true
  }
}