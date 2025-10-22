"""
IELTS AI Prep - AI Agents Dashboard Routes
Flask blueprint for viewing and managing support tickets and DevOps actions
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime, timedelta
import json

# Create blueprint
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')
tickets_table = dynamodb.Table('ielts-support-tickets')
actions_table = dynamodb.Table('ielts-devops-actions')

# Admin authentication check using session
def require_admin():
    """Check if user is authenticated as admin via session"""
    return session.get('is_admin', False)

@dashboard_bp.route('/support/tickets')
def support_tickets():
    """View all support tickets"""
    if not require_admin():
        return redirect(url_for('login'))
    
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    priority_filter = request.args.get('priority', 'all')
    
    try:
        # Query tickets based on filters
        if status_filter != 'all':
            response = tickets_table.query(
                IndexName='status-created_at-index',
                KeyConditionExpression=Key('status').eq(status_filter),
                ScanIndexForward=False,  # Most recent first
                Limit=50
            )
        elif priority_filter != 'all':
            response = tickets_table.query(
                IndexName='priority-created_at-index',
                KeyConditionExpression=Key('priority').eq(priority_filter),
                ScanIndexForward=False,
                Limit=50
            )
        else:
            # Get all recent tickets
            response = tickets_table.scan(Limit=50)
        
        tickets = response.get('Items', [])
        
        # Sort by created_at
        tickets.sort(key=lambda x: x.get('created_at', 0), reverse=True)
        
        # Format timestamps
        for ticket in tickets:
            ticket['created_at_formatted'] = format_timestamp(ticket.get('created_at'))
            ticket['escalated_at_formatted'] = format_timestamp(ticket.get('escalated_at'))
            ticket['resolved_at_formatted'] = format_timestamp(ticket.get('resolved_at'))
        
        # Get statistics
        stats = get_ticket_statistics()
        
        return render_template('dashboard/support_tickets.html',
                             tickets=tickets,
                             stats=stats,
                             status_filter=status_filter,
                             priority_filter=priority_filter)
    
    except Exception as e:
        print(f"Error loading tickets: {str(e)}")
        return render_template('dashboard/error.html', error=str(e))

@dashboard_bp.route('/support/tickets/<ticket_id>')
def ticket_detail(ticket_id):
    """View detailed ticket information"""
    if not require_admin():
        return redirect(url_for('login'))
    
    try:
        response = tickets_table.get_item(Key={'ticket_id': ticket_id})
        
        if 'Item' not in response:
            return render_template('dashboard/error.html', error='Ticket not found')
        
        ticket = response['Item']
        ticket['created_at_formatted'] = format_timestamp(ticket.get('created_at'))
        
        # Get associated DevOps action if exists
        devops_action = None
        if ticket.get('devops_action_id'):
            try:
                action_response = actions_table.get_item(
                    Key={'action_id': ticket['devops_action_id']}
                )
                if 'Item' in action_response:
                    devops_action = action_response['Item']
            except:
                pass
        
        return render_template('dashboard/ticket_detail.html',
                             ticket=ticket,
                             devops_action=devops_action)
    
    except Exception as e:
        print(f"Error loading ticket: {str(e)}")
        return render_template('dashboard/error.html', error=str(e))

@dashboard_bp.route('/devops/actions')
def devops_actions():
    """View all DevOps actions"""
    if not require_admin():
        return redirect(url_for('login'))
    
    status_filter = request.args.get('status', 'pending_review')
    service_filter = request.args.get('service', 'all')
    
    try:
        # Query actions based on filters
        if status_filter != 'all':
            response = actions_table.query(
                IndexName='status-timestamp-index',
                KeyConditionExpression=Key('status').eq(status_filter),
                ScanIndexForward=False,
                Limit=50
            )
        elif service_filter != 'all':
            response = actions_table.query(
                IndexName='affected_service-timestamp-index',
                KeyConditionExpression=Key('affected_service').eq(service_filter),
                ScanIndexForward=False,
                Limit=50
            )
        else:
            response = actions_table.scan(Limit=50)
        
        actions = response.get('Items', [])
        actions.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        
        # Format timestamps
        for action in actions:
            action['timestamp_formatted'] = format_timestamp(action.get('timestamp'))
            action['reviewed_at_formatted'] = format_timestamp(action.get('reviewed_at'))
        
        # Get statistics
        stats = get_devops_statistics()
        
        return render_template('dashboard/devops_actions.html',
                             actions=actions,
                             stats=stats,
                             status_filter=status_filter,
                             service_filter=service_filter)
    
    except Exception as e:
        print(f"Error loading actions: {str(e)}")
        return render_template('dashboard/error.html', error=str(e))

@dashboard_bp.route('/devops/actions/<action_id>')
def action_detail(action_id):
    """View detailed DevOps action information"""
    if not require_admin():
        return redirect(url_for('login'))
    
    try:
        response = actions_table.get_item(Key={'action_id': action_id})
        
        if 'Item' not in response:
            return render_template('dashboard/error.html', error='Action not found')
        
        action = response['Item']
        action['timestamp_formatted'] = format_timestamp(action.get('timestamp'))
        
        # Get associated support ticket
        ticket = None
        if action.get('ticket_id'):
            try:
                ticket_response = tickets_table.get_item(
                    Key={'ticket_id': action['ticket_id']}
                )
                if 'Item' in ticket_response:
                    ticket = ticket_response['Item']
            except:
                pass
        
        return render_template('dashboard/action_detail.html',
                             action=action,
                             ticket=ticket)
    
    except Exception as e:
        print(f"Error loading action: {str(e)}")
        return render_template('dashboard/error.html', error=str(e))

@dashboard_bp.route('/api/ticket/<ticket_id>/update', methods=['POST'])
def update_ticket(ticket_id):
    """Update ticket status or add notes"""
    if not require_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        data = request.json
        update_expr = []
        expr_values = {}
        
        if 'status' in data:
            update_expr.append('#status = :status')
            expr_values[':status'] = data['status']
            if data['status'] == 'resolved':
                update_expr.append('resolved_at = :resolved_at')
                expr_values[':resolved_at'] = int(datetime.utcnow().timestamp())
        
        if 'human_notes' in data:
            update_expr.append('human_notes = :notes')
            expr_values[':notes'] = data['human_notes']
        
        if update_expr:
            tickets_table.update_item(
                Key={'ticket_id': ticket_id},
                UpdateExpression='SET ' + ', '.join(update_expr),
                ExpressionAttributeNames={'#status': 'status'} if 'status' in data else {},
                ExpressionAttributeValues=expr_values
            )
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/api/action/<action_id>/review', methods=['POST'])
def review_action(action_id):
    """Approve or reject DevOps action"""
    if not require_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        data = request.json
        decision = data.get('decision')  # 'approved' or 'rejected'
        reviewer_email = data.get('reviewer', 'admin')
        rejection_reason = data.get('rejection_reason', '')
        
        if decision not in ['approved', 'rejected']:
            return jsonify({'error': 'Invalid decision'}), 400
        
        update_expr = 'SET #status = :status, reviewed_by = :reviewer, reviewed_at = :time'
        expr_values = {
            ':status': decision,
            ':reviewer': reviewer_email,
            ':time': int(datetime.utcnow().timestamp())
        }
        
        # Add rejection reason if provided
        if decision == 'rejected' and rejection_reason:
            update_expr += ', rejection_reason = :reason'
            expr_values[':reason'] = rejection_reason
        
        actions_table.update_item(
            Key={'action_id': action_id},
            UpdateExpression=update_expr,
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues=expr_values
        )
        
        # TODO: If approved, trigger PR creation or auto-deployment
        
        return jsonify({'success': True, 'action_id': action_id, 'decision': decision})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/api/action/<action_id>/clarify', methods=['POST'])
def clarify_action(action_id):
    """Request clarification from Nova Pro about a DevOps action"""
    if not require_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        data = request.json
        question = data.get('question', '').strip()
        admin_email = data.get('admin_email', 'admin')
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        # Get the action details
        response = actions_table.get_item(Key={'action_id': action_id})
        if 'Item' not in response:
            return jsonify({'error': 'Action not found'}), 404
        
        action = response['Item']
        
        # Call Bedrock Nova Pro for clarification
        try:
            import boto3
            bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
            
            # Build context for Nova Pro
            context = f"""You are reviewing a DevOps action proposal. Here are the details:

Action Type: {action.get('action_type', 'N/A')}
Affected Service: {action.get('affected_service', 'N/A')}
Issue Description: {action.get('issue_description', 'N/A')}
Root Cause: {action.get('root_cause', 'N/A')}
Proposed Fix: {action.get('proposed_fix', 'N/A')}

The admin has the following question about this proposal:
{question}

Please provide a clear, detailed answer that helps the admin make an informed decision about approving or rejecting this action."""

            # Call Bedrock Nova Pro
            bedrock_response = bedrock.invoke_model(
                modelId='us.amazon.nova-pro-v1:0',
                body=json.dumps({
                    "messages": [
                        {
                            "role": "user",
                            "content": [{"text": context}]
                        }
                    ],
                    "inferenceConfig": {
                        "temperature": 0.3,
                        "max_new_tokens": 1000
                    }
                })
            )
            
            response_body = json.loads(bedrock_response['body'].read())
            answer = response_body['output']['message']['content'][0]['text']
            
        except Exception as e:
            print(f"Bedrock error: {str(e)}")
            answer = f"Error getting clarification from Nova Pro: {str(e)}"
        
        # Store clarification in DynamoDB
        clarifications = action.get('clarifications', [])
        clarifications.append({
            'question': question,
            'answer': answer,
            'timestamp': int(datetime.utcnow().timestamp()),
            'timestamp_formatted': format_timestamp(int(datetime.utcnow().timestamp())),
            'asked_by': admin_email
        })
        
        actions_table.update_item(
            Key={'action_id': action_id},
            UpdateExpression='SET clarifications = :clarifications',
            ExpressionAttributeValues={':clarifications': clarifications}
        )
        
        return jsonify({
            'success': True,
            'question': question,
            'answer': answer
        })
    
    except Exception as e:
        print(f"Error in clarify_action: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

def get_ticket_statistics():
    """Get aggregate statistics for support tickets"""
    try:
        # Get counts by status
        new_count = tickets_table.query(
            IndexName='status-created_at-index',
            KeyConditionExpression=Key('status').eq('new'),
            Select='COUNT'
        ).get('Count', 0)
        
        escalated_count = tickets_table.query(
            IndexName='status-created_at-index',
            KeyConditionExpression=Key('status').eq('escalated'),
            Select='COUNT'
        ).get('Count', 0)
        
        resolved_count = tickets_table.query(
            IndexName='status-created_at-index',
            KeyConditionExpression=Key('status').eq('resolved'),
            Select='COUNT'
        ).get('Count', 0)
        
        urgent_count = tickets_table.query(
            IndexName='priority-created_at-index',
            KeyConditionExpression=Key('priority').eq('urgent'),
            Select='COUNT'
        ).get('Count', 0)
        
        return {
            'new': new_count,
            'escalated': escalated_count,
            'resolved': resolved_count,
            'urgent': urgent_count,
            'total': new_count + escalated_count + resolved_count
        }
    except Exception as e:
        print(f"Error getting stats: {str(e)}")
        return {'new': 0, 'escalated': 0, 'resolved': 0, 'urgent': 0, 'total': 0}

def get_devops_statistics():
    """Get aggregate statistics for DevOps actions"""
    try:
        pending_count = actions_table.query(
            IndexName='status-timestamp-index',
            KeyConditionExpression=Key('status').eq('pending_review'),
            Select='COUNT'
        ).get('Count', 0)
        
        approved_count = actions_table.query(
            IndexName='status-timestamp-index',
            KeyConditionExpression=Key('status').eq('approved'),
            Select='COUNT'
        ).get('Count', 0)
        
        applied_count = actions_table.query(
            IndexName='status-timestamp-index',
            KeyConditionExpression=Key('status').eq('applied'),
            Select='COUNT'
        ).get('Count', 0)
        
        return {
            'pending_review': pending_count,
            'approved': approved_count,
            'applied': applied_count,
            'total': pending_count + approved_count + applied_count
        }
    except Exception as e:
        print(f"Error getting stats: {str(e)}")
        return {'pending_review': 0, 'approved': 0, 'applied': 0, 'total': 0}

def format_timestamp(timestamp):
    """Format Unix timestamp to readable datetime"""
    if not timestamp:
        return 'N/A'
    try:
        dt = datetime.fromtimestamp(int(timestamp))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return 'Invalid'

def get_cloudwatch_alarms():
    """Fetch CloudWatch alarm states"""
    try:
        response = cloudwatch.describe_alarms(
            MaxRecords=100
        )
        
        alarms = response.get('MetricAlarms', [])
        
        alarm_data = {
            'total': len(alarms),
            'alarm': 0,
            'ok': 0,
            'insufficient_data': 0,
            'alarms_list': []
        }
        
        for alarm in alarms:
            state = alarm.get('StateValue', 'INSUFFICIENT_DATA')
            if state == 'ALARM':
                alarm_data['alarm'] += 1
            elif state == 'OK':
                alarm_data['ok'] += 1
            else:
                alarm_data['insufficient_data'] += 1
            
            alarm_data['alarms_list'].append({
                'name': alarm.get('AlarmName', 'Unknown'),
                'description': alarm.get('AlarmDescription', ''),
                'state': state,
                'reason': alarm.get('StateReason', ''),
                'updated': alarm.get('StateUpdatedTimestamp'),
                'metric_name': alarm.get('MetricName', ''),
                'namespace': alarm.get('Namespace', '')
            })
        
        # Sort by state (ALARM first, then OK, then INSUFFICIENT_DATA)
        state_priority = {'ALARM': 0, 'OK': 1, 'INSUFFICIENT_DATA': 2}
        alarm_data['alarms_list'].sort(key=lambda x: state_priority.get(x['state'], 3))
        
        return alarm_data
    except Exception as e:
        print(f"Error fetching CloudWatch alarms: {str(e)}")
        return {
            'total': 0,
            'alarm': 0,
            'ok': 0,
            'insufficient_data': 0,
            'alarms_list': [],
            'error': str(e)
        }

@dashboard_bp.route('/')
@dashboard_bp.route('/security')
def security_dashboard():
    """Main security dashboard showing alarms, tickets, and DevOps actions"""
    if not require_admin():
        return redirect(url_for('admin_login'))
    
    try:
        # Get CloudWatch alarms
        alarm_data = get_cloudwatch_alarms()
        
        # Get DevOps action stats
        devops_stats = get_devops_statistics()
        
        # Get support ticket stats
        ticket_stats = get_ticket_statistics()
        
        # Get recent pending DevOps actions (last 10)
        try:
            pending_actions_response = actions_table.query(
                IndexName='status-timestamp-index',
                KeyConditionExpression=Key('status').eq('pending_review'),
                ScanIndexForward=False,
                Limit=10
            )
            pending_actions = pending_actions_response.get('Items', [])
            for action in pending_actions:
                action['timestamp_formatted'] = format_timestamp(action.get('timestamp'))
        except:
            pending_actions = []
        
        # Get recent alarms (CloudWatch alarms in ALARM state)
        critical_alarms = [a for a in alarm_data['alarms_list'] if a['state'] == 'ALARM']
        
        return render_template('dashboard/security_dashboard.html',
                             alarm_data=alarm_data,
                             devops_stats=devops_stats,
                             ticket_stats=ticket_stats,
                             pending_actions=pending_actions,
                             critical_alarms=critical_alarms[:5])  # Show top 5
    
    except Exception as e:
        print(f"Error loading security dashboard: {str(e)}")
        import traceback
        traceback.print_exc()
        return render_template('dashboard/error.html', error=str(e))

@dashboard_bp.route('/alarms')
def alarms():
    """Detailed CloudWatch alarms page"""
    if not require_admin():
        return redirect(url_for('admin_login'))
    
    try:
        alarm_data = get_cloudwatch_alarms()
        
        return render_template('dashboard/alarms.html',
                             alarm_data=alarm_data)
    except Exception as e:
        print(f"Error loading alarms: {str(e)}")
        return render_template('dashboard/error.html', error=str(e))
