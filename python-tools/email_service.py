"""
Verity Systems - Email Service
==============================
SendGrid integration for transactional emails
"""

import os
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import aiohttp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('EmailService')


@dataclass
class EmailConfig:
    """Email configuration"""
    api_key: str = os.getenv('SENDGRID_API_KEY', '')
    from_email: str = os.getenv('FROM_EMAIL', 'noreply@verity-systems.com')
    from_name: str = os.getenv('FROM_NAME', 'Verity Systems')
    api_url: str = 'https://api.sendgrid.com/v3/mail/send'


class EmailService:
    """SendGrid email service"""
    
    def __init__(self, config: Optional[EmailConfig] = None):
        self.config = config or EmailConfig()
        self._session: Optional[aiohttp.ClientSession] = None
    
    @property
    def is_configured(self) -> bool:
        return bool(self.config.api_key)
    
    async def get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_content: Optional[str] = None,
        to_name: Optional[str] = None,
        reply_to: Optional[str] = None,
        categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Send an email via SendGrid"""
        
        if not self.is_configured:
            logger.warning("Email service not configured - SENDGRID_API_KEY not set")
            return {'success': False, 'error': 'Email service not configured'}
        
        # Build email payload
        payload = {
            'personalizations': [{
                'to': [{'email': to_email, 'name': to_name or to_email}]
            }],
            'from': {
                'email': self.config.from_email,
                'name': self.config.from_name
            },
            'subject': subject,
            'content': [
                {'type': 'text/html', 'value': html_content}
            ]
        }
        
        # Add plain text fallback
        if plain_content:
            payload['content'].insert(0, {'type': 'text/plain', 'value': plain_content})
        
        # Add reply-to
        if reply_to:
            payload['reply_to'] = {'email': reply_to}
        
        # Add categories for tracking
        if categories:
            payload['categories'] = categories
        
        try:
            session = await self.get_session()
            async with session.post(
                self.config.api_url,
                json=payload,
                headers={
                    'Authorization': f'Bearer {self.config.api_key}',
                    'Content-Type': 'application/json'
                }
            ) as response:
                if response.status in (200, 201, 202):
                    logger.info(f"Email sent to {to_email}: {subject}")
                    return {'success': True, 'status': response.status}
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to send email: {response.status} - {error_text}")
                    return {'success': False, 'status': response.status, 'error': error_text}
        except Exception as e:
            logger.error(f"Email error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def send_welcome_email(self, to_email: str, user_name: str) -> Dict[str, Any]:
        """Send welcome email to new user"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0a0a0b; color: #fafafa; margin: 0; padding: 40px 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #111113; border-radius: 16px; border: 1px solid rgba(255,255,255,0.06); overflow: hidden; }}
                .header {{ background: linear-gradient(135deg, #f59e0b, #fbbf24); padding: 40px 32px; text-align: center; }}
                .header h1 {{ color: #0a0a0b; margin: 0; font-size: 28px; font-weight: 700; }}
                .content {{ padding: 40px 32px; }}
                .content h2 {{ color: #fafafa; margin: 0 0 16px; font-size: 22px; }}
                .content p {{ color: #a3a3a3; line-height: 1.7; margin: 0 0 20px; }}
                .btn {{ display: inline-block; background: #f59e0b; color: #0a0a0b; padding: 14px 28px; border-radius: 10px; text-decoration: none; font-weight: 600; }}
                .footer {{ padding: 24px 32px; border-top: 1px solid rgba(255,255,255,0.06); text-align: center; }}
                .footer p {{ color: #525252; font-size: 13px; margin: 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to Verity</h1>
                </div>
                <div class="content">
                    <h2>Hey {user_name}!</h2>
                    <p>Welcome to Verity Systems – the most advanced AI-powered fact-checking platform. You now have access to 32+ AI models for verifying any claim.</p>
                    <p>Get started by verifying your first claim:</p>
                    <a href="https://vrsystemss.vercel.app/verify.html" class="btn">Start Verifying →</a>
                    <p style="margin-top: 24px;">If you have any questions, just reply to this email.</p>
                </div>
                <div class="footer">
                    <p>Verity Systems - AI-Powered Truth Verification</p>
                </div>
            </div>
        </body>
        </html>
        """
        return await self.send_email(
            to_email=to_email,
            subject="Welcome to Verity Systems 🛡️",
            html_content=html,
            to_name=user_name,
            categories=['welcome', 'onboarding']
        )
    
    async def send_verification_result(
        self,
        to_email: str,
        user_name: str,
        claim: str,
        verdict: str,
        score: int,
        explanation: str
    ) -> Dict[str, Any]:
        """Send verification result email"""
        
        # Color based on verdict
        color = '#10b981' if score >= 70 else '#f59e0b' if score >= 40 else '#ef4444'
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0a0a0b; color: #fafafa; margin: 0; padding: 40px 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #111113; border-radius: 16px; border: 1px solid rgba(255,255,255,0.06); overflow: hidden; }}
                .header {{ background: #18181b; padding: 24px 32px; border-bottom: 1px solid rgba(255,255,255,0.06); }}
                .header h1 {{ color: #fafafa; margin: 0; font-size: 20px; }}
                .result {{ padding: 32px; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.06); }}
                .score {{ font-size: 48px; font-weight: 700; color: {color}; margin-bottom: 8px; }}
                .verdict {{ display: inline-block; background: {color}20; color: {color}; padding: 8px 16px; border-radius: 8px; font-weight: 600; text-transform: uppercase; font-size: 12px; }}
                .content {{ padding: 32px; }}
                .claim {{ background: #18181b; padding: 16px; border-radius: 10px; border-left: 3px solid {color}; margin-bottom: 20px; }}
                .claim-label {{ font-size: 11px; color: #525252; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }}
                .claim-text {{ color: #fafafa; font-style: italic; }}
                .explanation {{ color: #a3a3a3; line-height: 1.7; }}
                .footer {{ padding: 24px 32px; background: #0a0a0b; text-align: center; }}
                .footer a {{ color: #f59e0b; text-decoration: none; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Verification Complete</h1>
                </div>
                <div class="result">
                    <div class="score">{score}</div>
                    <div class="verdict">{verdict}</div>
                </div>
                <div class="content">
                    <div class="claim">
                        <div class="claim-label">Claim Verified</div>
                        <div class="claim-text">"{claim[:150]}{'...' if len(claim) > 150 else ''}"</div>
                    </div>
                    <p class="explanation">{explanation}</p>
                </div>
                <div class="footer">
                    <p><a href="https://vrsystemss.vercel.app/verify.html">Verify another claim →</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        return await self.send_email(
            to_email=to_email,
            subject=f"Verification Result: {verdict} ({score}%)",
            html_content=html,
            to_name=user_name,
            categories=['verification', 'result']
        )
    
    async def send_password_reset(self, to_email: str, reset_token: str) -> Dict[str, Any]:
        """Send password reset email"""
        reset_link = f"https://vrsystemss.vercel.app/reset-password.html?token={reset_token}"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0a0a0b; color: #fafafa; margin: 0; padding: 40px 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #111113; border-radius: 16px; border: 1px solid rgba(255,255,255,0.06); overflow: hidden; }}
                .header {{ background: #18181b; padding: 32px; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.06); }}
                .header h1 {{ color: #fafafa; margin: 0; font-size: 22px; }}
                .content {{ padding: 40px 32px; text-align: center; }}
                .content p {{ color: #a3a3a3; line-height: 1.7; margin: 0 0 24px; }}
                .btn {{ display: inline-block; background: #f59e0b; color: #0a0a0b; padding: 14px 32px; border-radius: 10px; text-decoration: none; font-weight: 600; }}
                .expires {{ color: #525252; font-size: 13px; margin-top: 24px; }}
                .footer {{ padding: 24px 32px; border-top: 1px solid rgba(255,255,255,0.06); text-align: center; }}
                .footer p {{ color: #525252; font-size: 13px; margin: 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Reset Your Password</h1>
                </div>
                <div class="content">
                    <p>We received a request to reset your password. Click the button below to create a new password.</p>
                    <a href="{reset_link}" class="btn">Reset Password</a>
                    <p class="expires">This link expires in 1 hour.</p>
                </div>
                <div class="footer">
                    <p>If you didn't request this, you can safely ignore this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return await self.send_email(
            to_email=to_email,
            subject="Reset Your Password - Verity Systems",
            html_content=html,
            categories=['password-reset', 'security']
        )


# Global email service instance
email_service = EmailService()


# Test function
async def test_email():
    """Test email service"""
    service = EmailService()
    if service.is_configured:
        result = await service.send_email(
            to_email="test@example.com",
            subject="Test Email from Verity",
            html_content="<h1>Hello!</h1><p>This is a test email.</p>"
        )
        print(f"Email test result: {result}")
    else:
        print("Email service not configured - set SENDGRID_API_KEY in .env")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_email())
