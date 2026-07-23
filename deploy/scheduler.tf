resource "aws_scheduler_schedule" "omm_refresh" {
  action_after_completion      = "NONE"
  description                  = "Get new OMM data for the orbital-decay-app and update propagations"
  group_name                   = "default"
  name                         = "orbital-decay-refresh-omm"
  schedule_expression          = "rate(12 hours)"
  schedule_expression_timezone = "America/Denver"
  state                        = "ENABLED"
  flexible_time_window {
    mode = "OFF"
  }
  target {
    arn      = local.ecs_cluster_arn
    role_arn = local.scheduler_role_arn
    ecs_parameters {
      enable_ecs_managed_tags = true
      enable_execute_command  = false
      launch_type             = "FARGATE"
      platform_version        = "LATEST"
      task_count              = 1
      task_definition_arn     = aws_ecs_task_definition.app.arn
      network_configuration {
        assign_public_ip = true
        security_groups  = ["sg-0a4f5ee0bd21e59a8"]
        subnets          = ["subnet-0471b67dd775ab38a", "subnet-0e2f22ef9faec9748"]
      }
    }
    retry_policy {
      maximum_event_age_in_seconds = 86400
      maximum_retry_attempts       = 0
    }
  }
}
