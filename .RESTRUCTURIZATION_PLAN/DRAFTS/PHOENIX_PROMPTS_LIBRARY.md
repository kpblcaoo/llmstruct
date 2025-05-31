# 📚 PHOENIX: БИБЛИОТЕКА ПРОМПТОВ

**Автор:** Claude (LLM Prompt Engineer)  
**Дата:** 2025-05-30  
**Назначение:** Готовые к использованию промпты для каждой фазы реструктуризации

---

## 🎯 ПРОМПТЫ ПО ФАЗАМ

### 📍 **ФАЗА 0: ПРЕДПОЛЕТНАЯ ПРОВЕРКА**

#### **Промпт 0.1: Полная диагностика системы**
```
You are analyzing the llmstruct project to ensure all systems are operational before restructuring.

TASKS:
1. Test each LLM integration:
   - Grok API: Send test query, verify response format
   - Anthropic API: Check availability and context limits
   - Ollama: List available models, test with small query

2. Validate caching system:
   - Verify StructCacheManager indexes all 272 modules
   - Test search performance (should be <100ms)
   - Check cache validity and MD5 hashing

3. Confirm metrics tracking:
   - Verify token counting for each provider
   - Check session tracking functionality
   - Validate cost calculation accuracy

4. Identify critical issues:
   - List any broken functionality that blocks restructuring
   - Prioritize fixes by impact on project
   - Estimate time to fix each issue

5. Document working features:
   - Create inventory of all functional components
   - Mark features that must be preserved
   - Identify features safe to refactor

OUTPUT FORMAT:
{
  "system_status": {
    "grok_api": {"status": "working/broken", "details": "..."},
    "anthropic_api": {"status": "working/broken", "details": "..."},
    "ollama": {"status": "working/broken", "models": ["..."]},
    "cache_system": {"valid": true/false, "performance": "Xms"},
    "metrics": {"tracking": true/false, "accuracy": "..."}
  },
  "blocking_issues": [
    {"component": "...", "issue": "...", "fix_time": "X hours", "priority": "high/medium/low"}
  ],
  "working_features": [
    {"component": "...", "description": "...", "preserve": true/false}
  ],
  "go_no_go": "GO/NO-GO",
  "reasoning": "..."
}
```

---

### 📍 **ФАЗА 1: ИНВЕНТАРИЗАЦИЯ И КАТЕГОРИЗАЦИЯ**

#### **Промпт 1.1: Полная категоризация модулей**
```
Using the struct.json file and StructCacheManager, perform comprehensive categorization of all 272 modules in the llmstruct project.

CONTEXT:
- The project has grown organically with many experiments
- There are 8 different bot versions that need consolidation
- User prefers the integrations/telegram_bot implementation
- Many root-level files are experimental and non-working
- The project needs to support Grok, Anthropic, and Ollama APIs

CLASSIFICATION RULES:
1. CORE (🟢): Essential functionality that the project cannot work without
   - Main application entry points
   - Critical infrastructure (caching, metrics, logging)
   - Working API implementations
   - Essential utilities

2. REFACTOR (🟡): Working code that needs improvement
   - Poor code quality but functional
   - Missing error handling or logging
   - Needs performance optimization
   - Lacks proper documentation

3. CONSOLIDATE (🔵): Multiple implementations of same functionality
   - Identify the best version to keep
   - List features to merge from other versions
   - Mark versions for archiving

4. ARCHIVE (🟣): Experimental or incomplete but contains valuable ideas
   - Unfinished features with potential
   - Alternative approaches worth preserving
   - Historical implementations for reference

5. REMOVE (🔴): Code with no value
   - Completely broken with no salvageable parts
   - Obsolete approaches replaced by better ones
   - Test files for non-existent code
   - Auto-generated files that can be recreated

SPECIAL FOCUS AREAS:
1. Bot implementations (8 versions):
   - Compare feature sets
   - Identify unique capabilities
   - Plan consolidation strategy

2. API implementations:
   - Find most complete version
   - Identify missing features
   - Plan unified API structure

3. LLM integrations:
   - Ensure all providers are supported
   - Identify abstraction opportunities
   - Find common patterns

OUTPUT FORMAT:
{
  "summary": {
    "total_modules": 272,
    "core": X,
    "refactor": Y,
    "consolidate": Z,
    "archive": A,
    "remove": B
  },
  "core": {
    "modules": [
      {
        "path": "src/llmstruct/...",
        "description": "...",
        "dependencies": ["..."],
        "reason": "Critical for..."
      }
    ]
  },
  "refactor": {
    "modules": [
      {
        "path": "...",
        "current_issues": ["..."],
        "improvements_needed": ["..."],
        "estimated_effort": "X hours"
      }
    ]
  },
  "consolidate": {
    "bot_versions": {
      "analysis": {
        "version1": {"path": "...", "features": ["..."], "quality": "X/10"},
        "version2": {"path": "...", "features": ["..."], "quality": "X/10"},
        ...
      },
      "recommendation": {
        "keep": "integrations/telegram_bot",
        "merge_features": {
          "from_version": "...",
          "features": ["..."]
        },
        "archive": ["version1", "version3", ...],
        "remove": ["version5", ...]
      }
    },
    "api_implementations": {
      ...similar structure...
    }
  },
  "archive": {
    "modules": [
      {
        "path": "...",
        "valuable_ideas": ["..."],
        "potential_future_use": "...",
        "archive_location": "ARCHIVED/experiments/..."
      }
    ]
  },
  "remove": {
    "modules": [
      {
        "path": "...",
        "reason": "Completely broken, no salvageable code",
        "safe_to_delete": true
      }
    ]
  },
  "migration_plan": {
    "phase1": "Archive experimental code",
    "phase2": "Consolidate duplicates", 
    "phase3": "Refactor remaining code",
    "phase4": "Remove deprecated files"
  }
}
```

#### **Промпт 1.2: Детальный анализ ботов**
```
Perform detailed analysis of all 8 bot implementations in the llmstruct project.

CONTEXT:
- User prefers integrations/telegram_bot version
- Need to consolidate into single extensible framework
- Must preserve unique valuable features
- Should support multiple platforms (Telegram, Discord, Slack)

ANALYZE each bot for:
1. Core functionality and features
2. Code quality and maintainability
3. Unique capabilities not in other versions
4. Integration points with rest of system
5. External dependencies
6. Performance characteristics
7. Error handling and robustness

COMPARE bots on:
- Feature completeness (commands, interactions)
- Code architecture (modularity, extensibility)
- Platform support (single vs multi-platform)
- Integration quality (with LLMs, APIs, metrics)
- User experience (response time, error messages)

CREATE consolidation plan:
1. Base framework design
2. Feature migration strategy
3. Platform abstraction approach
4. Plugin/extension system
5. Configuration management
6. Testing strategy

OUTPUT detailed comparison matrix and migration roadmap.
```

---

### 📍 **ФАЗА 2: АРХИТЕКТУРНЫЙ РЕФАКТОРИНГ**

#### **Промпт 2.1: LLM Abstraction Layer Design**
```
Design a unified LLM abstraction layer for llmstruct that elegantly handles multiple providers.

REQUIREMENTS:
1. Support for multiple providers:
   - Grok (X.AI): Fast, limited context, good for quick queries
   - Anthropic (Claude): Large context, high quality, expensive
   - Ollama (Local): VRAM-limited, free, variable quality
   - Future providers: OpenAI, Cohere, etc.

2. Smart routing logic:
   - Route by context size (use Grok for small, Anthropic for large)
   - Route by task type (code generation, analysis, chat)
   - Route by cost constraints (budget remaining)
   - Route by availability (fallback on errors)

3. Common interface:
   ```python
   response = llm.query(
       prompt="...",
       model=None,  # auto-select
       max_tokens=None,
       temperature=0.7,
       system_prompt=None,
       preferred_provider=None,
       constraints={"max_cost": 0.10, "max_time": 30}
   )
   ```

4. Advanced features:
   - Response caching with semantic similarity
   - Token counting before sending
   - Cost estimation and tracking
   - Streaming support where available
   - Conversation memory management
   - Automatic retry with backoff

5. Configuration:
   - Environment variables for API keys
   - Runtime provider switching
   - Model preference profiles
   - Rate limit handling

DESIGN CONSIDERATIONS:
- Minimize latency for provider selection
- Graceful degradation on failures
- Extensible for new providers
- Testable with mock providers
- Observable with metrics

OUTPUT:
1. Abstract base class definition
2. Provider implementations outline
3. Router algorithm pseudocode
4. Configuration schema
5. Example usage scenarios
6. Testing strategy
```

#### **Промпт 2.2: Unified Bot Framework**
```
Design a unified, extensible bot framework consolidating 8 existing implementations.

BASE REQUIREMENTS:
- Start from integrations/telegram_bot (user preference)
- Support multiple platforms with shared logic
- Plugin architecture for extending functionality
- Async/await throughout for performance
- Comprehensive error handling and logging

ARCHITECTURE COMPONENTS:
1. Core Bot Engine:
   - Message routing and dispatching
   - Command parsing and validation
   - Response formatting and sending
   - Session/conversation management
   - Rate limiting and abuse prevention

2. Platform Adapters:
   - Telegram (primary)
   - Discord
   - Slack
   - Web API
   - CLI interface

3. Command System:
   - Declarative command registration
   - Automatic help generation
   - Parameter validation
   - Permission checking
   - Command aliasing

4. Plugin System:
   - Plugin discovery and loading
   - Dependency injection
   - Event hooks (pre/post command)
   - Shared services access
   - Hot reload capability

5. Integration Layer:
   - LLM abstraction layer
   - Metrics collection
   - Cache access
   - API endpoints
   - Database operations

MIGRATION STRATEGY:
1. Extract best features from each bot version
2. Create compatibility layer for existing commands
3. Gradual migration path for users
4. Preserve configuration formats
5. Maintain backwards compatibility

OUTPUT:
- Framework class hierarchy
- Plugin interface specification
- Platform adapter template
- Migration script outline
- Example bot implementation
```

#### **Промпт 2.3: API Architecture Unification**
```
Create unified API architecture consolidating multiple implementations into a single, professional service.

REQUIREMENTS:
1. Single FastAPI application with:
   - RESTful endpoints for all operations
   - WebSocket support for real-time features
   - GraphQL endpoint for flexible queries
   - OpenAPI/Swagger documentation
   - Health check and metrics endpoints

2. Endpoint categories:
   - /api/v1/llm/* - LLM operations
   - /api/v1/bot/* - Bot management
   - /api/v1/struct/* - Project structure queries
   - /api/v1/metrics/* - Analytics and monitoring
   - /api/v1/session/* - Session management
   - /ws/* - WebSocket endpoints

3. Standardization:
   - Consistent response format
   - Unified error handling
   - Request/response validation
   - Rate limiting per endpoint
   - API versioning strategy

4. Security:
   - JWT-based authentication
   - API key management
   - Role-based access control
   - Request signing for webhooks
   - CORS configuration

5. Integration requirements:
   - Connect to LLM abstraction layer
   - Use cache for performance
   - Emit metrics for monitoring
   - Support for webhooks
   - Event streaming capabilities

DESIGN PATTERNS:
- Repository pattern for data access
- Service layer for business logic
- Dependency injection throughout
- Middleware for cross-cutting concerns
- Event-driven architecture where appropriate

OUTPUT:
- API structure with all endpoints
- Request/response schemas
- Authentication flow diagram
- Integration points specification
- Performance optimization strategies
```

---

### 📍 **ФАЗА 3: IMPLEMENTATION & CLEANUP**

#### **Промпт 3.1: Code Migration and Cleanup**
```
Implement the refactoring plan for [COMPONENT_NAME] following the architecture from Phase 2.

MIGRATION RULES:
1. Preserve all working functionality
2. Improve code quality standards:
   - Type hints on all functions
   - Docstrings with examples
   - Error handling with specific exceptions
   - Logging at appropriate levels
   - Unit tests for critical paths

3. Code cleanup checklist:
   - Remove commented code older than 3 months
   - Delete print() debugging statements
   - Consolidate duplicate utility functions
   - Fix all linting errors (flake8, black)
   - Update imports to new structure
   - Remove unused imports and variables

4. Refactoring patterns:
   - Extract method for long functions (>50 lines)
   - Replace magic numbers with constants
   - Use dependency injection over globals
   - Implement builder pattern for complex objects
   - Add factory methods where appropriate

5. Archive strategy:
   - Move experimental code to ARCHIVED/ with README
   - Preserve commit history in archive
   - Document why code was archived
   - Keep reference to original location

SPECIFIC TASKS for [COMPONENT_NAME]:
- Current location: ...
- New location: ...
- Dependencies to update: ...
- Tests to write: ...
- Documentation to create: ...

OUTPUT:
1. Refactored code files
2. Migration script (if needed)
3. Updated tests
4. Documentation updates
5. Archive contents (if any)
```

#### **Промпт 3.2: Test Suite Creation**
```
Create comprehensive test suite for the refactored [COMPONENT_NAME].

TEST CATEGORIES:
1. Unit Tests:
   - Test each public method
   - Mock external dependencies
   - Test edge cases and errors
   - Achieve >90% code coverage

2. Integration Tests:
   - Test component interactions
   - Verify API contracts
   - Test with real dependencies
   - Validate data flow

3. Performance Tests:
   - Benchmark critical operations
   - Memory usage profiling
   - Load testing for APIs
   - Cache effectiveness

4. Security Tests:
   - Input validation
   - Authentication/authorization
   - SQL injection prevention
   - XSS prevention

TEST STRUCTURE:
```python
def test_[function_name]_[scenario]():
    """Test [what is being tested]."""
    # Arrange
    ...
    
    # Act
    ...
    
    # Assert
    ...
```

MOCK STRATEGIES:
- LLM providers: Return predetermined responses
- Network calls: Use responses library
- File system: Use tmp_path fixture
- Time-dependent: Freeze time

OUTPUT:
- Test files following pytest conventions
- Fixtures for common test data
- Mock implementations
- Performance benchmarks
- CI/CD test configuration
```

---

### 📍 **ФАЗА 4: ДОКУМЕНТАЦИЯ**

#### **Промпт 4.1: Comprehensive Documentation Suite**
```
Create professional documentation for the restructured llmstruct project.

DOCUMENTATION COMPONENTS:

1. README.md (Main landing page):
   ```markdown
   # 🧠 LLMStruct - AI-Powered Development Framework
   
   [Brief, compelling description]
   
   ## ✨ Features
   - Multi-LLM support (Grok, Anthropic, Ollama)
   - Extensible bot framework
   - Advanced caching and optimization
   - IDE integrations (Cursor, VS Code)
   
   ## 🚀 Quick Start
   [5-minute setup guide]
   
   ## 📚 Documentation
   [Links to detailed docs]
   
   ## 🤝 Contributing
   [Contribution guidelines]
   ```

2. Getting Started Guides:
   - Installation (pip, docker, from source)
   - Configuration (environment setup)
   - First LLM query
   - First bot creation
   - First API call

3. User Guides by Persona:
   - For Cursor users: Leveraging Cursor features
   - For VS Code users: Copilot integration
   - For API developers: REST API usage
   - For bot developers: Creating custom bots
   - For contributors: Development setup

4. Architecture Documentation:
   - System overview with diagrams
   - Component interactions (sequence diagrams)
   - Data flow diagrams
   - Decision records (ADRs)
   - Performance considerations

5. API Reference:
   - OpenAPI specification
   - Example requests/responses
   - Error codes and handling
   - Rate limits and quotas
   - Webhook documentation

6. Tutorials:
   - "Build a Telegram bot in 10 minutes"
   - "Add a new LLM provider"
   - "Create custom commands"
   - "Implement caching strategies"
   - "Deploy to production"

WRITING GUIDELINES:
- Clear, concise language
- Plenty of examples
- Visual diagrams where helpful
- Runnable code snippets
- Links to related topics

OUTPUT:
- Complete documentation structure
- All markdown files
- Diagram sources (Mermaid)
- Example code repository
- Documentation tests
```

#### **Промпт 4.2: Interactive Examples**
```
Create interactive examples and tutorials for llmstruct.

EXAMPLE CATEGORIES:
1. Basic Usage:
   - Hello World with each LLM
   - Simple bot commands
   - Basic API calls
   - Cache usage examples

2. Advanced Patterns:
   - Multi-LLM orchestration
   - Streaming responses
   - Custom bot plugins
   - Performance optimization

3. Real-world Scenarios:
   - Code review bot
   - Documentation generator
   - Q&A system
   - Development assistant

4. Integration Examples:
   - Cursor workflow automation
   - VS Code extension
   - CI/CD integration
   - Monitoring setup

CREATE:
- Runnable example files
- Step-by-step tutorials
- Video script outlines
- Colab/Jupyter notebooks
- Docker compose setups

Each example should:
- Solve a real problem
- Be copy-paste ready
- Include error handling
- Show best practices
- Link to relevant docs
```

---

### 📍 **ФАЗА 5: ВАЛИДАЦИЯ**

#### **Промпт 5.1: Comprehensive Validation Suite**
```
Create validation framework to ensure the restructured llmstruct meets all quality standards.

VALIDATION CATEGORIES:

1. Functional Validation:
   - All LLM providers respond correctly
   - Bot commands work as expected
   - API endpoints return correct data
   - Cache improves performance
   - Metrics track accurately

2. Performance Validation:
   - API response time < 500ms (p95)
   - Cache operations < 100ms
   - LLM routing < 50ms
   - Memory usage < 512MB idle
   - Startup time < 5 seconds

3. Integration Validation:
   - Cursor features work correctly
   - VS Code integration functions
   - Docker container builds
   - CI/CD pipeline passes
   - Documentation builds

4. User Journey Validation:
   - New user can start in 5 minutes
   - Developer can add new feature
   - API user can integrate easily
   - Bot creator can extend framework
   - Contributor can submit PR

5. Quality Validation:
   - Code coverage > 90%
   - All linting passes
   - Security scan clean
   - Dependencies up to date
   - Documentation accurate

CREATE:
1. Automated test suites
2. Manual test checklists
3. Performance benchmarks
4. User acceptance criteria
5. Quality gates for release

OUTPUT:
- Validation scripts
- Test result dashboard
- Performance reports
- Quality metrics
- Go/no-go criteria
```

#### **Промпт 5.2: Final Quality Report**
```
Generate comprehensive quality report for the Phoenix restructuring project.

ANALYZE:
1. Code Quality Metrics:
   - Lines of code (before/after)
   - Cyclomatic complexity
   - Test coverage
   - Technical debt
   - Duplication percentage

2. Architecture Improvements:
   - Modularity score
   - Coupling/cohesion metrics
   - API consistency
   - Pattern compliance
   - Extensibility rating

3. Performance Gains:
   - Response time improvements
   - Memory usage reduction
   - Cache hit rates
   - Error rates
   - Throughput increases

4. Developer Experience:
   - Setup time reduction
   - Documentation completeness
   - API usability score
   - Error message quality
   - Development velocity

5. User Satisfaction:
   - Feature completeness
   - Ease of use rating
   - Performance satisfaction
   - Documentation helpfulness
   - Overall NPS score

GENERATE:
- Executive summary
- Detailed metrics report
- Before/after comparisons
- Recommendations for future
- Success celebration points
```

---

## 🛠️ СПЕЦИАЛЬНЫЕ ПРОМПТЫ

### **Промпт для решения проблем**
```
The [COMPONENT] refactoring has encountered an issue: [DESCRIBE ISSUE]

CONTEXT:
- Current state: ...
- Expected state: ...
- Error messages: ...
- What was tried: ...

ANALYZE the problem and provide:
1. Root cause analysis
2. Multiple solution approaches
3. Recommended solution with rationale
4. Implementation steps
5. Prevention strategies

Consider:
- Minimal disruption to other components
- Maintaining backward compatibility
- Performance implications
- Future maintainability
```

### **Промпт для оптимизации производительности**
```
The [COMPONENT] is showing performance issues:
- Current metrics: ...
- Expected metrics: ...
- Bottleneck analysis: ...

OPTIMIZE for:
1. Response time
2. Memory usage
3. CPU utilization
4. I/O operations
5. Cache effectiveness

PROVIDE:
- Optimization strategies
- Code changes needed
- Benchmark comparisons
- Trade-off analysis
- Monitoring recommendations
```

---

## 📋 КОНТРОЛЬНЫЕ ВОПРОСЫ ДЛЯ КАЖДОЙ ФАЗЫ

### **Перед началом фазы:**
1. Все ли зависимости от предыдущей фазы выполнены?
2. Есть ли блокирующие проблемы?
3. Достаточно ли времени выделено?
4. Все ли инструменты готовы?

### **Во время выполнения:**
1. Следуем ли мы плану?
2. Нужны ли корректировки?
3. Возникли ли неожиданные сложности?
4. Сохраняется ли качество?

### **После завершения:**
1. Все ли цели достигнуты?
2. Что можно улучшить?
3. Какие уроки извлечены?
4. Готовы ли к следующей фазе?

---

**💡 Эти промпты разработаны для максимальной эффективности и качества. Используйте их как отправную точку и адаптируйте под конкретные нужды проекта.** 