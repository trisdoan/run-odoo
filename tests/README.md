# Test Suite for run-odoo

This directory contains comprehensive tests for the `run-odoo` package. The test suite is designed to cover all functionality including CLI commands, configuration management, Runner class, and utility functions.

## Test Structure

### Test Files

- `test_cli.py` - Tests for all CLI commands (try-module, test-module, upgrade-module, shell, harlequin)
- `test_config.py` - Tests for configuration management and profile handling
- `test_runner.py` - Tests for the Runner class functionality
- `test_utils.py` - Tests for utility functions (dependency installation, git operations)
- `conftest.py` - Shared pytest fixtures and configuration

### Test Data

- `data/` - Test configuration files and sample data
  - `good_config.run_odoo.toml` - Valid configuration file
  - `comprehensive_config.toml` - Configuration with all possible fields
  - `invalid_config.toml` - Invalid configurations for error testing
  - `run_odoo.toml` - Empty configuration file

## Running Tests

### Basic Test Execution

```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_cli.py

# Run specific test class
python -m pytest tests/test_cli.py::TestTryModule

# Run specific test method
python -m pytest tests/test_cli.py::TestTryModule::test_try_module_basic
```

### Using the Test Runner Script

```bash
# Run all tests
python run_tests.py

# Run with coverage
python run_tests.py --coverage

# Run specific test file
python run_tests.py tests/test_cli.py

# Run with verbose output
python run_tests.py -v

# Run tests in parallel
python run_tests.py --parallel

# List all available tests
python run_tests.py --list-tests

# List all available markers
python run_tests.py --list-markers
```

### Test Markers

Tests are categorized using pytest markers:

```bash
# Run only CLI tests
python -m pytest -m cli

# Run only configuration tests
python -m pytest -m config

# Run only unit tests (exclude integration)
python -m pytest -m "not integration"

# Run only fast tests (exclude slow)
python -m pytest -m "not slow"

# Run multiple marker combinations
python -m pytest -m "cli and not slow"
```

Available markers:
- `cli` - CLI command tests
- `config` - Configuration management tests
- `runner` - Runner class tests
- `utils` - Utility function tests
- `integration` - Integration tests
- `unit` - Unit tests
- `slow` - Slow-running tests
- `fedora` - Fedora-specific tests
- `debian` - Debian/Ubuntu-specific tests
- `git` - Git operation tests
- `subprocess` - Subprocess-related tests
- `mock` - Tests using mocking
- `error` - Error handling tests
- `edge_case` - Edge case tests

## Test Coverage

### CLI Tests (`test_cli.py`)

Tests all CLI commands:
- `try-module` - Basic module testing with various options
- `test-module` - Module testing functionality
- `upgrade-module` - Module upgrade functionality
- `shell` - Odoo shell functionality
- `harlequin` - Database IDE integration

Each command is tested with:
- Basic functionality
- All command-line options
- Profile configuration
- Local configuration files
- Error handling
- Edge cases

### Configuration Tests (`test_config.py`)

Tests configuration management:
- `ConfigFile` class functionality
- Configuration file discovery
- Profile management
- Configuration validation
- Error handling for invalid configurations
- Integration scenarios

### Runner Tests (`test_runner.py`)

Tests the Runner class:
- Initialization and validation
- Environment setup (Odoo source, Enterprise, virtual environment)
- Parameter building
- Execution methods (run, run_tests, run_shell, upgrade_modules)
- Utility methods
- Integration scenarios

### Utility Tests (`test_utils.py`)

Tests utility functions:
- Fedora dependency installation
- Debian/Ubuntu dependency installation
- Git repository operations
- Error handling
- Edge cases

## Test Data

### Configuration Files

The test suite includes various configuration files to test different scenarios:

1. **Valid Configurations**
   - `good_config.run_odoo.toml` - Simple valid configuration
   - `comprehensive_config.toml` - Configuration with all possible fields

2. **Invalid Configurations**
   - `invalid_config.toml` - Various invalid configurations for error testing

3. **Edge Cases**
   - `run_odoo.toml` - Empty configuration file

## Mocking Strategy

The test suite uses extensive mocking to avoid external dependencies:

- **Subprocess calls** - All system commands are mocked
- **File system operations** - Path operations are mocked where appropriate
- **External services** - Network calls and external services are mocked
- **Environment variables** - System environment is mocked

## Error Testing

The test suite includes comprehensive error testing:

- Invalid configurations
- Missing dependencies
- Network failures
- Permission errors
- Invalid command-line arguments
- Subprocess failures

## Performance Considerations

- Tests are designed to run quickly (most complete in < 1 second)
- Heavy operations are mocked
- Parallel execution is supported
- Slow tests are marked with `@pytest.mark.slow`

## Continuous Integration

The test suite is designed to work in CI environments:

- No external dependencies required
- Deterministic results
- Clear error messages
- Coverage reporting
- Parallel execution support

## Adding New Tests

When adding new tests:

1. **Follow naming conventions**:
   - Test files: `test_*.py`
   - Test classes: `Test*`
   - Test methods: `test_*`

2. **Use appropriate markers**:
   - Mark tests with relevant categories
   - Use `@pytest.mark.slow` for slow tests
   - Use `@pytest.mark.integration` for integration tests

3. **Mock external dependencies**:
   - Use `@patch` decorators for external calls
   - Mock file system operations when needed
   - Mock subprocess calls

4. **Test error conditions**:
   - Include tests for error handling
   - Test edge cases
   - Test invalid inputs

5. **Document test purpose**:
   - Use descriptive test names
   - Add docstrings explaining test purpose
   - Include comments for complex test logic

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure you're running tests from the project root
2. **Mock issues**: Check that mocks are applied to the correct module path
3. **Path issues**: Use `Path` objects consistently for cross-platform compatibility
4. **Subprocess mocking**: Ensure subprocess calls are properly mocked

### Debugging Tests

```bash
# Run with maximum verbosity
python -m pytest -vvv

# Run with print statement output
python -m pytest -s

# Run single test with debugging
python -m pytest tests/test_cli.py::TestTryModule::test_try_module_basic -vvv -s

# Run with coverage and show missing lines
python -m pytest --cov=run_odoo --cov-report=term-missing
```

## Coverage Goals

The test suite aims for:
- **Line coverage**: > 90%
- **Branch coverage**: > 85%
- **Function coverage**: > 95%

Run coverage analysis:
```bash
python run_tests.py --coverage
```

This will generate both terminal and HTML coverage reports. 