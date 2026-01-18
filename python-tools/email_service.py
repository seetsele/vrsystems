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
import httpx
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('EmailService')


@dataclass
class EmailConfig:
    """Email configuration"""
    api_key: str = os.getenv('SENDGRID_API_KEY', '')
    from_email: str = os.getenv('FROM_EMAIL', 'noreply@verity-systems.com')
    from_name: str = os.getenv('FROM_NAME', 'Verity Systems')
    api_url: str = 'https://api.sendgrid.com/v3/mail/send'
    # Local SMTP fallback (e.g., MailHog or local relay)
    smtp_host: str = os.getenv('LOCAL_SMTP_HOST', 'localhost')
    smtp_port: int = int(os.getenv('LOCAL_SMTP_PORT', '1025'))
    smtp_user: str = os.getenv('LOCAL_SMTP_USER', '')
    smtp_pass: str = os.getenv('LOCAL_SMTP_PASS', '')


class EmailService:
    """SendGrid email service"""
    
    def __init__(self, config: Optional[EmailConfig] = None):
        self.config = config or EmailConfig()
        self._session: Optional[aiohttp.ClientSession] = None
    
    @property
    def is_configured(self) -> bool:
        # Consider local SMTP as a valid configured transport
        return bool(self.config.api_key) or bool(self.config.smtp_host)
    
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
        
        # Implement retries and idempotency via Supabase `email_logs` (preferred) or local file fallback
        idempotency_key = payload.get('headers', {}).get('Idempotency-Key') or f"email:{to_email}:{subject}:{hash(html_content) % 1000000}"

        # First, try Supabase to see if this idempotency_key already exists
        SUPABASE_URL = os.getenv('SUPABASE_URL')
        SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
        if SUPABASE_URL and SUPABASE_SERVICE_KEY:
            try:
                headers = {
                    'apikey': SUPABASE_SERVICE_KEY,
                    'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
                    'Content-Type': 'application/json'
                }
                async with httpx.AsyncClient(timeout=5) as _c:
                    r = await _c.get(f"{SUPABASE_URL}/rest/v1/email_logs?idempotency_key=eq.{idempotency_key}&select=id", headers=headers)
                    if r.status_code == 200 and r.json():
                        logger.info('Email already logged in Supabase (idempotent): %s', idempotency_key)
                        return {'success': True, 'status': 'cached'}
            except Exception:
                logger.debug('Supabase idempotency check failed, falling back to local cache')

        # Local persistent cache file (best-effort fallback)
        cache_file = os.path.join(os.path.dirname(__file__), '.email_sent_cache.json')
        sent_cache = {}
        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as cf:
                    import json as _json
                    sent_cache = _json.load(cf)
        except Exception:
            sent_cache = {}

        if idempotency_key in sent_cache:
            logger.info('Email already sent (local cache): %s', idempotency_key)
            return {'success': True, 'status': 'cached'}

        max_attempts = 3
        backoff = 0.8
        attempt = 0
        last_err = None
        while attempt < max_attempts:
            attempt += 1
            try:
                # If local SMTP is configured, use it as a fallback transport
                if self.config.smtp_host:
                    # Build plain text + html message
                    from email.message import EmailMessage
                    msg = EmailMessage()
                    msg['Subject'] = subject
                    msg['From'] = f"{self.config.from_name} <{self.config.from_email}>"
                    msg['To'] = to_email
                    if plain_content:
                        msg.set_content(plain_content)
                    # Add HTML alternative
                    msg.add_alternative(html_content, subtype='html')

                    import smtplib

                    # Perform synchronous SMTP send inside a thread (simpler and reliable)
                    def _send_blocking():
                        try:
                            with smtplib.SMTP(self.config.smtp_host, int(self.config.smtp_port or 1025), timeout=10) as s:
                                s.ehlo()
                                try:
                                    s.starttls()
                                except Exception:
                                    pass
                                if self.config.smtp_user and self.config.smtp_pass:
                                    s.login(self.config.smtp_user, self.config.smtp_pass)
                                s.send_message(msg)
                            return True, None
                        except Exception as e:
                            return False, str(e)

                    success, err = await asyncio.to_thread(_send_blocking)
                    if success:
                        logger.info(f"Email sent to {to_email} via local SMTP {self.config.smtp_host}:{self.config.smtp_port}")
                        sent_cache[idempotency_key] = { 'to': to_email, 'subject': subject, 'ts': datetime.utcnow().isoformat() }
                        import json as _json
                        try:
                            with open(cache_file, 'w', encoding='utf-8') as cf:
                                _json.dump(sent_cache, cf)
                        except Exception:
                            logger.debug('Failed to persist email cache')
                        return {'success': True, 'status': 'smtp_sent'}
                    else:
                        last_err = err
                        logger.exception('Local SMTP send failed: %s', err)

                else:
                    session = await self.get_session()
                    hdrs = {
                        'Authorization': f'Bearer {self.config.api_key}',
                        'Content-Type': 'application/json'
                    }
                    # SendGrid accepts categories and reply_to as part of payload (already set)
                    async with session.post(self.config.api_url, json=payload, headers=hdrs) as response:
                        if response.status in (200, 201, 202):
                            logger.info(f"Email sent to {to_email}: {subject} (attempt {attempt})")
                            # mark sent
                            try:
                                sent_cache[idempotency_key] = { 'to': to_email, 'subject': subject, 'ts': datetime.utcnow().isoformat() }
                                import json as _json
                                with open(cache_file, 'w', encoding='utf-8') as cf:
                                    _json.dump(sent_cache, cf)
                            except Exception:
                                logger.debug('Failed to persist email cache')

                            # Try to persist email log to Supabase (best-effort)
                            try:
                                if SUPABASE_URL and SUPABASE_SERVICE_KEY:
                                    headers = {
                                        'apikey': SUPABASE_SERVICE_KEY,
                                        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
                                        'Content-Type': 'application/json'
                                    }
                                    log_payload = {
                                        'idempotency_key': idempotency_key,
                                        'to_email': to_email,
                                        'subject': subject,
                                        'sent_at': datetime.utcnow().isoformat(),
                                        'status_code': response.status,
                                        'response_text': ''
                                    }
                                    async with httpx.AsyncClient(timeout=5) as _c:
                                        await _c.post(f"{SUPABASE_URL}/rest/v1/email_logs", json=[log_payload], headers=headers)
                            except Exception:
                                logger.debug('Failed to send email log to Supabase')
                            return {'success': True, 'status': response.status}
                        else:
                            error_text = await response.text()
                            logger.warning('Email send returned %s (attempt %s): %s', response.status, attempt, error_text[:200])
                            last_err = f"{response.status}: {error_text}"
            except Exception as e:
                logger.exception('Email error (attempt %s): %s', attempt, e)
                last_err = str(e)

            # Exponential backoff
            await asyncio.sleep(backoff * attempt)

        logger.error('Email failed after %s attempts: %s', max_attempts, last_err)
        return {'success': False, 'error': last_err}
    
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
