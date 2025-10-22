"""
AWS SES Email Service
Handles all email operations using Amazon Simple Email Service
"""
import boto3
from botocore.exceptions import ClientError
import os
from typing import Dict, Optional

class SESEmailService:
    """AWS SES Email Service for IELTS AI Prep"""
    
    def __init__(self):
        """Initialize SES client"""
        self.region = os.environ.get('AWS_REGION', 'us-east-1')
        self.ses_client = boto3.client('ses', region_name=self.region)
        self.sender_email = os.environ.get('SES_SENDER_EMAIL', 'donotreply@ieltsaiprep.com')
        self.domain_url = os.environ.get('DOMAIN_URL', 'https://ieltsaiprep.com')
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> bool:
        """
        Send email via AWS SES
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML content of the email
            text_body: Plain text content (optional)
        
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Build the email message
            message = {
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {'Html': {'Data': html_body, 'Charset': 'UTF-8'}}
            }
            
            # Add text body if provided
            if text_body:
                message['Body']['Text'] = {'Data': text_body, 'Charset': 'UTF-8'}
            
            # Send the email
            response = self.ses_client.send_email(
                Source=self.sender_email,
                Destination={'ToAddresses': [to_email]},
                Message=message
            )
            
            print(f"[SES] Email sent to {to_email}: MessageId {response['MessageId']}")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            if error_code == 'MessageRejected':
                print(f"[SES] Email rejected: {error_message}")
            elif error_code == 'MailFromDomainNotVerified':
                print(f"[SES] Sender domain not verified: {self.sender_email}")
            elif error_code == 'ConfigurationSetDoesNotExist':
                print(f"[SES] Configuration set does not exist")
            else:
                print(f"[SES] Error sending email: {error_code} - {error_message}")
            
            return False
            
        except Exception as e:
            print(f"[SES] Unexpected error: {str(e)}")
            return False
    
    def send_password_reset_email(self, email: str, reset_token: str) -> bool:
        """
        Send password reset email
        
        Args:
            email: User's email address
            reset_token: Password reset token
        
        Returns:
            bool: True if email sent successfully
        """
        reset_link = f"{self.domain_url}/reset_password?token={reset_token}"
        
        subject = "Password Reset - IELTS AI Prep"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
                
                body {{
                    font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f8f9fa;
                }}
                .header {{
                    background: white;
                    color: #e74c3c;
                    padding: 20px 30px;
                    text-align: left;
                    border-bottom: 1px solid #dee2e6;
                    border-radius: 10px 10px 0 0;
                }}
                .header h1 {{
                    margin: 0;
                    font-weight: 700;
                    font-size: 22px;
                    letter-spacing: -0.5px;
                }}
                .content {{
                    background: white;
                    padding: 30px;
                    border: 1px solid #e9ecef;
                    border-radius: 0 0 10px 10px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background: #3498db;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: 500;
                    margin: 20px 0;
                }}
                .button:hover {{
                    background: #2980b9;
                }}
                .footer {{
                    text-align: center;
                    color: #6c757d;
                    font-size: 12px;
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid #e9ecef;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>IELTS AI Prep</h1>
            </div>
            <div class="content">
                <p>Hello,</p>
                <p>We received a request to reset your password for your IELTS AI Prep account.</p>
                
                <h3 style="color: #2c3e50; margin-top: 25px;">How to Reset Your Password:</h3>
                <ol style="line-height: 1.8;">
                    <li><strong>Click the button below</strong> to open the password reset page</li>
                    <li><strong>Enter your new password</strong> (minimum 8 characters)</li>
                    <li><strong>Confirm your new password</strong> by typing it again</li>
                    <li><strong>Click "Reset Password"</strong> to save your changes</li>
                </ol>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_link}" class="button">Reset My Password</a>
                </div>
                
                <p style="background: #fff3cd; padding: 15px; border-left: 3px solid #e74c3c; margin: 20px 0;">
                    <strong>⏱️ Important:</strong> This reset link will expire in <strong>30 minutes</strong> for your security.
                </p>
                
                <p style="font-size: 13px; color: #6c757d;">If the button doesn't work, copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #3498db; font-size: 12px; background: #f8f9fa; padding: 10px; border-radius: 5px;">{reset_link}</p>
                
                <p style="margin-top: 25px;">If you didn't request a password reset, please ignore this email. Your password will remain unchanged.</p>
            </div>
            <div class="footer">
                <p>© 2025 IELTS AI Prep. All rights reserved.</p>
                <p>Need help? Contact us at <a href="mailto:info@ieltsaiprep.com" style="color: #3498db; text-decoration: none;">info@ieltsaiprep.com</a></p>
                <p style="margin-top: 10px; font-size: 11px;">This email was sent from donotreply@ieltsaiprep.com. Please do not reply to this address.</p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Password Reset Request
        
        Hello,
        
        We received a request to reset your password for your IELTS AI Prep account.
        
        How to Reset Your Password:
        1. Click the link below to open the password reset page
        2. Enter your new password (minimum 8 characters)
        3. Confirm your new password by typing it again
        4. Click "Reset Password" to save your changes
        
        Reset Link:
        {reset_link}
        
        IMPORTANT: This reset link will expire in 30 minutes for your security.
        
        If you didn't request a password reset, please ignore this email. Your password will remain unchanged.
        
        Need help? Contact us at info@ieltsaiprep.com
        
        Best regards,
        IELTS AI Prep Team
        
        This email was sent from donotreply@ieltsaiprep.com. Please do not reply to this address.
        """
        
        return self.send_email(email, subject, html_body, text_body)
    
    def send_verification_email(self, email: str, verification_token: str) -> bool:
        """
        Send welcome email with login instructions
        
        Args:
            email: User's email address
            verification_token: Email verification token (optional - for compatibility)
        
        Returns:
            bool: True if email sent successfully
        """
        login_link = f"{self.domain_url}/login"
        forgot_password_link = f"{self.domain_url}/forgot-password"
        
        subject = "Welcome to IELTS AI Prep!"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
                
                body {{
                    font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f8f9fa;
                }}
                .header {{
                    background: white;
                    color: #e74c3c;
                    padding: 20px 30px;
                    text-align: left;
                    border-bottom: 1px solid #dee2e6;
                    border-radius: 10px 10px 0 0;
                }}
                .header h1 {{
                    margin: 0;
                    font-weight: 700;
                    font-size: 22px;
                    letter-spacing: -0.5px;
                }}
                .content {{
                    background: white;
                    padding: 30px;
                    border: 1px solid #e9ecef;
                    border-radius: 0 0 10px 10px;
                }}
                .content ul {{
                    list-style-type: none;
                    padding-left: 0;
                }}
                .content ul li {{
                    padding: 8px 0;
                    padding-left: 25px;
                    position: relative;
                }}
                .content ul li:before {{
                    content: "✓";
                    position: absolute;
                    left: 0;
                    color: #3498db;
                    font-weight: bold;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background: #3498db;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: 500;
                    margin: 20px 0;
                }}
                .button:hover {{
                    background: #2980b9;
                }}
                .footer {{
                    text-align: center;
                    color: #6c757d;
                    font-size: 12px;
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid #e9ecef;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>IELTS AI Prep</h1>
            </div>
            <div class="content">
                <p>Hello!</p>
                <p>Welcome to <strong>IELTS AI Prep</strong> - your AI-powered IELTS preparation platform. We're excited to support you on your IELTS journey!</p>
                
                <h3 style="color: #2c3e50; margin-top: 30px; margin-bottom: 15px;">📧 Your Login Details</h3>
                <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 3px solid #3498db;">
                    <p style="margin: 5px 0;"><strong>Email Address:</strong> {email}</p>
                    <p style="margin: 5px 0; color: #6c757d; font-size: 14px;">Use this email address to log in to your account</p>
                </div>
                
                <h3 style="color: #2c3e50; margin-top: 30px; margin-bottom: 15px;">🔑 Your Password</h3>
                <p>You can access your account using the same password you set during registration.</p>
                <p style="background: #fff3cd; padding: 12px; border-left: 3px solid #e74c3c; margin: 15px 0; font-size: 14px;">
                    <strong>💡 Tip:</strong> If you forgot your password, you can easily reset it using the "Forgot Password" link on the login page.
                </p>
                
                <h3 style="color: #2c3e50; margin-top: 30px; margin-bottom: 15px;">🚀 Ready to Get Started?</h3>
                <p>Click the button below to log in and access your AI-powered IELTS assessments:</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{login_link}" class="button">Log In Now</a>
                </div>
                
                <p style="text-align: center; margin-top: 20px;">
                    <a href="{forgot_password_link}" style="color: #3498db; text-decoration: none; font-size: 14px;">Forgot your password? Click here to reset it →</a>
                </p>
                
                <hr style="border: none; border-top: 1px solid #e9ecef; margin: 35px 0;">
                
                <p style="text-align: center; color: #2c3e50; font-size: 16px; margin: 25px 0;">
                    <strong>We wish you all the best in your IELTS journey!</strong>
                </p>
                
                <p style="text-align: center; margin-top: 20px;">
                    <strong>Best Wishes,</strong><br>
                    The IELTS AI Prep Team
                </p>
            </div>
            <div class="footer">
                <p>© 2025 IELTS AI Prep. All rights reserved.</p>
                <p>Need help? Contact us at <a href="mailto:info@ieltsaiprep.com" style="color: #3498db; text-decoration: none;">info@ieltsaiprep.com</a></p>
                <p style="margin-top: 10px; font-size: 11px;">This email was sent from donotreply@ieltsaiprep.com. Please do not reply to this address.</p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Welcome to IELTS AI Prep!
        
        Hello!
        
        Welcome to IELTS AI Prep - your AI-powered IELTS preparation platform. We're excited to support you on your IELTS journey!
        
        YOUR LOGIN DETAILS
        ------------------
        Email Address: {email}
        Use this email address to log in to your account
        
        YOUR PASSWORD
        -------------
        You can access your account using the same password you set during registration.
        
        Tip: If you forgot your password, you can easily reset it using the "Forgot Password" link on the login page.
        
        READY TO GET STARTED?
        ---------------------
        Log in now: {login_link}
        
        Forgot Password? {forgot_password_link}
        
        ------------------
        
        We wish you all the best in your IELTS journey!
        
        Best Wishes,
        The IELTS AI Prep Team
        
        ------------------
        
        Need help? Contact us at info@ieltsaiprep.com
        
        This email was sent from donotreply@ieltsaiprep.com. Please do not reply to this address.
        
        © 2025 IELTS AI Prep. All rights reserved.
        """
        
        return self.send_email(email, subject, html_body, text_body)
    
    def send_support_response_email(self, email: str, subject: str, response_text: str, ticket_id: str = None) -> bool:
        """
        Send customer support response email
        
        Args:
            email: User's email address
            subject: Email subject
            response_text: Support agent response
            ticket_id: Support ticket ID (optional)
        
        Returns:
            bool: True if email sent successfully
        """
        
        subject_line = f"Re: {subject}" if not subject.startswith("Re:") else subject
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
                
                body {{
                    font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f8f9fa;
                }}
                .header {{
                    background: white;
                    color: #e74c3c;
                    padding: 20px 30px;
                    text-align: left;
                    border-bottom: 1px solid #dee2e6;
                    border-radius: 10px 10px 0 0;
                }}
                .header h1 {{
                    margin: 0;
                    font-weight: 700;
                    font-size: 22px;
                    letter-spacing: -0.5px;
                }}
                .content {{
                    background: white;
                    padding: 30px;
                    border: 1px solid #e9ecef;
                    border-radius: 0 0 10px 10px;
                }}
                .ticket-id {{
                    background: #f8f9fa;
                    padding: 10px;
                    border-left: 3px solid #3498db;
                    margin: 15px 0;
                    font-size: 14px;
                    color: #6c757d;
                }}
                .response-text {{
                    margin: 20px 0;
                    white-space: pre-wrap;
                }}
                .footer {{
                    text-align: center;
                    color: #6c757d;
                    font-size: 12px;
                    margin-top: 20px;
                    padding-top: 20px;
                    border-top: 1px solid #e9ecef;
                }}
                .help-link {{
                    display: inline-block;
                    margin-top: 15px;
                    color: #3498db;
                    text-decoration: none;
                    font-weight: 500;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>IELTS AI Prep</h1>
            </div>
            <div class="content">
                <p>Hello,</p>
                {"<div class='ticket-id'>Ticket ID: " + ticket_id + "</div>" if ticket_id else ""}
                <div class="response-text">{response_text}</div>
                <p>If you have any additional questions, please don't hesitate to reach out.</p>
                <p>Best regards,<br>
                <strong>IELTS AI Prep Support Team</strong></p>
                <div style="text-align: center;">
                    <a href="{self.domain_url}/contact" class="help-link">Visit Help Center →</a>
                </div>
            </div>
            <div class="footer">
                <p>© 2025 IELTS AI Prep. All rights reserved.</p>
                <p>Need further assistance? Reply to this email or contact us at <a href="mailto:info@ieltsaiprep.com" style="color: #3498db; text-decoration: none;">info@ieltsaiprep.com</a></p>
                <p style="margin-top: 10px; font-size: 11px;">You're receiving this email because you contacted our support team.</p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        IELTS AI Prep Support
        {"Ticket ID: " + ticket_id if ticket_id else ""}
        
        Hello,
        
        {response_text}
        
        If you have any additional questions, please don't hesitate to reach out.
        
        Best regards,
        IELTS AI Prep Support Team
        
        ------------------
        
        Need further assistance? Reply to this email or contact us at info@ieltsaiprep.com
        
        Visit our help center: {self.domain_url}/contact
        
        © 2025 IELTS AI Prep. All rights reserved.
        You're receiving this email because you contacted our support team.
        """
        
        return self.send_email(email, subject_line, html_body, text_body)
    
    def test_connection(self) -> Dict:
        """
        Test SES connection and configuration
        
        Returns:
            Dict: Status information
        """
        try:
            # Get send quota
            quota = self.ses_client.get_send_quota()
            
            # Get verified identities
            identities = self.ses_client.list_verified_email_addresses()
            
            return {
                'status': 'connected',
                'region': self.region,
                'sender_email': self.sender_email,
                'send_quota': {
                    'max_24hour_send': quota.get('Max24HourSend', 0),
                    'sent_last_24hours': quota.get('SentLast24Hours', 0),
                    'max_send_rate': quota.get('MaxSendRate', 0)
                },
                'verified_emails': identities.get('VerifiedEmailAddresses', [])
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

# Initialize global instance
ses_service = SESEmailService()