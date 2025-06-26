"""
Hash Utilities for LLMStruct

Provides consistent hashing for files, functions, and code entities
to support incremental builds and change detection.
"""

import hashlib
from typing import Optional, Dict, Any
from pathlib import Path


def hash_content(content: str, algorithm: str = "sha256") -> str:
    """
    Generate hash for string content.
    
    Args:
        content: String content to hash
        algorithm: Hash algorithm (sha256, md5, sha1)
        
    Returns:
        Hex digest of the hash
    """
    if not content:
        return ""
    
    hasher = hashlib.new(algorithm)
    hasher.update(content.encode('utf-8'))
    return hasher.hexdigest()


def hash_file(file_path: str, algorithm: str = "sha256") -> Optional[str]:
    """
    Generate hash for file content.
    
    Args:
        file_path: Path to file
        algorithm: Hash algorithm
        
    Returns:
        Hex digest of file hash, None if file doesn't exist
    """
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        return None
    
    try:
        with open(path, 'rb') as f:
            hasher = hashlib.new(algorithm)
            # Read in chunks to handle large files
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except (IOError, OSError):
        return None


def hash_source(content: str, algorithm: str = "sha256") -> str:
    """
    Generate hash for source code content.
    
    Normalizes whitespace and removes comments for consistent hashing.
    
    Args:
        content: Source code content
        algorithm: Hash algorithm
        
    Returns:
        Hex digest of normalized source hash
    """
    if not content:
        return ""
    
    # Normalize content for consistent hashing
    normalized = normalize_source_for_hashing(content)
    return hash_content(normalized, algorithm)


def normalize_source_for_hashing(content: str) -> str:
    """
    Normalize source code for consistent hashing.
    
    - Removes leading/trailing whitespace
    - Normalizes line endings
    - Removes empty lines
    - Strips inline comments (# comments)
    
    Args:
        content: Source code content
        
    Returns:
        Normalized content
    """
    if not content:
        return ""
    
    lines = []
    for line in content.splitlines():
        # Strip whitespace
        stripped = line.strip()
        
        # Skip empty lines
        if not stripped:
            continue
            
        # Remove inline comments (simple approach)
        if '#' in stripped:
            # Find comment start (not in strings)
            in_string = False
            quote_char = None
            for i, char in enumerate(stripped):
                if char in ('"', "'") and (i == 0 or stripped[i-1] != '\\'):
                    if not in_string:
                        in_string = True
                        quote_char = char
                    elif char == quote_char:
                        in_string = False
                        quote_char = None
                elif char == '#' and not in_string:
                    stripped = stripped[:i].rstrip()
                    break
        
        if stripped:
            lines.append(stripped)
    
    return '\n'.join(lines)


def hash_entity(entity: Dict[str, Any], algorithm: str = "sha256") -> str:
    """
    Generate hash for a code entity (function, class, etc.).
    
    Uses entity content and metadata for hashing.
    
    Args:
        entity: Entity dictionary with 'content', 'name', 'type' keys
        algorithm: Hash algorithm
        
    Returns:
        Hex digest of entity hash
    """
    if not entity:
        return ""
    
    # Create content for hashing
    hash_parts = []
    
    # Add entity type and name
    if 'type' in entity:
        hash_parts.append(f"type:{entity['type']}")
    if 'name' in entity:
        hash_parts.append(f"name:{entity['name']}")
    
    # Add normalized source content
    if 'content' in entity and entity['content']:
        normalized_content = normalize_source_for_hashing(entity['content'])
        hash_parts.append(f"content:{normalized_content}")
    
    # Add parameters for functions
    if 'parameters' in entity and entity['parameters']:
        param_str = ','.join(p.get('name', '') for p in entity['parameters'])
        hash_parts.append(f"params:{param_str}")
    
    # Add return type if available
    if 'return_type' in entity and entity['return_type']:
        hash_parts.append(f"return:{entity['return_type']}")
    
    # Combine all parts
    combined_content = '\n'.join(hash_parts)
    return hash_content(combined_content, algorithm)


def create_file_hash_map(file_paths: list, algorithm: str = "sha256") -> Dict[str, Optional[str]]:
    """
    Create hash map for multiple files.
    
    Args:
        file_paths: List of file paths
        algorithm: Hash algorithm
        
    Returns:
        Dictionary mapping file paths to their hashes
    """
    hash_map = {}
    for file_path in file_paths:
        hash_map[file_path] = hash_file(file_path, algorithm)
    return hash_map


def has_file_changed(file_path: str, previous_hash: str, algorithm: str = "sha256") -> bool:
    """
    Check if file has changed since previous hash.
    
    Args:
        file_path: Path to file
        previous_hash: Previously computed hash
        algorithm: Hash algorithm
        
    Returns:
        True if file has changed, False otherwise
    """
    current_hash = hash_file(file_path, algorithm)
    return current_hash != previous_hash


def create_incremental_hash_database(base_path: str, 
                                    file_patterns: list = None,
                                    algorithm: str = "sha256") -> Dict[str, str]:
    """
    Create hash database for incremental builds.
    
    Args:
        base_path: Base directory to scan
        file_patterns: List of glob patterns for files to include
        algorithm: Hash algorithm
        
    Returns:
        Dictionary mapping file paths to hashes
    """
    if file_patterns is None:
        file_patterns = ["**/*.py", "**/*.go", "**/*.js", "**/*.ts"]
    
    base_path = Path(base_path)
    hash_db = {}
    
    for pattern in file_patterns:
        for file_path in base_path.glob(pattern):
            if file_path.is_file():
                rel_path = str(file_path.relative_to(base_path))
                file_hash = hash_file(str(file_path), algorithm)
                if file_hash:
                    hash_db[rel_path] = file_hash
    
    return hash_db


def compare_hash_databases(old_db: Dict[str, str], 
                          new_db: Dict[str, str]) -> Dict[str, list]:
    """
    Compare two hash databases to find changes.
    
    Args:
        old_db: Previous hash database
        new_db: Current hash database
        
    Returns:
        Dictionary with 'added', 'modified', 'deleted' file lists
    """
    old_files = set(old_db.keys())
    new_files = set(new_db.keys())
    
    added = list(new_files - old_files)
    deleted = list(old_files - new_files)
    
    modified = []
    for file_path in old_files & new_files:
        if old_db[file_path] != new_db[file_path]:
            modified.append(file_path)
    
    return {
        'added': sorted(added),
        'modified': sorted(modified),
        'deleted': sorted(deleted)
    }


# Convenience functions for common use cases

def quick_file_hash(file_path: str) -> Optional[str]:
    """Quick SHA-256 hash of a file"""
    return hash_file(file_path, "sha256")


def quick_content_hash(content: str) -> str:
    """Quick SHA-256 hash of content"""
    return hash_content(content, "sha256")


def quick_source_hash(source_code: str) -> str:
    """Quick SHA-256 hash of normalized source code"""
    return hash_source(source_code, "sha256") 