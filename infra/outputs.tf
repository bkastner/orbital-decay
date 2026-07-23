output "ecr_repository_url" {
  value = aws_ecr_repository.orbital_decay.repository_url
}
output "ecs_cluster_arn" {
  value = aws_ecs_cluster.orbital-decay-cluster.arn
}
output "task_role_arn" {
  value = aws_iam_role.task_role.arn
}
output "frontend_bucket_name" {
  value = local.frontend_bucket_name
}