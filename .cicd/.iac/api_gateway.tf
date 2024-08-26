resource "aws_api_gateway_rest_api" "jira_api" {
  name        = "jira-management-api"
  description = "API Gateway for JIRA Management"
}

resource "aws_api_gateway_resource" "jira" {
  rest_api_id = aws_api_gateway_rest_api.jira_api.id
  parent_id   = aws_api_gateway_rest_api.jira_api.root_resource_id
  path_part   = "jira"
}

resource "aws_api_gateway_method" "jira_post" {
  rest_api_id   = aws_api_gateway_rest_api.jira_api.id
  resource_id   = aws_api_gateway_resource.jira.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "jira_integration" {
  rest_api_id = aws_api_gateway_rest_api.jira_api.id
  resource_id = aws_api_gateway_resource.jira.id
  http_method = aws_api_gateway_method.jira_post.http_method
  type        = "AWS_PROXY"
  uri         = aws_lambda_function.jira_function.invoke_arn
}

resource "aws_api_gateway_deployment" "jira_deployment" {
  rest_api_id = aws_api_gateway_rest_api.jira_api.id
  stage_name  = "prod"

  depends_on = [
    aws_api_gateway_integration.jira_integration,
  ]
}
