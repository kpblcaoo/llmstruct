import argparse
import json
import fnmatch
import os
import logging
from pathlib import Path

def load_gitignore(gitignore_path):
    """Load and normalize .gitignore patterns."""
    patterns = []
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Normalize slashes, remove trailing /
                    pattern = line.replace('\\', '/').rstrip('/')
                    patterns.append(pattern)
    return patterns

def is_path_excluded(module_path, patterns):
    """Check if module_path matches any pattern or is a subpath."""
    module_path = Path(module_path).as_posix()  # Normalize to forward slashes
    for pattern in patterns:
        # Handle ** for recursive paths
        if '**' in pattern:
            pattern = pattern.replace('**', '*')
        # Check if path matches pattern or is a subpath
        if fnmatch.fnmatch(module_path, pattern) or fnmatch.fnmatch(module_path, f"{pattern}/*"):
            return True
        # Check if path starts with pattern (e.g., venv/ matches venv/lib/...)
        if module_path.startswith(pattern + '/') or module_path == pattern:
            return True
    return False

def filter_json(data, gitignore_patterns, include_tests=False):
    """Filter struct.json to exclude .gitignore paths and optionally tests."""
    filtered_data = {
        "metadata": data.get("metadata", {}),
        "toc": [],
        "modules": []
    }
    
    gitignore_patterns = gitignore_patterns or []
    test_patterns = ['test_*', 'tests/*'] if not include_tests else []
    
    for module in data.get("modules", []):
        module_path = module.get("path", "")
        # Check if module path matches .gitignore or test patterns
        if is_path_excluded(module_path, gitignore_patterns + test_patterns):
            logging.debug(f"Excluded module: {module_path}")
            continue
        # Keep essential fields
        filtered_module = {
            "path": module_path,
            "category": module.get("category", ""),
            "module_doc": module.get("module_doc", ""),
            "file_metadata": module.get("file_metadata", {}),
            "functions": module.get("functions", []),
            "classes": module.get("classes", []),
            "dependencies": module.get("dependencies", []),  # Reintroduced
            "callgraph": module.get("callgraph", {}) if "callgraph" in module else {}  # Optional
        }
        filtered_data["modules"].append(filtered_module)
        filtered_data["toc"].append({
            "path": module_path,
            "category": module.get("category", ""),
            "functions": len(module.get("functions", [])),
            "classes": len(module.get("classes", []))
        })
    
    return filtered_data

def main():
    parser = argparse.ArgumentParser(description="Filter struct.json to exclude unwanted paths.")
    parser.add_argument("--input", required=True, help="Input struct.json file")
    parser.add_argument("--output", default="filtered_struct.json", help="Output filtered JSON file")
    parser.add_argument("--gitignore", default=".gitignore", help="Path to .gitignore file")
    parser.add_argument("--include-tests", action="store_true", help="Include test files")
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
    
    try:
        with open(args.input, 'r') as f:
            data = json.load(f)
        
        gitignore_patterns = load_gitignore(args.gitignore)
        logging.info(f"Loaded {len(gitignore_patterns)} .gitignore patterns: {gitignore_patterns}")
        
        filtered_data = filter_json(data, gitignore_patterns, args.include_tests)
        
        with open(args.output, 'w') as f:
            json.dump(filtered_data, f, indent=2)
        
        logging.info(f"Filtered JSON saved to {args.output}")
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    main()