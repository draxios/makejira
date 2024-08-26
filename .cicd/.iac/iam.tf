resource "aws_iam_role" "lambda_exec_role" {
  name = "jira_lambda_exec_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        },
      },
    ],
  })
}

resource "aws_iam_role_policy" "lambda_exec_policy" {
  name = "jira_lambda_exec_policy"
  role = aws_iam_role.lambda_exec_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "dynamodb:GetItem",
          "dynamodb:UpdateItem",
          "secretsmanager:GetSecretValue",
          "logs:*",
          "lambda:InvokeFunction"
        ],
        Effect   = "Allow",
        Resource = "*",
      },
    ],
  })
}
