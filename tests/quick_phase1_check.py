#!/usr/bin/env python3
"""
Quick Phase 1 v2.1.0 validation check
Run this to validate current phase 1 implementation quickly
"""

import json
import sys
from pathlib import Path

def quick_validate():
    """Quick validation of Phase 1 v2.1.0 features."""
    
    print("🔍 Quick Phase 1 v2.1.0 Validation Check")
    print("=" * 50)
    
    # Check for output files
    struct_file = Path("tests/fixtures/phase1/struct_v2.1_final.json")
    index_file = Path("tests/fixtures/phase1/struct_v2.1_final_index.json")
    
    if not struct_file.exists():
        print("❌ Missing struct_v2.1_final.json")
        return False
        
    if not index_file.exists():
        print("❌ Missing struct_v2.1_final_index.json")
        return False
    
    # Load and validate struct
    with open(struct_file) as f:
        data = json.load(f)
    
    # Check schema version
    schema_version = data["metadata"].get("schema_version")
    if schema_version != "2.1.0":
        print(f"❌ Wrong schema version: {schema_version} (expected 2.1.0)")
        return False
    print(f"✅ Schema version: {schema_version}")
    
    # Check hash presence
    hash_count = 0
    for module in data["modules"]:
        if module.get("hash"):
            hash_count += 1
        for func in module["functions"]:
            if func.get("hash"):
                hash_count += 1
        for cls in module["classes"]:
            if cls.get("hash"):
                hash_count += 1
            for method in cls["methods"]:
                if method.get("hash"):
                    hash_count += 1
    
    print(f"✅ Hash count: {hash_count}")
    
    # Check UID system
    uid_count = 0
    for module in data["modules"]:
        if module.get("uid"):
            uid_count += 1
        for func in module["functions"]:
            if func.get("uid"):
                uid_count += 1
        for cls in module["classes"]:
            if cls.get("uid"):
                uid_count += 1
            for method in cls["methods"]:
                if method.get("uid"):
                    uid_count += 1
    
    print(f"✅ UID count: {uid_count}")
    
    # Check call edges accuracy
    reported_edges = data["metadata"]["stats"]["call_edges_count"]
    actual_edges = 0
    for module in data["modules"]:
        callgraph = module.get("callgraph", {})
        for caller, callees in callgraph.items():
            actual_edges += len(callees)
    
    if reported_edges == actual_edges:
        print(f"✅ Call edges accurate: {reported_edges}")
    else:
        print(f"❌ Call edges mismatch: reported {reported_edges}, actual {actual_edges}")
        return False
    
    # Check TOC hashes
    toc_with_hash = sum(1 for entry in data["toc"] if entry.get("hash"))
    print(f"✅ TOC entries with hash: {toc_with_hash}/{len(data['toc'])}")
    
    # Check index.json
    with open(index_file) as f:
        index_data = json.load(f)
    
    index_version = index_data.get("version")
    if index_version != "2.1.0":
        print(f"❌ Wrong index version: {index_version}")
        return False
    print(f"✅ Index version: {index_version}")
    
    total_entities = index_data.get("total_entities", 0)
    print(f"✅ Index entities: {total_entities}")
    
    print("\n🎉 Phase 1 v2.1.0 Quick Validation PASSED!")
    return True

if __name__ == "__main__":
    success = quick_validate()
    sys.exit(0 if success else 1)
