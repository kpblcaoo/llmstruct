#!/usr/bin/env python3
"""
Simple Integration Test for LLMStruct v2.1 Phase 1
Tests basic functionality with real codebase
"""

import sys
import json
import os
import time
from pathlib import Path

sys.path.insert(0, 'src')

from llmstruct.generators.json_generator import generate_json
from llmstruct.core import (
    # UID System
    generate_uid, generate_uid_components, UIDType,
    
    # Hash System
    hash_content, hash_file,
    
    # Summary System  
    generate_summary, get_summary_system
)

def test_phase1_basic_integration():
    """Basic integration test of Phase 1 features."""
    print("🚀 LLMStruct v2.1 Phase 1 - Basic Integration Test")
    print("="*70)
    
    # Test target: small subset of our codebase
    target_path = "src/llmstruct/core"
    
    print(f"🎯 Target: {target_path}")
    print(f"📁 Testing with core module analysis...")
    
    # Test JSON generation with all Phase 1 features
    print("\n📊 Testing Phase 1 JSON Generation")
    try:
        result_json = generate_json(
            root_dir=target_path,
            include_patterns=["*.py"],
            exclude_patterns=[],
            gitignore_patterns=[],
            include_ranges=True,
            include_hashes=True,  # Enable hashes
            goals=["Test Phase 1 integration"],
            exclude_dirs=[]
        )
        
        assert result_json is not None
        assert "metadata" in result_json
        assert "modules" in result_json
        
        print(f"✅ Generation successful: {len(result_json['modules'])} modules found")
        print(f"✅ Schema version: {result_json['metadata'].get('schema_version', 'unknown')}")
        
        # Test Phase 1 features
        features_found = []
        
        # Check for hashes
        hash_count = 0
        for module in result_json["modules"]:
            if module.get("hash"):
                hash_count += 1
            for func in module.get("functions", []):
                if func.get("hash"):
                    hash_count += 1
            for cls in module.get("classes", []):
                if cls.get("hash"):
                    hash_count += 1
                for method in cls.get("methods", []):
                    if method.get("hash"):
                        hash_count += 1
        
        if hash_count > 0:
            features_found.append(f"Hashes: {hash_count}")
        
        # Check for UIDs
        uid_count = 0
        for module in result_json["modules"]:
            if module.get("uid"):
                uid_count += 1
            for func in module.get("functions", []):
                if func.get("uid"):
                    uid_count += 1
            for cls in module.get("classes", []):
                if cls.get("uid"):
                    uid_count += 1
                for method in cls.get("methods", []):
                    if method.get("uid"):
                        uid_count += 1
        
        if uid_count > 0:
            features_found.append(f"UIDs: {uid_count}")
        
        # Check for callgraph
        callgraph_edges = 0
        for module in result_json["modules"]:
            if "callgraph" in module:
                for caller, callees in module["callgraph"].items():
                    callgraph_edges += len(callees)
        
        if callgraph_edges > 0:
            features_found.append(f"Call edges: {callgraph_edges}")
        
        # Check for summaries
        summary_count = 0
        for module in result_json["modules"]:
            if module.get("summary"):
                summary_count += 1
            for func in module.get("functions", []):
                if func.get("summary"):
                    summary_count += 1
            for cls in module.get("classes", []):
                if cls.get("summary"):
                    summary_count += 1
                for method in cls.get("methods", []):
                    if method.get("summary"):
                        summary_count += 1
        
        if summary_count > 0:
            features_found.append(f"Summaries: {summary_count}")
        
        print(f"✅ Phase 1 features found: {', '.join(features_found)}")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Integration test failed: {e}"

def test_phase1_core_functions():
    """Test core Phase 1 functions directly."""
    print("\n🔧 Testing Core Phase 1 Functions")
    
    try:
        # Test UID generation
        test_uid = generate_uid(UIDType.FUNCTION, "test_module.py", "test_function")
        test_components = generate_uid_components(UIDType.FUNCTION, "test_module.py", "test_function")
        print(f"✅ UID generation: {test_uid}")
        print(f"✅ UID components: {test_components}")
        
        # Test hashing
        test_content = "def hello(): return 'world'"
        content_hash = hash_content(test_content)
        print(f"✅ Content hash: {content_hash[:16]}...")
        
        # Test summary system
        summary_system = get_summary_system()
        print(f"✅ Summary system: {type(summary_system).__name__}")
        
    except Exception as e:
        print(f"❌ Core functions test failed: {e}")
        assert False, f"Core functions test failed: {e}"

def main():
    """Run all integration tests."""
    print("🧪 LLMStruct Phase 1 Integration Test Suite")
    print("=" * 80)
    
    success = True
    
    # Test 1: Basic integration
    if not test_phase1_basic_integration():
        success = False
    
    # Test 2: Core functions
    if not test_phase1_core_functions():
        success = False
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 All integration tests PASSED!")
        return 0
    else:
        print("❌ Some integration tests FAILED!")
        return 1

if __name__ == "__main__":
    exit(main())