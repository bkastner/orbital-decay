resource "aws_ecr_repository" "orbital_decay" {
  image_tag_mutability = "IMMUTABLE"
  name                 = "orbital-decay"
  encryption_configuration {
    encryption_type = "AES256"
  }
  image_scanning_configuration {
    scan_on_push = false
  }
}