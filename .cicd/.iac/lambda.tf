resource "aws_lambda_function" "jira_function" {
  filename         = "function.zip"
  function_name    = "JiraManagementFunction"
  role             = aws_iam_role.lambda_exec_role.arn
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.9"
  source_code_hash = filebase64sha256("function.zip")
  environment {
    variables = {
      DYNAMODB_TABLE_NAME = aws_dynamodb_table.api_keys.name
      SECRET_ID           = aws_secretsmanager_secret.openai_api_key.id
      API_LIMIT_PER_DAY   = var.api_limit_per_day
    }
  }
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.jira_function.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.jira_api.execution_arn}/*/*"
}
