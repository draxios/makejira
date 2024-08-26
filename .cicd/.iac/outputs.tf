output "jira_api_url" {
  value = "${aws_api_gateway_rest_api.jira_api.execution_arn}/jira"
}
