resource "aws_ecr_repository" "app" {
  name                 = "state-reconciliation-platform"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecs_cluster" "main" {
  name = "state-reconciliation-platform"
}

resource "aws_cloudwatch_log_group" "api" {
  name              = "/ecs/state-reconciliation/api"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "worker" {
  name              = "/ecs/state-reconciliation/worker"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "beat" {
  name              = "/ecs/state-reconciliation/beat"
  retention_in_days = 30
}

locals {
  common_secrets = [
    {
      name      = "DATABASE_URL"
      valueFrom = var.database_url_secret_arn
    },
    {
      name      = "REDIS_URL"
      valueFrom = var.redis_url_secret_arn
    },
  ]

  log_options = {
    awslogs-region        = var.aws_region
    awslogs-stream-prefix = "ecs"
  }
}

resource "aws_ecs_task_definition" "api" {
  family                   = "state-reconciliation-api"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = "api"
      image     = var.container_image
      essential = true
      command   = ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
          protocol      = "tcp"
        }
      ]
      secrets = local.common_secrets
      logConfiguration = {
        logDriver = "awslogs"
        options   = merge(local.log_options, { awslogs-group = aws_cloudwatch_log_group.api.name })
      }
    }
  ])
}

resource "aws_ecs_task_definition" "worker" {
  family                   = "state-reconciliation-worker"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = "worker"
      image     = var.container_image
      essential = true
      command   = ["celery", "-A", "app.celery_app.celery_app", "worker", "--loglevel=INFO"]
      secrets   = local.common_secrets
      logConfiguration = {
        logDriver = "awslogs"
        options   = merge(local.log_options, { awslogs-group = aws_cloudwatch_log_group.worker.name })
      }
    }
  ])
}

resource "aws_ecs_task_definition" "beat" {
  family                   = "state-reconciliation-beat"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = "beat"
      image     = var.container_image
      essential = true
      command   = ["celery", "-A", "app.celery_app.celery_app", "beat", "--loglevel=INFO"]
      secrets   = local.common_secrets
      logConfiguration = {
        logDriver = "awslogs"
        options   = merge(local.log_options, { awslogs-group = aws_cloudwatch_log_group.beat.name })
      }
    }
  ])
}

resource "aws_ecs_service" "api" {
  name            = "api"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = var.desired_api_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.api.arn
    container_name   = "api"
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.https]
}

resource "aws_ecs_service" "worker" {
  name            = "worker"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.worker.arn
  desired_count   = var.desired_worker_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = false
  }
}

resource "aws_ecs_service" "beat" {
  name            = "beat"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.beat.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = false
  }
}
