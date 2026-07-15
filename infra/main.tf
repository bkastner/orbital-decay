# Resources will be added here as we import them, then split into
# per-domain files (storage.tf, compute.tf, etc.) as the config grows.

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
