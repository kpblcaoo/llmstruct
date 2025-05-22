import json
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from jsonschema import validate, ValidationError

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

EMBEDDED_FILES = {
    "data/tasks.json": {
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
                "ai-generated": False
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
                "ai-generated": False
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
                "ai-generated": False
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
                "ai-generated": False
            }
        ]
    },
    "data/ideas.json": {
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
                "ai-generated": True,
                "converted_to": None
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
                "ai-generated": True,
                "converted_to": None
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
                "ai-generated": True,
                "converted_to": None
            }
        ]
    },
    "data/weights.json": {
        "version": "0.2.0",
        "status": "Draft",
        "author": "@kpblcaoo",
        "date": "2025-05-21",
        "license": "GPL-3.0",
        "artifact_id": "c5d6e7f8-a9b0-41c2-d3e4-f5a6b7c8d9e0",
        "summary": "Weights for tasks and ideas",
        "tags": ["weights"],
        "weights": {
            "TSK-006": {"base_weight": 0.7, "manual_adjustment": 0.2, "weight": 0.9, "normalized_weight": 0.486},
            "TSK-027": {"base_weight": 0.6, "manual_adjustment": 0.1, "weight": 0.7, "normalized_weight": 0.378},
            "TSK-119": {"base_weight": 0.9, "manual_adjustment": 0.05, "weight": 0.95, "normalized_weight": 0.514},
            "TSK-126": {"base_weight": 0.7, "manual_adjustment": 0.1, "weight": 0.8, "normalized_weight": 0.432},
            "IDEA-001": {"base_weight": 0.7, "manual_adjustment": 0.1, "weight": 0.8, "normalized_weight": 0.432},
            "IDEA-002": {"base_weight": 0.6, "manual_adjustment": 0.1, "weight": 0.7, "normalized_weight": 0.378},
            "IDEA-126": {"base_weight": 0.7, "manual_adjustment": 0.0, "weight": 0.7, "normalized_weight": 0.378}
        }
    },
    "data/prs.json": {
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
    },
    "data/cli.json": {
        "version": "0.1.0",
        "status": "Draft",
        "author": "@kpblcaoo",
        "date": "2025-05-22",
        "license": "GPL-3.0",
        "artifact_id": "e5f6a7b8-c9d0-41e2-f3a4-b5c6d7e8f9a0",
        "summary": "CLI commands for llmstruct",
        "tags": ["cli"],
        "commands": [
            {
                "name": "parse",
                "description": "Parse codebase and generate struct.json",
                "arguments": [
                    {"name": "root_dir", "type": "string", "required": True, "description": "Root directory of the project"},
                    {"name": "output", "type": "string", "required": False, "description": "Output JSON file"},
                    {"name": "filters", "type": "array", "required": False, "description": "Glob patterns to filter files (e.g., src/*,!tests/*)"},
                    {"name": "use_cache", "type": "boolean", "required": False, "description": "Cache generated JSON"}
                ],
                "examples": [
                    {"command": "llmstruct parse . --output struct.json --filters src/*,!tests/*", "description": "Generate struct.json with filters"}
                ],
                "prompt_templates": ["Parse codebase in {root_dir} with filters {filters} and output to {output}"],
                "related_tasks": ["TSK-006", "TSK-126"],
                "related_ideas": ["IDEA-001"]
            },
            {
                "name": "interactive",
                "description": "Run interactive CLI with LLM",
                "arguments": [
                    {"name": "root_dir", "type": "string", "required": True, "description": "Root directory of the project"},
                    {"name": "context", "type": "string", "required": False, "description": "Context JSON file"}
                ],
                "examples": [{"command": "llmstruct interactive . --context init.json", "description": "Start interactive mode"}],
                "prompt_templates": ["Run interactive CLI for {root_dir} with context {context}"],
                "related_tasks": ["TSK-119"],
                "related_ideas": ["IDEA-126"]
            },
            {
                "name": "query",
                "description": "Query LLMs with prompt and context",
                "arguments": [
                    {"name": "prompt", "type": "string", "required": True, "description": "Prompt for LLM"},
                    {"name": "context", "type": "string", "required": False, "description": "Context JSON file"},
                    {"name": "threshold", "type": "number", "required": False, "description": "Weight threshold for task focus"}
                ],
                "examples": [{"command": "llmstruct query --prompt 'Analyze code' --threshold 0.8", "description": "Query with high-priority tasks"}],
                "prompt_templates": ["Query LLM with prompt {prompt} and context {context}, focus on tasks with weights > {threshold}: {tasks}"],
                "related_tasks": ["TSK-119"],
                "related_ideas": []
            },
            {
                "name": "insights",
                "description": "Manage insights",
                "arguments": [
                    {"name": "action", "type": "string", "required": True, "description": "Action (add, list)"},
                    {"name": "description", "type": "string", "required": False, "description": "Insight description"}
                ],
                "examples": [{"command": "llmstruct insights add 'Validate references'", "description": "Add new insight"}],
                "prompt_templates": ["Add insight: {description}"],
                "related_tasks": ["TSK-006"],
                "related_ideas": ["IDEA-001"]
            },
            {
                "name": "artifacts",
                "description": "Manage artifacts",
                "arguments": [
                    {"name": "action", "type": "string", "required": True, "description": "Action (list)"}
                ],
                "examples": [{"command": "llmstruct artifacts list", "description": "List artifacts"}],
                "prompt_templates": ["List artifacts"],
                "related_tasks": ["TSK-119"],
                "related_ideas": []
            },
            {
                "name": "weights",
                "description": "Adjust task/idea weights",
                "arguments": [
                    {"name": "action", "type": "string", "required": True, "description": "Action (adjust)"},
                    {"name": "id", "type": "string", "required": True, "description": "Task or idea ID"},
                    {"name": "adjustment", "type": "number", "required": True, "description": "Weight adjustment"}
                ],
                "examples": [{"command": "llmstruct weights adjust TSK-006 0.2", "description": "Adjust weight for TSK-006"}],
                "prompt_templates": ["Adjust weight for {id} by {adjustment}"],
                "related_tasks": ["TSK-035"],
                "related_ideas": []
            }
        ]
    },
    "data/metrics.json": {
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
    },
    "data/conflicts.json": {
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
                "status": "resolved",
                "issue_ref": "#141",
                "artifact_id": "a5b6c7d8-e9f0-41a2-b3c4-d5e6f7a8b9c0"
            }
        ]
    },
    "data/references.json": {
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
                "type": "dependency",
                "backlink": {"file": "data/tasks.json", "id": "TSK-006", "type": "backlink"}
            },
            {
                "source": {"file": "data/ideas.json", "id": "IDEA-002", "artifact_id": "e1f2a3b4-c5d6-47e8-b9f0-a1b2c3d4e5f6"},
                "target": {"file": "data/tasks.json", "id": "TSK-027", "artifact_id": "f2a3b4c5-d6e7-48f9-a0b1-c2d3e4f5a6b7"},
                "type": "dependency",
                "backlink": {"file": "data/tasks.json", "id": "TSK-027", "type": "backlink"}
            },
            {
                "source": {"file": "data/ideas.json", "id": "IDEA-126", "artifact_id": "e1f2a3b4-c5d6-47e8-b9f0-a1b2c3d4e5f6"},
                "target": {"file": "data/prs.json", "id": "PR-001", "artifact_id": "d2e3f4a5-b6c7-48d9-e0f1-a2b3c4d5e6f7"},
                "type": "implementation",
                "backlink": {"file": "data/prs.json", "id": "PR-001", "type": "backlink"}
            },
            {
                "source": {"file": "data/metrics.json", "id": "METRICS-001", "artifact_id": "b0c1d2e3-f4a5-46b7-c8d9-e0f1a2b3c4d5"},
                "target": {"file": "data/tasks.json", "id": "TSK-006", "artifact_id": "f2a3b4c5-d6e7-48f9-a0b1-c2d3e4f5a6b7"},
                "type": "metric",
                "backlink": {"file": "data/tasks.json", "id": "TSK-006", "type": "backlink"}
            },
            {
                "source": {"file": "data/conflicts.json", "id": "CONF-001", "artifact_id": "f4a5b6c7-d8e9-40f1-a2b3-c4d5e6f7a8b9"},
                "target": {"file": "docs/llmstruct_format.md", "id": None, "artifact_id": "e6f7a8b9-c0d1-52e3-f4a5-b6c7d8e9f0a1"},
                "type": "conflict",
                "backlink": {"file": "docs/llmstruct_format.md", "id": None, "type": "backlink"}
            }
        ]
    },
    "data/vision.json": {
        "version": "0.2.0",
        "status": "Draft",
        "author": "@kpblcaoo",
        "date": "2025-05-22",
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
        "weights": {
            "methodology": "Base weights from priority (critical=0.9-1.0, high=0.7-0.9, medium=0.5-0.7, low=0.0-0.5). Manual adjustments via CLI."
        },
        "integrations": {
            "ci_cd": {"github_actions": ["validate_refs", "sync_issues"], "tasks": ["TSK-012", "TSK-119"]},
            "telegram": {"bot": "llmstruct-bot", "tasks": ["TSK-023", "TSK-119"]}
        },
        "structure": {
            "core_files": ["data/tasks.json", "data/ideas.json", "data/insights.json", "data/artifacts/index.json"],
            "docs": ["docs/llmstruct_format.md"],
            "modules": ["cli", "collector"]
        }
    },
    "data/init.json": {
        "version": "0.1.0",
        "status": "Draft",
        "author": "@kpblcaoo",
        "date": "2025-05-22",
        "license": "GPL-3.0",
        "artifact_id": "1a2b3c4d-5e6f-47a8-b9c0-d1e2f3a4b5c6",
        "summary": "Introduction to llmstruct JSON structure and usage",
        "tags": ["init", "guide"],
        "guide": {
            "description": "llmstruct is a universal JSON format for codebases, enabling LLM-driven automation and transparent collaboration.",
            "structure": {
                "core_files": ["data/tasks.json", "data/ideas.json", "data/insights.json", "data/artifacts/index.json"],
                "docs": ["docs/llmstruct_format.md", "docs/cli_commands.md", "docs/llmstruct_format.ru.md", "docs/cli_commands.ru.md"],
                "schemas": ["schema/llmstruct_schema.json", "schema/core.json", "schema/plugins/insights.json", "schema/plugins/artifacts.json"],
                "auxiliary": ["data/ideas_cache.json", "data/metrics.json", "data/prs.json", "data/cli.json"]
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
    },
    "data/insights.json": {
        "version": "0.1.0",
        "status": "Draft",
        "author": "@kpblcaoo",
        "date": "2025-05-22",
        "license": "GPL-3.0",
        "artifact_id": "a2b3c4d5-e6f7-48a9-b0c1-d2e3f4a5b6c7",
        "summary": "Insights and findings for llmstruct improvements",
        "tags": ["insights", "automation"],
        "insights": [
            {
                "id": "INS-001",
                "description": "Implement validation for broken references in references.json",
                "related_tasks": ["TSK-006"],
                "related_ideas": ["IDEA-001"],
                "priority": "high",
                "created_at": "2025-05-22T08:00:00Z",
                "author": "Grok (xAI)",
                "ai-generated": True
            },
            {
                "id": "INS-002",
                "description": "Automate metrics updates in metrics.json via collector.py",
                "related_tasks": ["TSK-035"],
                "related_ideas": [],
                "priority": "medium",
                "created_at": "2025-05-22T08:00:00Z",
                "author": "Grok (xAI)",
                "ai-generated": True
            }
        ]
    },
    "data/artifacts/index.json": {
        "version": "0.1.0",
        "status": "Draft",
        "author": "@kpblcaoo",
        "date": "2025-05-22",
        "license": "GPL-3.0",
        "artifact_id": "b3c4d5e6-f7a8-49b0-c1d2-e3f4a5b6c7d8",
        "summary": "Index of artifacts stored on disk",
        "tags": ["artifacts", "index"],
        "artifacts": [
            {
                "artifact_id": "e5f6a7b8-c9d0-41e2-f3a4-b5c6d7e8f9a0",
                "path": "data/cli.json",
                "versions": ["0.1.0"],
                "created_at": "2025-05-20T18:00:00Z"
            },
            {
                "artifact_id": "f2a3b4c5-d6e7-48f9-a0b1-c2d3e4f5a6b7",
                "path": "data/tasks.json",
                "versions": ["0.4.0"],
                "created_at": "2025-05-20T19:00:00Z"
            }
        ]
    },
    "schema/llmstruct_schema.json": {
        "version": "0.2.0",
        "status": "Draft",
        "author": "@kpblcaoo",
        "date": "2025-05-22",
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
            },
            "filters": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Glob patterns to include/exclude files (e.g., ['src/*', '!tests/*'])"
            }
        }
    },
    "schema/core.json": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "LLMstruct Core Schema",
        "description": "Core schema for llmstruct project JSONs",
        "type": "object",
        "required": ["metadata", "version", "artifact_id"],
        "properties": {
            "metadata": {
                "$ref": "common/definitions.json#/definitions/metadata"
            },
            "version": {
                "type": "string",
                "pattern": "^\\d+\\.\\d+\\.\\d+$"
            },
            "status": {
                "type": "string",
                "enum": ["Draft", "Proposed", "Active", "Deprecated"]
            },
            "author": {
                "type": "string"
            },
            "date": {
                "type": "string",
                "format": "date"
            },
            "license": {
                "type": "string",
                "enum": ["GPL-3.0"]
            },
            "artifact_id": {
                "$ref": "common/definitions.json#/definitions/artifact_id"
            },
            "summary": {
                "type": "string"
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"}
            },
            "modules": {
                "type": "array",
                "items": {
                    "$ref": "common/definitions.json#/definitions/module"
                }
            },
            "plugins": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["id", "schema", "version"],
                    "properties": {
                        "id": {"type": "string"},
                        "schema": {"type": "string", "format": "uri-reference"},
                        "version": {"type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$"}
                    }
                }
            },
            "artifacts": {
                "type": "array",
                "items": {
                    "$ref": "common/definitions.json#/definitions/artifact"
                }
            }
        }
    },
    "schema/common/definitions.json": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "LLMstruct Common Definitions",
        "definitions": {
            "artifact_id": {
                "type": "string",
                "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
            },
            "metadata": {
                "type": "object",
                "properties": {
                    "project_name": {"type": "string", "default": "llmstruct"},
                    "description": {"type": "string"},
                    "authors": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "github": {"type": "string"},
                                "email": {"type": "string", "format": "email"}
                            }
                        }
                    }
                }
            },
            "module": {
                "type": "object",
                "required": ["path", "artifact_id"],
                "properties": {
                    "path": {"type": "string"},
                    "category": {"type": "string"},
                    "artifact_id": {"$ref": "#/definitions/artifact_id"},
                    "summary": {"type": "string"}
                }
            },
            "artifact": {
                "type": "object",
                "required": ["artifact_id", "path"],
                "properties": {
                    "artifact_id": {"$ref": "#/definitions/artifact_id"},
                    "path": {"type": "string"},
                    "versions": {"type": "array", "items": {"type": "string"}},
                    "created_at": {"type": "string", "format": "date-time"}
                }
            }
        }
    },
    "schema/plugins/cli.json": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "LLMstruct CLI Plugin Schema",
        "description": "Schema for CLI commands in llmstruct",
        "type": "object",
        "required": ["commands", "artifact_id"],
        "properties": {
            "commands": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["name", "description"],
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "arguments": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "type": {"type": "string", "enum": ["string", "boolean", "array", "number"]},
                                    "required": {"type": "boolean"},
                                    "description": {"type": "string"}
                                }
                            }
                        },
                        "examples": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "command": {"type": "string"},
                                    "description": {"type": "string"}
                                }
                            }
                        },
                        "prompt_templates": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                }
            },
            "artifact_id": {"$ref": "../common/definitions.json#/definitions/artifact_id"}
        }
    },
    "schema/plugins/insights.json": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "LLMstruct Insights Schema",
        "description": "Schema for insights in llmstruct",
        "type": "object",
        "required": ["insights", "artifact_id"],
        "properties": {
            "insights": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["id", "description", "priority"],
                    "properties": {
                        "id": {"type": "string", "pattern": "^INS-\\d+$"},
                        "description": {"type": "string"},
                        "related_tasks": {"type": "array", "items": {"type": "string"}},
                        "related_ideas": {"type": "array", "items": {"type": "string"}},
                        "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                        "created_at": {"type": "string", "format": "date-time"},
                        "author": {"type": "string"},
                        "ai-generated": {"type": "boolean"}
                    }
                }
            },
            "artifact_id": {"$ref": "../common/definitions.json#/definitions/artifact_id"}
        }
    },
    "schema/plugins/artifacts.json": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "LLMstruct Artifacts Index Schema",
        "description": "Schema for artifacts index in llmstruct",
        "type": "object",
        "required": ["artifacts", "artifact_id"],
        "metadata": {
            "project_name": "llmstruct",
            "description": "Schema for indexing artifacts",
            "authors": [{"name": "@kpblcaoo", "github": "kpblcaoo", "email": "kpblcaoo@example.com"}]
        },
        "version": "0.1.0",
        "status": "Draft",
        "author": "@kpblcaoo",
        "date": "2025-05-22",
        "license": "GPL-3.0",
        "artifact_id": "b3c4d5e6-f7a8-49b0-c1d2-e3f4a5b6c7d8",
        "summary": "Schema for artifacts index",
        "tags": ["artifacts", "schema"],
        "properties": {
            "artifacts": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["artifact_id", "path", "versions"],
                    "properties": {
                        "artifact_id": {"$ref": "../common/definitions.json#/definitions/artifact_id"},
                        "path": {"type": "string"},
                        "versions": {"type": "array", "items": {"type": "string"}},
                        "created_at": {"type": "string", "format": "date-time"}
                    }
                }
            },
            "artifact_id": {"$ref": "../common/definitions.json#/definitions/artifact_id"}
        }
    },
    "scripts/validate_refs.py": """import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def validate_references():
    try:
        refs = json.load(Path("data/references.json").open())
        ideas = json.load(Path("data/ideas.json").open())
        conversions = {idea["id"]: idea.get("converted_to") for idea in ideas["ideas"] if idea.get("converted_to")}
        broken_links = []
        updated_refs = refs["references"].copy()
        
        for i, ref in enumerate(refs["references"]):
            source_id = ref["source"]["id"]
            target_id = ref["target"]["id"]
            source_file = Path(ref["source"]["file"])
            target_file = Path(ref["target"]["file"])
            
            if not source_file.exists() or not target_file.exists():
                broken_links.append((source_id, target_id))
                continue
                
            if source_id in conversions:
                logger.info(f"Redirecting {source_id} to {conversions[source_id]}")
                updated_refs[i]["source"]["id"] = conversions[source_id]
            
        if broken_links:
            logger.warning(f"Broken links found: {broken_links}")
        else:
            logger.info("All references valid")
            
        with Path("data/references.json").open("w", encoding="utf-8") as f:
            json.dump({"references": updated_refs}, f, indent=2)
            
    except Exception as e:
        logger.error(f"Validation failed: {e}")

def main():
    validate_references()

if __name__ == "__main__":
    main()
""",
    "scripts/collector.py": """import json
import logging
import uuid
from pathlib import Path
import fnmatch

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def apply_filters(files, filters):
    filtered = []
    for file in files:
        if not filters:
            filtered.append(file)
            continue
        include = False
        for pattern in filters:
            if pattern.startswith("!"):
                if fnmatch.fnmatch(file, pattern[1:]):
                    include = False
                    break
            elif fnmatch.fnmatch(file, pattern):
                include = True
        if include:
            filtered.append(file)
    return filtered

def collect_files(root_dir: Path, filters: list = None):
    files = []
    for path in root_dir.rglob("*"):
        if path.is_file():
            rel_path = str(path.relative_to(root_dir))
            files.append(rel_path)
    return apply_filters(files, filters or [])

def generate_struct(root_dir: str, output: str = "struct.json"):
    root_path = Path(root_dir)
    struct = {
        "metadata": {
            "project_name": "llmstruct",
            "version": "0.2.0",
            "authors": [{"name": "@kpblcaoo", "github": "kpblcaoo", "email": "kpblcaoo@example.com"}],
            "stats": {"modules_count": 0, "functions_count": 0},
            "artifact_id": str(uuid.uuid4()),
            "summary": "LLMstruct project structure",
            "tags": ["struct"]
        },
        "toc": [],
        "modules": [],
        "folder_structure": [],
        "filters": ["src/*", "!tests/*", "!venv/*", "!build/*"]
    }
    
    output_path = Path(output)
    if output_path.exists():
        with output_path.open("r", encoding="utf-8") as f:
            existing = json.load(f)
            struct["filters"] = existing.get("filters", struct["filters"])
    
    files = collect_files(root_path, struct["filters"])
    
    for file in files:
        struct["folder_structure"].append({
            "path": file,
            "type": "file",
            "artifact_id": str(uuid.uuid4()),
            "metadata": {}
        })
    
    struct["modules"] = [
        {"name": "cli", "path": "src/cli", "artifact_id": str(uuid.uuid4()), "functions": []},
        {"name": "collector", "path": "src/collector", "artifact_id": str(uuid.uuid4()), "functions": []}
    ]
    struct["toc"] = files
    struct["metadata"]["stats"]["modules_count"] = len(struct["modules"])
    
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(struct, f, indent=2)
    logger.info(f"Generated {output}")

def main():
    generate_struct(".", "struct.json")

if __name__ == "__main__":
    main()
""",
    ".github/workflows/ci.yml": """name: CI
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"
      - name: Install dependencies
        run: pip install jsonschema
      - name: Validate references
        run: python scripts/validate_refs.py
"""
}

def validate_json(data: dict, schema: dict) -> bool:
    try:
        validate(instance=data, schema=schema)
        return True
    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        return False

def backup_files(target_dir: Path, backup_root: Path):
    if target_dir.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_root / timestamp / target_dir.name
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(target_dir, backup_path, dirs_exist_ok=True)
        logger.info(f"Backed up {target_dir} to {backup_path}")

def deploy_embedded_files():
    backup_root = Path("./bak")
    schemas_dir = Path("schema")
    data_dir = Path("data")
    scripts_dir = Path("scripts")
    github_dir = Path(".github/workflows")
    core_schema = EMBEDDED_FILES.get("schema/core.json", {})
    
    for filename, content in EMBEDDED_FILES.items():
        target_path = Path(filename)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        if target_path.exists():
            backup_files(target_path.parent, backup_root)
        
        try:
            if target_path.suffix == ".json":
                if not validate_json(content, core_schema):
                    logger.error(f"Skipping invalid JSON: {filename}")
                    continue
                with target_path.open("w", encoding="utf-8") as f:
                    json.dump(content, f, indent=2, ensure_ascii=False)
            else:
                with target_path.open("w", encoding="utf-8") as f:
                    f.write(content)
            logger.info(f"Deployed {filename} to {target_path}")
        except Exception as e:
            logger.error(f"Error writing {filename}: {e}")

def main():
    deploy_embedded_files()

if __name__ == "__main__":
    main()