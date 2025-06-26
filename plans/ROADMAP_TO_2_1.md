# LLMStruct Roadmap to v2.1

**Current Status:** Phase 1.5 ✅ Complete | Phase 1.6 🚧 Planning  
**Target v2.1:** Q1 2025  
**Last Updated:** 2024-12-26

## 📊 Current State Assessment

### ✅ **Phase 1.5 - COMPLETED**
- UID collision system fixed (0/103 collisions)
- Tag inference system implemented 
- Comprehensive test coverage (40/40 tests passing)
- Architecture compliance (modules ≤400 LOC, ≤5 classes)
- Unused CLI commands cleaned up (dogfood, review, copilot)

### 🎯 **Critical Decision Point: struct/ Migration**

**Current Structure:**
```
/
├── struct_src.json (1.3MB) - Main structure
├── struct_src_index.json (348KB) - Index
└── .llmstruct_cache/ - Various caches
```

**Target Structure:**
```
struct/
├── struct.json              # Main aggregate
├── index.json               # Module summary (tags, hash, summary)
├── modules/                 # Per-module detailed JSON
│   ├── core.exporter.json
│   ├── parsers.python.json
│   └── ...
├── callgraph.json          # Global call graph
├── schema.json             # Current format schema
├── coverage.json           # Test coverage (Phase 2)
├── metrics.json            # Complexity metrics (Phase 2)
└── toc.json               # Viewer navigation (optional)
```

## 🗺️ Phase Breakdown to v2.1

### **Phase 1.6: struct/ Migration & Foundation** 
**Duration:** 1-2 weeks  
**Priority:** P0 (Foundation for all future work)

#### **Epic 1.6.1: struct/ Directory Migration**
- [ ] Create struct/ directory structure
- [ ] Migrate current JSON files to new layout
- [ ] Implement modular JSON generation (modules/*.json)
- [ ] Update CLI to read/write from struct/
- [ ] Add struct/schema.json with current v2.1 format
- [ ] Backward compatibility layer for existing tools

#### **Epic 1.6.2: Index System Enhancement**
- [ ] Rich index.json with uid, module_path, tags, hash, summary
- [ ] Fast lookup by uid/tags/module patterns
- [ ] Module dependency tracking in index
- [ ] Performance optimization for large codebases

#### **Epic 1.6.3: API & CLI Updates** 
- [ ] Update parse command to generate struct/
- [ ] Add validate command for struct/ integrity
- [ ] API endpoints for struct/ navigation
- [ ] Migration tool: legacy → struct/

**Success Criteria:**
- [ ] All existing functionality works with struct/
- [ ] Generation time ≤ 2x current baseline
- [ ] Index lookup performance < 100ms for 1000+ modules
- [ ] 100% backward compatibility

---

### **Phase 1.7: LLM Integration & MCP Foundation**
**Duration:** 2-3 weeks  
**Priority:** P1 (Enables advanced LLM workflows)

#### **Epic 1.7.1: MCP Tool Development**
- [ ] MCP server for struct/ navigation
- [ ] Query interface: fetch by uid/tags/module
- [ ] Markdown formatter for LLM consumption
- [ ] Context-aware snippet extraction

#### **Epic 1.7.2: Smart Context Assembly**
- [ ] Relevance scoring for modules/functions
- [ ] Dynamic context building by query
- [ ] Token-aware context sizing
- [ ] Cross-reference resolution (calls, dependencies)

#### **Epic 1.7.3: Markdown Report Generation**
- [ ] Template system for different report types
- [ ] Code overview cards for LLM
- [ ] Architecture summary generation
- [ ] Coverage/quality reports in markdown

**MCP Tool Examples:**
```typescript
// Fetch relevant modules by query
mcp.fetch_modules({
  query: "authentication and security",
  max_modules: 5,
  include_calls: true
})

// Generate focused markdown
mcp.generate_markdown({
  uids: ["auth.login", "auth.validate"],
  format: "code_review",
  include_tests: true
})
```

**Success Criteria:**
- [ ] MCP server handles 10+ concurrent queries
- [ ] Markdown generation < 2s for 50-module context
- [ ] LLM context reduction: 50-80% token savings
- [ ] Integration with Claude/GPT/Cursor

---

### **Phase 2.0: Advanced Analysis & Metrics**
**Duration:** 3-4 weeks  
**Priority:** P1 (Core v2.1 features)

#### **Epic 2.0.1: Code Quality Metrics**
- [ ] Cyclomatic complexity analysis
- [ ] Test coverage integration
- [ ] Code smell detection
- [ ] Technical debt scoring

#### **Epic 2.0.2: Advanced Call Graph**
- [ ] Cross-language call tracking
- [ ] Dynamic vs static call analysis  
- [ ] Call graph visualization data
- [ ] Performance hotspot identification

#### **Epic 2.0.3: Semantic Analysis**
- [ ] Intent classification for functions
- [ ] API surface analysis
- [ ] Breaking change detection
- [ ] Refactoring suggestions

**New struct/ Files:**
- `struct/metrics.json` - Quality metrics per module
- `struct/coverage.json` - Test coverage data
- `struct/analysis.json` - Semantic analysis results
- `struct/hotspots.json` - Performance/complexity hotspots

---

### **Phase 2.1: Viewer & Integration Polish**
**Duration:** 2-3 weeks  
**Priority:** P2 (User experience)

#### **Epic 2.1.1: Web Viewer Enhancement**
- [ ] struct/ native support in viewer
- [ ] Interactive call graph visualization
- [ ] Metrics dashboard
- [ ] Real-time struct/ updates

#### **Epic 2.1.2: IDE Integrations**
- [ ] VSCode extension updates for struct/
- [ ] Cursor integration improvements
- [ ] JetBrains plugin (basic)
- [ ] GitHub Actions integration

#### **Epic 2.1.3: Documentation & Examples**
- [ ] Complete API documentation
- [ ] MCP integration examples
- [ ] Best practices guide
- [ ] Migration documentation

---

## 🚀 Implementation Strategy

### **Phase 1.6 (Next 2 weeks) - IMMEDIATE**

**Week 1: struct/ Foundation**
1. Create struct/ directory structure
2. Implement modular JSON generation
3. Create migration script from current format
4. Update core CLI commands

**Week 2: Index & Validation**
1. Rich index.json implementation
2. struct/schema.json generation
3. Validation system
4. Performance optimization

### **Parallel Development Tracks**

**Track A: Core Infrastructure** (Phase 1.6-1.7)
- struct/ migration and optimization
- Index system and fast lookup
- Schema validation and evolution

**Track B: LLM Integration** (Phase 1.7-2.0)  
- MCP server development
- Markdown generation system
- Context assembly algorithms

**Track C: Analysis Engine** (Phase 2.0-2.1)
- Metrics collection and analysis
- Advanced call graph features
- Semantic analysis tools

## 🎯 Success Metrics by Phase

| Phase | Metric | Target |
|-------|--------|--------|
| 1.6 | struct/ migration | 100% feature parity |
| 1.6 | Performance | ≤ 2x current generation time |
| 1.7 | MCP queries | < 500ms average response |
| 1.7 | Token reduction | 50-80% for LLM context |
| 2.0 | Metrics coverage | 90%+ functions analyzed |
| 2.1 | Integration | 3+ IDE/tool integrations |

## 🔧 Technical Decisions

### **struct/ Design Principles**
1. **Modularity:** Each module = separate JSON file
2. **Index-first:** Fast lookup without loading full data
3. **Schema-driven:** Strict validation and evolution
4. **LLM-friendly:** Easy context assembly and markdown generation
5. **Backward compatible:** Existing tools continue working

### **MCP Integration Strategy**
1. **Query-driven:** LLM requests specific data, not full dumps
2. **Context-aware:** Smart relevance scoring and filtering
3. **Format-flexible:** JSON for tools, Markdown for LLM
4. **Performance-first:** Sub-second response times

### **Quality Gates**
- All tests pass before phase completion
- Performance benchmarks maintained
- Documentation updated with each phase
- Backward compatibility preserved

---

**Next Action:** Begin Phase 1.6 struct/ migration planning and implementation. 