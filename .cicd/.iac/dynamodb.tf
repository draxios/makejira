resource "aws_dynamodb_table" "api_keys" {
  name           = "APIKeys"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "api_key"

  attribute {
    name = "api_key"
    type = "S"
  }
}
