resource "aws_cloudwatch_log_group" "ecs_task" {
  log_group_class   = "STANDARD"
  name              = "/ecs/orbital-decay-task"
  retention_in_days = 60
}
