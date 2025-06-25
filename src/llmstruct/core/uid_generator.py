"""
Advanced UID Generator System for LLMStruct v2.1

Generates stable, unique identifiers for code entities using FQNAME-based approach.
Fixes duplicate issues in uid_components array.
"""

import hashlib
from enum import Enum
from typing import List, Optional, Dict, Any
from pathlib import Path


class UIDType(Enum):
    """Types of entities that can have UIDs"""
    MODULE = "module"
    CLASS = "class" 
    FUNCTION = "function"
    METHOD = "method"
    PROPERTY = "property"
    VARIABLE = "variable"
    PARAMETER = "parameter"


def normalize_path(path: str) -> str:
    """Normalize file path for consistent UID generation"""
    if not path:
        return ""
    
    # Convert to Path for normalization
    p = Path(path)
    
    # Remove common prefixes
    parts = list(p.parts)
    if parts and parts[0] in ('src', 'lib', 'app'):
        parts = parts[1:]
    
    # Join with dots, remove file extension
    normalized = '.'.join(parts)
    if normalized.endswith('.py'):
        normalized = normalized[:-3]
    elif normalized.endswith('.go'):
        normalized = normalized[:-3]
    
    return normalized


def generate_uid(entity_type: UIDType, 
                module_path: str,
                entity_name: str,
                parent_name: Optional[str] = None) -> str:
    """
    Generate stable UID using FQNAME approach.
    
    Args:
        entity_type: Type of entity
        module_path: Path to module (e.g., 'src/llmstruct/core/uid_generator.py')
        entity_name: Name of entity
        parent_name: Parent entity name (for methods, nested classes)
        
    Returns:
        Stable UID string
    """
    # Normalize module path
    normalized_module = normalize_path(module_path)
    
    # Build FQNAME components
    fqname_parts = []
    
    if normalized_module:
        fqname_parts.append(normalized_module)
    
    if parent_name:
        fqname_parts.append(parent_name)
        
    if entity_name:
        fqname_parts.append(entity_name)
    
    # Create FQNAME
    fqname = '.'.join(fqname_parts)
    
    # Add type prefix for disambiguation
    uid = f"{fqname}#{entity_type.value}"
    
    return uid


def generate_uid_components(entity_type: UIDType,
                           module_path: str, 
                           entity_name: str,
                           parent_name: Optional[str] = None) -> List[str]:
    """
    Generate hierarchical UID components for navigation.
    
    FIXED: Removes duplicates and ensures each level is unique.
    
    Args:
        entity_type: Type of entity
        module_path: Path to module
        entity_name: Name of entity  
        parent_name: Parent entity name
        
    Returns:
        List of hierarchical components without duplicates
    """
    components = []
    
    # Normalize module path
    normalized_module = normalize_path(module_path)
    
    # Add module components (split by dots)
    if normalized_module:
        module_parts = normalized_module.split('.')
        # Filter out empty parts and build incrementally
        current_path = []
        for part in module_parts:
            if part and part.strip():  # Skip empty parts
                current_path.append(part)
                component = '.'.join(current_path)
                if component not in components:  # Avoid duplicates
                    components.append(component)
    
    # Add parent if exists
    if parent_name and parent_name.strip():
        parent_component = f"{normalized_module}.{parent_name}" if normalized_module else parent_name
        if parent_component not in components:
            components.append(parent_component)
    
    # Add current entity
    if entity_name and entity_name.strip():
        if parent_name:
            entity_component = f"{normalized_module}.{parent_name}.{entity_name}" if normalized_module else f"{parent_name}.{entity_name}"
        else:
            entity_component = f"{normalized_module}.{entity_name}" if normalized_module else entity_name
        
        if entity_component not in components:
            components.append(entity_component)
    
    # Remove any remaining duplicates while preserving order
    unique_components = []
    seen = set()
    for component in components:
        if component not in seen:
            unique_components.append(component)
            seen.add(component)
    
    return unique_components


def create_stable_uid(content: str, entity_type: UIDType) -> str:
    """
    Create stable UID based on content hash (fallback method).
    
    Args:
        content: Entity content
        entity_type: Type of entity
        
    Returns:
        Stable hash-based UID
    """
    if not content:
        return f"empty#{entity_type.value}"
    
    # Create hash of content
    content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()[:12]
    
    return f"hash_{content_hash}#{entity_type.value}"


def create_legacy_artifact_id(entity: Dict[str, Any]) -> str:
    """
    Create legacy artifact_id for backward compatibility.
    
    Args:
        entity: Entity dictionary
        
    Returns:
        Legacy artifact ID
    """
    # Extract key components
    entity_type = entity.get('type', 'unknown')
    name = entity.get('name', 'unnamed')
    file_path = entity.get('file_path', '')
    
    # Create consistent string for hashing
    id_components = [
        f"type:{entity_type}",
        f"name:{name}",
        f"file:{normalize_path(file_path)}"
    ]
    
    # Add parent info if available
    if 'parent' in entity:
        id_components.append(f"parent:{entity['parent']}")
    
    # Add parameters for functions
    if 'parameters' in entity and entity['parameters']:
        param_names = [p.get('name', '') for p in entity['parameters']]
        id_components.append(f"params:{','.join(param_names)}")
    
    # Create hash
    combined = '|'.join(id_components)
    artifact_hash = hashlib.md5(combined.encode('utf-8')).hexdigest()
    
    return f"{entity_type}_{artifact_hash[:8]}"


def enhance_entity_with_uid(entity: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhance entity with UID system components.
    
    Args:
        entity: Entity dictionary
        
    Returns:
        Enhanced entity with uid, uid_components, and artifact_id
    """
    # Determine entity type
    entity_type_str = entity.get('type', 'unknown')
    try:
        entity_type = UIDType(entity_type_str)
    except ValueError:
        entity_type = UIDType.FUNCTION  # Default fallback
    
    # Extract information
    name = entity.get('name', 'unnamed')
    file_path = entity.get('file_path', '')
    parent_name = entity.get('parent')
    
    # Generate UID and components
    uid = generate_uid(entity_type, file_path, name, parent_name)
    uid_components = generate_uid_components(entity_type, file_path, name, parent_name)
    
    # Create legacy artifact_id
    artifact_id = create_legacy_artifact_id(entity)
    
    # Add to entity
    enhanced_entity = entity.copy()
    enhanced_entity['uid'] = uid
    enhanced_entity['uid_components'] = uid_components
    enhanced_entity['artifact_id'] = artifact_id
    
    return enhanced_entity


def validate_uid_uniqueness(entities: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Validate UID uniqueness across entities.
    
    Args:
        entities: List of entities with UIDs
        
    Returns:
        Dictionary with 'duplicates' and 'conflicts' lists
    """
    uid_map = {}
    duplicates = []
    conflicts = []
    
    for entity in entities:
        uid = entity.get('uid')
        if not uid:
            continue
            
        if uid in uid_map:
            # Found duplicate
            existing = uid_map[uid]
            duplicate_info = f"UID '{uid}' used by both '{existing.get('name')}' and '{entity.get('name')}'"
            duplicates.append(duplicate_info)
        else:
            uid_map[uid] = entity
    
    return {
        'duplicates': duplicates,
        'conflicts': conflicts
    }


# Convenience functions

def create_module_uid(module_path: str) -> str:
    """Create UID for module"""
    return generate_uid(UIDType.MODULE, module_path, Path(module_path).stem)


def create_function_uid(module_path: str, function_name: str) -> str:
    """Create UID for function"""
    return generate_uid(UIDType.FUNCTION, module_path, function_name)


def create_class_uid(module_path: str, class_name: str) -> str:
    """Create UID for class"""
    return generate_uid(UIDType.CLASS, module_path, class_name)


def create_method_uid(module_path: str, class_name: str, method_name: str) -> str:
    """Create UID for method"""
    return generate_uid(UIDType.METHOD, module_path, method_name, class_name)


# Legacy compatibility wrappers removed in v2.1.0 — new API is the single source of truth. 