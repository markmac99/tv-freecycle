# SES rules to manage email forwarding

data "aws_ses_active_receipt_rule_set" "active_rs" {
  provider      = aws.euw1-prov
  #rule_set_name = "default-rule-set"
}

# lambdas created by AWS SAM
data "aws_lambda_function" "toycycle_lambda" {
  provider      = aws.euw1-prov
  function_name = "toycycle_handler"
}

data "aws_lambda_function" "freecycle_lambda" {
  provider      = aws.euw1-prov
  function_name = "freecycle_handler"
}

resource "aws_ses_receipt_rule" "freecycle" {
  provider      = aws.euw1-prov
  name          = "Save-Freecycle"
  rule_set_name = data.aws_ses_active_receipt_rule_set.active_rs.rule_set_name
  recipients    = ["a1234@marymcintyreastronomy.co.uk"]
  enabled       = true
  scan_enabled  = true

  s3_action {
    bucket_name       = aws_s3_bucket.tv-freecycle.id
    object_key_prefix = "freecycle/"
    position          = 1
  }
  lambda_action {
    function_arn    = data.aws_lambda_function.freecycle_lambda.arn
    invocation_type = "Event"
    position        = 2
  }
}

resource "aws_ses_receipt_rule" "toycycle" {
  provider      = aws.euw1-prov
  name          = "Save-Toycycle"
  rule_set_name = data.aws_ses_active_receipt_rule_set.active_rs.rule_set_name
  recipients    = ["toycycle@marymcintyreastronomy.co.uk"]
  enabled       = true
  scan_enabled  = true

  s3_action {
    bucket_name       = aws_s3_bucket.tv-freecycle.id
    object_key_prefix = "freecycle/"
    position          = 1
  }
  lambda_action {
    function_arn    = data.aws_lambda_function.toycycle_lambda.arn
    invocation_type = "Event"
    position        = 2
  }
}
