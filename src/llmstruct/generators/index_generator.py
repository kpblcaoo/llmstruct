"""
Index.json Generator for LLMStruct Phase 1

Generates manifest file with uid → hash mapping for diff capabilities.
"""

import datetime
from typing import Dict, Any, List


def generate_index_json(struct_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate index.json manifest from struct data.
    
    Args:
        struct_data: Full struct.json data
        
    Returns:
        Dict containing index manifest with uid → hash mappings
    """
    entities = []
    
    # Process modules
    for module in struct_data.get("modules", []):
        if module.get("uid") and module.get("hash"):
            entities.append({
                "uid": module["uid"],
                "hash": module["hash"],
                "hash_source": module.get("hash_source"),
                "hash_version": module.get("hash_version"),
                "type": "module",
                "module": module["module_id"],
                "path": module["path"]
            })
            
        # Process functions
        for func in module.get("functions", []):
            if func.get("uid") and func.get("hash"):
                entities.append({
                    "uid": func["uid"],
                    "hash": func["hash"],
                    "hash_source": func.get("hash_source"),
                    "hash_version": func.get("hash_version"),
                    "type": "function",
                    "module": module["module_id"],
                    "name": func["name"]
                })
                
        # Process classes
        for cls in module.get("classes", []):
            if cls.get("uid") and cls.get("hash"):
                entities.append({
                    "uid": cls["uid"],
                    "hash": cls["hash"],
                    "hash_source": cls.get("hash_source"),
                    "hash_version": cls.get("hash_version"),
                    "type": "class",
                    "module": module["module_id"],
                    "name": cls["name"]
                })
                
            # Process methods
            for method in cls.get("methods", []):
                if method.get("uid") and method.get("hash"):
                    entities.append({
                        "uid": method["uid"],
                        "hash": method["hash"],
                        "hash_source": method.get("hash_source"),
                        "hash_version": method.get("hash_version"),
                        "type": "method",
                        "module": module["module_id"],
                        "class": cls["name"],
                        "name": method["name"]
                    })
    
    return {
        "version": "2.1.0",
        "generated": datetime.datetime.utcnow().isoformat() + "Z",
        "source_file": "struct.json",
        "total_entities": len(entities),
        "entities_by_type": {
            "module": len([e for e in entities if e["type"] == "module"]),
            "function": len([e for e in entities if e["type"] == "function"]),
            "class": len([e for e in entities if e["type"] == "class"]),
            "method": len([e for e in entities if e["type"] == "method"])
        },
        "hash_sources": list(set(e.get("hash_source") for e in entities if e.get("hash_source"))),
        "entities": entities
    }


def save_index_json(struct_data: Dict[str, Any], output_path: str = "index.json") -> None:
    """Save index.json to file.
    
    Args:
        struct_data: Full struct.json data
        output_path: Path to save index.json
    """
    import json
    
    index_data = generate_index_json(struct_data)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)


def diff_by_hash(old_index_path: str, new_index_path: str) -> Dict[str, List[Dict[str, Any]]]:
    """Compare two index.json files and return differences.
    
    Args:
        old_index_path: Path to old index.json
        new_index_path: Path to new index.json
        
    Returns:
        Dict with added, modified, deleted entities
    """
    import json
    
    with open(old_index_path, "r", encoding="utf-8") as f:
        old_index = json.load(f)
    
    with open(new_index_path, "r", encoding="utf-8") as f:
        new_index = json.load(f)
    
    old_entities = {e["uid"]: e for e in old_index["entities"]}
    new_entities = {e["uid"]: e for e in new_index["entities"]}
    
    added = []
    modified = []
    deleted = []
    
    # Find added entities
    for uid, entity in new_entities.items():
        if uid not in old_entities:
            added.append(entity)
    
    # Find deleted entities
    for uid, entity in old_entities.items():
        if uid not in new_entities:
            deleted.append(entity)
    
    # Find modified entities (same uid, different hash)
    for uid, new_entity in new_entities.items():
        if uid in old_entities:
            old_entity = old_entities[uid]
            if old_entity["hash"] != new_entity["hash"]:
                modified.append({
                    "uid": uid,
                    "old_hash": old_entity["hash"],
                    "new_hash": new_entity["hash"],
                    "entity": new_entity
                })
    
    return {
        "added": added,
        "modified": modified,
        "deleted": deleted,
        "summary": {
            "added_count": len(added),
            "modified_count": len(modified),
            "deleted_count": len(deleted),
            "total_changes": len(added) + len(modified) + len(deleted)
        }
    } 