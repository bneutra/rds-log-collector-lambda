locals {
    db_instance_name = "dev-infrateam1b-migration-2022-08-02-12-27-01"

}
resource "aws_sns_topic" "rds-events" {
  name = var.prefix
}

resource "aws_sns_topic_subscription" "rds-events" {
  topic_arn = aws_sns_topic.rds-events.arn
  protocol  = "lambda"
  endpoint  = module.webhook.lambda_function_arn
}

resource "aws_lambda_permission" "allow_sns_invoke_lambda" {
  statement_id  = "AllowSNSInvokeLambda"
  action        = "lambda:InvokeFunction"
  function_name = module.webhook.lambda_function_arn
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.rds-events.arn
}

# TODO: add this resource to each RDS database
# lookup the sns topic with a data source
resource "aws_db_event_subscription" "default" {
  name      = var.prefix
  sns_topic = aws_sns_topic.rds-events.arn

  source_type = "db-instance"
  source_ids  = [local.db_instance_name]

  event_categories = [
    "availability",
    "deletion",
    "failover",
    "failure",
    "low storage",
    "maintenance",
    "notification",
    "read replica",
    "recovery",
    "restoration",
  ]
}
