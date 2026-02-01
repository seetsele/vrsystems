import requests


class OllamaProvider:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip("/")

    def verify_claim(self, claim: str, model: str = "llama3.3:70b", **kwargs) -> dict:
        """Verify claim using Ollama model.

        This will try several common Ollama HTTP endpoints and response shapes,
        falling back gracefully if the local Ollama server uses a different path.
        """
        sources = kwargs.get("sources") or []
        prompt = (
            f"""Verify this claim and respond in EXACT format:
VERDICT: [TRUE/FALSE/MISLEADING/UNVERIFIABLE]
CONFIDENCE: [0-100]
REASONING: [Detailed explanation]

CLAIM: {claim}"""
        )
        if sources:
            prompt += "\n\nSources:\n" + "\n".join(f"- {s}" for s in sources)

        endpoints = ["/api/chat", "/api/generate", "/v1/generate", "/api/v1/chat"]
        last_exc = None
        result_text = None

        payload_variants = [
            {"model": model, "prompt": prompt, "stream": False},
            {"model": model, "messages": [{"role": "user", "content": prompt}]},
            {"model": model, "input": prompt},
        ]

        for ep in endpoints:
            url = f"{self.base_url}{ep}"
            for payload in payload_variants:
                try:
                    resp = requests.post(url, json=payload, timeout=15)
                    if resp.status_code >= 400:
                        # try next shape/endpoint
                        last_exc = Exception(f"{resp.status_code} {resp.text}")
                        continue
                    data = resp.json()
                    # common shapes: {'response': '...'}, {'content': '...'}, {'choices':[{'text':...}]}, {'output':[{'content':...}]}
                    if isinstance(data, dict):
                        if "response" in data:
                            result_text = data.get("response")
                        elif "content" in data:
                            result_text = data.get("content")
                        elif "choices" in data and isinstance(data.get("choices"), list):
                            c = data.get("choices")[0]
                            result_text = c.get("text") or c.get("message") or c.get("content")
                        elif "output" in data and isinstance(data.get("output"), list):
                            out = data.get("output")[0]
                            result_text = out.get("content") or out.get("text")
                        else:
                            # try to stringify
                            result_text = str(data)
                    else:
                        result_text = str(data)

                    if result_text is not None:
                        break
                except Exception as e:
                    last_exc = e
                    continue
            if result_text is not None:
                break

        if result_text is None:
            return {
                "provider": f"ollama_{model.replace(':', '_')}",
                "verdict": "UNVERIFIABLE",
                "confidence": 0,
                "reasoning": str(last_exc) if last_exc else "no response",
                "raw_response": "",
                "cost": 0.0,
            }

        parsed = self._parse_response(result_text, model)
        parsed.setdefault("raw_response", str(result_text))
        parsed.setdefault("cost", 0.0)
        return parsed

    def _parse_response(self, response: str, model: str) -> dict:
        import re
        if not isinstance(response, str):
            response = str(response)
        verdict_match = re.search(r"VERDICT:\s*(TRUE|FALSE|MISLEADING|UNVERIFIABLE)", response, re.IGNORECASE)
        verdict = verdict_match.group(1).upper() if verdict_match else "UNVERIFIABLE"
        conf_match = re.search(r"CONFIDENCE:\s*(\d+)", response)
        confidence = int(conf_match.group(1)) if conf_match else 50
        reasoning_match = re.search(r"REASONING:\s*(.+)", response, re.DOTALL)
        reasoning = reasoning_match.group(1).strip() if reasoning_match else response.strip()[:200]
        return {
            "provider": f"ollama_{model.replace(':', '_')}",
            "verdict": verdict,
            "confidence": confidence,
            "reasoning": reasoning,
            "raw_response": response,
        }
