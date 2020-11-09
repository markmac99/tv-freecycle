# powershell script to build and deploy the lambda function
# 
# remember to set AWS credentials  before running this or it'll fail
# $env:AWS_ACCESS_KEY_ID=....
# $env:AWS_SECRET_ACCESS_KEY=....
#
$env:AWS_DEFAULT_REGION="eu-west-1"

compress-archive -path .\*.py -destinationpath .\function.zip -update
aws lambda update-function-code --function-name freecycleHandler --zip-file fileb://function.zip
