"""
IELTS AI Prep - Customer Support Lambda Function
Powered by Amazon Bedrock Nova Micro for cost-effective email support

Features:
- Email classification and routing
- FAQ knowledge base retrieval
- Automated response generation
- Escalation to DevOps agent for technical issues
- Confidence-based human escalation

Environment Variables Required:
- KNOWLEDGE_BASE_ID: Bedrock KB ID for customer FAQs
- MODEL_ID: amazon.nova-micro-v1:0
- SUPPORT_EMAIL: info@ieltsaiprep.com
- ESCALATION_EMAIL: Your email for urgent issues
- DYNAMODB_TICKETS_TABLE: ielts-support-tickets
- SNS_TOPIC_DEVOPS: ARN for DevOps agent SNS topic
"""

import boto3
import json
import os
import re
import hashlib
from datetime import datetime, timedelta
from email.parser import Parser
from email.utils import parseaddr

# Initialize AWS clients
bedrock_agent = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
ses = boto3.client('ses', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
sns = boto3.client('sns', region_name='us-east-1')

# Configuration from environment
KB_ID = os.environ.get('KNOWLEDGE_BASE_ID')
MODEL_ID_MICRO = os.environ.get('MODEL_ID_MICRO', 'amazon.nova-micro-v1:0')
MODEL_ID_PRO = os.environ.get('MODEL_ID_PRO', 'amazon.nova-pro-v1:0')
SUPPORT_EMAIL = os.environ.get('SUPPORT_EMAIL', 'info@ieltsaiprep.com')
ESCALATION_EMAIL = os.environ.get('ESCALATION_EMAIL')
TICKETS_TABLE = os.environ.get('DYNAMODB_TICKETS_TABLE', 'ielts-support-tickets')
SNS_TOPIC_DEVOPS = os.environ.get('SNS_TOPIC_DEVOPS')

# DynamoDB table
tickets_table = dynamodb.Table(TICKETS_TABLE)

# Classification keywords
URGENT_KEYWORDS = [
    'urgent', 'charged', 'refund', 'scam', 'fraud', 'terrible', 
    'worst', 'angry', 'cant access', 'lost money', 'help immediately',
    'right now', 'asap', 'emergency'
]

CATEGORY_KEYWORDS = {
    'purchase': ['buy', 'purchase', 'payment', 'charged', 'cost', 'price', 'pay'],
    'qr_code': ['qr', 'qr code', 'scan', 'authenticate', 'expired', 'generate', 'camera'],
    'audio': ['microphone', 'audio', 'cant hear', 'maya', 'sound', 'speaking', 'disconnecting'],
    'access': ['login', 'access', 'account', 'cant login', 'locked out', 'password'],
    'refund': ['refund', 'cancel', 'money back', 'return', 'chargeback'],
    'technical': ['error', 'not working', 'broken', 'bug', 'crash', 'failed']
}

TECHNICAL_ESCALATION_KEYWORDS = [
    'maya', 'disconnecting', 'part 2', 'part 3', 'regional', 'timeout',
    'gemini', 'slow', 'laggy', 'connection lost', 'keeps failing'
]

def lambda_handler(event, context):
    """
    Main Lambda handler for SES email events
    """
    try:
        print(f"Received event: {json.dumps(event)}")
        
        # Parse SES email
        email_data = parse_ses_email(event)
        print(f"Parsed email from: {email_data['from']}")
        
        # Generate ticket ID
        ticket_id = generate_ticket_id(email_data['from'], email_data['timestamp'])
        
        # Classify email
        classification = classify_email(email_data)
        print(f"Classification: {classification}")
        
        # Query knowledge base
        kb_response = query_knowledge_base(
            email_data['subject'] + " " + email_data['body'],
            classification['category']
        )
        
        # Generate AI response with Nova Micro
        ai_response_micro = generate_response_micro(
            email_data,
            classification,
            kb_response
        )
        
        # Check if Nova Pro escalation needed
        escalation_tier = 'micro'
        final_response = ai_response_micro
        
        if should_escalate_to_pro(classification, ai_response_micro, email_data):
            print(f"Escalating to Nova Pro for enhanced analysis")
            ai_response_pro = generate_response_pro(
                email_data,
                classification,
                kb_response,
                ai_response_micro
            )
            final_response = ai_response_pro
            escalation_tier = 'pro'
        
        # Determine if human escalation is needed
        should_escalate_human = determine_escalation(
            classification,
            final_response['confidence']
        )
        
        # Save ticket to DynamoDB with escalation tier
        ticket = save_ticket(
            ticket_id,
            email_data,
            classification,
            ai_response_micro,
            final_response,
            should_escalate_human,
            escalation_tier
        )
        
        # Handle escalation
        if should_escalate_human:
            handle_escalation(ticket, email_data, classification)
        else:
            # Send automated response
            send_email_response(
                email_data['from'],
                email_data['subject'],
                final_response['response'],
                ticket_id
            )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'ticket_id': ticket_id,
                'escalation_tier': escalation_tier,
                'escalated_to_human': should_escalate_human,
                'confidence': final_response['confidence']
            })
        }
        
    except Exception as e:
        print(f"Error processing email: {str(e)}")
        raise

def parse_ses_email(event):
    """
    Extracts email data from SES event
    """
    # SES provides email in Records
    if 'Records' in event and len(event['Records']) > 0:
        ses_notification = event['Records'][0]['ses']
        mail = ses_notification['mail']
        
        # Get sender
        from_address = mail['source']
        
        # Get subject and body from commonHeaders or parse message
        subject = mail.get('commonHeaders', {}).get('subject', 'No Subject')
        
        # For now, simplified body extraction
        # In production, parse full MIME message
        body = "Email body extraction requires S3 message storage"
        
        return {
            'from': from_address,
            'subject': subject,
            'body': body,
            'timestamp': datetime.utcnow().isoformat(),
            'message_id': mail['messageId']
        }
    
    # Fallback for testing
    return {
        'from': event.get('from', 'test@example.com'),
        'subject': event.get('subject', 'Test'),
        'body': event.get('body', ''),
        'timestamp': datetime.utcnow().isoformat(),
        'message_id': 'test-' + str(int(datetime.utcnow().timestamp()))
    }

def generate_ticket_id(email, timestamp):
    """
    Generates unique ticket ID
    """
    hash_input = f"{email}{timestamp}".encode('utf-8')
    hash_hex = hashlib.sha256(hash_input).hexdigest()[:12]
    return f"TKT-{hash_hex.upper()}"

def classify_email(email_data):
    """
    Classifies email by category, priority, and sentiment
    """
    text = (email_data['subject'] + " " + email_data['body']).lower()
    
    # Determine category
    category = 'general'
    max_matches = 0
    
    for cat, keywords in CATEGORY_KEYWORDS.items():
        matches = sum(1 for kw in keywords if kw in text)
        if matches > max_matches:
            max_matches = matches
            category = cat
    
    # Determine priority
    priority = 'normal'
    if any(kw in text for kw in URGENT_KEYWORDS):
        priority = 'urgent'
    elif category in ['refund', 'purchase'] and 'charged' in text:
        priority = 'high'
    
    # Determine sentiment
    sentiment = 'neutral'
    angry_words = ['terrible', 'worst', 'angry', 'frustrated', 'scam', 'fraud']
    positive_words = ['thank', 'great', 'excellent', 'love', 'appreciate']
    
    if any(word in text for word in angry_words):
        sentiment = 'angry'
    elif any(word in text for word in positive_words):
        sentiment = 'positive'
    
    # Check if technical escalation needed
    needs_devops = any(kw in text for kw in TECHNICAL_ESCALATION_KEYWORDS)
    
    return {
        'category': category,
        'priority': priority,
        'sentiment': sentiment,
        'needs_devops': needs_devops
    }

def query_knowledge_base(query_text, category):
    """
    Queries Bedrock Knowledge Base for relevant FAQs
    """
    try:
        response = bedrock_agent.retrieve(
            knowledgeBaseId=KB_ID,
            retrievalQuery={
                'text': query_text
            },
            retrievalConfiguration={
                'vectorSearchConfiguration': {
                    'numberOfResults': 3,
                    'overrideSearchType': 'HYBRID'  # Vector + keyword search
                }
            }
        )
        
        # Extract relevant chunks
        results = []
        for result in response.get('retrievalResults', []):
            results.append({
                'content': result['content']['text'],
                'score': result.get('score', 0),
                'source': result.get('location', {}).get('s3Location', {})
            })
        
        return results
        
    except Exception as e:
        print(f"Error querying KB: {str(e)}")
        return []

def generate_response_micro(email_data, classification, kb_results):
    """
    Generates AI response using Bedrock Nova Micro
    """
    # Build context from KB results
    kb_context = "\n\n".join([r['content'] for r in kb_results[:2]])
    
    # Create prompt
    prompt = f"""You are a helpful customer support agent for IELTS AI Prep. 

Customer Email:
Subject: {email_data['subject']}
Message: {email_data['body']}

Category: {classification['category']}
Sentiment: {classification['sentiment']}

Relevant FAQ Information:
{kb_context}

Instructions:
1. Provide a helpful, empathetic response
2. Use the FAQ information when relevant
3. Be concise but complete
4. If technical issue, acknowledge and mention escalation
5. If refund/billing, show understanding and explain process
6. Sign as "IELTS AI Prep Support Team"

Generate a professional email response:"""

    try:
        # Invoke Nova Micro
        response = bedrock_runtime.invoke_model(
            modelId=MODEL_ID_MICRO,
            contentType='application/json',
            accept='application/json',
            body=json.dumps({
                'prompt': prompt,
                'max_tokens': 500,
                'temperature': 0.7,
                'top_p': 0.9
            })
        )
        
        response_body = json.loads(response['body'].read())
        generated_text = response_body.get('completion', '')
        
        # Calculate confidence based on KB match scores
        confidence = 0.5  # Default
        if kb_results:
            confidence = min(0.95, max([r['score'] for r in kb_results]))
        
        # Lower confidence for angry sentiment or urgent priority
        if classification['sentiment'] == 'angry':
            confidence *= 0.7
        if classification['priority'] == 'urgent':
            confidence *= 0.8
        
        return {
            'response': generated_text,
            'confidence': confidence,
            'kb_sources': [r['source'] for r in kb_results]
        }
        
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        return {
            'response': 'Thank you for contacting IELTS AI Prep. We have received your inquiry and will respond within 24 hours.',
            'confidence': 0.3,
            'kb_sources': []
        }

def should_escalate_to_pro(classification, micro_response, email_data):
    """
    Determines if Nova Pro escalation is needed
    """
    # Low confidence from Micro
    if micro_response['confidence'] < 0.6:
        return True
    
    # Complex question indicators
    body_lower = email_data['body'].lower()
    complex_keywords = ['why', 'how does', 'explain', 'comparison', 'difference between', 'multiple']
    if any(kw in body_lower for kw in complex_keywords):
        return True
    
    # Technical questions
    if classification['category'] in ['technical', 'access']:
        return True
    
    # Multi-part questions (more than 2 question marks)
    if email_data['body'].count('?') > 2:
        return True
    
    return False

def generate_response_pro(email_data, classification, kb_results, micro_response):
    """
    Generates enhanced AI response using Bedrock Nova Pro
    Provides second opinion when Nova Micro confidence is low
    """
    # Build context from KB results
    kb_context = "\n\n".join([r['content'] for r in kb_results[:3]])
    
    # Create comprehensive prompt for Nova Pro
    prompt = f"""You are a senior customer support specialist for IELTS AI Prep. A junior AI assistant (Nova Micro) attempted to answer this customer inquiry but couldn't provide a confident response. Your task is to provide a comprehensive, accurate answer.

CUSTOMER EMAIL:
From: {email_data['from']}
Subject: {email_data['subject']}
Message: {email_data['body']}

CLASSIFICATION:
Category: {classification['category']}
Priority: {classification['priority']}
Sentiment: {classification['sentiment']}

MICRO AI'S ATTEMPT:
Response: {micro_response['response']}
Confidence: {micro_response['confidence']}
Issue: Low confidence suggests the question is complex or requires deeper analysis.

KNOWLEDGE BASE CONTEXT:
{kb_context if kb_context else "No relevant FAQ found"}

YOUR TASK:
1. Analyze the customer's question thoroughly
2. Provide a detailed, accurate response
3. Address any nuances the Micro AI may have missed
4. If this is technical, explain clearly for non-technical users
5. If you need human expert review, explicitly state why

IMPORTANT:
- Be comprehensive but clear
- Use simple language (customers are non-technical)
- If uncertain, recommend human review rather than guessing
- Score your confidence 0-1 (be conservative)

Generate response in this exact JSON format:
{{
    "response": "your detailed response here",
    "confidence": 0.85,
    "reasoning": "why this answer is appropriate",
    "requires_human": false,
    "suggested_actions": ["action 1", "action 2"]
}}"""

    try:
        # Invoke Nova Pro
        response = bedrock_runtime.invoke_model(
            modelId=MODEL_ID_PRO,
            contentType='application/json',
            accept='application/json',
            body=json.dumps({
                'prompt': prompt,
                'max_tokens': 2000,
                'temperature': 0.3,  # Lower temperature for more consistent responses
                'top_p': 0.9
            })
        )
        
        response_body = json.loads(response['body'].read())
        generated_text = response_body.get('completion', '')
        
        # Try to parse JSON response from Pro
        try:
            import re
            json_match = re.search(r'\{[^}]+\}', generated_text, re.DOTALL)
            if json_match:
                pro_result = json.loads(json_match.group())
                return {
                    'response': pro_result.get('response', generated_text),
                    'confidence': float(pro_result.get('confidence', 0.75)),
                    'kb_sources': [r['source'] for r in kb_results],
                    'reasoning': pro_result.get('reasoning', ''),
                    'model': 'nova-pro'
                }
        except:
            pass
        
        # Fallback if JSON parsing fails
        return {
            'response': generated_text,
            'confidence': 0.75,  # Default Pro confidence
            'kb_sources': [r['source'] for r in kb_results],
            'model': 'nova-pro'
        }
        
    except Exception as e:
        print(f"Error with Nova Pro: {str(e)}")
        # Fallback to Micro response
        return {
            'response': micro_response['response'],
            'confidence': micro_response['confidence'],
            'kb_sources': micro_response['kb_sources'],
            'model': 'nova-micro-fallback'
        }

def determine_escalation(classification, confidence):
    """
    Determines if human escalation is needed
    """
    # Always escalate if low confidence
    if confidence < 0.6:
        return True
    
    # Escalate urgent issues
    if classification['priority'] == 'urgent':
        return True
    
    # Escalate refunds
    if classification['category'] == 'refund':
        return True
    
    # Escalate angry customers
    if classification['sentiment'] == 'angry':
        return True
    
    # Escalate technical issues needing DevOps
    if classification['needs_devops']:
        return True
    
    return False

def save_ticket(ticket_id, email_data, classification, micro_response, final_response, escalated, escalation_tier):
    """
    Saves ticket to DynamoDB with escalation tier tracking
    """
    now = int(datetime.utcnow().timestamp())
    
    ticket = {
        'ticket_id': ticket_id,
        'created_at': now,
        'user_email': email_data['from'],
        'subject': email_data['subject'],
        'message': email_data['body'],
        'category': classification['category'],
        'priority': classification['priority'],
        'sentiment': classification['sentiment'],
        'status': 'escalated' if escalated else 'resolved',
        'escalation_tier': escalation_tier,
        'micro_confidence': str(micro_response['confidence']),
        'final_confidence': str(final_response['confidence']),
        'ai_response': final_response['response'],
        'escalated_at': now if escalated else None,
        'resolved_at': now if not escalated else None,
        'response_sent': not escalated,
        'model_used': final_response.get('model', escalation_tier)
    }
    
    # Add Pro-specific fields if Pro was used
    if escalation_tier == 'pro':
        ticket['pro_confidence'] = str(final_response['confidence'])
        ticket['pro_reasoning'] = final_response.get('reasoning', '')
    
    tickets_table.put_item(Item=ticket)
    print(f"Saved ticket: {ticket_id} (Tier: {escalation_tier}, Confidence: {final_response['confidence']:.2f})")
    
    return ticket

def handle_escalation(ticket, email_data, classification):
    """
    Handles ticket escalation
    """
    # If technical issue, trigger DevOps agent via SNS
    if classification['needs_devops'] and SNS_TOPIC_DEVOPS:
        notify_devops_agent(ticket, email_data)
    
    # Notify human via email
    send_escalation_notification(ticket, email_data)
    
    # Send acknowledgment to customer
    ack_message = f"""Thank you for contacting IELTS AI Prep Support.

We have received your inquiry (Ticket ID: {ticket['ticket_id']}) and our team is reviewing it.

{generate_acknowledgment_message(classification)}

You will receive a detailed response within 24 hours.

Best regards,
IELTS AI Prep Support Team"""
    
    send_email_response(
        email_data['from'],
        email_data['subject'],
        ack_message,
        ticket['ticket_id']
    )

def notify_devops_agent(ticket, email_data):
    """
    Notifies DevOps agent via SNS for technical issues
    """
    try:
        sns.publish(
            TopicArn=SNS_TOPIC_DEVOPS,
            Subject=f"Technical Issue - {ticket['ticket_id']}",
            Message=json.dumps({
                'ticket_id': ticket['ticket_id'],
                'category': ticket['category'],
                'issue': email_data['subject'] + " - " + email_data['body'][:200],
                'user_email': email_data['from'],
                'priority': ticket['priority']
            })
        )
        print(f"Notified DevOps agent for ticket: {ticket['ticket_id']}")
    except Exception as e:
        print(f"Error notifying DevOps: {str(e)}")

def generate_acknowledgment_message(classification):
    """
    Generates context-specific acknowledgment
    """
    if classification['category'] == 'refund':
        return "Your refund request is being reviewed by our billing team."
    elif classification['needs_devops']:
        return "Our technical team is investigating this issue."
    elif classification['priority'] == 'urgent':
        return "This has been marked as urgent and escalated to our senior support team."
    else:
        return "A support specialist is reviewing your case."

def send_escalation_notification(ticket, email_data):
    """
    Sends email notification to human support team
    """
    if not ESCALATION_EMAIL:
        return
    
    notification = f"""New Support Ticket Escalation

Ticket ID: {ticket['ticket_id']}
From: {email_data['from']}
Subject: {email_data['subject']}
Category: {ticket['category']}
Priority: {ticket['priority']}
Sentiment: {ticket['sentiment']}

Message:
{email_data['body']}

AI Response (Confidence: {ticket['ai_confidence']}):
{ticket['ai_response']}

Action Required: Review and respond to customer within 24 hours.
View ticket: https://dashboard.ieltsaiprep.com/support/tickets/{ticket['ticket_id']}
"""
    
    try:
        ses.send_email(
            Source=SUPPORT_EMAIL,
            Destination={'ToAddresses': [ESCALATION_EMAIL]},
            Message={
                'Subject': {'Data': f"[{ticket['priority'].upper()}] Ticket {ticket['ticket_id']}"},
                'Body': {'Text': {'Data': notification}}
            }
        )
    except Exception as e:
        print(f"Error sending escalation email: {str(e)}")

def send_email_response(to_email, original_subject, response_body, ticket_id):
    """
    Sends email response to customer
    """
    subject = f"Re: {original_subject} [Ticket: {ticket_id}]"
    
    try:
        ses.send_email(
            Source=SUPPORT_EMAIL,
            Destination={'ToAddresses': [to_email]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': response_body}}
            }
        )
        print(f"Sent response email to: {to_email}")
    except Exception as e:
        print(f"Error sending email: {str(e)}")
