# copyright Mark McIntyre, 2024-

# set Cloudwatch loggroup retentions

resource "aws_cloudwatch_log_group" "freecycle" {
  provider      = aws.euw1-prov
  name = "/aws/lambda/freecycle_handler"
  retention_in_days = 30
  lifecycle {
    create_before_destroy = true
    prevent_destroy       = false
  }
}

resource "aws_cloudwatch_log_group" "toycycle" {
  provider      = aws.euw1-prov
  name = "/aws/lambda/toycycle_handler"
  retention_in_days = 30
  lifecycle {
    create_before_destroy = true
    prevent_destroy       = false
  }
}