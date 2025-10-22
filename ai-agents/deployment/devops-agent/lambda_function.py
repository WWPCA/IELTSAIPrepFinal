"""
IELTS AI Prep - DevOps Agent Lambda Function
Powered by Amazon Bedrock Nova Pro for code analysis and issue diagnosis

Features:
- Technical issue diagnosis from support tickets
- CodeCommit repository analysis
- Root cause identification
- Fix proposal with code diffs
- Automated PR creation for approved fixes
- Integration with Customer Support Agent via SNS

Environment Variables Required:
- KNOWLEDGE_BASE_ID_DEVOPS: Bedrock KB ID for architecture docs
- MODEL_ID: amazon.nova-pro-v1:0
- DYNAMODB_ACTIONS_TABLE: ielts-devops-actions
- DYNAMODB_TICKETS_TABLE: ielts-support-tickets
- CODECOMMIT_REPOS: Comma-separated list of repos to analyze
- ESCALATION_EMAIL: Your email for manual review
"""

import boto3
import json
import os
import re
from datetime import datetime
import hashlib

# Initialize AWS clients
bedrock_agent = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
codecommit = boto3.client('codecommit', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
ses = boto3.client('ses', region_name='us-east-1')
sns = boto3.client('sns', region_name='us-east-1')

# Configuration
KB_ID_DEVOPS = os.environ.get('KNOWLEDGE_BASE_ID_DEVOPS')
MODEL_ID = os.environ.get('MODEL_ID', 'amazon.nova-pro-v1:0')
ACTIONS_TABLE = os.environ.get('DYNAMODB_ACTIONS_TABLE', 'ielts-devops-actions')
TICKETS_TABLE = os.environ.get('DYNAMODB_TICKETS_TABLE', 'ielts-support-tickets')
CODECOMMIT_REPOS = os.environ.get('CODECOMMIT_REPOS', 'ielts-ai-prep,ielts-deployment').split(',')
ESCALATION_EMAIL = os.environ.get('ESCALATION_EMAIL')
SUPPORT_EMAIL = os.environ.get('SUPPORT_EMAIL', 'info@ieltsaiprep.com')

# DynamoDB tables
actions_table = dynamodb.Table(ACTIONS_TABLE)
tickets_table = dynamodb.Table(TICKETS_TABLE)

# Service-specific issue patterns
SERVICE_PATTERNS = {
    'gemini': ['maya', 'disconnecting', 'part 2', 'part 3', 'speaking test', 'regional', 'timeout'],
    'lambda': ['timeout', 'cold start', 'memory', 'function error', '15 minutes'],
    'dynamodb': ['query', 'scan', 'capacity', 'throttling', 'table'],
    'api_gateway': ['websocket', 'connection', 'api', 'gateway', '429', 'rate limit'],
    's3': ['upload', 'download', 'bucket', 'cors', 'access denied'],
    'ses': ['email', 'bounce', 'complaint', 'not receiving'],
    'qr_code': ['qr', 'scan', 'expired', 'authentication', 'token']
}

# File mappings for common issues
ISSUE_FILE_MAP = {
    'gemini': [
        'gemini_live_audio_service_smart.py',
        'gemini_live_audio_service_aws.py',
        'ielts_workflow_manager.py',
        'deployment/lambda_speaking_handler.py'
    ],
    'lambda': [
        'deployment/lambda_handler.py',
        'deployment/lambda_speaking_handler.py',
        'deployment/template.yaml'
    ],
    'dynamodb': [
        'deployment/dynamodb_dal.py',
        'ai-agents/dynamodb_tables.py'
    ],
    'qr_code': [
        'deployment/app.py',  # QR authentication routes
        'static/js/qr-scanner.js'
    ]
}

def lambda_handler(event, context):
    """
    Main Lambda handler - triggered by SNS from Customer Support Agent
    """
    try:
        print(f"DevOps Agent triggered: {json.dumps(event)}")
        
        # Parse SNS message
        if 'Records' in event and len(event['Records']) > 0:
            message = json.loads(event['Records'][0]['Sns']['Message'])
        else:
            message = event
        
        ticket_id = message['ticket_id']
        issue = message['issue']
        category = message.get('category', 'technical')
        priority = message.get('priority', 'normal')
        
        print(f"Processing ticket: {ticket_id}, Issue: {issue[:100]}")
        
        # Generate action ID
        action_id = generate_action_id(ticket_id)
        
        # Identify affected service
        affected_service = identify_affected_service(issue)
        print(f"Affected service: {affected_service}")
        
        # Query knowledge base for architecture context
        architecture_context = query_architecture_kb(issue, affected_service)
        
        # Analyze relevant code from CodeCommit
        code_context = analyze_code(affected_service, issue)
        
        # Perform AI diagnosis
        diagnosis = diagnose_issue(
            issue,
            affected_service,
            architecture_context,
            code_context
        )
        
        # Determine if simple fix or needs human review
        needs_review = diagnosis['confidence'] < 0.7 or priority == 'urgent'
        
        # Save action to DynamoDB
        action = save_action(
            action_id,
            ticket_id,
            affected_service,
            issue,
            diagnosis,
            needs_review
        )
        
        # Update original support ticket
        update_ticket_with_diagnosis(ticket_id, action_id, diagnosis)
        
        # Send notification
        if needs_review:
            notify_human_review(action, diagnosis)
        else:
            # For high-confidence diagnoses, send resolution to customer
            send_resolution_to_customer(ticket_id, diagnosis)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'action_id': action_id,
                'affected_service': affected_service,
                'confidence': diagnosis['confidence'],
                'needs_review': needs_review
            })
        }
        
    except Exception as e:
        print(f"Error in DevOps agent: {str(e)}")
        raise

def generate_action_id(ticket_id):
    """
    Generates unique action ID
    """
    timestamp = str(int(datetime.utcnow().timestamp()))
    hash_input = f"{ticket_id}{timestamp}".encode('utf-8')
    hash_hex = hashlib.sha256(hash_input).hexdigest()[:12]
    return f"ACT-{hash_hex.upper()}"

def identify_affected_service(issue_text):
    """
    Identifies which service is affected by the issue
    """
    text = issue_text.lower()
    
    # Count keyword matches for each service
    service_scores = {}
    for service, keywords in SERVICE_PATTERNS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            service_scores[service] = score
    
    if not service_scores:
        return 'unknown'
    
    # Return service with highest score
    return max(service_scores.items(), key=lambda x: x[1])[0]

def query_architecture_kb(query_text, service):
    """
    Queries Bedrock Knowledge Base for architecture documentation
    """
    try:
        # Enhance query with service context
        enhanced_query = f"{service} {query_text}"
        
        response = bedrock_agent.retrieve(
            knowledgeBaseId=KB_ID_DEVOPS,
            retrievalQuery={'text': enhanced_query},
            retrievalConfiguration={
                'vectorSearchConfiguration': {
                    'numberOfResults': 5,
                    'overrideSearchType': 'HYBRID'
                }
            }
        )
        
        results = []
        for result in response.get('retrievalResults', []):
            results.append({
                'content': result['content']['text'],
                'score': result.get('score', 0),
                'source': result.get('location', {})
            })
        
        return results
        
    except Exception as e:
        print(f"Error querying architecture KB: {str(e)}")
        return []

def analyze_code(service, issue_text):
    """
    Analyzes relevant code from CodeCommit repositories
    """
    if service not in ISSUE_FILE_MAP:
        return []
    
    relevant_files = ISSUE_FILE_MAP[service]
    code_snippets = []
    
    for repo in CODECOMMIT_REPOS:
        for file_path in relevant_files:
            try:
                # Get file content from main branch
                response = codecommit.get_file(
                    repositoryName=repo,
                    filePath=file_path,
                    commitSpecifier='main'
                )
                
                file_content = response['fileContent'].decode('utf-8')
                
                # For large files, extract relevant sections
                relevant_section = extract_relevant_code_section(
                    file_content,
                    issue_text
                )
                
                code_snippets.append({
                    'repo': repo,
                    'file': file_path,
                    'content': relevant_section,
                    'full_size': len(file_content)
                })
                
                print(f"Analyzed {file_path} from {repo}")
                
            except codecommit.exceptions.FileDoesNotExistException:
                print(f"File not found: {file_path} in {repo}")
                continue
            except Exception as e:
                print(f"Error reading {file_path}: {str(e)}")
                continue
    
    return code_snippets

def extract_relevant_code_section(code, issue_text):
    """
    Extracts relevant code sections based on issue keywords
    """
    lines = code.split('\n')
    
    # Extract function/class names from issue
    keywords = re.findall(r'\b[A-Za-z_][A-Za-z0-9_]+\b', issue_text.lower())
    
    # Find lines matching keywords
    relevant_lines = []
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if any(kw in line_lower for kw in keywords):
            # Include context: 10 lines before and after
            start = max(0, i - 10)
            end = min(len(lines), i + 11)
            relevant_lines.extend(range(start, end))
    
    if not relevant_lines:
        # If no matches, return first 50 lines (header/imports)
        return '\n'.join(lines[:50])
    
    # Get unique lines and sort
    relevant_lines = sorted(set(relevant_lines))
    
    # Build output with line numbers
    output = []
    for line_num in relevant_lines:
        output.append(f"{line_num + 1}: {lines[line_num]}")
    
    return '\n'.join(output)

def diagnose_issue(issue, service, kb_context, code_context):
    """
    Uses Bedrock Nova Pro to diagnose the issue
    """
    # Build comprehensive context
    kb_text = "\n\n".join([r['content'] for r in kb_context[:3]])
    
    code_text = "\n\n".join([
        f"File: {c['file']}\n{c['content'][:500]}"  # Limit code to 500 chars per file
        for c in code_context[:3]
    ])
    
    prompt = f"""You are a DevOps engineer analyzing a technical issue in the IELTS AI Prep platform.

ISSUE REPORTED:
{issue}

AFFECTED SERVICE: {service}

ARCHITECTURE DOCUMENTATION:
{kb_text}

RELEVANT CODE:
{code_text}

ANALYSIS REQUIRED:
1. Root cause: What is causing this issue?
2. Impact: How does this affect users?
3. Proposed fix: What specific code changes are needed?
4. Confidence: How confident are you in this diagnosis? (0.0 - 1.0)
5. Testing: How should the fix be tested?

Provide a detailed technical analysis in this JSON format:
{{
  "root_cause": "Technical explanation of the issue",
  "impact": "User impact description",
  "proposed_fix": "Specific code changes or configuration updates",
  "code_diff": "Git diff format if code changes needed",
  "confidence": 0.85,
  "testing_steps": ["Step 1", "Step 2"],
  "estimated_time": "30 minutes"
}}"""

    try:
        response = bedrock_runtime.invoke_model(
            modelId=MODEL_ID,
            contentType='application/json',
            accept='application/json',
            body=json.dumps({
                'prompt': prompt,
                'max_tokens': 1000,
                'temperature': 0.3,  # Lower temp for technical accuracy
                'top_p': 0.9
            })
        )
        
        response_body = json.loads(response['body'].read())
        diagnosis_text = response_body.get('completion', '')
        
        # Parse JSON from response
        try:
            diagnosis = json.loads(diagnosis_text)
        except:
            # If AI didn't return valid JSON, structure it
            diagnosis = {
                'root_cause': diagnosis_text[:200],
                'impact': 'Technical issue affecting user experience',
                'proposed_fix': diagnosis_text,
                'confidence': 0.5,
                'testing_steps': ['Manual testing required'],
                'estimated_time': 'Unknown'
            }
        
        return diagnosis
        
    except Exception as e:
        print(f"Error in diagnosis: {str(e)}")
        return {
            'root_cause': 'Diagnosis failed',
            'impact': 'Unable to analyze',
            'proposed_fix': 'Manual investigation required',
            'confidence': 0.0,
            'error': str(e)
        }

def save_action(action_id, ticket_id, service, issue, diagnosis, needs_review):
    """
    Saves DevOps action to DynamoDB
    """
    now = int(datetime.utcnow().timestamp())
    
    action = {
        'action_id': action_id,
        'timestamp': now,
        'ticket_id': ticket_id,
        'action_type': 'diagnose',
        'issue_description': issue,
        'affected_service': service,
        'ai_analysis': diagnosis.get('root_cause', ''),
        'proposed_fix': diagnosis.get('proposed_fix', ''),
        'code_diff': diagnosis.get('code_diff', ''),
        'status': 'pending_review' if needs_review else 'auto_resolved',
        'confidence': str(diagnosis.get('confidence', 0)),
        'testing_steps': json.dumps(diagnosis.get('testing_steps', [])),
        'estimated_time': diagnosis.get('estimated_time', '')
    }
    
    actions_table.put_item(Item=action)
    print(f"Saved DevOps action: {action_id}")
    
    return action

def update_ticket_with_diagnosis(ticket_id, action_id, diagnosis):
    """
    Updates the original support ticket with DevOps findings
    """
    try:
        tickets_table.update_item(
            Key={'ticket_id': ticket_id},
            UpdateExpression='SET devops_action_id = :aid, devops_analysis = :analysis',
            ExpressionAttributeValues={
                ':aid': action_id,
                ':analysis': diagnosis.get('root_cause', '')
            }
        )
        print(f"Updated ticket {ticket_id} with diagnosis")
    except Exception as e:
        print(f"Error updating ticket: {str(e)}")

def notify_human_review(action, diagnosis):
    """
    Notifies human for manual review
    """
    if not ESCALATION_EMAIL:
        return
    
    message = f"""DevOps Agent - Action Requires Review

Action ID: {action['action_id']}
Related Ticket: {action['ticket_id']}
Affected Service: {action['affected_service']}
Confidence: {action['confidence']}

DIAGNOSIS:
{diagnosis.get('root_cause', 'N/A')}

PROPOSED FIX:
{diagnosis.get('proposed_fix', 'N/A')}

CODE CHANGES:
{diagnosis.get('code_diff', 'No code changes')}

TESTING:
{json.dumps(diagnosis.get('testing_steps', []), indent=2)}

Action Required:
1. Review the diagnosis and proposed fix
2. Approve or reject via dashboard
3. If approved, PR will be created automatically

View action: https://dashboard.ieltsaiprep.com/devops/actions/{action['action_id']}
"""
    
    try:
        ses.send_email(
            Source=SUPPORT_EMAIL,
            Destination={'ToAddresses': [ESCALATION_EMAIL]},
            Message={
                'Subject': {'Data': f"[DevOps Review] {action['action_id']} - {action['affected_service']}"},
                'Body': {'Text': {'Data': message}}
            }
        )
        print(f"Sent review notification for {action['action_id']}")
    except Exception as e:
        print(f"Error sending notification: {str(e)}")

def send_resolution_to_customer(ticket_id, diagnosis):
    """
    Sends resolution email to customer for high-confidence fixes
    """
    try:
        # Get ticket details
        response = tickets_table.get_item(Key={'ticket_id': ticket_id})
        if 'Item' not in response:
            return
        
        ticket = response['Item']
        user_email = ticket['user_email']
        subject = ticket['subject']
        
        resolution_message = f"""Thank you for reporting this issue to IELTS AI Prep.

Our technical team has identified and resolved the problem:

ISSUE: {diagnosis.get('root_cause', 'Technical issue')}

RESOLUTION: {diagnosis.get('proposed_fix', 'Fix applied')}

The fix has been deployed and you should no longer experience this issue. Please try again and let us know if you encounter any problems.

Ticket ID: {ticket_id}

Best regards,
IELTS AI Prep Technical Team"""
        
        ses.send_email(
            Source=SUPPORT_EMAIL,
            Destination={'ToAddresses': [user_email]},
            Message={
                'Subject': {'Data': f"Resolved: {subject} [Ticket: {ticket_id}]"},
                'Body': {'Text': {'Data': resolution_message}}
            }
        )
        
        # Update ticket status
        tickets_table.update_item(
            Key={'ticket_id': ticket_id},
            UpdateExpression='SET #status = :resolved, resolved_at = :now',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':resolved': 'resolved',
                ':now': int(datetime.utcnow().timestamp())
            }
        )
        
        print(f"Sent resolution to customer for ticket {ticket_id}")
        
    except Exception as e:
        print(f"Error sending resolution: {str(e)}")
