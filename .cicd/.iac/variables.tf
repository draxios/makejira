variable "region" {
  description = "The AWS region where resources will be created"
  type        = string
  default     = "us-east-1"
}

variable "api_limit_per_day" {
  description = "API request limit per day per API key"
  type        = number
  default     = 10
}
