resource "aws_iam_role_policy_attachment" "task_role_s3" {
  policy_arn = "arn:aws:iam::864144288881:policy/OrbitalDecayS3UploadPolicy"
  role       = "OrbitalDecayFargateTaskRole"
}

resource "aws_iam_policy" "s3_upload" {
  description                       = "Policy to allow upload from compute container to S3 bucket"
  name                              = "OrbitalDecayS3UploadPolicy"
  path                              = "/"
  policy = jsonencode({
    Statement = [{
      Action   = ["s3:PutObject"]
      Effect   = "Allow"
      Resource = "arn:aws:s3:::orbital-decay-frontend-864144288881-us-west-2-an/decays.geojson"
      Sid      = "AllowGeoJsonUpload"
    }]
    Version = "2012-10-17"
  })
}

resource "aws_iam_role" "task_role" {
  assume_role_policy = jsonencode({
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
      Sid = ""
    }]
    Version = "2012-10-17"
  })
  description           = "Allows ECS to upload to S3"
  force_detach_policies = false
  max_session_duration  = 3600
  name                  = "OrbitalDecayFargateTaskRole"
  path                  = "/"
}
