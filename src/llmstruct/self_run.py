import json
import re
from typing import Dict, Any

def filter_json(struct: Dict[str, Any], query: str) -> Dict[str, Any]:
    """Filter JSON to include only modules/functions relevant to the query."""
    filtered = {"metadata": struct["metadata"], "modules": []}
    keywords = re.findall(r'\w+', query.lower())
    
    for module in struct["modules"]:
        filtered_module = {"path": module["path"], "functions": [], "classes": []}
        for func in module.get("functions", []):
            if func["name"].lower() in keywords:
                filtered_module["functions"].append(func)
        for cls in module.get("classes", []):
            if cls["name"].lower() in keywords:
                filtered_module["classes"].append(cls)
        if filtered_module["functions"] or filtered_module["classes"]:
            filtered_module["callgraph"] = {
                k: v for k, v in module.get("callgraph", {}).items()
                if k.lower() in keywords
            }
            filtered["modules"].append(filtered_module)
    
    return filtered

def attach_to_llm_request(json_path: str, prompt: str) -> str:
    """Attach filtered JSON structure to LLM prompt."""
    with open(json_path, "r", encoding="utf-8") as f:
        struct = json.load(f)
    filtered_struct = filter_json(struct, prompt)
    return f"{prompt}\n\nProject Structure:\n{json.dumps(filtered_struct, indent=2)}"

if __name__ == "__main__":
    # Example usage
    prompt = "Explain how analyze_module works"
    print(attach_to_llm_request("struct.json", prompt))