# Workspace Mode System - Design Clarifications

**Date:** 2025-05-27  
**Session:** [discuss][meta]  
**Status:** Design Questions - Awaiting Decisions  

## Current Situation Summary

### Branch Status
- **Current Branch:** `feature/llm-context-capability-testing`
- **Intended Target:** `testing/v0.2.0` 
- **Actual PR Target:** `main` (incorrect)
- **Issue:** Branch has conflicts that need resolution
- **Impact:** Blocking workspace state implementation until resolved

### Outstanding Design Questions

## Question 1: Permission Granularity

**Option A: File-Level Permissions**
```json
"permissions": ["write:/tmp/test.py", "read:/src/cache.py"]
```
- **Pros:** Very specific, maximum safety
- **Cons:** Verbose, hard to predict all needed files

**Option B: Capability-Level Permissions** 
```json
"permissions": ["file_writes", "code_execution", "network_access"]
```
- **Pros:** Simpler, more flexible
- **Cons:** Less granular control

**Option C: Hybrid System**
```json
"permissions": {
  "capabilities": ["file_writes"],
  "specific_files": ["/tmp/test.py"],
  "restricted_paths": ["/src/core/*"]
}
```

**Recommendation Needed:** Which approach do you prefer?

## Question 2: Override Authority

**Option A: AI Auto-Grant for "Safe" Operations**
```json
"auto_grant_permissions": [
  "tmp_file_writes",
  "read_operations", 
  "documentation_writes"
]
```
- **Pros:** Smoother workflow, less interruption
- **Cons:** Risk of security gaps

**Option B: Human Approval Required**
- All permission requests require explicit human approval
- **Pros:** Maximum control and security
- **Cons:** Potential workflow interruptions

**Option C: Context-Dependent**
- Emergency situations: AI can auto-grant
- Normal workflow: Human approval required
- Safe operations: AI auto-grant with logging

**Recommendation Needed:** What level of AI autonomy is acceptable?

## Question 3: Mode Strictness Strategy

**Option A: Start Strict, Add Flexibility**
- Begin with restrictive modes
- Gradually add permissions as needed
- Learn safe patterns over time

**Option B: Start Flexible, Add Restrictions**
- Begin with minimal restrictions
- Add safety boundaries based on issues encountered
- Faster initial implementation

**Recommendation Needed:** Which development approach?

## Question 4: Branch Strategy Resolution

### Current Conflict Resolution Options:

**Option A: Fix Current Branch**
```bash
# Resolve conflicts in current branch
git checkout feature/llm-context-capability-testing
# Resolve conflicts manually
# Continue workspace state work on same branch
```

**Option B: New Clean Branch from testing/v0.2.0**
```bash
git checkout testing/v0.2.0
git pull origin testing/v0.2.0
git checkout -b feature/workspace-state-system
# Start fresh workspace state implementation
```

**Option C: Merge/Rebase Strategy**
```bash
# First resolve current branch conflicts
# Then create new branch for workspace state
# Keep work separated by feature
```

**Current Preference:** Option B (new clean branch) for separation of concerns

## Immediate Decision Points

### Required Before Implementation:
1. **Branch Strategy** - How to handle current conflicts?
2. **Permission Model** - Which granularity approach?
3. **AI Authority Level** - How much autonomy for AI?
4. **Mode Strictness** - Start strict or flexible?

### Implementation Readiness:
- ✅ Core design documented
- ✅ Session plan created  
- ✅ Task breakdown complete
- ❌ Branch conflicts unresolved
- ❌ Design questions pending

## Recommended Next Steps

### Immediate (Today):
1. **Decide branch strategy** - resolve conflicts or new branch?
2. **Answer design questions** above
3. **Prepare clean workspace** for implementation

### Short Term (This Session):
1. Implement basic workspace_state.json structure
2. Create WorkspaceStateManager class
3. Add fundamental CLI integration
4. Test mode switching basics

### Medium Term (Next Session):
1. Implement permission system
2. Add AI context awareness
3. Create mode restriction enforcement
4. Comprehensive testing

## Notes for Decision Making

### Branch Strategy Considerations:
- **Current branch conflicts** may be complex to resolve
- **New branch** provides clean slate but requires re-establishing context
- **Feature separation** makes PR management cleaner

### Permission System Considerations:
- **Capability-level** seems most practical for AI workflow
- **Hybrid approach** offers flexibility with safety
- **Auto-grant for safe operations** reduces friction

### Mode Strictness Considerations:
- **Start strict** forces careful design of permission system
- **Add flexibility gradually** ensures safety boundaries are respected
- **Learn patterns** from real usage to optimize permissions

---

**Status:** Awaiting decisions on design questions before proceeding with SES-004A implementation.

**Decision Required From:** @kpblcaoo  
**Dependencies:** Branch conflict resolution, design question answers  
**Next Session:** SES-004A (pending decisions)
