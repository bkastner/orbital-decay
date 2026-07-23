resource "aws_iam_openid_connect_provider" "github" {
  url            = "https://token.actions.githubusercontent.com"
  client_id_list = ["sts.amazonaws.com"]
}


resource "aws_iam_role" "github_deploy" {
  name        = "orbital-decay-github-deploy"
  description = "Assumed by GitHub Actions (bkastner/orbital-decay, main only) to run terraform apply."

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Federated = aws_iam_openid_connect_provider.github.arn }
      Action    = "sts:AssumeRoleWithWebIdentity"
      Condition = {
        StringEquals = {
          "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          "token.actions.githubusercontent.com:sub" = "repo:bkastner/orbital-decay:ref:refs/heads/main"
        }
      }
    }]
  })
}

# Least-privilege deploy policy. Scoped to exactly what the deploy/ root module
# touches: push an image, register a task definition revision, repoint the
# schedule at it, and read/write its own state.
resource "aws_iam_policy" "github_deploy" {
  name        = "OrbitalDecayGitHubDeployPolicy"
  description = "Allows GitHub Actions to build, push, and apply the deploy/ root module."

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "EcrAuth"
        Effect   = "Allow"
        Action   = ["ecr:GetAuthorizationToken"]
        Resource = "*"
      },
      {
        Sid    = "EcrPush"
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:CompleteLayerUpload",
          "ecr:InitiateLayerUpload",
          "ecr:PutImage",
          "ecr:UploadLayerPart",
          "ecr:BatchGetImage",
          "ecr:DescribeImages",
        ]
        Resource = aws_ecr_repository.orbital_decay.arn
      },
      {
        Sid    = "TaskDefinitions"
        Effect = "Allow"
        Action = [
          "ecs:RegisterTaskDefinition",
          "ecs:DescribeTaskDefinition",
          "ecs:DeregisterTaskDefinition",
          "ecs:TagResource",
        ]
        Resource = "*"
      },
      {
        Sid    = "PassExecutionAndTaskRoles"
        Effect = "Allow"
        Action = ["iam:PassRole"]
        Resource = [
          "arn:aws:iam::${local.account_id}:role/ecsTaskExecutionRole",
          aws_iam_role.task_role.arn,
        ]
      },
      {
        Sid    = "Scheduler"
        Effect = "Allow"
        Action = [
          "scheduler:GetSchedule",
          "scheduler:UpdateSchedule",
        ]
        Resource = "arn:aws:scheduler:${local.region}:${local.account_id}:schedule/default/orbital-decay-refresh-omm"
      },
      {
        Sid      = "PassSchedulerRole"
        Effect   = "Allow"
        Action   = ["iam:PassRole"]
        Resource = "arn:aws:iam::${local.account_id}:role/service-role/Amazon_EventBridge_Scheduler_ECS_4035645f48"
      },
      {
        Sid    = "DeployStateReadWrite"
        Effect = "Allow"
        Action = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
        Resource = [
          "arn:aws:s3:::orbital-decay-tfstate-${local.account_id}/orbital-decay/deploy.tfstate",
          "arn:aws:s3:::orbital-decay-tfstate-${local.account_id}/orbital-decay/deploy.tfstate.tflock",
        ]
      },
      {
        Sid      = "InfraStateReadOnly"
        Effect   = "Allow"
        Action   = ["s3:GetObject"]
        Resource = "arn:aws:s3:::orbital-decay-tfstate-${local.account_id}/orbital-decay/terraform.tfstate"
      },
      {
        Sid      = "StateBucketList"
        Effect   = "Allow"
        Action   = ["s3:ListBucket"]
        Resource = "arn:aws:s3:::orbital-decay-tfstate-${local.account_id}"
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "github_deploy" {
  role       = aws_iam_role.github_deploy.name
  policy_arn = aws_iam_policy.github_deploy.arn
}

output "github_deploy_role_arn" {
  description = "Role ARN for the GitHub Actions deploy workflow to assume."
  value       = aws_iam_role.github_deploy.arn
}