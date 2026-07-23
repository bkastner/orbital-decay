data "terraform_remote_state" "infra" {
  backend = "s3"
  config = {
    bucket = "orbital-decay-tfstate-864144288881"
    key    = "orbital-decay/terraform.tfstate"
    region = "us-west-2"
  }
}

locals {
  ecr_repository_url   = data.terraform_remote_state.infra.outputs.ecr_repository_url
  ecs_cluster_arn      = data.terraform_remote_state.infra.outputs.ecs_cluster_arn
  task_role_arn        = data.terraform_remote_state.infra.outputs.task_role_arn
  frontend_bucket_name = data.terraform_remote_state.infra.outputs.frontend_bucket_name

  # Pre-existing AWS service roles — not managed by our Terraform.
  execution_role_arn = "arn:aws:iam::864144288881:role/ecsTaskExecutionRole"
  scheduler_role_arn = "arn:aws:iam::864144288881:role/service-role/Amazon_EventBridge_Scheduler_ECS_4035645f48"
}