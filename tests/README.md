# LLMStruct Test Suite

Comprehensive test suite for LLMStruct following testing best practices.

## 📁 Test Structure

The test suite is organized by test type and mirrors the source code structure:

```
tests/
├── conftest.py                 # Global fixtures and configuration
├── unit/                       # Unit tests (fast, isolated)
│   ├── core/                  # Tests for src/llmstruct/core/
│   ├── parsers/               # Tests for src/llmstruct/parsers/
│   ├── generators/            # Tests for src/llmstruct/generators/
│   ├── api/                   # Tests for src/llmstruct/api/
│   └── validators/            # Tests for src/llmstruct/validators/
├── integration/               # Integration tests (moderate speed)
├── e2e/                      # End-to-end tests (slow, full system)
├── performance/              # Performance tests (benchmarking)
└── fixtures/                 # Test data and fixtures
    ├── phase1/               # Phase 1 validation fixtures
    └── sample_code/          # Sample code for parser testing
```

## 🏷️ Test Types and Markers

Tests are automatically marked based on their location:

- **`@pytest.mark.unit`** - Fast, isolated tests (< 1s each)
- **`@pytest.mark.integration`** - Module interaction tests (< 5s each)  
- **`@pytest.mark.e2e`** - End-to-end system tests (< 30s each)
- **`@pytest.mark.performance`** - Performance benchmarks
- **`@pytest.mark.slow`** - Tests that may take several seconds

## 🚀 Running Tests

### All Tests
```bash
pytest tests/
```

### By Test Type
```bash
pytest tests/unit/                    # Unit tests only
pytest tests/integration/             # Integration tests only
pytest tests/e2e/                     # E2E tests only
pytest -m "not slow"                  # Skip slow tests
```

### By Module
```bash
pytest tests/unit/core/               # Core module tests
pytest tests/unit/parsers/            # Parser tests
pytest tests/integration/             # All integration tests
```

### With Coverage
```bash
pytest tests/ --cov=src/llmstruct --cov-report=html
```

## 📊 Current Test Statistics

- **Total Tests**: 34
- **Unit Tests**: 23 (core functionality)
- **Integration Tests**: 4 (module interactions)
- **E2E Tests**: 7 (complete system validation)
- **Performance Tests**: 0 (to be added)

## 🛠️ Test Guidelines

### Unit Tests
- **Fast** (< 1 second each)
- **Isolated** (no external dependencies)
- **Focused** (test one function/class)
- **Deterministic** (same result every time)

Example:
```python
def test_uid_generation_format():
    """Test UID generation follows correct format."""
    uid = generate_uid(UIDType.FUNCTION, "module.py", "function_name")
    assert uid == "module.function_name#function"
```

### Integration Tests
- **Module interactions** (2-3 modules working together)
- **Moderate speed** (< 5 seconds each)
- **Real data** (use fixtures, avoid mocks when possible)

Example:
```python
def test_parser_generator_integration():
    """Test parser output works with generator."""
    parsed_data = python_parser.analyze_module(sample_file)
    json_output = json_generator.generate(parsed_data)
    assert json_output["metadata"]["schema_version"] == "2.1.0"
```

### E2E Tests
- **Complete workflows** (full system functionality)
- **Real scenarios** (actual use cases)
- **Comprehensive validation** (check all outputs)

Example:
```python
@pytest.mark.e2e
def test_complete_codebase_analysis():
    """Test complete codebase analysis workflow."""
    result = analyze_codebase(project_path)
    validate_schema(result)
    validate_completeness(result)
```

## 🔧 Fixtures and Utilities

### Global Fixtures (conftest.py)
- `clean_config` - Clean configuration for each test
- `temp_dir` - Temporary directory for file operations
- `sample_python_code` - Sample Python code for parser testing
- `sample_struct_data` - Sample structure data for validation

### Test Data
- `fixtures/phase1/` - Phase 1 validation data
- `fixtures/sample_code/` - Sample code files for testing

## 📈 Adding New Tests

### For New Modules
1. Create corresponding test directory: `tests/unit/new_module/`
2. Add `__init__.py` file
3. Create test files: `test_module_name.py`

### Test File Naming
- Unit tests: `test_<module_name>.py`
- Integration tests: `test_<feature>_integration.py`
- E2E tests: `test_<workflow>_e2e.py`

### Test Function Naming
- Descriptive: `test_function_does_what_when_condition()`
- Specific: `test_uid_generation_with_line_numbers()`
- Clear: `test_parser_handles_malformed_syntax()`

## 🔍 Test Quality Standards

### Coverage Requirements
- **Unit tests**: All public functions/classes
- **Integration tests**: Key workflows and interactions
- **E2E tests**: Main user scenarios

### Test Size Limits
- **Unit test files**: ≤ 200 lines
- **Integration test files**: ≤ 300 lines
- **E2E test files**: ≤ 500 lines

### Performance Guidelines
- **Unit tests**: < 1 second each
- **Integration tests**: < 5 seconds each
- **E2E tests**: < 30 seconds each
- **Full suite**: < 2 minutes

## 🚨 Common Issues

### Import Errors
If you see import errors, ensure `conftest.py` is properly setting up the Python path:
```python
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
```

### Fixture Scope
- Use `scope="function"` for test isolation
- Use `scope="session"` for expensive setup
- Use `scope="module"` for moderate setup

### Test Dependencies
- Avoid test dependencies (each test should be independent)
- Use fixtures for shared setup
- Clean up resources in teardown

## 📝 Best Practices

1. **Test Names Should Be Documentation**
   ```python
   def test_uid_generator_creates_unique_ids_for_same_name_different_lines():
   ```

2. **Use Descriptive Assertions**
   ```python
   assert uid_count > 100, f"Expected >100 UIDs, got {uid_count}"
   ```

3. **Test Edge Cases**
   ```python
   def test_parser_handles_empty_file():
   def test_parser_handles_syntax_errors():
   def test_parser_handles_unicode_content():
   ```

4. **Use Fixtures for Complex Setup**
   ```python
   @pytest.fixture
   def complex_codebase(temp_dir):
       # Create test codebase structure
       return setup_test_project(temp_dir)
   ```

5. **Keep Tests Simple and Focused**
   - One concept per test
   - Clear arrange/act/assert structure
   - Minimal setup required

## 🔄 Continuous Integration

Tests are automatically run on:
- Every commit (unit + integration tests)
- Pull requests (full test suite)
- Nightly builds (including performance tests)

Target metrics:
- **Test coverage**: > 90%
- **Test speed**: Full suite < 2 minutes
- **Test reliability**: > 99% pass rate 