import requests
import os

class GrokClient:
    def __init__(self, api_key, proxy=None):
        self.api_url = "https://api.x.ai/v1/chat/completions"
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.session = requests.Session()
        if proxy:
            self.session.proxies.update({"http": proxy, "https": proxy})

    def generate(self, prompt, model="grok3"):
        payload = {"prompt": prompt, "model": model}
        response = self.session.post(self.api_url, json=payload, headers=self.headers)
        response.raise_for_status()
        return {
            "text": response.json().get("text", ""),
            "tokens_in": len(prompt.split()),
            "tokens_out": len(response.json().get("text", "").split())
        }

def test_grok(api_key, prompt, proxy=None):
    client = GrokClient(api_key, proxy)
    start_time = time.perf_counter()
    result = client.generate(prompt)
    end_time = time.perf_counter()
    result["response_time"] = end_t01ime - start_time
    return result