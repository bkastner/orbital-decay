resource "aws_ecs_task_definition" "app" {
  container_definitions = jsonencode([{
    environment = [{
      name  = "CELESTRAK_ENDPOINT_URL"
      value = "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=csv"
      }, {
      name  = "S3_BUCKET_NAME"
      value = local.frontend_bucket_name
      }, {
      name  = "WORKER_COUNT"
      value = "8"
    }]
    environmentFiles = []
    essential        = true
    image            = "${local.ecr_repository_url}:${var.image_tag}"
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-create-group  = "true"
        awslogs-group         = "/ecs/orbital-decay-task"
        awslogs-region        = "us-west-2"
        awslogs-stream-prefix = "ecs"
      }
      secretOptions = []
    }
    mountPoints = []
    name        = "orbital-decay-app"
    portMappings = [{
      appProtocol   = "http"
      containerPort = 80
      hostPort      = 80
      name          = "orbital-decay-app-80-tcp"
      protocol      = "tcp"
    }]
    systemControls = []
    ulimits        = []
    volumesFrom    = []
  }])
  cpu                      = "4096"
  enable_fault_injection   = false
  execution_role_arn       = local.execution_role_arn
  family                   = "orbital-decay-task"
  memory                   = "8192"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  skip_destroy             = true
  task_role_arn            = local.task_role_arn
  track_latest             = false
  runtime_platform {
    cpu_architecture        = "ARM64"
    operating_system_family = "LINUX"
  }
}