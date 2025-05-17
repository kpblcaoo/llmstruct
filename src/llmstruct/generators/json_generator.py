import datetime
from typing import List, Dict, Any

class JSONGenerator:
    def generate(self, modules: List[Dict[str, Any]], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate LLMStruct JSON from parsed module data and metadata."""
        toc = []
        for module in modules:
            if "error" in module:
                continue
            toc.append({
                "path": module.get("path", ""),
                "category": module.get("category", "unknown"),
                "functions": len(module.get("functions", [])),
                "classes": len(module.get("classes", [])),
                "summary": (module.get("module_doc") or "").split("\n")[0] if module.get("module_doc") else ""
            })

        # Ensure metadata has required fields
        metadata_defaults = {
            "project_name": "unknown",
            "description": "",
            "version": datetime.datetime.now().isoformat() + "Z",
            "instructions": [],
            "goals": [],
            "tasks": [],
            "stats": {
                "modules_count": len(modules),
                "functions_count": sum(len(m.get("functions", [])) for m in modules),
                "classes_count": sum(len(m.get("classes", [])) for m in modules),
                "call_edges_count": sum(len(m.get("callgraph", {})) for m in modules)
            }
        }
        for key, value in metadata_defaults.items():
            metadata.setdefault(key, value)

        return {
            "metadata": metadata,
            "toc": toc,
            "modules": [m for m in modules if "error" not in m]
        }