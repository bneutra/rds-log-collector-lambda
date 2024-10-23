
resource "aws_sns_topic" "rds-events" {
  name = local.lambda_name
}

resource "aws_sns_topic_subscription" "rds-events" {
  topic_arn = aws_sns_topic.rds-events.arn
  protocol  = "lambda"
  endpoint  = module.rds_lambda.lambda_function_arn
}

resource "aws_lambda_permission" "allow_sns_invoke_lambda" {
  statement_id  = "AllowSNSInvokeLambda"
  action        = "lambda:InvokeFunction"
  function_name = module.rds_lambda.lambda_function_arn
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.rds-events.arn
}
