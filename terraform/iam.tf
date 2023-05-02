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


