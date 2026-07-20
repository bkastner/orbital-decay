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

resource "aws_ecs_cluster" "orbital-decay-cluster" {
  name = "orbital-decay-cluster"
  configuration {
    execute_command_configuration {
      logging = "DEFAULT"
    }
  }
  setting {
    name  = "containerInsights"
    value = "disabled"
  }
}

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
    image            = "${aws_ecr_repository.orbital_decay.repository_url}:${var.image_tag}"
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
  execution_role_arn       = "arn:aws:iam::864144288881:role/ecsTaskExecutionRole"
  family                   = "orbital-decay-task"
  memory                   = "8192"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  skip_destroy             = true
  task_role_arn            = aws_iam_role.task_role.arn
  track_latest             = false
  runtime_platform {
    cpu_architecture        = "ARM64"
    operating_system_family = "LINUX"
  }
}
