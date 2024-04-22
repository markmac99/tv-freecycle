resource "aws_iam_role" "lambdatriggerrole" {
  name        = "S3LambdaTriggerRole"
  description = "Allows Lambda functions to call AWS services on your behalf."
  assume_role_policy = jsonencode(
    {
      Statement = [
        {
          Action = "sts:AssumeRole"
          Effect = "Allow"
          Principal = {
            Service = "lambda.amazonaws.com"
          }
        },
      ]
      Version = "2012-10-17"
    }
  )
  tags = {
    "billingtag" = "freecycle"
    "creator" = "mark"
  }
}

resource "aws_iam_role_policy_attachment" "lambdatriggerrole_polatt" {
  role       = aws_iam_role.lambdatriggerrole.name
  policy_arn = aws_iam_policy.freecycle_policy.arn
}

resource "aws_iam_policy" "freecycle_policy" {
  name = "PolicyForFreecycle"
  policy = jsonencode(
    {
      Statement = [
        {
          Action = [
            #"logs:FilterLogEvents",
            #"logs:GetLogEvents",
            "logs:*",
            "s3:*",
            "s3-object-lambda:*",
          ]
          Effect = "Allow"
          Resource = [
            "*",
          ]
        }
      ]
      Version = "2012-10-17"
    }
  )
  tags = {
    "billingtag" = "ukmon"
  }
}

# lambda permissions to allow functions to be executed from ses
resource "aws_lambda_permission" "perm_freecycle_lambda" {
  statement_id   = "allowSesInvoke"
  action         = "lambda:InvokeFunction"
  provider       = aws.euw1-prov
  function_name  = data.aws_lambda_function.freecycle_lambda.arn
  principal      = "ses.amazonaws.com"
  source_account = "317976261112"
  #source_arn     = aws_s3_bucket.tv-freecycle.arn
}

# lambda permissions to allow functions to be executed from ses
resource "aws_lambda_permission" "perm_toycycle_lambda" {
  statement_id   = "allowSesInvoke"
  action         = "lambda:InvokeFunction"
  provider       = aws.euw1-prov
  function_name  = data.aws_lambda_function.toycycle_lambda.arn
  principal      = "ses.amazonaws.com"
  source_account = "317976261112"
  #source_arn     = aws_s3_bucket.tv-freecycle.arn
}
