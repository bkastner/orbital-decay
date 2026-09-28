# Account-wide monthly cost guardrail (see docs/adr/0001-airflow-orchestration.md).
# A single budget carries both thresholds, staying within the free budget allowance.
resource "aws_budgets_budget" "monthly" {
  name         = "orbital-decay-monthly"
  budget_type  = "COST"
  limit_amount = "20"
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 15
    threshold_type             = "ABSOLUTE_VALUE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = [var.budget_alert_email]
  }

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 20
    threshold_type             = "ABSOLUTE_VALUE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = [var.budget_alert_email]
  }

  # Early warning: month-end forecast exceeds the ceiling.
  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 20
    threshold_type             = "ABSOLUTE_VALUE"
    notification_type          = "FORECASTED"
    subscriber_email_addresses = [var.budget_alert_email]
  }

  # AWS has no "send test notification" button. Enable once to confirm delivery, then disable.
  dynamic "notification" {
    for_each = var.budget_test_alert ? [1] : []
    content {
      comparison_operator        = "GREATER_THAN"
      threshold                  = 0.01
      threshold_type             = "ABSOLUTE_VALUE"
      notification_type          = "ACTUAL"
      subscriber_email_addresses = [var.budget_alert_email]
    }
  }
}
