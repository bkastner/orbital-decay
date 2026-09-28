variable "budget_alert_email" {
  type        = string
  description = "Email address that receives AWS Budgets alerts. Set in terraform.tfvars (gitignored)."
}

variable "budget_test_alert" {
  type        = bool
  description = "Temporarily add a $0.01 actual-spend alert to confirm budget emails are delivered."
  default     = false
}
