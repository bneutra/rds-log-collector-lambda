provider "aws" {
  region = var.region
}
locals {
  lambda_name = "${var.prefix}-rds-failures"
}

# create webhook
module "webhook" {
  source             = "terraform-aws-modules/lambda/aws"
  version            = "7.4.0"
  function_name      = local.lambda_name
  description        = "Receives RDS SNS events."
  handler            = "main.lambda_handler"
  runtime            = "python3.12"
  policies           = [aws_iam_policy.lambda_policy.arn]
  number_of_policies = 1
  attach_policies    = true
  memory_size        = 1024
  create_role        = true
  role_name          = local.lambda_name
  timeout            = 30
  source_path = [
    {
      path             = "${path.module}/files",
      pip_requirements = "${path.module}/files/requirements.txt"
    }
  ]

  environment_variables = {
    REGION         = var.region
    #S3_BUCKET      = aws_s3_bucket.rds-event-storage.id
  }
  tags = {
    datadog  = true
    service  = local.lambda_name
    CostType = "OpEx-RnD"
  }
}

resource "aws_iam_policy" "lambda_policy" {
  name   = "${var.prefix}-state-saver-lambda-webhook-policy"
  policy = data.aws_iam_policy_document.lambda_policy_definition.json
}

data "aws_iam_policy_document" "lambda_policy_definition" {
  statement {
    effect    = "Allow"
    actions   = ["rds:DownloadDBLogFilePortion"]
    resources = [ "*" ]
  }
    statement {
    effect    = "Allow"
    actions   = ["rds:Describe*"]
    resources = [ "*" ]
  }
}
