# Workspace State & Mode System Design

**Date:** 2024-12-19  
**Session:** [discuss][meta]  
**Status:** ⏸️ BLOCKED - Awaiting User Decisions  
**Priority:** High  

---

**🚨 IMPLEMENTATION BLOCKED - DECISIONS REQUIRED**

### Critical Issues Requiring Decisions:

1. **Branch Targeting Issue (PR #16):**
   - Current PR targets `main` instead of `testing/v0.2.0`
   - Need decision on branch strategy before proceeding

2. **Design Decisions Required:**
   - Permission granularity level (file vs capability vs hybrid)
   - AI override authority (conservative vs balanced vs permissive)
   - Mode strictness strategy (strict-first vs flexible-first)
   - Emergency override protocols
   - Mode combination rules

📋 **See:** `docs/internal/ses-004-implementation-decisions.md` for complete decision matrix

### Current State:
- ✅ Design planning complete
- ✅ Task breakdown structured (TSK-165 to TSK-168)
- ⏸️ Implementation sessions blocked pending decisions
- 🔄 Awaiting user input on critical design choices

**Next Actions After Decisions:**
1. Resolve PR #16 branch targeting
2. Begin SES-004A workspace state implementation
3. Create WorkspaceStateManager class
4. Add CLI integration
5. Test basic functionality

**Status:** Implementation-ready but blocked on user decisions

## Vision

Design a multi-dimensional session control system that goes beyond simple session tracking to provide contextual work modes with intelligent boundaries, safety features, and enhanced AI collaboration patterns.

## Core Concepts

### 1. Workspace State Controller
Replace simple `session.json` with `workspace_state.json` - a master control file that manages:
- Current session tracking
- Active work modes (with combinations)
- Context level management
- Mode transition history
- Workspace focus areas

### 2. Work Modes Framework
Multi-dimensional mode system allowing combinations:

**Core Modes:**
- `[discuss]` - Planning, ideation, no file changes
- `[meta]` - Working on LLM interaction mechanisms, tooling  
- `[llmstruct]` - Core project development
- `[code]` - Pure implementation work
- `[docs]` - Documentation focused
- `[plan]` - Strategic planning, roadmaps
- `[session]` - Session management work
- `[debug]` - Troubleshooting, fixing issues
- `[test]` - Testing, validation
- `[refactor]` - Code restructuring

**Mode Combinations:**
- `[discuss][meta]` - Planning LLM interaction improvements (like this note)
- `[plan][llmstruct]` - Strategic project planning
- `[code][debug]` - Implementation + troubleshooting
- `[docs][meta]` - Documenting LLM interaction patterns

### 3. AI Context Awareness & Permission System
**CRITICAL DESIGN REQUIREMENT**: The mode system must not create workflow handicaps.

**AI Mode Awareness Protocol:**
- AI receives current mode restrictions at session start
- AI can recognize when restrictions block necessary work
- AI can request permission escalation with justification
- Emergency override capabilities for critical work

**Dynamic Permission System:**
```json
{
  "permission_requests": [
    {
      "timestamp": "2025-05-27T12:34:56",
      "requested_by": "ai_agent", 
      "reason": "Need to create test file to verify hypothesis",
      "permissions": ["write_to_tmp"],
      "status": "pending"
    }
  ],
  "emergency_overrides": {
    "enabled": true,
    "log_all": true,
    "auto_grant_safe": ["tmp_writes", "read_operations"]
  }
}
```

**Permission Escalation Commands:**
- `/mode add [tag]` - Add temporary capability
- `/mode permit [specific_action]` - Grant specific permission
- `/mode emergency [reason]` - Override restrictions with logging

## Planned Tasks

### TSK-165: Workspace State System Core
**Priority:** High  
**Estimated Time:** 2-3 hours  
**Dependencies:** Current session system understanding

**Subtasks:**
1. Design `workspace_state.json` schema
2. Create `WorkspaceStateManager` class
3. Implement mode validation and combination logic
4. Add CLI integration (`/workspace`, `/mode` commands)
5. Update existing session system to use new controller

### TSK-166: Mode System Implementation  
**Priority:** High  
**Estimated Time:** 3-4 hours  
**Dependencies:** TSK-165

**Subtasks:**
1. Define mode behavior rules and restrictions
2. Implement mode safety boundaries (e.g., `[discuss]` prevents file writes)
3. Create mode transition validation
4. Add mode-specific AI behavior tuning
5. Implement mode persistence and inheritance

### TSK-167: Enhanced CLI Integration
**Priority:** Medium  
**Estimated Time:** 2 hours  
**Dependencies:** TSK-165, TSK-166

**Subtasks:**
1. Update CLI commands to respect mode boundaries
2. Add workspace state visualization 
3. Create mode suggestion system
4. Implement mode analytics and reporting

### TSK-168: Documentation & Testing
**Priority:** Medium  
**Estimated Time:** 2 hours  
**Dependencies:** TSK-165, TSK-166, TSK-167

**Subtasks:**
1. Write comprehensive mode system documentation
2. Create usage examples and best practices
3. Implement unit tests for mode system
4. Create integration tests for workspace state management

## Documentation Plan

### DOC-020: Workspace State Architecture
**File:** `docs/architecture/workspace-state-system.md`
**Content:**
- System overview and benefits
- Mode definitions and combinations
- State management lifecycle
- Integration points with existing systems

### DOC-021: Mode System User Guide
**File:** `docs/user-guides/work-modes.md`  
**Content:**
- How to use different modes
- Mode combination strategies
- Best practices for mode transitions
- Troubleshooting mode conflicts

### DOC-022: API Reference
**File:** `docs/api/workspace-state-api.md`
**Content:**
- WorkspaceStateManager class documentation
- CLI command reference
- Mode configuration options
- Integration examples

## Session Planning

### SES-004: Workspace State JSON Implementation
**Type:** [meta][code]  
**Duration:** 2-3 hours  
**Goals:**
1. Create initial `workspace_state.json` structure
2. Implement basic `WorkspaceStateManager` class
3. Add fundamental CLI integration
4. Test basic mode switching functionality

**Deliverables:**
- `data/workspace_state.json` (initial structure)
- `src/llmstruct/workspace_state.py` (core manager)
- Updated CLI commands for workspace state
- Basic integration tests

**Session Tasks:**
- Design and implement workspace state schema
- Create WorkspaceStateManager with mode validation
- Update CLI to support workspace state commands
- Write initial tests and validation

### SES-005: Advanced Mode System Implementation
**Type:** [meta][code][test]  
**Duration:** 3-4 hours  
**Goals:**
1. Implement full mode system with combinations
2. Add mode safety boundaries and restrictions
3. Create mode-specific AI behavior patterns
4. Comprehensive testing of mode transitions

**Deliverables:**
- Complete mode system implementation
- Mode behavior rules and validation
- Enhanced CLI integration
- Comprehensive test suite

## Immediate Next Session: Workspace State JSON

### SES-004A: Initial Workspace State Implementation
**Mode:** [meta][code]  
**Duration:** 1-2 hours  
**Immediate Goals:**

1. **Create workspace_state.json structure:**
   ```json
   {
     "version": "0.1.0",
     "current_session": "SES-004A",
     "active_modes": ["meta", "code"],
     "context_level": "FOCUSED",
     "workspace_focus": "workspace-state-implementation",
     "mode_history": [],
     "session_metadata": {},
     "mode_rules": {}
   }
   ```

2. **Basic WorkspaceStateManager class:**
   - Load/save workspace state
   - Basic mode validation
   - Simple mode switching

3. **CLI integration:**
   - `/workspace status` - show current state
   - `/workspace mode [modes...]` - set active modes
   - `/workspace focus [area]` - set focus area

4. **Integration points:**
   - Update existing session system
   - Ensure compatibility with current workflows

## Benefits & Impact

### For Development:
- **Context Clarity** - Always know what type of work is happening
- **Safety Boundaries** - Prevent accidental changes in planning modes
- **Focus Management** - Maintain scope and reduce context switching
- **Better AI Collaboration** - Mode-specific AI behavior patterns

### For Project Management:
- **Session Analytics** - Track what types of work happen when
- **Workflow Optimization** - Identify efficient mode combinations
- **Quality Control** - Mode-specific validation and restrictions
- **Knowledge Management** - Context-aware documentation and caching

## Implementation Strategy

### Phase 1: Foundation (SES-004A)
- Basic workspace state structure
- Simple mode switching
- CLI integration
- Core validation

### Phase 2: Advanced Features (SES-005)
- Mode combinations and rules
- Safety boundaries
- AI behavior tuning
- Comprehensive testing

### Phase 3: Enhancement (Future)
- Temporal modes (morning-planning, deep-focus)
- Collaboration modes (pair-programming, review)
- Auto-mode detection
- Advanced analytics

## Notes for Implementation

### Technical Considerations:
- Maintain backward compatibility with existing session system
- Use JSON schema validation for workspace state
- Implement atomic state transitions
- Add comprehensive error handling

### User Experience:
- Make mode switching intuitive and fast
- Provide clear feedback on mode restrictions
- Offer mode suggestions based on context
- Maintain session history for analysis

### Integration Points:
- CLI command system
- Session management
- Context orchestration
- Cache system
- Documentation system

---

**Next Actions:**
1. Start SES-004A to implement basic workspace_state.json
2. Create WorkspaceStateManager class
3. Add initial CLI integration
4. Test basic functionality before advancing to full mode system

**Current Status:** Ready to begin implementation in immediate session SES-004A
