import os
import re

try:
    import together
except Exception:
    together = None


class TogetherProvider:
    def __init__(self):
        # Respect enable flag
        self.enabled = os.getenv('ENABLE_TOGETHER', '1') not in ('0', 'false', 'False')
        self.client = None
        if not self.enabled:
            return
        if together is not None:
            try:
                api_key = os.getenv('TOGETHER_API_KEY')
                if hasattr(together, 'Client'):
                    try:
                        self.client = together.Client(api_key) if api_key else together.Client()
                    except Exception:
                        self.client = together
                else:
                    self.client = together
            except Exception:
                self.client = together

    def verify_claim(self, claim: str, **kwargs) -> dict:
        provider_name = "together_llama3_70b"
        if self.client is None:
            return {"provider": provider_name, "verdict": "UNVERIFIABLE", "confidence": 0, "reasoning": "Together API not available or disabled"}

        text = None
        raw = None
        try:
            Complete = getattr(self.client, 'Complete', None)
            if Complete is not None:
                create = getattr(Complete, 'create', None)
                run = getattr(Complete, 'run', None)
                if callable(create):
                    sources = kwargs.get("sources") or []
                    prompt = f"Fact-check: {claim}"
                    if sources:
                        prompt += "\n\nSources:\n" + "\n".join(f"- {s}" for s in sources)
                    raw = create(model="meta-llama/Llama-3-70b-chat-hf", prompt=prompt, max_tokens=512)
                elif callable(run):
                    sources = kwargs.get("sources") or []
                    prompt = f"Fact-check: {claim}"
                    if sources:
                        prompt += "\n\nSources:\n" + "\n".join(f"- {s}" for s in sources)
                    raw = run(model="meta-llama/Llama-3-70b-chat-hf", prompt=prompt, max_tokens=512)

            if raw is None:
                for fn_name in ('complete', 'run', 'create', 'complete_sync'):
                    fn = getattr(self.client, fn_name, None)
                    if callable(fn):
                        try:
                            sources = kwargs.get("sources") or []
                            prompt = f"Fact-check: {claim}"
                            if sources:
                                prompt += "\n\nSources:\n" + "\n".join(f"- {s}" for s in sources)
                            raw = fn(model="meta-llama/Llama-3-70b-chat-hf", prompt=prompt, max_tokens=512)
                            break
                        except Exception:
                            continue

            if raw is None:
                raise RuntimeError("Unable to call Together SDK in detected environment")

            if isinstance(raw, dict):
                if 'output' in raw:
                    out = raw.get('output') or {}
                    choices = out.get('choices') or out.get('outputs') or []
                    if choices:
                        text = choices[0].get('text') or choices[0].get('output') or str(choices[0])
                    else:
                        text = str(out)
                elif 'choices' in raw and raw['choices']:
                    text = raw['choices'][0].get('text')
                else:
                    text = str(raw)
            else:
                text = getattr(raw, 'text', None) or getattr(raw, 'output', None) or None
                if text is None:
                    try:
                        choices = getattr(raw, 'choices', None)
                        if choices and len(choices) > 0:
                            first = choices[0]
                            text = getattr(first, 'text', None) or getattr(first, 'output', None) or str(first)
                    except Exception:
                        text = str(raw)

        except Exception as e:
            return {"provider": provider_name, "verdict": "UNVERIFIABLE", "confidence": 0, "reasoning": str(e)}

        if not text:
            text = str(raw)

        verdict = self._extract_verdict(text)
        confidence = 50

        return {"provider": provider_name, "verdict": verdict, "confidence": confidence, "reasoning": text, "raw_response": str(raw), "cost": 0.0}

    def _extract_verdict(self, text: str) -> str:
        m = re.search(r'VERDICT:\s*(TRUE|FALSE|MISLEADING|UNVERIFIABLE)', text, re.IGNORECASE)
        return m.group(1).upper() if m else 'UNVERIFIABLE'
import os
import re

try:
    import together
except Exception:
    together = None


class TogetherProvider:
    def __init__(self):
        # Some together SDKs expect setting an env var or attribute
        self.client = None
        if together is not None:
            try:
                api_key = os.getenv('TOGETHER_API_KEY')
                # newer variants may expose Client or direct methods
                if hasattr(together, 'Client'):
                    try:
                        self.client = together.Client(api_key) if api_key else together.Client()
                    except Exception:
                        self.client = together
                else:
                    self.client = together
            except Exception:
                self.client = together

    def verify_claim(self, claim: str, **kwargs) -> dict:
        provider_name = "together_llama3_70b"
        if self.client is None:
            return {"provider": provider_name, "verdict": "UNVERIFIABLE", "confidence": 0, "reasoning": "Together API not available"}

        text = None
        raw = None
        try:
            # Try common call shapes: together.Complete.create or together.Complete.run or client.complete
            Complete = getattr(self.client, 'Complete', None)
            if Complete is not None:
                # Prefer create/run methods
                create = getattr(Complete, 'create', None)
                run = getattr(Complete, 'run', None)
                if callable(create):
                    raw = create(model="meta-llama/Llama-3-70b-chat-hf", prompt=f"Fact-check: {claim}", max_tokens=512)
                elif callable(run):
                    raw = run(model="meta-llama/Llama-3-70b-chat-hf", prompt=f"Fact-check: {claim}", max_tokens=512)

            # Some SDKs expose a top-level complete/complete_sync function
            if raw is None:
                for fn_name in ('complete', 'run', 'create', 'complete_sync'):
                    fn = getattr(self.client, fn_name, None)
                    if callable(fn):
                        try:
                            raw = fn(model="meta-llama/Llama-3-70b-chat-hf", prompt=f"Fact-check: {claim}", max_tokens=512)
                            break
                        except Exception:
                            continue

            if raw is None:
                raise RuntimeError("Unable to call Together SDK in detected environment")

            # Normalize raw to text
            if isinstance(raw, dict):
                # e.g., {'output': {'choices': [{'text': '...'}]}}
                if 'output' in raw:
                    out = raw.get('output') or {}
                    choices = out.get('choices') or out.get('outputs') or []
                    if choices:
                        text = choices[0].get('text') or choices[0].get('output') or str(choices[0])
                    else:
                        text = str(out)
                elif 'choices' in raw and raw['choices']:
                    text = raw['choices'][0].get('text')
                else:
                    text = str(raw)
            else:
                text = getattr(raw, 'text', None) or getattr(raw, 'output', None) or None
                if text is None:
                    try:
                        choices = getattr(raw, 'choices', None)
                        if choices and len(choices) > 0:
                            first = choices[0]
                            text = getattr(first, 'text', None) or getattr(first, 'output', None) or str(first)
                    except Exception:
                        text = str(raw)

        except Exception as e:
            return {"provider": provider_name, "verdict": "UNVERIFIABLE", "confidence": 0, "reasoning": str(e)}

        if not text:
            text = str(raw)

        verdict = self._extract_verdict(text)
        # default confidence if not provided in text
        confidence = 50

        return {"provider": provider_name, "verdict": verdict, "confidence": confidence, "reasoning": text, "raw_response": str(raw), "cost": 0.0}

    def _extract_verdict(self, text: str) -> str:
        m = re.search(r'VERDICT:\s*(TRUE|FALSE|MISLEADING|UNVERIFIABLE)', text, re.IGNORECASE)
        return m.group(1).upper() if m else 'UNVERIFIABLE'
