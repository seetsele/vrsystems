import os
import logging
import aiohttp

logger = logging.getLogger('SlackNotifier')

async def send_slack_message(webhook_url: str, text: str) -> bool:
    try:
        async with aiohttp.ClientSession() as session:
            payload = {'text': text}
            async with session.post(webhook_url, json=payload, timeout=10) as resp:
                if resp.status in (200, 201):
                    return True
                else:
                    logger.warning('Slack webhook returned %s', resp.status)
                    return False
    except Exception:
        logger.exception('Failed to send Slack message')
        return False
