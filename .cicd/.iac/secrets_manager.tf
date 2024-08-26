resource "aws_secretsmanager_secret" "openai_api_key" {
  name = "azure_openai_api_key"
}

resource "aws_secretsmanager_secret_version" "openai_api_key_version" {
  secret_id     = aws_secretsmanager_secret.openai_api_key.id
  secret_string = "<YOUR_OPENAI_API_KEY>"
}
