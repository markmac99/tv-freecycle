# powershell script to build and deploy the lambda function
# 
# remember to set AWS credentials  before running this or it'll fail
# $env:AWS_ACCESS_KEY_ID=....
# $env:AWS_SECRET_ACCESS_KEY=....
#
$env:AWS_DEFAULT_REGION="eu-west-1"

Copy-Item .\fsconfig.py .\config.py
compress-archive -literalpath .\lambda_handler.py, .\updateCSV.py, .\config.py -destinationpath .\freecycle.zip -update
aws lambda update-function-code --function-name freecycleHandler --zip-file fileb://freecycle.zip

Copy-Item .\tsconfig.py .\config.py
compress-archive -literalpath .\lambda_handler.py, .\updateCSV.py, .\config.py -destinationpath .\toycycle.zip -update
aws lambda update-function-code --function-name toycycleHandler --zip-file fileb://toycycle.zip

Copy-Item .\fsconfig.py .\config.py
