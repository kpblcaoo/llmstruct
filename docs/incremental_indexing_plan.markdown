# Incremental Parsing and Indexing Plan for LLMstruct

This document outlines the plan to implement incremental parsing and indexing for the LLMstruct project, ensuring compatibility with the modular structure and alignment with project goals. Incremental parsing and indexing are not yet implemented, as confirmed by the absence of related code in `struct.json` or artifacts.

## 1. Incremental Parsing

**Goal**: Parse only modified files to reduce processing time by ~80–90% for small changes (1–2 files).

### Implementation

- **Cache File**: Store parsed module data in `.llmstruct_cache.json`, keyed by file path, with `hash` and `last_modified` for validation.
- **Logic**:
  - In `src/llmstruct/generators/json_generator.py`, add:
    ```python
    def load_cache(cache_file: str) -> Dict[str, Any]:
        try:
            with open(cache_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_cache(cache: Dict[str, Any], cache_file: str) -> None:
        with open(cache_file, 'w') as f:
            json.dump(cache, f, indent=2)
    
    def build_toc_and_modules(root_dir: str, include_patterns: Optional[List[str]], exclude_patterns: Optional[List[str]], gitignore_patterns: Optional[List[str]], include_ranges: bool, include_hashes: bool, incremental: bool) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        cache = load_cache('.llmstruct_cache.json') if incremental else {}
        modules = []
        toc = []
        files = [f for f in Path(root_dir).rglob('*.py') if not any(f.match(p) for p in (exclude_patterns or []) + (gitignore_patterns or []))]
        
        for file_path in files:
            file_path_str = str(file_path)
            file_hash = hashlib.sha256(open(file_path, 'rb').read()).hexdigest() if include_hashes else None
            stat = os.stat(file_path)
            last_modified = datetime.fromtimestamp(stat.st_mtime).isoformat() + 'Z'
            cached = cache.get(file_path_str)
            if incremental and cached and cached['hash'] == file_hash and cached['last_modified'] == last_modified:
                modules.append(cached['module'])
                toc.append(cached['toc'])
            else:
                module = python_parser.analyze_module(file_path_str, root_dir, include_ranges, include_hashes)
                if module:
                    modules.append(module)
                    toc.append({
                        "module_id": module['module_id'],
                        "path": module['path'],
                        "category": module['category'],
                        "functions": len(module['functions']),
                        "classes": len(module['classes']),
                        "summary": module['module_doc'].split('\n')[0] if module['module_doc'] else ''
                    })
                    cache[file_path_str] = {'module': module, 'toc': toc[-1], 'hash': file_hash, 'last_modified': last_modified}
        if incremental:
            save_cache(cache, '.llmstruct_cache.json')
        return toc, modules
    ```
  - Update `generate_json` to accept `incremental` parameter.
- **CLI Flag**:
  - In `src/llmstruct/cli.py`, add:
    ```python
    parser.add_argument('--incremental', action='store_true', help="Parse only modified files")
    ```
  - Pass `args.incremental` to `generate_json`.
- **gitignore**:
  - Add to `.gitignore`:
    ```
    .llmstruct_cache.json
    ```

### Impact

- **Performance**: ~0.1–0.2 sec for 1 changed file (vs. 1–2 sec full parse).
- **Tokens**: Fewer modules in `struct.json` (~90% savings for small changes).
- **Resources**: ~20–50 KB for cache file.
- **Risks**:
  - Cache invalidation on `.gitignore` or pattern changes.
  - Requires testing (`tests/test_incremental.py`).

## 2. Indexing

**Goal**: Enable fast module/function lookup (~10–20x faster) for LLM queries.

### Implementation

- **Index File**: Use SQLite database `llmstruct_index.db` for keyword-based search.
- **Logic**:
  - Create `src/llmstruct/indexer/indexer.py`:
    ```python
    import sqlite3
    from typing import Dict, Any

    def create_index(struct_data: Dict[str, Any], index_db: str = 'llmstruct_index.db') -> None:
        conn = sqlite3.connect(index_db)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS index (
            id TEXT PRIMARY KEY,
            type TEXT,
            path TEXT,
            keywords TEXT,
            module_id TEXT
        )''')
        for module in struct_data['modules']:
            keywords = f"{module['path']} {module.get('module_doc', '')}"
            cursor.execute('INSERT OR REPLACE INTO index VALUES (?, ?, ?, ?, ?)',
                          (module['module_id'], 'module', module['path'], keywords, module['module_id']))
            for func in module['functions']:
                keywords += f" {func['name']} {func.get('doc', '')}"
                cursor.execute('INSERT OR REPLACE INTO index VALUES (?, ?, ?, ?, ?)',
                              (func['function_id'], 'function', module['path'], keywords, module['module_id']))
            for cls in module['classes']:
                keywords += f" {cls['name']} {cls.get('doc', '')}"
                cursor.execute('INSERT OR REPLACE INTO index VALUES (?, ?, ?, ?, ?)',
                              (cls['class_id'], 'class', module['path'], keywords, module['module_id']))
        conn.commit()
        conn.close()
    ```
  - Call in `src/llmstruct/cli.py`:
    ```python
    from ..indexer.indexer import create_index
    # In main():
    if struct_data:
        create_index(struct_data)
    ```
- **Structure**:
  - Place in `src/llmstruct/indexer/`.
  - Update `src/llmstruct/__init__.py`:
    ```python
    from .cli import main
    from .parsers import python_parser
    from .generators import json_generator
    from .indexer import create_index
    ```
- **gitignore**:
  - Add to `.gitignore`:
    ```
    llmstruct_index.db
    ```

### Impact

- **Performance**: Search ~0.01–0.02 sec (vs. 0.1–0.2 sec for regex).
- **Tokens**: Precise module selection (~80–90% savings).
- **Resources**: ~10–20 MB for index.
- **Risks**:
  - Index synchronization with incremental updates.
  - Requires testing (`tests/test_indexer.py`).

## 3. Timeline

- **May 2025**: Prototype incremental parsing (cache, `--incremental` flag).
- **June 2025**: Test and optimize incremental parsing.
- **July 2025**: Prototype indexing (SQLite, `indexer.py`).
- **August 2025**: Integrate indexing with LLM queries, add tests.
- **September 2025**: Release v0.2.0 with incremental parsing and indexing.

## 4. Integration with Modular Structure

- **Modules**:
  - `indexer.py` in `src/llmstruct/indexer/`.
  - Update `json_generator.py` and `cli.py` minimally.
- **Tests**:
  - Add `tests/test_incremental.py` and `tests/test_indexer.py`.
- **Docs**:
  - Update `docs/llmstruct_format.md` with incremental/indexing notes.
  - Add usage examples in `examples/`.

## 5. Risks and Mitigation

- **Cache Invalidation**: Add CLI flag `--force` to clear cache.
- **Index Sync**: Update index only for changed modules.
- **Testing**: Ensure >80% coverage with `pytest --cov=src`.