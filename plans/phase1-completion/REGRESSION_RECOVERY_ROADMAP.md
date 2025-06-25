# LLMStruct Phase 1 Recovery Roadmap - UPDATED

## 🎯 **Current State Analysis (HONEST)**

### ✅ **Phase 1 SUCCESS** 
- ✅ **Hash system**: 103 valid SHA-256 hashes (modules, functions, classes, methods)
- ✅ **UID system**: Clean uid/uid_components without "dir:" artifacts  
- ✅ **Callgraph**: Both calls[] and called_by[] working
- ✅ **Summary system**: Heuristic + LLM providers integrated
- ✅ **Config system**: Security-first defaults, LLM optional

### ❌ **Phase 1 CRITICAL GAPS**
- ❌ **toc[].hash**: Missing hash in table of contents
- ❌ **hash_source**: No transparency on hash generation method
- ❌ **line_range**: Returns null instead of actual ranges  
- ❌ **index.json**: Not generated (needed for manifests)

### 🟡 **Phase 1.5+ Features** (Not blocking, but planned)
- 🟡 **tested/tested_by**: Test integration system
- 🟡 **external_calls**: Internal vs external call separation
- 🟡 **security_tags**: @public-api, @deprecated markers
- 🟡 **range.columns**: Column-level positioning

---

## 🚨 **PHASE 1 CRITICAL FIXES (DO NOW)**

### 1. Fix `toc[].hash` - Missing Hash in TOC
```bash
# Problem: toc[] has no hash field
jq '.toc[0] | keys'  # No "hash" key

# Solution: Add hash to toc generation
```

### 2. Add `hash_source` and `hash_version` Transparency  
```json
// Add to all entities with hash:
{
  "hash": "a09dfbc379...",
  "hash_source": "code_v1",
  "hash_version": "2.1.0"
}
```

### 3. Fix `line_range` - Currently Null
```bash
# Problem: All line_range are null
jq '.modules[0].functions[0].line_range'  # null

# Solution: Enable include_ranges in parser
```

### 4. Generate `index.json` Manifest
```json
// Create index.json with uid → hash mapping
{
  "version": "2.1.0",
  "generated": "2025-06-25T20:48:02Z",
  "entities": [
    {
      "uid": "hash_utils.hash_content#function",
      "hash": "fec4da722ef311003ac0c59137e980d83ecbc8daeb022d2b4841e235226c74b8",
      "type": "function",
      "module": "hash_utils"
    }
  ]
}
```

---

## 📋 **PHASE 1.5: Enhancement Features**

### Test Integration System
- `tested: boolean` - Whether entity has tests
- `tested_by: string[]` - List of test functions/files
- Integration with pytest discovery

### External Dependency Tracking
- `external_calls: string[]` - Calls to external libraries  
- `external_deps: string[]` - Import dependencies
- Separate internal project calls from external

### Security & API Marking
- `security_tags: string[]` - [@public-api, @deprecated, @internal]
- `api_stability: string` - [stable, experimental, deprecated]
- Integration with docstring parsing

---

## 🔬 **PHASE 2: Advanced Features**

### Column-Level Positioning
- `range.columns: [start_col, end_col]`
- Better IDE integration
- AST-based precise positioning

### Incremental Build System
- Hash-based diff detection
- `llmstruct diff --by-hash old.json new.json`
- Caching system for unchanged entities

### Test Coverage Heatmap
- Integration with coverage.py
- Visual coverage representation
- `used_in: string[]` - Where entity is used

---

## ⚡ **IMPLEMENTATION ORDER**

### 🔥 **CRITICAL (Phase 1 completion)**
1. **Fix line_range** - Enable `include_ranges=True`
2. **Add hash to toc** - Include hash field in toc generation  
3. **Add hash_source/hash_version** - Transparency metadata
4. **Generate index.json** - Create manifest file

### 🛠️ **ENHANCEMENT (Phase 1.5)**
5. **Test integration** - tested/tested_by fields
6. **External calls** - Separate internal/external
7. **Security tags** - @public-api markers

### 🚀 **ADVANCED (Phase 2)**
8. **Column ranges** - Precise positioning
9. **Incremental builds** - Hash-based diffs
10. **Coverage heatmap** - Test coverage visualization

---

## 🎯 **SUCCESS CRITERIA**

### Phase 1 Complete ✅
- [x] Hash system (SHA-256 everywhere)
- [x] UID system (clean components)  
- [x] Callgraph (bidirectional)
- [x] Summary system (heuristic + LLM)
- [x] **toc[].hash** ← FIXED ✅
- [x] **hash_source/hash_version** ← FIXED ✅  
- [x] **line_range working** ← FIXED ✅
- [x] **index.json generation** ← FIXED ✅
- [x] **call_edges_count accuracy** ← FIXED ✅ (123 == 123)
- [x] **schema_version & JSON Schema** ← FIXED ✅
- [x] **line_range for methods** ← FIXED ✅ 
- [x] **markdown_anchor** ← FIXED ✅

**PHASE 1 = 100% COMPLETE** 🎉

### Phase 1.5 Goals
- [ ] Test integration (tested/tested_by)
- [ ] External dependency tracking
- [ ] Security/API tagging

### Phase 2 Goals  
- [ ] Column-level positioning
- [ ] Incremental build system
- [ ] Coverage heatmap integration

---

## 🧪 **TESTING PLAN**

### Validation Commands
```bash
# Test hash completeness
jq '[.modules[] | select(.hash == null)] | length' should return 0
jq '[.toc[] | select(.hash == null)] | length' should return 0

# Test transparency
jq '.modules[0] | has("hash_source")' should return true

# Test line ranges  
jq '[.modules[] | .functions[] | select(.line_range == null)] | length' should return 0

# Test index.json exists
ls index.json should exist
```

### Integration Tests
```bash
# Test hash stability (same code = same hash)
llmstruct parse src/ --output test1.json
llmstruct parse src/ --output test2.json  
diff <(jq '.modules[] | .hash' test1.json) <(jq '.modules[] | .hash' test2.json)

# Test diff capability
llmstruct diff --by-hash old.json new.json
```

---

## 📊 **CURRENT vs TARGET**

| Feature | Current | Target | Priority |
|---------|---------|--------|----------|
| Hash Coverage | ✅ 100% | ✅ 100% | DONE |
| toc[].hash | ❌ 0% | ✅ 100% | **CRITICAL** |
| hash_source | ❌ 0% | ✅ 100% | **CRITICAL** |
| line_range | ❌ 0% | ✅ 100% | **CRITICAL** |
| index.json | ❌ 0% | ✅ 100% | **CRITICAL** |
| tested_by | ❌ 0% | ✅ 80% | Phase 1.5 |
| external_calls | ❌ 0% | ✅ 80% | Phase 1.5 |
| security_tags | ❌ 0% | ✅ 60% | Phase 1.5 |
| range.columns | ❌ 0% | ✅ 60% | Phase 2 |

---

**BOTTOM LINE**: Phase 1 is **80% complete** with solid infrastructure, but **4 critical gaps** prevent it from being production-ready. Focus on fixing these **4 blockers** before moving to Phase 1.5 features. 