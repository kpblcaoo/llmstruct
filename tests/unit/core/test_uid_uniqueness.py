"""
UID Uniqueness Tests for Phase 1.5

Tests to detect and prevent UID collisions in the UID system.
Critical for maintaining entity uniqueness across the codebase.
"""

import pytest
import json
from pathlib import Path
from collections import defaultdict, Counter

from llmstruct.core.uid_generator import generate_uid, generate_uid_components, UIDType
from llmstruct.generators.json_generator import generate_json


class TestUIDUniqueness:
    """Test UID system for uniqueness and collision detection."""
    
    @pytest.fixture
    def phase1_fixture_data(self):
        """Load Phase 1 fixture data for testing."""
        fixture_path = Path("tests/fixtures/phase1/struct_v2.1_final.json")
        with open(fixture_path, "r") as f:
            return json.load(f)
    
    def test_uid_components_uniqueness_in_fixture(self, phase1_fixture_data):
        """Test that all uid_components in fixture are unique."""
        uid_components_map = defaultdict(list)
        collision_count = 0
        
        # Collect all uid_components
        for module in phase1_fixture_data["modules"]:
            components = tuple(module.get("uid_components", []))
            uid_components_map[components].append({
                "type": "module", 
                "name": module.get("module_id", "unknown"),
                "path": module.get("file_path", "unknown")
            })
            
            for func in module.get("functions", []):
                components = tuple(func.get("uid_components", []))
                uid_components_map[components].append({
                    "type": "function",
                    "name": func.get("name", "unknown"),
                    "module": module.get("module_id", "unknown")
                })
                
            for cls in module.get("classes", []):
                components = tuple(cls.get("uid_components", []))
                uid_components_map[components].append({
                    "type": "class",
                    "name": cls.get("name", "unknown"),
                    "module": module.get("module_id", "unknown")
                })
                
                for method in cls.get("methods", []):
                    components = tuple(method.get("uid_components", []))
                    uid_components_map[components].append({
                        "type": "method",
                        "name": method.get("name", "unknown"),
                        "class": cls.get("name", "unknown"),
                        "module": module.get("module_id", "unknown")
                    })
        
        # Find collisions
        collisions = {}
        for components, entities in uid_components_map.items():
            if len(entities) > 1:
                collisions[components] = entities
                collision_count += len(entities) - 1  # Count extra entities as collisions
        
        # Report collisions in detail
        if collisions:
            collision_report = []
            for components, entities in collisions.items():
                collision_report.append(f"Components {components}:")
                for entity in entities:
                    if entity["type"] == "method":
                        collision_report.append(f"  - {entity['type']}: {entity['module']}.{entity['class']}.{entity['name']}")
                    else:
                        collision_report.append(f"  - {entity['type']}: {entity['module']}.{entity['name']}")
            
            pytest.fail(f"Found {collision_count} UID collisions across {len(collisions)} component groups:\n" + 
                       "\n".join(collision_report))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
