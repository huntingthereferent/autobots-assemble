variable "aws_region" {
  description = "AWS region for the platform."
  type        = string
  default     = "us-east-1"
}

variable "container_image" {
  description = "Immutable container image URI for API, worker, and beat."
  type        = string
}

variable "database_url_secret_arn" {
  description = "Secrets Manager ARN containing the full DATABASE_URL."
  type        = string
  sensitive   = true
}

variable "redis_url_secret_arn" {
  description = "Secrets Manager ARN containing the full REDIS_URL."
  type        = string
  sensitive   = true
}

variable "desired_api_count" {
  type    = number
  default = 2
}

variable "desired_worker_count" {
  type    = number
  default = 1
}
