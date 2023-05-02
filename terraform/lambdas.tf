# Freecycle Lambdas

data "archive_file" "freecycle_lambda_zip" {
  type        = "zip"
  source_dir  = "${path.root}/files/freecycle/"
  output_path = "${path.root}/files/freecycle.zip"
}

resource "aws_lambda_function" "freecycle_lambda" {
  function_name    = "freecycleHandler"
  provider = aws.euw1-prov
  description      = "Triggered when email is recieved for Freecycle"
  filename         = data.archive_file.freecycle_lambda_zip.output_path
  source_code_hash = data.archive_file.freecycle_lambda_zip.output_base64sha256
  handler          = "lambda_handler.lambda_handler"
  runtime          = "python3.8"
  memory_size      = 256
  timeout          = 900
  role             = aws_iam_role.lambdatriggerrole.arn
  publish          = false
  environment {
    variables = {
      "INDEXFILE" = "freecycle-data.csv"
      "INDEXFLDR" = "fslist"
      "TMP" = "/tmp"
    }
  }
  ephemeral_storage {
    size = 512
  }
  tags = {
    Name       = "freecycleHandler"
    billingtag = "freecycle"
  }
}

data "archive_file" "toycycle_lambda_zip" {
  type        = "zip"
  source_dir  = "${path.root}/files/freecycle/"
  output_path = "${path.root}/files/toycycle.zip"
}

resource "aws_lambda_function" "toycycle_lambda" {
  function_name    = "toycycleHandler"
  provider = aws.euw1-prov
  description      = "Triggered when email is recieved for Toycycle"
  filename         = data.archive_file.toycycle_lambda_zip.output_path
  source_code_hash = data.archive_file.toycycle_lambda_zip.output_base64sha256
  handler          = "lambda_handler.lambda_handler"
  runtime          = "python3.8"
  memory_size      = 256
  timeout          = 900
  role             = aws_iam_role.lambdatriggerrole.arn
  publish          = false
  environment {
    variables = {
      "INDEXFILE" = "toycycle-data.csv"
      "INDEXFLDR" = "tslist"
      "TMP" = "/tmp"
    }
  }
  ephemeral_storage {
    size = 512
  }
  tags = {
    Name       = "toycycleHandler"
    billingtag = "freecycle"
  }
}
