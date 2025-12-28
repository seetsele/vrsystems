"""Quick test for the 6 problematic APIs"""
import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    print("=" * 60)
    print("Testing the 6 problematic APIs")
    print("=" * 60)
    
    # 1. Google Gemini - with correct model names
    print("\n1. Google Gemini...")
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    if api_key:
        async with httpx.AsyncClient(timeout=30) as client:
            for model in ['gemini-2.0-flash', 'gemini-2.5-flash']:
                response = await client.post(
                    f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}',
                    json={'contents': [{'parts': [{'text': 'Say OK'}]}]}
                )
                if response.status_code == 200:
                    print(f"   ✓ Google Gemini: OK with {model}")
                    break
            else:
                print(f"   ✗ Google Gemini: FAILED - {response.status_code}")
    
    # 2. Brave Search
    print("\n2. Brave Search...")
    api_key = os.getenv('BRAVE_API_KEY')
    if api_key:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                'https://api.search.brave.com/res/v1/web/search',
                headers={'X-Subscription-Token': api_key, 'Accept': 'application/json'},
                params={'q': 'test query', 'count': 1}
            )
            if response.status_code == 200:
                data = response.json()
                results = data.get('web', {}).get('results', [])
                print(f"   ✓ Brave Search: OK ({len(results)} results)")
            else:
                print(f"   ✗ Brave Search: FAILED - {response.status_code}")
    
    # 3. Anthropic Claude
    print("\n3. Anthropic Claude...")
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if api_key:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                'https://api.anthropic.com/v1/messages',
                headers={
                    'x-api-key': api_key,
                    'anthropic-version': '2023-06-01',
                    'content-type': 'application/json'
                },
                json={
                    'model': 'claude-3-haiku-20240307',
                    'max_tokens': 50,
                    'messages': [{'role': 'user', 'content': 'Say OK'}]
                }
            )
            if response.status_code == 200:
                print(f"   ✓ Anthropic Claude: OK")
            elif response.status_code == 401:
                print(f"   ✗ Anthropic Claude: Invalid API key (key may be revoked/expired)")
            else:
                print(f"   ✗ Anthropic Claude: {response.status_code}")
    
    # 4. OpenAI
    print("\n4. OpenAI...")
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                'https://api.openai.com/v1/chat/completions',
                headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
                json={'model': 'gpt-3.5-turbo', 'max_tokens': 10, 'messages': [{'role': 'user', 'content': 'Hi'}]}
            )
            if response.status_code == 200:
                print(f"   ✓ OpenAI: OK")
            elif response.status_code == 429:
                print(f"   ✗ OpenAI: Rate limited / Quota exceeded (add billing credits)")
            else:
                print(f"   ✗ OpenAI: {response.status_code}")
    
    # 5. DeepSeek
    print("\n5. DeepSeek...")
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if api_key:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                'https://api.deepseek.com/v1/chat/completions',
                headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
                json={'model': 'deepseek-chat', 'max_tokens': 10, 'messages': [{'role': 'user', 'content': 'Hi'}]}
            )
            if response.status_code == 200:
                print(f"   ✓ DeepSeek: OK")
            elif response.status_code == 402:
                print(f"   ✗ DeepSeek: Insufficient balance (add credits)")
            else:
                print(f"   ✗ DeepSeek: {response.status_code}")
    
    # 6. You.com
    print("\n6. You.com...")
    api_key = os.getenv('YOU_API_KEY')
    if api_key:
        async with httpx.AsyncClient(timeout=30) as client:
            # Try different endpoints
            for endpoint in ['/news', '/search', '/rag']:
                response = await client.get(
                    f'https://api.ydc-index.io{endpoint}',
                    headers={'X-API-Key': api_key},
                    params={'query': 'test'}
                )
                if response.status_code == 200:
                    print(f"   ✓ You.com: OK ({endpoint})")
                    break
            else:
                print(f"   ✗ You.com: {response.status_code} - API key may not have access")
    
    print("\n" + "=" * 60)
    print("Summary: APIs requiring action:")
    print("  - Anthropic: Regenerate API key at console.anthropic.com")
    print("  - OpenAI: Add billing credits at platform.openai.com")
    print("  - DeepSeek: Add credits at platform.deepseek.com")
    print("  - You.com: Check API permissions at api.you.com")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
