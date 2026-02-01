import os
import re

try:
    import cohere
except Exception:
    cohere = None


class CohereProvider:
    """Cohere SDK wrapper that supports multiple SDK variants.

    Attempts several call patterns to be compatible with different Cohere
    client versions. Accepts `sources` via **kwargs and appends them to the
    prompt when available.
    """

    def __init__(self):
        if cohere is None:
            self.client = None
            return

        api_key = os.getenv("COHERE_API_KEY")
        try:
            self.client = cohere.Client(api_key) if api_key else cohere.Client()
        except Exception:
            self.client = cohere

    def verify_claim(self, claim: str, **kwargs) -> dict:
        provider_name = "cohere_command_r"
        if self.client is None:
            return {
                "provider": provider_name,
                "verdict": "UNVERIFIABLE",
                "confidence": 0,
                "reasoning": "Cohere client not available",
                "raw_response": None,
                "cost": 0.0,
                "sources": kwargs.get("sources", []),
            }

        sources = kwargs.get("sources", []) or []
        prompt = f"VERDICT:\nCONFIDENCE:\nREASONING:\n\nFact-check: {claim}"
        if sources:
            prompt += "\n\nSources:\n" + "\n".join(f"- {s}" for s in sources)

        raw = None
        text = None

        try:
            # Prefer Chat-style APIs first (SDK or HTTP), then fall back to legacy generate/create
            chat = getattr(self.client, "chat", None)
            if callable(chat):
                try:
                    raw = chat(model="command-r", messages=[{"role": "user", "content": prompt}])
                except TypeError:
                    # Try alternative kw/arg names
                    for argname in ("input", "inputs", "prompt", "text", None):
                        try:
                            if argname:
                                raw = chat(model="command-r", **{argname: prompt})
                            else:
                                raw = chat(prompt)
                            break
                        except TypeError:
                            continue

            # If SDK chat did not work, try HTTP Chat API as the authoritative path
            if raw is None:
                api_key = os.getenv("COHERE_API_KEY")
                if api_key:
                    try:
                        import requests

                        url = "https://api.cohere.com/v1/chat"
                        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                        # Try a few reasonable chat-model names that Cohere uses
                        candidate_models = ["command-r", "command", "command-xlarge", "xlarge"]
                        last_exc = None
                        for m in candidate_models:
                            try:
                                payload = {"model": m, "messages": [{"role": "user", "content": prompt}]}
                                resp = requests.post(url, json=payload, headers=headers, timeout=15)
                                if resp.ok:
                                    raw = resp.json()
                                    break
                                else:
                                    # keep trying other model names if server responds 4xx/5xx
                                    last_exc = RuntimeError(f"Cohere HTTP fallback failed for model={m}: {resp.status_code} {resp.text}")
                                    continue
                            except Exception as rexc:
                                last_exc = rexc
                                continue
                        if raw is None and last_exc:
                            raise last_exc
                    except Exception as http_e:
                        # Record HTTP fallback failure but allow next legacy attempts
                        http_fallback_error = http_e

            # If still no response, try legacy SDK generate/create functions
            if raw is None:
                for candidate in ("generate", "create", "chat_generate", "chat_completion"):
                    fn = getattr(self.client, candidate, None)
                    if not callable(fn):
                        continue
                    try:
                        raw = fn(model="command-r", prompt=prompt)
                        break
                    except TypeError:
                        try:
                            raw = fn(prompt)
                            break
                        except Exception:
                            continue

            if raw is None:
                # If we reached here without raw and no HTTP fallback succeeded, raise
                if 'http_fallback_error' in locals():
                    raise RuntimeError(f"Cohere HTTP fallback error: {http_fallback_error}")
                else:
                    raise RuntimeError("Unable to invoke Cohere SDK in detected environment")

            if isinstance(raw, dict):
                text = raw.get("output") or raw.get("text") or raw.get("response") or str(raw)
            else:
                text = getattr(raw, "text", None) or getattr(raw, "output", None)
                if text is None:
                    gens = getattr(raw, "generations", None) or getattr(raw, "choices", None) or getattr(raw, "responses", None)
                    if gens:
                        first = gens[0]
                        text = getattr(first, "text", None) or (first.get("text") if isinstance(first, dict) else None)
                        if not text:
                            msg = getattr(first, "message", None) or (first.get("message") if isinstance(first, dict) else None)
                            if msg and hasattr(msg, "content"):
                                text = msg.content
                            elif isinstance(msg, str):
                                text = msg
                    else:
                        text = str(raw)

        except Exception as e:
            return {
                "provider": provider_name,
                "verdict": "UNVERIFIABLE",
                "confidence": 0,
                "reasoning": str(e),
                "raw_response": None,
                "cost": 0.0,
                "sources": sources,
            }

        if not text:
            text = str(raw)

        verdict = self._extract_verdict(text)
        confidence = self._extract_confidence(text)

        return {
            "provider": provider_name,
            "verdict": verdict,
            "confidence": confidence,
            "reasoning": text,
            "raw_response": str(raw),
            "cost": 0.0,
            "sources": sources,
        }

    def _extract_verdict(self, text: str) -> str:
        m = re.search(r"VERDICT:\s*(TRUE|FALSE|MISLEADING|UNVERIFIABLE)", text, re.IGNORECASE)
        return m.group(1).upper() if m else "UNVERIFIABLE"

    def _extract_confidence(self, text: str) -> int:
        m = re.search(r"CONFIDENCE:\s*(\d+)", text)
        try:
            return int(m.group(1)) if m else 50
        except Exception:
            return 50
