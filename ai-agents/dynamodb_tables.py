"""
IELTS AI Agents - DynamoDB Table Definitions
Creates tables for Customer Support Agent and DevOps Agent
"""

import boto3
from datetime import datetime

dynamodb = boto3.client('dynamodb', region_name='us-east-1')

def create_support_tickets_table():
    """
    Table: ielts-support-tickets
    Stores customer support tickets with AI responses and escalations
    """
    table_name = 'ielts-support-tickets'
    
    try:
        response = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'ticket_id', 'KeyType': 'HASH'}  # Partition key only
            ],
            AttributeDefinitions=[
                {'AttributeName': 'ticket_id', 'AttributeType': 'S'},
                {'AttributeName': 'created_at', 'AttributeType': 'N'},
                {'AttributeName': 'status', 'AttributeType': 'S'},
                {'AttributeName': 'priority', 'AttributeType': 'S'},
                {'AttributeName': 'user_email', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'status-created_at-index',
                    'KeySchema': [
                        {'AttributeName': 'status', 'KeyType': 'HASH'},
                        {'AttributeName': 'created_at', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                },
                {
                    'IndexName': 'priority-created_at-index',
                    'KeySchema': [
                        {'AttributeName': 'priority', 'KeyType': 'HASH'},
                        {'AttributeName': 'created_at', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                },
                {
                    'IndexName': 'user_email-created_at-index',
                    'KeySchema': [
                        {'AttributeName': 'user_email', 'KeyType': 'HASH'},
                        {'AttributeName': 'created_at', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            BillingMode='PAY_PER_REQUEST',
            StreamSpecification={
                'StreamEnabled': True,
                'StreamViewType': 'NEW_AND_OLD_IMAGES'
            },
            Tags=[
                {'Key': 'Project', 'Value': 'IELTS-AI-Prep'},
                {'Key': 'Component', 'Value': 'Customer-Support'},
                {'Key': 'Environment', 'Value': 'Production'}
            ]
        )
        
        print(f"✅ Created table: {table_name}")
        print(f"   Status: {response['TableDescription']['TableStatus']}")
        return response
        
    except dynamodb.exceptions.ResourceInUseException:
        print(f"⚠️  Table {table_name} already exists")
        return None

def create_devops_actions_table():
    """
    Table: ielts-devops-actions
    Stores DevOps agent actions, diagnoses, and proposed fixes
    """
    table_name = 'ielts-devops-actions'
    
    try:
        response = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'action_id', 'KeyType': 'HASH'}  # Partition key only
            ],
            AttributeDefinitions=[
                {'AttributeName': 'action_id', 'AttributeType': 'S'},
                {'AttributeName': 'timestamp', 'AttributeType': 'N'},
                {'AttributeName': 'status', 'AttributeType': 'S'},
                {'AttributeName': 'affected_service', 'AttributeType': 'S'},
                {'AttributeName': 'ticket_id', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'status-timestamp-index',
                    'KeySchema': [
                        {'AttributeName': 'status', 'KeyType': 'HASH'},
                        {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                },
                {
                    'IndexName': 'affected_service-timestamp-index',
                    'KeySchema': [
                        {'AttributeName': 'affected_service', 'KeyType': 'HASH'},
                        {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                },
                {
                    'IndexName': 'ticket_id-timestamp-index',
                    'KeySchema': [
                        {'AttributeName': 'ticket_id', 'KeyType': 'HASH'},
                        {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            BillingMode='PAY_PER_REQUEST',
            StreamSpecification={
                'StreamEnabled': True,
                'StreamViewType': 'NEW_AND_OLD_IMAGES'
            },
            Tags=[
                {'Key': 'Project', 'Value': 'IELTS-AI-Prep'},
                {'Key': 'Component', 'Value': 'DevOps-Agent'},
                {'Key': 'Environment', 'Value': 'Production'}
            ]
        )
        
        print(f"✅ Created table: {table_name}")
        print(f"   Status: {response['TableDescription']['TableStatus']}")
        return response
        
    except dynamodb.exceptions.ResourceInUseException:
        print(f"⚠️  Table {table_name} already exists")
        return None

def get_table_schemas():
    """
    Returns the schema documentation for both tables
    """
    return {
        'ielts-support-tickets': {
            'partition_key': 'ticket_id (String)',
            'sort_key': 'None',
            'attributes': {
                'ticket_id': 'Unique ticket identifier (hash of email + timestamp)',
                'created_at': 'Unix timestamp when ticket was created',
                'user_email': 'Customer email address',
                'subject': 'Email subject line',
                'message': 'Original customer message',
                'category': 'Auto-classified: purchase, qr_code, audio, access, refund, technical',
                'priority': 'urgent, high, normal, low',
                'status': 'new, in_progress, resolved, escalated',
                'ai_response': 'Auto-generated response from Customer Support Agent',
                'ai_confidence': 'Confidence score 0.0-1.0',
                'escalated_at': 'Unix timestamp when escalated to DevOps',
                'resolved_at': 'Unix timestamp when resolved',
                'human_notes': 'Notes added by human operator',
                'devops_action_id': 'Link to devops-actions table if escalated',
                'response_sent': 'Boolean - was response emailed to user',
                'sentiment': 'positive, neutral, negative, angry'
            },
            'gsis': [
                'status-created_at-index: Query by status',
                'priority-created_at-index: Query urgent/high priority tickets',
                'user_email-created_at-index: User ticket history'
            ]
        },
        'ielts-devops-actions': {
            'partition_key': 'action_id (String)',
            'sort_key': 'None',
            'attributes': {
                'action_id': 'Unique action identifier',
                'timestamp': 'Unix timestamp of action',
                'action_type': 'diagnose, fix_proposed, fix_applied, monitoring',
                'ticket_id': 'Link to support ticket that triggered this',
                'issue_description': 'Technical issue being addressed',
                'affected_service': 'lambda, dynamodb, api_gateway, s3, gemini, bedrock, ses',
                'ai_analysis': 'DevOps agent analysis and root cause',
                'proposed_fix': 'Suggested fix with code changes',
                'code_diff': 'Git diff of proposed changes',
                'status': 'pending_review, approved, rejected, applied, failed',
                'reviewed_by': 'Human who reviewed the fix',
                'reviewed_at': 'Unix timestamp of review',
                'result': 'Outcome after applying fix',
                'pr_url': 'GitHub/CodeCommit PR URL if created',
                'confidence': 'AI confidence in diagnosis 0.0-1.0'
            },
            'gsis': [
                'status-timestamp-index: Query pending approvals',
                'affected_service-timestamp-index: Service-specific issues',
                'ticket_id-timestamp-index: Link to originating ticket'
            ]
        }
    }

if __name__ == '__main__':
    print("Creating DynamoDB tables for IELTS AI Agents...")
    print("=" * 60)
    
    # Create tables
    create_support_tickets_table()
    create_devops_actions_table()
    
    print("\n" + "=" * 60)
    print("✅ Table creation complete!")
    print("\nSchema documentation:")
    print("-" * 60)
    
    schemas = get_table_schemas()
    for table_name, schema in schemas.items():
        print(f"\n📊 {table_name}")
        print(f"   Primary Key: {schema['partition_key']} + {schema['sort_key']}")
        print(f"   GSIs: {len(schema['gsis'])}")
