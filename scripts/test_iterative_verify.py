import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Ensure repo python-tools path is importable
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'python-tools'))

import api_server_v10 as api

async def main():
    claim = "Vaccines cause autism"

    async with api.AIProviders() as providers:
        # Force mock providers regardless of env config
        providers.available_providers = ['perplexity', 'openai']

        async def verify_with_perplexity(claim, context=''):
            await asyncio.sleep(0.1)
            return {
                'success': True,
                'provider': 'perplexity',
                'response': 'VERDICT: false\nCONFIDENCE: 0.95\nEXPLANATION: Large epidemiological studies find no causal link.',
                'explanation': 'Large epidemiological studies find no causal link.'
            }

        async def verify_with_openai(claim, context=''):
            await asyncio.sleep(0.2)
            return {
                'success': True,
                'provider': 'openai',
                'response': 'VERDICT: false\nCONFIDENCE: 0.92\nEXPLANATION: Multiple systematic reviews show no link.',
                'explanation': 'Multiple systematic reviews show no link.'
            }

        # Attach mocks to instance
        providers.verify_with_perplexity = verify_with_perplexity
        providers.verify_with_openai = verify_with_openai

        # Run verification
        result = await providers.verify_claim(claim, tier='free')

        # Build detailed report
        report = {
            'generated_at': datetime.utcnow().isoformat() + 'Z',
            'claim': claim,
            'result': result
        }

        out_txt = json.dumps(report, indent=2)
        out_path = 'COMPREHENSIVE_VERIFICATION_OUTPUT.txt'
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(out_txt)

        print(f"Saved verification output to {out_path}")
        print(out_txt)

if __name__ == '__main__':
    asyncio.run(main())
