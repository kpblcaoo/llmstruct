#!/bin/bash
# Deploy llmstruct JSON bundle, scripts, and docs

set -e
PROJECT_DIR="llmstruct_project"
DATA_DIR="$PROJECT_DIR/data"
SCHEMAS_DIR="$PROJECT_DIR/schemas"
DOCS_DIR="$PROJECT_DIR/docs"
SCRIPTS_DIR="$PROJECT_DIR/scripts"

# Create directories
mkdir -p "$DATA_DIR" "$SCHEMAS_DIR" "$DOCS_DIR" "$SCRIPTS_DIR"

# Write JSON files
cat << 'EOF' > "$DATA_DIR/init.json"
{
  "version": "0.1.0",
  "status": "Draft",
  "author": "@kpblcaoo",
  "date": "2025-05-21",
  "license": "GPL-3.0",
  "artifact_id": "1a2b3c4d-5e6f-47a8-b9c0-d1e2f3a4b5c6",
  "summary": "Introduction to llmstruct JSON structure and usage",
  "tags": ["init", "guide"],
  "guide": {
    "description": "llmstruct is a universal JSON format for codebases, enabling LLM-driven automation and transparent collaboration.",
    "structure": {
      "core_files": ["data/tasks.json", "data/ideas.json", "data/weights.json"],
      "docs": ["docs/llmstruct_format.md", "docs/llm_instructions.md"],
      "schemas": ["schemas/llmstruct_schema.json"],
      "auxiliary": ["data/ideas_cache.json", "data/metrics.json", "data/prs.json"]
    },
    "usage": {
      "cli": "llmstruct validate data/tasks.json schemas/llmstruct_schema.json",
      "api": "GET /json/ideas.json?filter=priority=high",
      "parser": "llmstruct parse ideas.json --filter 'priority=high' --fields id,description"
    },
    "principles": [
      {"id": "PRINCIPLE-001", "name": "Dogfooding", "ref": "data/concept.json"},
      {"id": "PRINCIPLE-002", "name": "Idempotence", "ref": "data/concept.json"},
      {"id": "PRINCIPLE-003", "name": "Transparency", "ref": "data/concept.json"}
    ],
    "examples": [
      {
        "task": "Validate JSON",
        "command": "llmstruct validate data/ideas.json schemas/llmstruct_schema.json",
        "output": "JSON is valid: data/ideas.json"
      },
      {
        "task": "Filter high-priority ideas",
        "command": "llmstruct parse ideas.json --filter 'priority=high' --fields id,description",
        "output": [{"id": "IDEA-001", "description": "Dynamic Task Generation from struct.json"}]
      }
    ]
  }
}
EOF

cat << 'EOF' > "$DATA_DIR/ideas.json"
{
  "version": "0.4.0",
  "status": "Draft",
  "author": "@kpblcaoo",
  "date": "2025-05-21",
  "license": "GPL-3.0",
  "artifact_id": "e1f2a3b4-c5d6-47e8-b9f0-a1b2c3d4e5f6",
  "summary": "High-priority ideas for automation and transparency",
  "tags": ["automation", "transparency"],
  "ideas": [
    {
      "id": "IDEA-001",
      "description": "Dynamic Task Generation from struct.json",
      "goal": "Automate task creation",
      "weight": 0.8,
      "priority": "high",
      "estimated_effort": "5d",
      "status": "proposed",
      "dependencies": ["TSK-006"],
      "created_at": "2025-05-20T18:00:00Z",
      "author": "Grok (xAI)",
      "ai-generated": true
    },
    {
      "id": "IDEA-002",
      "description": "RFC-Driven Development with struct.json",
      "goal": "Enhance transparency",
      "weight": 0.7,
      "priority": "medium",
      "estimated_effort": "7d",
      "status": "proposed",
      "dependencies": ["TSK-027"],
      "created_at": "2025-05-20T18:00:00Z",
      "author": "Grok (xAI)",
      "ai-generated": true
    },
    {
      "id": "IDEA-126",
      "description": "Automate CI/CD with GitHub Actions and Telegram notifications",
      "goal": "Streamline development",
      "weight": 0.7,
      "priority": "high",
      "estimated_effort": "3d",
      "status": "proposed",
      "dependencies": ["TSK-012", "TSK-023"],
      "created_at": "2025-05-20T22:20:00Z",
      "author": "Grok (xAI)",
      "ai-generated": true
    }
  ]
}
EOF

cat << 'EOF' > "$DATA_DIR/tasks.json"
{
  "version": "0.4.0",
  "status": "Draft",
  "author": "@kpblcaoo",
  "date": "2025-05-21",
  "license": "GPL-3.0",
  "artifact_id": "f2a3b4c5-d6e7-48f9-a0b1-c2d3e4f5a6b7",
  "summary": "Critical tasks for parser and API",
  "tags": ["parser", "api"],
  "tasks": [
    {
      "id": "TSK-006",
      "description": "Improve parser for multi-language support (Python, JS)",
      "status": "in_progress",
      "priority": "high",
      "estimated_effort": "10d",
      "dependencies": [],
      "assignee": "@kpblcaoo",
      "created_at": "2025-05-20T19:00:00Z",
      "author": "@kpblcaoo",
      "ai-generated": false
    },
    {
      "id": "TSK-027",
      "description": "Implement RFC documentation process",
      "status": "proposed",
      "priority": "medium",
      "estimated_effort": "5d",
      "dependencies": [],
      "assignee": "@kpblcaoo",
      "created_at": "2025-05-20T19:00:00Z",
      "author": "@kpblcaoo",
      "ai-generated": false
    },
    {
      "id": "TSK-119",
      "description": "Implement FastAPI for project access",
      "status": "proposed",
      "priority": "critical",
      "estimated_effort": "7d",
      "dependencies": ["TSK-126"],
      "assignee": "@kpblcaoo",
      "created_at": "2025-05-20T22:20:00Z",
      "author": "@kpblcaoo",
      "ai-generated": false
    },
    {
      "id": "TSK-126",
      "description": "Complete struct.json and struct_light.json",
      "status": "proposed",
      "priority": "high",
      "estimated_effort": "5d",
      "dependencies": [],
      "assignee": "@kpblcaoo",
      "created_at": "2025-05-20T22:20:00Z",
      "author": "@kpblcaoo",
      "ai-generated": false
    }
  ]
}
EOF

cat << 'EOF' > "$DATA_DIR/references.json"
{
  "version": "0.1.0",
  "status": "Draft",
  "author": "@kpblcaoo",
  "date": "2025-05-21",
  "license": "GPL-3.0",
  "artifact_id": "2b3c4d5e-6f7a-48b9-c0d1-e2f3a4b5c6d7",
  "summary": "Cross-references between JSON entities",
  "tags": ["references", "linking"],
  "references": [
    {
      "source": {"file": "data/ideas.json", "id": "IDEA-001", "artifact_id": "e1f2a3b4-c5d6-47e8-b9f0-a1b2c3d4e5f6"},
      "target": {"file": "data/tasks.json", "id": "TSK-006", "artifact_id": "f2a3b4c5-d6e7-48f9-a0b1-c2d3e4f5a6b7"},
      "type": "dependency"
    },
    {
      "source": {"file": "data/ideas.json", "id": "IDEA-002", "artifact_id": "e1f2a3b4-c5d6-47e8-b9f0-a1b2c3d4e5f6"},
      "target": {"file": "data/tasks.json", "id": "TSK-027", "artifact_id": "f2a3b4c5-d6e7-48f9-a0b1-c2d3e4f5a6b7"},
      "type": "dependency"
    },
    {
      "source": {"file": "data/ideas.json", "id": "IDEA-126", "artifact_id": "e1f2a3b4-c5d6-47e8-b9f0-a1b2c3d4e5f6"},
      "target": {"file": "data/prs.json", "id": "PR-001", "artifact_id": "d2e3f4a5-b6c7-48d9-e0f1-a2b3c4d5e6f7"},
      "type": "implementation"
    }
  ]
}
EOF

cat << 'EOF' > "$DATA_DIR/ideas_low_priority.json"
{
  "version": "0.2.0",
  "status": "Draft",
  "author": "@kpblcaoo",
  "date": "2025-05-21",
  "license": "GPL-3.0",
  "artifact_id": "a3b4c5d6-e7f8-49a0-b1c2-d3e4f5a6b7c8",
  "summary": "Low-priority ideas for onboarding",
  "tags": ["onboarding"],
  "ideas": [
    {
      "id": "IDEA-114",
      "description": "Update README with proxy and testing instructions",
      "goal": "Improve onboarding",
      "weight": 0.5,
      "priority": "medium",
      "estimated_effort": "1d",
      "status": "proposed",
      "dependencies": [],
      "created_at": "2025-05-20T19:02:00Z",
      "author": "@kpblcaoo",
      "ai-generated": false
    }
  ]
}
EOF

cat << 'EOF' > "$DATA_DIR/concept.json"
{
  "version": "0.2.0",
  "status": "Draft",
  "author": "@kpblcaoo",
  "date": "2025-05-21",
  "license": "GPL-3.0",
  "artifact_id": "b4c5d6e7-f8a9-40b1-c2d3-e4f5a6b7c8d9",
  "summary": "Core principles and goals for llmstruct",
  "tags": ["principles", "goals"],
  "principles": [
    {"id": "PRINCIPLE-001", "name": "Dogfooding", "description": "Use llmstruct to develop llmstruct"},
    {"id": "PRINCIPLE-002", "name": "Idempotence", "description": "Ensure reproducible changes"},
    {"id": "PRINCIPLE-003", "name": "Transparency", "description": "Use RFC-style docs and open collaboration"}
  ],
  "goals": [
    "Create universal JSON format for codebases",
    "Integrate with LLMs for context economy",
    "Support extensible parsers and automation"
  ]
}
EOF

cat << 'EOF' > "$DATA_DIR/weights.json"
{
  "version": "0.2.0",
  "status": "Draft",
  "author": "@kpblcaoo",
  "date": "2025-05-21",
  "license": "GPL-3.0",
  "artifact_id": "c5d6e7f8-a9b0-41c2-d3e4-f5a6b7c8d9e0",
  "summary": "Weights for tasks and ideas",
  "tags": ["weights"],
  "weights": {
    "TSK-006": 0.9,
    "TSK-027": 0.7,
    "TSK-119": 0.95,
    "TSK-126": 0.9,
    "IDEA-001": 0.8,
    "IDEA-002": 0.7,
    "IDEA-114": 0.5,
    "IDEA-126": 0.7
  }
}
EOF

cat << 'EOF' > "$DATA_DIR/docs.json"
{
  "version": "0.2.0",
  "status": "Draft",
  "author": "@kpblcaoo",
  "date": "2025-05-21",
  "license": "GPL-3.0",
  "artifact_id": "d6e7f8a9-b0c1-42d3-e4f5-a6b7c8d9e0f1",
  "summary": "Documentation files for llmstruct",
  "tags": ["docs"],
  "docs": [
    {
      "path": "docs/llmstruct_format.md",
      "title": "LLMstruct JSON Format Specification",
      "version": "0.2.0",
      "status": "Draft",
      "author": "@kpblcaoo",
      "issue": "#141",
      "artifact_id": "e7f8a9b0-c1d2-43e4-f5a6-b7c8d9e0f1a2"
    },
    {
      "path": "docs/llm_instructions.md",
      "title": "LLMstruct Instructions for LLM",
      "version": "0.1.0",
      "status": "Proposed",
      "author": "@kpblcaoo",
      "issue": "#137",
      "artifact_id": "f8a9b0c1-d2e3-44f5-a6b7-c8d9e0f1a2b3"
    }
  ]
}
EOF

cat << 'EOF' > "$DATA_DIR/ideas_cache.json"
{
  "version": "0.2.0",
  "status": "Draft",
  "author": "@kpblcaoo",
  "date": "2025-05-21",
  "license": "GPL-3.0",
  "artifact_id": "a9b0c1d2-e3f4-45a6-b7c8-d9e0f1a2b3c4",
  "summary": "Cached high-priority ideas",
  "tags": ["cache", "ideas"],
  "ideas": [
    {
      "id": "IDEA-001",
      "description": "Dynamic Task Generation from struct.json",
      "goal": "Automate task creation",
      "weight": 0.8,
      "priority": "high",
      "estimated_effort": "5d",
      "status": "proposed",
      "dependencies": ["TSK-006"],
      "created_at": "2025-05-20T18:00:00Z",
      "author": "Grok (xAI)",
      "ai-generated": true
    },
    {
      "id": "IDEA-126",
      "description": "Automate CI/CD with GitHub Actions and Telegram notifications",
      "goal": "Streamline development",
      "weight": 0.7,
      "priority": "high",
      "estimated_effort": "3d",
      "status": "proposed",
      "dependencies": ["TSK-012", "TSK-023"],
      "created_at": "2025-05-20T22:20:00Z",
      "author": "Grok (xAI)",
      "ai-generated": true
    }
  ]
}
EOF

cat << 'EOF' > "$DATA_DIR/metrics.json"
{
  "version": "0.2.0",
  "status": "Draft",
  "author": "@kpblcaoo",
  "date": "2025-05-21",
  "license": "GPL-3.0",
  "artifact_id": "b0c1d2e3-f4a5-46b7-c8d9-e0f1a2b3c4d5",
  "summary": "Project metrics",
  "tags": ["metrics"],
  "metrics": {
    "tasks_completed": 0,
    "ideas_proposed": 4,
    "ideas_approved": 0,
    "code_lines": 1000,
    "doc_lines": 500
  }
}
EOF

cat << 'EOF' > "$DATA_DIR/prs.json"
{
  "version": "0.2.0",
  "status": "Draft",
  "author": "@kpblcaoo",
  "date": "2025-05-21",
  "license": "GPL-3.0",
  "artifact_id": "c1d2e3f4-a5b6-47c8-d9e0-f1a2b3c4d5e6",
  "summary": "Pull requests for ideas",
  "tags": ["prs"],
  "prs": [
    {
      "pr_id": "PR-001",
      "idea_id": "IDEA-126",
      "branch": "ai-generated",
      "status": "pending",
      "created_at": "2025-05-20T22:20:00Z",
      "issue": "#138",
      "artifact_id": "d2e3f4a5-b6c7-48d9-e0f1-a2b3c4d5e6f7"
    }
  ]
}
EOF

cat << 'EOF' > "$DATA_DIR/vision.json"
{
  "version": "0.2.0",
  "status": "Draft",
  "author": "@kpblcaoo",
  "date": "2025-05-21",
  "license": "GPL-3.0",
  "artifact_id": "e3f4a5b6-c7d8-49e0-f1a2-b3c4d5e6f7a8",
  "summary": "Project vision and priorities",
  "tags": ["vision"],
  "concept": {
    "description": "Universal JSON for codebases with LLM integration",
    "principles": ["dogfooding", "idempotence", "transparency"],
    "goals": ["Universal format", "LLM integration", "Automation"]
  },
  "priorities": ["TSK-006", "TSK-119", "TSK-126"],
  "structure": {
    "core_files": ["data/tasks.json", "data/ideas.json"],
    "docs": ["docs/llmstruct_format.md"],
    "modules": ["cli", "collector"]
  }
}
EOF

cat << 'EOF' > "$DATA_DIR/conflicts.json"
{
  "version": "0.2.0",
  "status": "Draft",
  "author": "@kpblcaoo",
  "date": "2025-05-21",
  "license": "GPL-3.0",
  "artifact_id": "f4a5b6c7-d8e9-40f1-a2b3-c4d5e6f7a8b9",
  "summary": "Documentation conflicts",
  "tags": ["conflicts"],
  "conflicts": [
    {
      "conflict_id": "CONF-001",
      "file": "docs/llmstruct_format.md",
      "issue": "Missing folder_structure",
      "suggested_fix": "Update to match struct.json v0.1.1",
      "status": "pending",
      "issue_ref": "#141",
      "artifact_id": "a5b6c7d8-e9f0-41a2-b3c4-d5e6f7a8b9c0"
    }
  ]
}
EOF

cat << 'EOF' > "$SCHEMAS_DIR/llmstruct_schema.json"
{
  "version": "0.2.0",
  "status": "Draft",
  "author": "@kpblcaoo",
  "date": "2025-05-21",
  "license": "GPL-3.0",
  "artifact_id": "b6c7d8e9-f0a1-42b3-c4d5-e6f7a8b9c0d1",
  "summary": "Schema for llmstruct JSON",
  "tags": ["schema"],
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["metadata", "toc", "modules", "folder_structure"],
  "properties": {
    "metadata": {
      "type": "object",
      "required": ["project_name", "version", "authors", "stats", "artifact_id", "summary"],
      "properties": {
        "project_name": {"type": "string"},
        "version": {"type": "string"},
        "authors": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["name", "github", "email"],
            "properties": {
              "name": {"type": "string"},
              "github": {"type": "string"},
              "email": {"type": "string", "format": "email"}
            }
          }
        },
        "stats": {
          "type": "object",
          "required": ["modules_count", "functions_count"],
          "properties": {
            "modules_count": {"type": "integer"},
            "functions_count": {"type": "integer"}
          }
        },
        "artifact_id": {"type": "string", "format": "uuid"},
        "summary": {"type": "string"},
        "tags": {"type": "array", "items": {"type": "string"}}
      }
    },
    "toc": {"type": "array", "items": {"type": "string"}},
    "modules": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "path", "artifact_id"],
        "properties": {
          "name": {"type": "string"},
          "path": {"type": "string"},
          "artifact_id": {"type": "string", "format": "uuid"},
          "functions": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["name", "signature"],
              "properties": {
                "name": {"type": "string"},
                "signature": {"type": "string"}
              }
            }
          }
        }
      }
    },
    "folder_structure": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["path", "type", "artifact_id"],
        "properties": {
          "path": {"type": "string"},
          "type": {"type": "string", "enum": ["directory", "file"]},
          "artifact_id": {"type": "string", "format": "uuid"},
          "metadata": {"type": "object"}
        }
      }
    }
  }
}
EOF

# Write scripts
cat << 'EOF' > "$SCRIPTS_DIR/json_generator.py"
import datetime
import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import uuid

from ..parsers.python_parser import analyze_module

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_folder_structure(root_dir: str, gitignore_patterns: Optional[List[str]], include_patterns: Optional[List[str]], exclude_patterns: Optional[List[str]], exclude_dirs: Optional[List[str]]) -> List[Dict[str, Any]]:
    """Capture directory and file structure with artifact_id, respecting .gitignore and patterns."""
    structure = []
    root_path = Path(root_dir).resolve()
    default_exclude_dirs = {'venv', '__pycache__', '.git', '.pytest_cache', 'build', 'dist'}
    exclude_dirs_set = set(exclude_dirs or []) | default_exclude_dirs
    
    gitignore_patterns = gitignore_patterns or []
    normalized_gitignore = [p.rstrip('/') + '/*' if p.endswith('/') else p for p in gitignore_patterns]
    
    for dir_path, dirnames, filenames in os.walk(root_dir):
        rel_dir = str(Path(dir_path).relative_to(root_path))
        if rel_dir == '.':
            rel_dir = ''
        
        if any(Path(dir_path).match(p) for p in normalized_gitignore) or any(d in exclude_dirs_set for d in Path(dir_path).parts):
            dirnames[:] = []
            continue
        
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs_set and not any(Path(dir_path).joinpath(d).match(p) for p in normalized_gitignore + (exclude_patterns or []))]
        
        structure.append({
            "path": rel_dir or ".",
            "type": "directory",
            "artifact_id": str(uuid.uuid4()),
            "metadata": {}
        })
        for fname in sorted(filenames):
            file_path = Path(dir_path) / fname
            if any(file_path.match(p) for p in (include_patterns or ['*.py']) if not any(file_path.match(ep) for ep in (exclude_patterns or []) + normalized_gitignore)):
                structure.append({
                    "path": str(file_path.relative_to(root_path)),
                    "type": "file",
                    "artifact_id": str(uuid.uuid4()),
                    "metadata": {}
                })
    
    return sorted(structure, key=lambda x: x['path'])

def build_toc_and_modules(root_dir: str, include_patterns: Optional[List[str]], exclude_patterns: Optional[List[str]], gitignore_patterns: Optional[List[str]], include_ranges: bool, include_hashes: bool, exclude_dirs: Optional[List[str]]) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Build TOC and modules with artifact_id and robust filtering."""
    toc = []
    modules = []
    default_exclude_dirs = {'venv', '__pycache__', '.git', '.pytest_cache', 'build', 'dist'}
    exclude_dirs_set = set(exclude_dirs or []) | default_exclude_dirs
    
    gitignore_patterns = gitignore_patterns or []
    normalized_gitignore = [p.rstrip('/') + '/*' if p.endswith('/') else p for p in gitignore_patterns]
    
    files = [
        f for f in Path(root_dir).rglob('*.py')
        if not any(f.match(p) for p in (exclude_patterns or []) + normalized_gitignore)
        and not any(d in exclude_dirs_set for d in f.parts)
    ]
    
    for file_path in files:
        module = analyze_module(str(file_path), root_dir, include_ranges, include_hashes)
        if module:
            module['artifact_id'] = str(uuid.uuid4())
            modules.append(module)
            toc.append({
                "module_id": module['module_id'],
                "path": module['path'],
                "category": module['category'],
                "functions": len(module['functions']),
                "classes": len(module['classes']),
                "summary": module['module_doc'].split('\n')[0] if module['module_doc'] else '',
                "artifact_id": module['artifact_id']
            })
    
    return toc, modules

def generate_json(root_dir: str, include_patterns: Optional[List[str]], exclude_patterns: Optional[List[str]], gitignore_patterns: Optional[List[str]], include_ranges: bool, include_hashes: bool, goals: Optional[List[str]], exclude_dirs: Optional[List[str]]) -> Dict[str, Any]:
    """Generate JSON structure for project with artifact_id, summary, and tags."""
    root_path = Path(root_dir).resolve()
    toc, modules = build_toc_and_modules(root_dir, include_patterns, exclude_patterns, gitignore_patterns, include_ranges, include_hashes, exclude_dirs)
    
    stats = {
        "modules_count": len(modules),
        "functions_count": sum(len(m['functions']) for m in modules),
        "classes_count": sum(len(m['classes']) for m in modules),
        "call_edges_count": sum(len(set(sum((list(v) for v in m['callgraph'].values()), []))) for m in modules)
    }
    
    return {
        "metadata": {
            "project_name": "llmstruct",
            "description": "Utility for generating structured JSON for codebases",
            "version": datetime.datetime.utcnow().isoformat() + 'Z',
            "authors": [
                {
                    "name": "Mikhail Stepanov",
                    "github": "kpblcaoo",
                    "email": "kpblcaoo@gmail.com"
                }
            ],
            "instructions": [
                "Follow best practices, warn if instructions conflict with them",
                "Preserve functionality, ensure idempotency",
                "Use attached struct.json for context and navigation",
                "Request missing modules or functions if needed",
                "Regenerate JSON for significant changes, track via Git and artifacts",
                "Use internal comments for descriptions, append brief summary"
            ],
            "goals": goals or [],
            "stats": stats,
            "artifact_id": str(uuid.uuid4()),
            "summary": "Structured JSON for llmstruct codebase",
            "tags": ["codebase", "automation"],
            "folder_structure": get_folder_structure(root_dir, gitignore_patterns, include_patterns, exclude_patterns, exclude_dirs)
        },
        "toc": toc,
        "modules": modules
    }
EOF

cat << 'EOF' > "$SCRIPTS_DIR/json_validator.py"
import json
import logging
from pathlib import Path
from jsonschema import validate, ValidationError
from typing import List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def validate_struct_json(json_path: str, schema_path: str) -> bool:
    """Validate a single JSON file against a schema."""
    try:
        json_file = Path(json_path)
        schema_file = Path(schema_path)
        if not json_file.exists():
            logging.error(f"JSON file not found: {json_path}")
            return False
        if not schema_file.exists():
            logging.error(f"Schema file not found: {schema_path}")
            return False

        with open(json_file, "r", encoding="utf-8") as f:
            struct = json.load(f)
        with open(schema_file, "r", encoding="utf-8") as f:
            schema = json.load(f)

        validate(instance=struct, schema=schema)
        logging.info(f"JSON is valid: {json_path}")
        return True
    except ValidationError as e:
        logging.error(f"Validation error in {json_path}: {e.message}")
        return False
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error in {json_path}: {str(e)}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error in {json_path}: {str(e)}")
        return False

def validate_directory(directory: str, schema_path: str, include_patterns: Optional[List[str]] = None, exclude_patterns: Optional[List[str]] = None) -> bool:
    """Validate all JSON files in a directory against a schema."""
    include_patterns = include_patterns or ["*.json"]
    exclude_patterns = exclude_patterns or []
    valid = True
    
    for json_file in Path(directory).rglob("*.json"):
        if any(json_file.match(p) for p in include_patterns) and not any(json_file.match(ep) for ep in exclude_patterns):
            if not validate_struct_json(str(json_file), schema_path):
                valid = False
    
    return valid

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        logging.error("Usage: python json_validator.py <path> <schema.json> [--include <pattern>] [--exclude <pattern>]")
        sys.exit(1)
    
    path, schema_path = sys.argv[1], sys.argv[2]
    include_patterns = [sys.argv[sys.argv.index("--include") + 1]] if "--include" in sys.argv else None
    exclude_patterns = [sys.argv[sys.argv.index("--exclude") + 1]] if "--exclude" in sys.argv else None
    
    if Path(path).is_dir():
        success = validate_directory(path, schema_path, include_patterns, exclude_patterns)
    else:
        success = validate_struct_json(path, schema_path)
    
    sys.exit(0 if success else 1)
EOF

cat << 'EOF' > "$SCRIPTS_DIR/json_selector.py"
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def filter_json(data: Dict[str, Any], filter_key: str, filter_value: str, fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Filter JSON data by key-value pair and select fields."""
    filtered = []
    items = data.get("ideas", []) or data.get("tasks", []) or data.get("docs", []) or data.get("prs", []) or data.get("conflicts", [])
    
    for item in items:
        if item.get(filter_key) == filter_value:
            if fields:
                filtered.append({k: item[k] for k in fields if k in item})
            else:
                filtered.append(item)
    
    return filtered

def select_json(json_path: str, filter_key: str, filter_value: str, fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Load and filter JSON file."""
    try:
        json_file = Path(json_path)
        if not json_file.exists():
            logging.error(f"JSON file not found: {json_path}")
            return []
        
        with open(json_file, "r", encoding="utf-8") as f:
            data = json