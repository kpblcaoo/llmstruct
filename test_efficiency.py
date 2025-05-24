import time
import psutil
import json
import subprocess
import requests
from pathlib import Path
import argparse
import os
import shutil
from urllib.parse import urlparse
import ipaddress
from src.llmstruct.grok import test_grok


def get_system_metrics():
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_mb": psutil.virtual_memory().used / 1024 / 1024
    }


def is_local_address(url):
    try:
        hostname = urlparse(url).hostname
        ip = ipaddress.ip_address(hostname)
        return ip.is_private or ip.is_loopback
    except ValueError:
        return hostname in ("localhost",)


def setup_proxy(proxy_url=None):
    if proxy_url:
        return {"http": proxy_url, "https": proxy_url}
    return {"http": os.getenv("http_proxy"), "https": os.getenv("https_proxy")}


def check_ollama(api_url):
    try:
        response = requests.get(f"{api_url.replace('/api/generate', '/api/tags')}")
        return response.status_code == 200, response.json()
    except requests.RequestException as e:
        return False, str(e)


def optimize_prompt(struct_data, max_tokens=4000):
    tokens = struct_data.split()
    if len(tokens) > max_tokens:
        print(
            f"Warning: Prompt too long ({len(tokens)} tokens), truncating to {max_tokens}")
        return " ".join(tokens[:max_tokens])
    return struct_data


def run_llm_request(api_url, payload, proxy=None):
    start_time = time.perf_counter()
    system_metrics = get_system_metrics()
    session = requests.Session()
    if proxy and not is_local_address(api_url):
        session.proxies.update(proxy)
    try:
        response = session.post(api_url, json=payload)
        response.raise_for_status()
        tokens_out = len(response.json().get("response", "").split())
        text = response.json().get("response", "")
    except requests.RequestException as e:
        print(f"Error: {e}")
        tokens_out = 0
        text = ""
        response = type("obj", (), {"status_code": 500})()
    end_time = time.perf_counter()
    return {
        "response_time": end_time - start_time,
        "status_code": response.status_code,
        "tokens_in": len(payload["prompt"].split()),
        "tokens_out": tokens_out,
        "text": text,
        "system_metrics": system_metrics
    }


def check_llmstruct_cli():
    return shutil.which("llmstruct") is not None


def test_with_llmstruct(api_url, project_path, proxy, use_placeholder=False):
    struct_path = Path(project_path) / "data/struct.json"
    placeholder_path = Path(project_path) / "data/struct_placeholder.json"

    if use_placeholder:
        target_path = placeholder_path
        with open(target_path, "w") as f:
            json.dump({
                "version": "0.1.0",
                "modules": [
                    {"name": "collector", "path": "src/llmstruct/collector.py", "functions": []},
                    {"name": "cli", "path": "src/llmstruct/cli.py", "functions": []}
                ]
            }, f, indent=2)
    else:
        target_path = struct_path
        if not target_path.exists() and check_llmstruct_cli():
            subprocess.run(["llmstruct", "parse", project_path,
                           "--output", str(target_path)])

    if not target_path.exists():
        raise FileNotFoundError(f"Could not find or generate {target_path}")

    with open(target_path, "r") as f:
        struct_data = f.read()
    struct_data = optimize_prompt(struct_data, max_tokens=4000)
    prompt = f"Analyze this project structure and summarize key modules and their functions:\n{struct_data}"
    return run_llm_request(api_url, {"model": "mistral", "prompt": prompt}, proxy)


def test_without_llmstruct(api_url, project_path, proxy):
    code = ""
    for file in Path(project_path).glob("**/*.py"):
        with open(file, "r") as f:
            code += f"\n\n# {file}\n{f.read()}"
    code = optimize_prompt(code, max_tokens=4000)
    prompt = f"Analyze this project code and summarize key modules and their functions:\n{code}"
    return run_llm_request(api_url, {"model": "mistral", "prompt": prompt}, proxy)


def test_with_grok(api_key, project_path, proxy, use_placeholder=False):
    struct_path = Path(project_path) / "data/struct.json"
    placeholder_path = Path(project_path) / "data/struct_placeholder.json"

    target_path = placeholder_path if use_placeholder else struct_path
    if use_placeholder:
        with open(target_path, "w") as f:
            json.dump({
                "version": "0.1.0",
                "modules": [
                    {"name": "collector", "path": "src/llmstruct/collector.py", "functions": []},
                    {"name": "cli", "path": "src/llmstruct/cli.py", "functions": []}
                ]
            }, f, indent=2)

    if not target_path.exists():
        raise FileNotFoundError(f"Could not find {target_path}")

    with open(target_path, "r") as f:
        struct_data = f.read()
    struct_data = optimize_prompt(struct_data, max_tokens=4000)
    prompt = f"Analyze this project structure and summarize key modules and their functions:\n{struct_data}"
    return test_grok(api_key, prompt, proxy)


def evaluate_accuracy(response_text, expected):
    score = sum(1 for word in expected if word in response_text.lower()) / len(expected)
    return score * 100


def main():
    parser = argparse.ArgumentParser(description="Test llmstruct efficiency")
    parser.add_argument("--proxy", help="Proxy URL (e.g., socks5://127.0.0.1:1080)")
    parser.add_argument("--grok-key", help="Grok3 API key")
    parser.add_argument(
        "--use-placeholder",
        action="store_true",
        help="Use placeholder struct.json")
    args = parser.parse_args()

    api_url = "http://192.168.88.50:11434/api/generate"  # Ollama API
    project_path = "."
    expected_keywords = ["collector", "cli", "parse", "main"]
    proxy = setup_proxy(args.proxy)
    results = {
        "with_llmstruct": [],
        "without_llmstruct": [],
        "with_grok": [],
        "with_llmstruct_placeholder": []}

    # Check Ollama
    ollama_status, ollama_info = check_ollama(api_url)
    if not ollama_status:
        print(f"Error: Ollama not available at {api_url}. Info: {ollama_info}")
        return

    if not check_llmstruct_cli():
        print("Warning: 'llmstruct' CLI not found. Ensure 'pip install .' is run.")

    for _ in range(5):
        try:
            result = test_with_llmstruct(
                api_url, project_path, proxy, use_placeholder=False)
            result["accuracy"] = evaluate_accuracy(result["text"], expected_keywords)
            results["with_llmstruct"].append(result)
        except FileNotFoundError as e:
            print(f"Error: {e}")
            results["with_llmstruct"].append({"error": str(e)})

        if args.use_placeholder:
            result = test_with_llmstruct(
                api_url, project_path, proxy, use_placeholder=True)
            result["accuracy"] = evaluate_accuracy(result["text"], expected_keywords)
            results["with_llmstruct_placeholder"].append(result)

        result = test_without_llmstruct(api_url, project_path, proxy)
        result["accuracy"] = evaluate_accuracy(result["text"], expected_keywords)
        results["without_llmstruct"].append(result)

        if args.grok_key:
            result = test_with_grok(
                args.grok_key,
                project_path,
                proxy,
                use_placeholder=args.use_placeholder)
            result["accuracy"] = evaluate_accuracy(result["text"], expected_keywords)
            results["with_grok"].append(result)

    with open("data/test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Results saved to data/test_results.json")


if __name__ == "__main__":
    main()
