import json
import boto3
import requests
from datetime import datetime, timedelta
from botocore.exceptions import ClientError

# Initialize AWS clients
dynamodb = boto3.client('dynamodb')
secretsmanager = boto3.client('secretsmanager')
cloudwatch_logs = boto3.client('logs')

# Constants
API_LIMIT_PER_DAY = 10
LOG_GROUP_NAME = "/aws/lambda/JiraManagementFunction"
LOG_STREAM_NAME = f"JiraManagementFunction-{datetime.now().strftime('%Y%m%d%H%M%S')}"

def lambda_handler(event, context):
    try:
        # Extract headers and body
        api_key = event['headers'].get('x-api-key')
        body = json.loads(event['body'])

        if not api_key or not is_valid_api_key(api_key):
            log_event("Unauthorized access attempt", event)
            return respond_with(401, 'Unauthorized')

        # Check rate limits
        if not check_rate_limit(api_key):
            log_event("Rate limit exceeded", event)
            return respond_with(429, 'Rate limit exceeded')

        action = body.get('action')
        if action == 'create_ticket':
            response_payload = create_ticket(body, api_key)
        elif action == 'refine_ticket':
            response_payload = refine_ticket(body, api_key)
        else:
            return respond_with(400, 'Invalid action specified')

        log_event("Request processed successfully", event)
        return respond_with(200, response_payload)

    except Exception as e:
        log_event(f"Error: {str(e)}", event)
        return respond_with(500, 'Internal Server Error')

def is_valid_api_key(api_key):
    try:
        response = dynamodb.get_item(
            TableName='APIKeys',
            Key={'api_key': {'S': api_key}}
        )
        return 'Item' in response
    except ClientError as e:
        log_event(f"DynamoDB Error: {str(e)}", {"api_key": api_key})
        return False

def check_rate_limit(api_key):
    today = datetime.utcnow().strftime('%Y-%m-%d')
    try:
        response = dynamodb.get_item(
            TableName='APIKeys',
            Key={'api_key': {'S': api_key}}
        )
        usage = response['Item'].get('usage', {}).get(today, {'N': '0'})['N']
        if int(usage) >= API_LIMIT_PER_DAY:
            return False
        dynamodb.update_item(
            TableName='APIKeys',
            Key={'api_key': {'S': api_key}},
            UpdateExpression=f"SET #usage.#today = :new_usage",
            ExpressionAttributeNames={
                '#usage': 'usage',
                '#today': today
            },
            ExpressionAttributeValues={
                ':new_usage': {'N': str(int(usage) + 1)}
            }
        )
        return True
    except ClientError as e:
        log_event(f"DynamoDB Error: {str(e)}", {"api_key": api_key})
        return False

def create_ticket(body, api_key):
    prompt = body['prompt']
    template_url = body.get('template_url', '')
    template = get_template(template_url)

    # Generate the JIRA ticket using OpenAI
    new_ticket = generate_ticket(prompt, template)

    # Return the generated ticket details
    return {
        'ticket_details': new_ticket,
        'message': 'JIRA ticket created successfully'
    }

def refine_ticket(body, api_key):
    ticket_name = body['ticket_name']
    prompt = body['prompt']
    template_url = body.get('template_url', '')
    template = get_template(template_url)

    # Refine the existing ticket using OpenAI
    refined_ticket = generate_ticket(prompt, template)

    # Return the refined ticket details
    return {
        'ticket_name': ticket_name,
        'refined_ticket_details': refined_ticket,
        'message': 'JIRA ticket refined successfully'
    }

def get_template(template_url):
    if template_url.startswith("file://"):
        file_path = template_url[7:]
        with open(file_path, 'r') as file:
            return file.read()
    else:
        response = requests.get(template_url)
        return response.text

def generate_ticket(prompt, template):
    secret = secretsmanager.get_secret_value(SecretId="azure_openai_api_key")
    openai_api_key = secret['SecretString']

    combined_prompt = f"Generate a JIRA ticket: {template}\nDetails: {prompt}"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {openai_api_key}',
    }

    response = requests.post(
        'https://api.openai.com/v1/completions',
        headers=headers,
        json={
            'model': 'text-davinci-003',
            'prompt': combined_prompt,
            'temperature': 0.7,
            'max_tokens': 4000,
        }
    )

    return response.json().get('choices', [{}])[0].get('text', 'No response from OpenAI')

def respond_with(status_code, body):
    return {
        'statusCode': status_code,
        'body': json.dumps(body),
        'headers': {
            'Content-Type': 'application/json',
        },
    }

def log_event(message, event):
    log_data = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'message': message,
        'event': event
    }
    cloudwatch_logs.put_log_events(
        logGroupName=LOG_GROUP_NAME,
        logStreamName=LOG_STREAM_NAME,
        logEvents=[
            {
                'timestamp': int(datetime.now().timestamp() * 1000),
                'message': json.dumps(log_data)
            }
        ]
    )
