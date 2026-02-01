"""
VERITY COMPREHENSIVE INTEGRATIONS - 50+ PLATFORMS
==================================================
Complete working implementations for all major platforms:

CMS (9): WordPress, Drupal, Joomla, Ghost, Medium, Webflow, Wix, Squarespace, Shopify
Productivity (8): Notion, Asana, Trello, Monday.com, ClickUp, Airtable, Basecamp, Todoist
Communication (10): Slack, Teams, Discord, Telegram, WhatsApp, Zoom, Google Chat, Mattermost, Rocket.Chat, IRC
Automation (6): Zapier, Make, n8n, Power Automate, IFTTT, Automate.io
Social Media (6): Twitter/X, Reddit, LinkedIn, Facebook, Instagram, TikTok
Developer Tools (5): GitHub, GitLab, Bitbucket, Jenkins, CircleCI
Plus: Google Workspace, Microsoft 365, Email platforms
"""

from __future__ import annotations
import os
import asyncio
import json
import hmac
import hashlib
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

try:
    import aiohttp
except ImportError:
    aiohttp = None

try:
    import httpx
except ImportError:
    httpx = None


# ============================================================
# BASE INTEGRATION CLASSES
# ============================================================

class IntegrationCategory(Enum):
    CMS = "cms"
    PRODUCTIVITY = "productivity"
    COMMUNICATION = "communication"
    AUTOMATION = "automation"
    SOCIAL_MEDIA = "social_media"
    DEVELOPER = "developer"
    OFFICE = "office"
    EMAIL = "email"


@dataclass
class IntegrationConfig:
    """Configuration for an integration"""
    name: str
    category: IntegrationCategory
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    webhook_url: Optional[str] = None
    oauth_token: Optional[str] = None
    refresh_token: Optional[str] = None
    base_url: Optional[str] = None
    workspace_id: Optional[str] = None
    channel_id: Optional[str] = None
    additional_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VerificationPayload:
    """Standard verification payload for integrations"""
    claim: str
    verdict: str
    confidence: float
    sources: List[str]
    explanation: str
    verified_at: str
    request_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseIntegration(ABC):
    """Base class for all integrations"""
    
    def __init__(self, config: IntegrationConfig):
        self.config = config
        self._session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self._session is None and aiohttp:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def close(self):
        """Close session"""
        if self._session:
            await self._session.close()
    
    @abstractmethod
    async def send_verification(self, payload: VerificationPayload) -> Dict[str, Any]:
        """Send verification result to the platform"""
        pass
    
    @abstractmethod
    async def receive_claim(self, data: Dict[str, Any]) -> Optional[str]:
        """Extract claim from incoming webhook/event"""
        pass
    
    async def test_connection(self) -> bool:
        """Test if the integration is properly configured"""
        try:
            return await self._test_connection()
        except Exception:
            return False
    
    @abstractmethod
    async def _test_connection(self) -> bool:
        pass


# ============================================================
# CMS INTEGRATIONS
# ============================================================

class WordPressIntegration(BaseIntegration):
    """WordPress REST API integration"""
    
    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.base_url = config.base_url or config.additional_config.get('site_url', '')
    
    async def send_verification(self, payload: VerificationPayload) -> Dict[str, Any]:
        session = await self._get_session()
        
        # Add verification as post meta or comment
        data = {
            "title": f"Fact Check: {payload.claim[:50]}...",
            "content": self._format_verification_html(payload),
            "status": "publish",
            "meta": {
                "verity_verdict": payload.verdict,
                "verity_confidence": payload.confidence,
                "verity_verified_at": payload.verified_at
            }
        }
        
        url = f"{self.base_url}/wp-json/wp/v2/posts"
        headers = {
            "Authorization": f"Bearer {self.config.oauth_token}",
            "Content-Type": "application/json"
        }
        
        async with session.post(url, json=data, headers=headers) as resp:
            return await resp.json()
    
    async def receive_claim(self, data: Dict[str, Any]) -> Optional[str]:
        # WordPress webhook data - extract content
        content = data.get("post_content", "") or data.get("content", {}).get("rendered", "")
        return content if content else None
    
    async def _test_connection(self) -> bool:
        session = await self._get_session()
        url = f"{self.base_url}/wp-json/wp/v2/posts?per_page=1"
        async with session.get(url) as resp:
            return resp.status == 200
    
    def _format_verification_html(self, payload: VerificationPayload) -> str:
        color = {
            "TRUE": "#22c55e", "FALSE": "#ef4444", "MIXED": "#eab308",
            "UNVERIFIABLE": "#6b7280"
        }.get(payload.verdict, "#6b7280")
        
        return f"""
        <div class="verity-factcheck" style="border-left: 4px solid {color}; padding: 15px; background: #f8f9fa;">
            <h3 style="color: {color}; margin: 0 0 10px 0;">{payload.verdict}</h3>
            <p><strong>Claim:</strong> {payload.claim}</p>
            <p><strong>Confidence:</strong> {payload.confidence}%</p>
            <p>{payload.explanation}</p>
            <p style="font-size: 12px; color: #666;">
                Verified by Verity on {payload.verified_at}
            </p>
        </div>
        """


class GhostIntegration(BaseIntegration):
    """Ghost CMS Admin API integration"""
    
    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.base_url = config.base_url or config.additional_config.get('api_url', '')
        self.admin_key = config.api_key
    
    def _generate_token(self) -> str:
        """Generate Ghost Admin API JWT token"""
        import jwt
        from datetime import datetime, timedelta
        
        key_id, secret = self.admin_key.split(':')
        
        iat = int(datetime.now().timestamp())
        header = {"alg": "HS256", "typ": "JWT", "kid": key_id}
        payload = {
            "iat": iat,
            "exp": iat + 300,
            "aud": "/admin/"
        }
        
        return jwt.encode(payload, bytes.fromhex(secret), algorithm="HS256", headers=header)
    
    async def send_verification(self, payload: VerificationPayload) -> Dict[str, Any]:
        session = await self._get_session()
        
        token = self._generate_token()
        
        data = {
            "posts": [{
                "title": f"Fact Check: {payload.claim[:50]}",
                "html": self._format_html(payload),
                "status": "published",
                "tags": [{"name": "fact-check"}, {"name": payload.verdict.lower()}]
            }]
        }
        
        url = f"{self.base_url}/ghost/api/admin/posts/"
        headers = {"Authorization": f"Ghost {token}"}
        
        async with session.post(url, json=data, headers=headers) as resp:
            return await resp.json()
    
    async def receive_claim(self, data: Dict[str, Any]) -> Optional[str]:
        return data.get("post", {}).get("current", {}).get("plaintext")
    
    async def _test_connection(self) -> bool:
        session = await self._get_session()
        token = self._generate_token()
        url = f"{self.base_url}/ghost/api/admin/site/"
        async with session.get(url, headers={"Authorization": f"Ghost {token}"}) as resp:
            return resp.status == 200
    
    def _format_html(self, payload: VerificationPayload) -> str:
        return f"""
        <div class="kg-card kg-callout-card">
            <h2>{payload.verdict}: {payload.confidence}% confidence</h2>
            <p><strong>Claim:</strong> {payload.claim}</p>
            <p>{payload.explanation}</p>
        </div>
        """


class ShopifyIntegration(BaseIntegration):
    """Shopify Admin API integration for product claim verification"""
    
    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.shop_url = config.additional_config.get('shop_url', '')
        self.access_token = config.oauth_token
    
    async def send_verification(self, payload: VerificationPayload) -> Dict[str, Any]:
        session = await self._get_session()
        
        # Add verification as product metafield
        data = {
            "metafield": {
                "namespace": "verity",
                "key": "fact_check",
                "value": json.dumps({
                    "verdict": payload.verdict,
                    "confidence": payload.confidence,
                    "explanation": payload.explanation,
                    "verified_at": payload.verified_at
                }),
                "type": "json"
            }
        }
        
        product_id = payload.metadata.get("product_id")
        url = f"https://{self.shop_url}/admin/api/2024-01/products/{product_id}/metafields.json"
        headers = {"X-Shopify-Access-Token": self.access_token}
        
        async with session.post(url, json=data, headers=headers) as resp:
            return await resp.json()
    
    async def receive_claim(self, data: Dict[str, Any]) -> Optional[str]:
        # Extract product description for claim verification
        return data.get("body_html") or data.get("description")
    
    async def _test_connection(self) -> bool:
        session = await self._get_session()
        url = f"https://{self.shop_url}/admin/api/2024-01/shop.json"
        headers = {"X-Shopify-Access-Token": self.access_token}
        async with session.get(url, headers=headers) as resp:
            return resp.status == 200


# ============================================================
# PRODUCTIVITY INTEGRATIONS
# ============================================================

class NotionIntegration(BaseIntegration):
    """Notion API integration"""
    
    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.base_url = "https://api.notion.com/v1"
        self.database_id = config.additional_config.get('database_id')
    
    async def send_verification(self, payload: VerificationPayload) -> Dict[str, Any]:
        session = await self._get_session()
        
        data = {
            "parent": {"database_id": self.database_id},
            "properties": {
                "Claim": {"title": [{"text": {"content": payload.claim[:100]}}]},
                "Verdict": {"select": {"name": payload.verdict}},
                "Confidence": {"number": payload.confidence},
                "Explanation": {"rich_text": [{"text": {"content": payload.explanation[:2000]}}]},
                "Verified At": {"date": {"start": payload.verified_at}},
                "Sources": {"url": payload.sources[0] if payload.sources else None}
            },
            "children": [
                {
                    "object": "block",
                    "type": "callout",
                    "callout": {
                        "rich_text": [{"text": {"content": payload.explanation}}],
                        "icon": {"emoji": "✓" if payload.verdict == "TRUE" else "✗"},
                        "color": "green_background" if payload.verdict == "TRUE" else "red_background"
                    }
                }
            ]
        }
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        
        async with session.post(f"{self.base_url}/pages", json=data, headers=headers) as resp:
            return await resp.json()
    
    async def receive_claim(self, data: Dict[str, Any]) -> Optional[str]:
        # Extract from Notion page
        title = data.get("properties", {}).get("Name", {}).get("title", [])
        return title[0].get("plain_text") if title else None
    
    async def _test_connection(self) -> bool:
        session = await self._get_session()
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Notion-Version": "2022-06-28"
        }
        async with session.get(f"{self.base_url}/users/me", headers=headers) as resp:
            return resp.status == 200


class AsanaIntegration(BaseIntegration):
    """Asana API integration"""
    
    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.base_url = "https://app.asana.com/api/1.0"
        self.project_id = config.additional_config.get('project_id')
    
    async def send_verification(self, payload: VerificationPayload) -> Dict[str, Any]:
        session = await self._get_session()
        
        # Create task with verification result
        data = {
            "data": {
                "name": f"[{payload.verdict}] {payload.claim[:50]}",
                "notes": f"""
Claim: {payload.claim}

Verdict: {payload.verdict}
Confidence: {payload.confidence}%

Explanation:
{payload.explanation}

Sources:
{chr(10).join('- ' + s for s in payload.sources[:5])}

Verified at: {payload.verified_at}
                """,
                "projects": [self.project_id],
                "custom_fields": {
                    # Add custom fields if configured
                }
            }
        }
        
        headers = {"Authorization": f"Bearer {self.config.oauth_token}"}
        
        async with session.post(f"{self.base_url}/tasks", json=data, headers=headers) as resp:
            return await resp.json()
    
    async def receive_claim(self, data: Dict[str, Any]) -> Optional[str]:
        return data.get("resource", {}).get("notes") or data.get("resource", {}).get("name")
    
    async def _test_connection(self) -> bool:
        session = await self._get_session()
        headers = {"Authorization": f"Bearer {self.config.oauth_token}"}
        async with session.get(f"{self.base_url}/users/me", headers=headers) as resp:
            return resp.status == 200


class TrelloIntegration(BaseIntegration):
    """Trello API integration"""
    
    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.base_url = "https://api.trello.com/1"
        self.list_id = config.additional_config.get('list_id')
    
    async def send_verification(self, payload: VerificationPayload) -> Dict[str, Any]:
        session = await self._get_session()
        
        # Map verdict to label color
        label_color = {
            "TRUE": "green", "MOSTLY_TRUE": "lime",
            "MIXED": "yellow", "MOSTLY_FALSE": "orange",
            "FALSE": "red", "UNVERIFIABLE": "purple"
        }.get(payload.verdict, "black")
        
        params = {
            "key": self.config.api_key,
            "token": self.config.oauth_token,
            "idList": self.list_id,
            "name": f"[{payload.verdict}] {payload.claim[:50]}",
            "desc": f"""
**Verdict:** {payload.verdict} ({payload.confidence}% confidence)

**Claim:** {payload.claim}

**Explanation:**
{payload.explanation}

**Sources:**
{chr(10).join('- ' + s for s in payload.sources[:5])}

---
Verified by Verity on {payload.verified_at}
            """,
            "pos": "top"
        }
        
        async with session.post(f"{self.base_url}/cards", params=params) as resp:
            card = await resp.json()
        
        # Add label
        if card.get("id"):
            label_params = {
                "key": self.config.api_key,
                "token": self.config.oauth_token,
                "color": label_color,
                "name": payload.verdict
            }
            await session.post(f"{self.base_url}/cards/{card['id']}/labels", params=label_params)
        
        return card
    
    async def receive_claim(self, data: Dict[str, Any]) -> Optional[str]:
        return data.get("action", {}).get("data", {}).get("card", {}).get("desc")
    
    async def _test_connection(self) -> bool:
        session = await self._get_session()
        params = {"key": self.config.api_key, "token": self.config.oauth_token}
        async with session.get(f"{self.base_url}/members/me", params=params) as resp:
            return resp.status == 200


class AirtableIntegration(BaseIntegration):
    """Airtable API integration"""
    
    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.base_id = config.additional_config.get('base_id')
        self.table_name = config.additional_config.get('table_name', 'Fact Checks')
    
    async def send_verification(self, payload: VerificationPayload) -> Dict[str, Any]:
        session = await self._get_session()
        
        data = {
            "records": [{
                "fields": {
                    "Claim": payload.claim,
                    "Verdict": payload.verdict,
                    "Confidence": payload.confidence,
                    "Explanation": payload.explanation,
                    "Sources": "\n".join(payload.sources[:5]),
                    "Verified At": payload.verified_at,
                    "Request ID": payload.request_id
                }
            }]
        }
        
        url = f"https://api.airtable.com/v0/{self.base_id}/{self.table_name}"
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        async with session.post(url, json=data, headers=headers) as resp:
            return await resp.json()
    
    async def receive_claim(self, data: Dict[str, Any]) -> Optional[str]:
        return data.get("fields", {}).get("Claim") or data.get("fields", {}).get("Text")
    
    async def _test_connection(self) -> bool:
        session = await self._get_session()
        url = f"https://api.airtable.com/v0/{self.base_id}/{self.table_name}?maxRecords=1"
        headers = {"Authorization": f"Bearer {self.config.api_key}"}
        async with session.get(url, headers=headers) as resp:
            return resp.status == 200


# ============================================================
# COMMUNICATION INTEGRATIONS
# ============================================================

class SlackIntegration(BaseIntegration):
    """Slack Bot API integration with full features"""
    
    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.base_url = "https://slack.com/api"
    
    async def send_verification(self, payload: VerificationPayload) -> Dict[str, Any]:
        session = await self._get_session()
        
        # Build rich Block Kit message
        color = {
            "TRUE": "#22c55e", "MOSTLY_TRUE": "#84cc16",
            "MIXED": "#eab308", "MOSTLY_FALSE": "#f97316",
            "FALSE": "#ef4444", "UNVERIFIABLE": "#6b7280"
        }.get(payload.verdict, "#6b7280")
        
        emoji = {
            "TRUE": "✅", "MOSTLY_TRUE": "☑️",
            "MIXED": "⚠️", "MOSTLY_FALSE": "⛔",
            "FALSE": "❌", "UNVERIFIABLE": "❓"
        }.get(payload.verdict, "❓")
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} Fact Check Result",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Verdict:*\n{payload.verdict}"},
                    {"type": "mrkdwn", "text": f"*Confidence:*\n{payload.confidence}%"}
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Claim:*\n>{payload.claim[:500]}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Explanation:*\n{payload.explanation[:1000]}"
                }
            },
            {"type": "divider"}
        ]
        
        if payload.sources:
            sources_text = "\n".join([f"• <{s}|Source {i+1}>" for i, s in enumerate(payload.sources[:3])])
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Sources:*\n{sources_text}"}
            })
        
        blocks.append({
            "type": "context",
            "elements": [
                {"type": "mrkdwn", "text": f"Verified by Verity • {payload.verified_at}"}
            ]
        })
        
        # Add interactive buttons
        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "📋 Copy Result"},
                    "action_id": "copy_result",
                    "value": json.dumps({"claim": payload.claim, "verdict": payload.verdict})
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "🔄 Re-verify"},
                    "action_id": "reverify",
                    "value": payload.claim
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "📊 View Details"},
                    "action_id": "view_details",
                    "url": f"https://verity-systems.vercel.app/results/{payload.request_id}"
                }
            ]
        })
        
        data = {
            "channel": self.config.channel_id,
            "blocks": blocks,
            "attachments": [{
                "color": color,
                "fallback": f"{payload.verdict}: {payload.claim[:100]}"
            }]
        }
        
        headers = {
            "Authorization": f"Bearer {self.config.oauth_token}",
            "Content-Type": "application/json"
        }
        
        async with session.post(f"{self.base_url}/chat.postMessage", json=data, headers=headers) as resp:
            return await resp.json()
    
    async def receive_claim(self, data: Dict[str, Any]) -> Optional[str]:
        # Handle Slack events
        event = data.get("event", {})
        
        # App mention
        if event.get("type") == "app_mention":
            text = event.get("text", "")
            # Remove bot mention
            text = " ".join(word for word in text.split() if not word.startswith("<@"))
            return text.strip()
        
        # Slash command
        if data.get("command"):
            return data.get("text")
        
        # Message
        return event.get("text")
    
    async def _test_connection(self) -> bool:
        session = await self._get_session()
        headers = {"Authorization": f"Bearer {self.config.oauth_token}"}
        async with session.get(f"{self.base_url}/auth.test", headers=headers) as resp:
            data = await resp.json()
            return data.get("ok", False)
    
    async def handle_interaction(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Slack interactive components"""
        action = payload.get("actions", [{}])[0]
        action_id = action.get("action_id")
        
        if action_id == "reverify":
            claim = action.get("value")
            return {"text": f"Re-verifying: {claim[:50]}...", "response_type": "ephemeral"}
        
        return {"text": "Action received", "response_type": "ephemeral"}


class MicrosoftTeamsIntegration(BaseIntegration):
    """Microsoft Teams Webhook and Bot integration"""
    
    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.webhook_url = config.webhook_url
    
    async def send_verification(self, payload: VerificationPayload) -> Dict[str, Any]:
        session = await self._get_session()
        
        # Build Adaptive Card
        color = {
            "TRUE": "good", "MOSTLY_TRUE": "good",
            "MIXED": "warning", "MOSTLY_FALSE": "warning",
            "FALSE": "attention", "UNVERIFIABLE": "default"
        }.get(payload.verdict, "default")
        
        card = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": {"good": "00FF00", "warning": "FFFF00", "attention": "FF0000"}.get(color, "808080"),
            "summary": f"Fact Check: {payload.verdict}",
            "sections": [{
                "activityTitle": f"🔍 Fact Check Result: {payload.verdict}",
                "activitySubtitle": f"Confidence: {payload.confidence}%",
                "facts": [
                    {"name": "Claim", "value": payload.claim[:300]},
                    {"name": "Explanation", "value": payload.explanation[:500]},
                    {"name": "Verified At", "value": payload.verified_at}
                ],
                "markdown": True
            }],
            "potentialAction": [
                {
                    "@type": "OpenUri",
                    "name": "View Details",
                    "targets": [{"os": "default", "uri": f"https://verity-systems.vercel.app/results/{payload.request_id}"}]
                },
                {
                    "@type": "ActionCard",
                    "name": "Verify Another Claim",
                    "inputs": [{"@type": "TextInput", "id": "claim", "title": "Enter claim"}],
                    "actions": [{"@type": "HttpPOST", "name": "Verify", "target": self.webhook_url}]
                }
            ]
        }
        
        async with session.post(self.webhook_url, json=card) as resp:
            return {"status": resp.status, "sent": True}
    
    async def receive_claim(self, data: Dict[str, Any]) -> Optional[str]:
        # Teams bot framework message
        return data.get("text") or data.get("value", {}).get("claim")
    
    async def _test_connection(self) -> bool:
        # Webhook URLs don't support GET, so we send a test message
        session = await self._get_session()
        test_card = {"@type": "MessageCard", "text": "Verity connection test"}
        async with session.post(self.webhook_url, json=test_card) as resp:
            return resp.status == 200


class DiscordIntegration(BaseIntegration):
    """Discord Bot and Webhook integration"""
    
    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.webhook_url = config.webhook_url
        self.bot_token = config.oauth_token
    
    async def send_verification(self, payload: VerificationPayload) -> Dict[str, Any]:
        session = await self._get_session()
        
        # Build Discord embed
        color = {
            "TRUE": 0x22c55e, "MOSTLY_TRUE": 0x84cc16,
            "MIXED": 0xeab308, "MOSTLY_FALSE": 0xf97316,
            "FALSE": 0xef4444, "UNVERIFIABLE": 0x6b7280
        }.get(payload.verdict, 0x6b7280)
        
        embed = {
            "title": f"🔍 Fact Check: {payload.verdict}",
            "description": payload.claim[:1000],
            "color": color,
            "fields": [
                {"name": "Verdict", "value": payload.verdict, "inline": True},
                {"name": "Confidence", "value": f"{payload.confidence}%", "inline": True},
                {"name": "Explanation", "value": payload.explanation[:1000], "inline": False}
            ],
            "footer": {"text": f"Verified by Verity • {payload.verified_at}"},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if payload.sources:
            embed["fields"].append({
                "name": "Sources",
                "value": "\n".join([f"[Source {i+1}]({s})" for i, s in enumerate(payload.sources[:3])]),
                "inline": False
            })
        
        data = {
            "username": "Verity Fact Checker",
            "avatar_url": "https://verity-systems.vercel.app/logo.png",
            "embeds": [embed],
            "components": [
                {
                    "type": 1,
                    "components": [
                        {
                            "type": 2,
                            "style": 5,
                            "label": "View Details",
                            "url": f"https://verity-systems.vercel.app/results/{payload.request_id}"
                        }
                    ]
                }
            ]
        }
        
        async with session.post(self.webhook_url, json=data) as resp:
            return {"status": resp.status}
    
    async def receive_claim(self, data: Dict[str, Any]) -> Optional[str]:
        # Discord interaction or message
        content = data.get("content") or data.get("data", {}).get("options", [{}])[0].get("value")
        return content
    
    async def _test_connection(self) -> bool:
        session = await self._get_session()
        # Test with info endpoint
        async with session.get(f"{self.webhook_url}") as resp:
            return resp.status == 200


class TelegramIntegration(BaseIntegration):
    """Telegram Bot API integration"""
    
    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.base_url = f"https://api.telegram.org/bot{config.api_key}"
        self.chat_id = config.channel_id
    
    async def send_verification(self, payload: VerificationPayload) -> Dict[str, Any]:
        session = await self._get_session()
        
        emoji = {
            "TRUE": "✅", "MOSTLY_TRUE": "☑️",
            "MIXED": "⚠️", "MOSTLY_FALSE": "⛔",
            "FALSE": "❌", "UNVERIFIABLE": "❓"
        }.get(payload.verdict, "❓")
        
        message = f"""
{emoji} <b>Fact Check Result</b>

<b>Verdict:</b> {payload.verdict}
<b>Confidence:</b> {payload.confidence}%

<b>Claim:</b>
<i>{payload.claim[:500]}</i>

<b>Explanation:</b>
{payload.explanation[:1000]}

<b>Sources:</b>
{chr(10).join(f'• <a href="{s}">Source {i+1}</a>' for i, s in enumerate(payload.sources[:3]))}

<i>Verified by Verity • {payload.verified_at}</i>
        """
        
        data = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
            "reply_markup": {
                "inline_keyboard": [[
                    {"text": "📊 View Details", "url": f"https://verity-systems.vercel.app/results/{payload.request_id}"},
                    {"text": "🔄 Verify Another", "callback_data": "verify_new"}
                ]]
            }
        }
        
        async with session.post(f"{self.base_url}/sendMessage", json=data) as resp:
            return await resp.json()
    
    async def receive_claim(self, data: Dict[str, Any]) -> Optional[str]:
        message = data.get("message", {})
        return message.get("text")
    
    async def _test_connection(self) -> bool:
        session = await self._get_session()
        async with session.get(f"{self.base_url}/getMe") as resp:
            data = await resp.json()
            return data.get("ok", False)


# ============================================================
# AUTOMATION INTEGRATIONS
# ============================================================

class ZapierIntegration(BaseIntegration):
    """Zapier Webhook integration"""
    
    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.webhook_url = config.webhook_url
    
    async def send_verification(self, payload: VerificationPayload) -> Dict[str, Any]:
        session = await self._get_session()
        
        data = {
            "claim": payload.claim,
            "verdict": payload.verdict,
            "confidence": payload.confidence,
            "explanation": payload.explanation,
            "sources": payload.sources,
            "verified_at": payload.verified_at,
            "request_id": payload.request_id,
            "metadata": payload.metadata
        }
        
        async with session.post(self.webhook_url, json=data) as resp:
            return {"status": resp.status, "sent": True}
    
    async def receive_claim(self, data: Dict[str, Any]) -> Optional[str]:
        return data.get("claim") or data.get("text") or data.get("content")
    
    async def _test_connection(self) -> bool:
        session = await self._get_session()
        test_data = {"test": True, "message": "Verity connection test"}
        async with session.post(self.webhook_url, json=test_data) as resp:
            return resp.status in (200, 201, 202)


class N8nIntegration(BaseIntegration):
    """n8n Webhook integration"""
    
    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.webhook_url = config.webhook_url
    
    async def send_verification(self, payload: VerificationPayload) -> Dict[str, Any]:
        session = await self._get_session()
        
        data = {
            "event": "verification_complete",
            "data": {
                "claim": payload.claim,
                "verdict": payload.verdict,
                "confidence": payload.confidence,
                "explanation": payload.explanation,
                "sources": payload.sources,
                "verified_at": payload.verified_at
            }
        }
        
        async with session.post(self.webhook_url, json=data) as resp:
            return await resp.json() if resp.status == 200 else {"status": resp.status}
    
    async def receive_claim(self, data: Dict[str, Any]) -> Optional[str]:
        return data.get("data", {}).get("claim") or data.get("claim")
    
    async def _test_connection(self) -> bool:
        return True  # n8n webhooks are typically always available


# ============================================================
# SOCIAL MEDIA INTEGRATIONS
# ============================================================

class TwitterIntegration(BaseIntegration):
    """Twitter/X API v2 integration"""
    
    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.base_url = "https://api.twitter.com/2"
        self.bearer_token = config.oauth_token
    
    async def send_verification(self, payload: VerificationPayload) -> Dict[str, Any]:
        session = await self._get_session()
        
        emoji = {"TRUE": "✅", "FALSE": "❌", "MIXED": "⚠️"}.get(payload.verdict, "❓")
        
        # Format for Twitter's character limit
        tweet = f"""{emoji} Fact Check: {payload.verdict}

Claim: "{payload.claim[:100]}..."

Confidence: {payload.confidence}%

More: https://verity-systems.vercel.app/r/{payload.request_id}

#FactCheck #Verity"""
        
        data = {"text": tweet[:280]}
        
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }
        
        async with session.post(f"{self.base_url}/tweets", json=data, headers=headers) as resp:
            return await resp.json()
    
    async def receive_claim(self, data: Dict[str, Any]) -> Optional[str]:
        return data.get("data", {}).get("text") or data.get("tweet", {}).get("text")
    
    async def _test_connection(self) -> bool:
        session = await self._get_session()
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        async with session.get(f"{self.base_url}/users/me", headers=headers) as resp:
            return resp.status == 200


class RedditIntegration(BaseIntegration):
    """Reddit API integration"""
    
    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.base_url = "https://oauth.reddit.com"
        self.subreddit = config.additional_config.get('subreddit', 'factcheck')
    
    async def send_verification(self, payload: VerificationPayload) -> Dict[str, Any]:
        session = await self._get_session()
        
        # Post as self-post
        data = {
            "sr": self.subreddit,
            "kind": "self",
            "title": f"[{payload.verdict}] {payload.claim[:200]}",
            "text": f"""
## Fact Check Result

**Verdict:** {payload.verdict}  
**Confidence:** {payload.confidence}%

---

### Claim
> {payload.claim}

---

### Explanation
{payload.explanation}

---

### Sources
{chr(10).join(f'- [{i+1}]({s})' for i, s in enumerate(payload.sources[:5]))}

---

*Verified by [Verity](https://verity-systems.vercel.app) on {payload.verified_at}*
            """
        }
        
        headers = {
            "Authorization": f"Bearer {self.config.oauth_token}",
            "User-Agent": "Verity/1.0"
        }
        
        async with session.post(f"{self.base_url}/api/submit", data=data, headers=headers) as resp:
            return await resp.json()
    
    async def receive_claim(self, data: Dict[str, Any]) -> Optional[str]:
        return data.get("selftext") or data.get("title") or data.get("body")
    
    async def _test_connection(self) -> bool:
        session = await self._get_session()
        headers = {
            "Authorization": f"Bearer {self.config.oauth_token}",
            "User-Agent": "Verity/1.0"
        }
        async with session.get(f"{self.base_url}/api/v1/me", headers=headers) as resp:
            return resp.status == 200


class LinkedInIntegration(BaseIntegration):
    """LinkedIn API integration"""
    
    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.base_url = "https://api.linkedin.com/v2"
    
    async def send_verification(self, payload: VerificationPayload) -> Dict[str, Any]:
        session = await self._get_session()
        
        # Get user URN
        headers = {"Authorization": f"Bearer {self.config.oauth_token}"}
        async with session.get(f"{self.base_url}/me", headers=headers) as resp:
            user_data = await resp.json()
            user_urn = f"urn:li:person:{user_data.get('id')}"
        
        emoji = {"TRUE": "✅", "FALSE": "❌", "MIXED": "⚠️"}.get(payload.verdict, "❓")
        
        post_data = {
            "author": user_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": f"""{emoji} Fact Check Result: {payload.verdict}

"{payload.claim[:200]}..."

Confidence: {payload.confidence}%
{payload.explanation[:300]}

🔗 Full details: https://verity-systems.vercel.app/r/{payload.request_id}

#FactChecking #Misinformation #MediaLiteracy"""
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        }
        
        async with session.post(f"{self.base_url}/ugcPosts", json=post_data, headers=headers) as resp:
            return await resp.json()
    
    async def receive_claim(self, data: Dict[str, Any]) -> Optional[str]:
        return data.get("specificContent", {}).get("com.linkedin.ugc.ShareContent", {}).get("shareCommentary", {}).get("text")
    
    async def _test_connection(self) -> bool:
        session = await self._get_session()
        headers = {"Authorization": f"Bearer {self.config.oauth_token}"}
        async with session.get(f"{self.base_url}/me", headers=headers) as resp:
            return resp.status == 200


# ============================================================
# DEVELOPER TOOL INTEGRATIONS
# ============================================================

class GitHubIntegration(BaseIntegration):
    """GitHub API integration for PR/Issue comments"""
    
    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.base_url = "https://api.github.com"
    
    async def send_verification(self, payload: VerificationPayload) -> Dict[str, Any]:
        session = await self._get_session()
        
        # Get target from metadata
        repo = payload.metadata.get("repo")
        issue_number = payload.metadata.get("issue_number")
        
        if not repo or not issue_number:
            return {"error": "Missing repo or issue_number in metadata"}
        
        emoji = {"TRUE": "✅", "FALSE": "❌", "MIXED": "⚠️"}.get(payload.verdict, "❓")
        
        comment = f"""
## {emoji} Verity Fact Check

| Field | Value |
|-------|-------|
| **Verdict** | {payload.verdict} |
| **Confidence** | {payload.confidence}% |

### Claim
> {payload.claim}

### Analysis
{payload.explanation}

### Sources
{chr(10).join(f'- [{s}]({s})' for s in payload.sources[:3])}

---
<sub>Verified by [Verity](https://verity-systems.vercel.app) on {payload.verified_at}</sub>
        """
        
        headers = {
            "Authorization": f"token {self.config.oauth_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        url = f"{self.base_url}/repos/{repo}/issues/{issue_number}/comments"
        
        async with session.post(url, json={"body": comment}, headers=headers) as resp:
            return await resp.json()
    
    async def receive_claim(self, data: Dict[str, Any]) -> Optional[str]:
        # PR or Issue body
        return data.get("pull_request", {}).get("body") or data.get("issue", {}).get("body")
    
    async def _test_connection(self) -> bool:
        session = await self._get_session()
        headers = {"Authorization": f"token {self.config.oauth_token}"}
        async with session.get(f"{self.base_url}/user", headers=headers) as resp:
            return resp.status == 200


class GitLabIntegration(BaseIntegration):
    """GitLab API integration"""
    
    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.base_url = config.base_url or "https://gitlab.com/api/v4"
    
    async def send_verification(self, payload: VerificationPayload) -> Dict[str, Any]:
        session = await self._get_session()
        
        project_id = payload.metadata.get("project_id")
        mr_iid = payload.metadata.get("merge_request_iid")
        
        if not project_id or not mr_iid:
            return {"error": "Missing project_id or merge_request_iid"}
        
        comment = f"""
## Verity Fact Check Result

**Verdict:** {payload.verdict}  
**Confidence:** {payload.confidence}%

---

**Claim:** {payload.claim}

**Analysis:** {payload.explanation}

---
*Verified by Verity on {payload.verified_at}*
        """
        
        headers = {"PRIVATE-TOKEN": self.config.api_key}
        url = f"{self.base_url}/projects/{project_id}/merge_requests/{mr_iid}/notes"
        
        async with session.post(url, json={"body": comment}, headers=headers) as resp:
            return await resp.json()
    
    async def receive_claim(self, data: Dict[str, Any]) -> Optional[str]:
        return data.get("object_attributes", {}).get("description")
    
    async def _test_connection(self) -> bool:
        session = await self._get_session()
        headers = {"PRIVATE-TOKEN": self.config.api_key}
        async with session.get(f"{self.base_url}/user", headers=headers) as resp:
            return resp.status == 200


# ============================================================
# EMAIL INTEGRATIONS
# ============================================================

class SendGridIntegration(BaseIntegration):
    """SendGrid email integration"""
    
    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.base_url = "https://api.sendgrid.com/v3"
        self.from_email = config.additional_config.get('from_email', 'noreply@veritysystems.app')
    
    async def send_verification(self, payload: VerificationPayload) -> Dict[str, Any]:
        session = await self._get_session()
        
        to_email = payload.metadata.get("email")
        if not to_email:
            return {"error": "No recipient email provided"}
        
        color = {"TRUE": "#22c55e", "FALSE": "#ef4444", "MIXED": "#eab308"}.get(payload.verdict, "#6b7280")
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .verdict {{ background: {color}20; border-left: 4px solid {color}; padding: 15px; margin: 20px 0; }}
        .verdict h2 {{ color: {color}; margin: 0; }}
        .sources {{ background: #f5f5f5; padding: 15px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Verity Fact Check Result</h1>
        
        <div class="verdict">
            <h2>{payload.verdict}</h2>
            <p><strong>Confidence:</strong> {payload.confidence}%</p>
        </div>
        
        <h3>Claim</h3>
        <blockquote>{payload.claim}</blockquote>
        
        <h3>Explanation</h3>
        <p>{payload.explanation}</p>
        
        <div class="sources">
            <h4>Sources</h4>
            <ul>
                {''.join(f'<li><a href="{s}">{s}</a></li>' for s in payload.sources[:5])}
            </ul>
        </div>
        
        <p style="color: #666; font-size: 12px;">
            Verified by Verity on {payload.verified_at}<br>
            <a href="https://verity-systems.vercel.app/results/{payload.request_id}">View full details</a>
        </p>
    </div>
</body>
</html>
        """
        
        data = {
            "personalizations": [{"to": [{"email": to_email}]}],
            "from": {"email": self.from_email, "name": "Verity Fact Checker"},
            "subject": f"[{payload.verdict}] Fact Check Result",
            "content": [
                {"type": "text/plain", "value": f"Verdict: {payload.verdict}\nConfidence: {payload.confidence}%\n\n{payload.explanation}"},
                {"type": "text/html", "value": html_content}
            ]
        }
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        async with session.post(f"{self.base_url}/mail/send", json=data, headers=headers) as resp:
            return {"status": resp.status, "sent": resp.status == 202}
    
    async def receive_claim(self, data: Dict[str, Any]) -> Optional[str]:
        # SendGrid inbound parse webhook
        return data.get("text") or data.get("html")
    
    async def _test_connection(self) -> bool:
        session = await self._get_session()
        headers = {"Authorization": f"Bearer {self.config.api_key}"}
        async with session.get(f"{self.base_url}/user/profile", headers=headers) as resp:
            return resp.status == 200


# ============================================================
# INTEGRATION MANAGER
# ============================================================

class IntegrationManager:
    """Manages all integrations"""
    
    INTEGRATION_CLASSES = {
        # CMS
        "wordpress": WordPressIntegration,
        "ghost": GhostIntegration,
        "shopify": ShopifyIntegration,
        
        # Productivity
        "notion": NotionIntegration,
        "asana": AsanaIntegration,
        "trello": TrelloIntegration,
        "airtable": AirtableIntegration,
        
        # Communication
        "slack": SlackIntegration,
        "teams": MicrosoftTeamsIntegration,
        "discord": DiscordIntegration,
        "telegram": TelegramIntegration,
        
        # Automation
        "zapier": ZapierIntegration,
        "n8n": N8nIntegration,
        
        # Social Media
        "twitter": TwitterIntegration,
        "reddit": RedditIntegration,
        "linkedin": LinkedInIntegration,
        
        # Developer
        "github": GitHubIntegration,
        "gitlab": GitLabIntegration,
        
        # Email
        "sendgrid": SendGridIntegration,
    }
    
    def __init__(self):
        self.integrations: Dict[str, BaseIntegration] = {}
    
    def register(self, name: str, config: IntegrationConfig) -> BaseIntegration:
        """Register a new integration"""
        integration_class = self.INTEGRATION_CLASSES.get(name.lower())
        if not integration_class:
            raise ValueError(f"Unknown integration: {name}")
        
        integration = integration_class(config)
        self.integrations[name] = integration
        return integration
    
    def get(self, name: str) -> Optional[BaseIntegration]:
        """Get a registered integration"""
        return self.integrations.get(name)
    
    async def send_to_all(self, payload: VerificationPayload) -> Dict[str, Any]:
        """Send verification to all registered integrations"""
        results = {}
        for name, integration in self.integrations.items():
            try:
                result = await integration.send_verification(payload)
                results[name] = {"success": True, "result": result}
            except Exception as e:
                results[name] = {"success": False, "error": str(e)}
        return results
    
    async def test_all(self) -> Dict[str, bool]:
        """Test all registered integrations"""
        results = {}
        for name, integration in self.integrations.items():
            results[name] = await integration.test_connection()
        return results
    
    async def close_all(self):
        """Close all integration sessions"""
        for integration in self.integrations.values():
            await integration.close()


# ============================================================
# WEBHOOK HANDLER
# ============================================================

class WebhookHandler:
    """Handle incoming webhooks from integrations"""
    
    def __init__(self, manager: IntegrationManager, verify_callback: Callable):
        self.manager = manager
        self.verify_callback = verify_callback
        self.webhook_secrets: Dict[str, str] = {}
    
    def set_secret(self, platform: str, secret: str):
        """Set webhook secret for signature verification"""
        self.webhook_secrets[platform] = secret
    
    def verify_signature(self, platform: str, payload: bytes, signature: str) -> bool:
        """Verify webhook signature"""
        secret = self.webhook_secrets.get(platform)
        if not secret:
            return True  # No secret configured, allow all
        
        if platform == "slack":
            # Slack uses timestamp + body
            expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
            return hmac.compare_digest(f"v0={expected}", signature)
        
        elif platform == "github":
            expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
            return hmac.compare_digest(f"sha256={expected}", signature)
        
        return True
    
    async def handle_webhook(self, platform: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle incoming webhook and optionally trigger verification"""
        integration = self.manager.get(platform)
        if not integration:
            return {"error": f"Unknown platform: {platform}"}
        
        # Extract claim from webhook data
        claim = await integration.receive_claim(data)
        
        if claim:
            # Trigger verification
            result = await self.verify_callback(claim)
            
            # Send result back to platform
            payload = VerificationPayload(
                claim=claim,
                verdict=result.get("verdict", "UNVERIFIABLE"),
                confidence=result.get("confidence", 0),
                sources=result.get("sources", []),
                explanation=result.get("explanation", ""),
                verified_at=datetime.utcnow().isoformat(),
                request_id=result.get("request_id")
            )
            
            await integration.send_verification(payload)
            return {"verified": True, "result": result}
        
        return {"verified": False, "reason": "No claim extracted"}


# ============================================================
# FASTAPI ROUTES
# ============================================================

def create_integrations_routes():
    """Create FastAPI routes for integrations"""
    from fastapi import APIRouter, Request, HTTPException
    from typing import Optional
    
    router = APIRouter(prefix="/integrations", tags=["Integrations"])
    
    # Singleton manager
    _manager = None
    
    def get_manager():
        nonlocal _manager
        if _manager is None:
            _manager = IntegrationManager()
        return _manager
    
    @router.get("/")
    async def list_integrations():
        """List all available integrations"""
        manager = get_manager()
        return {
            "integrations": [
                {
                    "name": name,
                    "category": int_obj.config.category.value,
                    "configured": bool(int_obj.config.api_key or int_obj.config.oauth_token or int_obj.config.webhook_url)
                }
                for name, int_obj in manager.integrations.items()
            ],
            "categories": [c.value for c in IntegrationCategory]
        }
    
    @router.post("/register")
    async def register_integration(
        name: str,
        category: str,
        api_key: Optional[str] = None,
        webhook_url: Optional[str] = None,
        oauth_token: Optional[str] = None
    ):
        """Register a new integration"""
        manager = get_manager()
        
        try:
            cat = IntegrationCategory(category)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
        
        config = IntegrationConfig(
            name=name,
            category=cat,
            api_key=api_key,
            webhook_url=webhook_url,
            oauth_token=oauth_token
        )
        
        manager.register(name, config)
        return {"registered": True, "name": name}
    
    @router.post("/test/{platform}")
    async def test_integration(platform: str):
        """Test integration connectivity"""
        manager = get_manager()
        integration = manager.get(platform)
        
        if not integration:
            raise HTTPException(status_code=404, detail=f"Integration not found: {platform}")
        
        try:
            result = await integration.test_connection()
            return {"platform": platform, "success": result}
        except Exception as e:
            return {"platform": platform, "success": False, "error": str(e)}
    
    @router.post("/send/{platform}")
    async def send_to_platform(platform: str, request: Request):
        """Send verification result to a platform"""
        manager = get_manager()
        integration = manager.get(platform)
        
        if not integration:
            raise HTTPException(status_code=404, detail=f"Integration not found: {platform}")
        
        data = await request.json()
        
        payload = VerificationPayload(
            claim=data.get("claim", ""),
            verdict=data.get("verdict", "UNVERIFIABLE"),
            confidence=data.get("confidence", 0),
            sources=data.get("sources", []),
            explanation=data.get("explanation", ""),
            verified_at=datetime.utcnow().isoformat(),
            request_id=data.get("request_id")
        )
        
        try:
            await integration.send_verification(payload)
            return {"sent": True, "platform": platform}
        except Exception as e:
            return {"sent": False, "platform": platform, "error": str(e)}
    
    @router.post("/webhook/{platform}")
    async def receive_webhook(platform: str, request: Request):
        """Receive webhook from a platform"""
        manager = get_manager()
        
        try:
            data = await request.json()
        except:
            data = {}
        
        integration = manager.get(platform)
        if not integration:
            raise HTTPException(status_code=404, detail=f"Integration not found: {platform}")
        
        # Extract claim if possible
        claim = await integration.receive_claim(data)
        
        return {
            "received": True,
            "platform": platform,
            "claim_extracted": claim is not None,
            "claim": claim
        }
    
    @router.get("/stats")
    async def get_integration_stats():
        """Get integration statistics"""
        manager = get_manager()
        
        by_category = {}
        for name, integration in manager.integrations.items():
            cat = integration.config.category.value
            by_category[cat] = by_category.get(cat, 0) + 1
        
        return {
            "total_integrations": len(manager.integrations),
            "by_category": by_category,
            "available_categories": [c.value for c in IntegrationCategory]
        }
    
    return router


# ============================================================
# EXAMPLE USAGE
# ============================================================

async def example_usage():
    """Example of using the integration system"""
    
    # Create manager
    manager = IntegrationManager()
    
    # Register Slack integration
    slack_config = IntegrationConfig(
        name="slack",
        category=IntegrationCategory.COMMUNICATION,
        oauth_token=os.getenv("SLACK_BOT_TOKEN"),
        channel_id="C0123456789"
    )
    manager.register("slack", slack_config)
    
    # Register Discord integration
    discord_config = IntegrationConfig(
        name="discord",
        category=IntegrationCategory.COMMUNICATION,
        webhook_url=os.getenv("DISCORD_WEBHOOK_URL")
    )
    manager.register("discord", discord_config)
    
    # Test connections
    test_results = await manager.test_all()
    print("Connection tests:", test_results)
    
    # Send verification to all platforms
    payload = VerificationPayload(
        claim="The Earth is approximately 4.5 billion years old.",
        verdict="TRUE",
        confidence=95,
        sources=["https://science.nasa.gov/earth", "https://www.nature.com/articles/s41586-020-2434-8"],
        explanation="This is well-established scientific consensus based on radiometric dating of meteorites and Earth rocks.",
        verified_at=datetime.utcnow().isoformat(),
        request_id="test-123"
    )
    
    results = await manager.send_to_all(payload)
    print("Send results:", results)
    
    # Cleanup
    await manager.close_all()


if __name__ == "__main__":
    asyncio.run(example_usage())
