import os
import re
import asyncio

genai = None
try:
    # Prefer the newer google.genai package
    import google.genai as genai
except Exception:
    try:
        import google.generativeai as genai
    except Exception:
        genai = None


class GoogleProvider:
    def __init__(self):
        self.enabled = os.getenv('ENABLE_GOOGLE', '1') not in ('0', 'false', 'False')
        if self.enabled and genai is not None:
            try:
                # new package uses client.configure, older may use configure
                if hasattr(genai, 'configure'):
                    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
                elif hasattr(genai, 'Client'):
                    # instantiate a long-lived client to reuse across calls
                    try:
                        self.client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
                    except Exception:
                        # fall back to None if client construction fails
                        self.client = None
                else:
                    self.client = None
            except Exception:
                self.client = None
        else:
            self.client = None

    def __del__(self):
        try:
            self._safe_close(getattr(self, 'client', None))
        except Exception:
            pass

    def _safe_close(self, client):
        """Attempt to close google genai client safely without raising.

        Some google client implementations raise AttributeError when closing
        if internal async attributes are missing. Ensure necessary attrs
        exist and call close methods guarded by try/except.
        """
        if client is None:
            return
        try:
            # Ensure the attribute exists to avoid AttributeError during close
            if not hasattr(client, '_async_httpx_client'):
                try:
                    setattr(client, '_async_httpx_client', None)
                except Exception:
                    pass

            if hasattr(client, 'close'):
                try:
                    client.close()
                except Exception:
                    pass

            # If an async close exists, run it only if there's no running loop
            if hasattr(client, 'close_async'):
                try:
                    loop = None
                    try:
                        loop = asyncio.get_event_loop()
                    except Exception:
                        loop = None
                    if loop is None or not loop.is_running():
                        try:
                            asyncio.run(client.close_async())
                        except Exception:
                            pass
                except Exception:
                    pass
        except Exception:
            pass

    def verify_claim(self, claim: str, model: str = "gemini-2.0-flash-exp", **kwargs) -> dict:
        if not self.enabled or genai is None:
            return {
                "provider": "google",
                "verdict": "UNVERIFIABLE",
                "confidence": 0,
                "reasoning": "Google generative API not available or disabled",
            }

        sources = kwargs.get("sources") or []
        prompt = f"VERDICT:\nCONFIDENCE:\nREASONING:\n\nFact-check: {claim}"
        if sources:
            prompt += "\n\nSources:\n" + "\n".join(f"- {s}" for s in sources)

        created_local = False
        client = None
        try:
            # Try new genai API shape. Prefer reusing self.client if available
            client = getattr(self, 'client', None)
            if client is None and hasattr(genai, 'Client') and getattr(genai, 'Client') is not None:
                try:
                    client = getattr(genai, 'Client')()
                    created_local = True
                except Exception:
                    client = None

            # prefer synchronous generate if available on the client
            if client is not None:
                if hasattr(client, 'generate'):
                    resp = client.generate(model=model, prompt=prompt)
                    text = getattr(resp, 'output', None) or str(resp)
                elif hasattr(genai, 'generate'):
                    resp = genai.generate(model=model, prompt=prompt)
                    text = getattr(resp, 'output', None) or str(resp)
                else:
                    text = 'No compatible google.genai generate method available.'
            else:
                # older google.generativeai fallback
                model_instance = getattr(genai, 'GenerativeModel', None)
                if model_instance is not None:
                    inst = model_instance(model)
                    response = inst.generate_content(prompt)
                    text = getattr(response, 'text', None) or str(response)
                else:
                    text = 'No compatible Google GenAI client available.'

        except Exception as e:
            # Try REST fallback if API key present
            api_key = os.getenv('GOOGLE_AI_API_KEY') or os.getenv('GOOGLE_API_KEY')
            if api_key:
                try:
                    import requests
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                    payload = {"prompt": {"text": prompt}, "generationConfig": {"temperature": 0.1, "maxOutputTokens": 600}}
                    resp = requests.post(url, json=payload, timeout=15)
                    if resp.ok:
                        data = resp.json()
                        # try to extract text from known fields
                        text = ''
                        if 'candidates' in data:
                            text = '\n'.join([c.get('output') or c.get('content', '') for c in data.get('candidates', [])])
                        else:
                            # older shape
                            text = str(data)
                    else:
                        return {
                            "provider": "google",
                            "verdict": "UNVERIFIABLE",
                            "confidence": 0,
                            "reasoning": f"Google REST fallback failed: {resp.status_code} {resp.text}",
                        }
                except Exception as re:
                    return {
                        "provider": "google",
                        "verdict": "UNVERIFIABLE",
                        "confidence": 0,
                        "reasoning": f"Google client error and REST fallback error: {re}",
                    }
            else:
                return {
                    "provider": "google",
                    "verdict": "UNVERIFIABLE",
                    "confidence": 0,
                    "reasoning": str(e),
                }

        finally:
            try:
                if created_local:
                    self._safe_close(client)
            except Exception:
                pass

        return {
            "provider": f"google_{model.replace('-', '_')}",
            "verdict": self._extract_verdict(text),
            "confidence": self._extract_confidence(text),
            "reasoning": text[:300],
            "raw_response": str(text),
            "cost": 0.0,
        }

    def _extract_verdict(self, text: str) -> str:
        m = re.search(r"VERDICT:\s*(TRUE|FALSE|MISLEADING|UNVERIFIABLE)", text, re.IGNORECASE)
        return m.group(1).upper() if m else "UNVERIFIABLE"

    def _extract_confidence(self, text: str) -> int:
        m = re.search(r"CONFIDENCE:\s*(\d{1,3})", text)
        try:
            return int(m.group(1)) if m else 50
        except Exception:
            return 50
