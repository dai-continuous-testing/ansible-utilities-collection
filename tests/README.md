# Test Configuration for DAI Continuous Testing Utilities

## Test Structure

```
tests/
├── unit/                          # Unit tests for individual modules
│   ├── test_application_properties.py
│   ├── test_health_check.py
│   ├── test_win_health_check.py
│   └── test_win_drive_letter_to_disk_info.py
├── integration/                   # Integration tests for complete workflows
│   └── test_modules_integration.py
└── run_tests.py                   # Test runner script
```

## Running Tests

### Run All Tests
```bash
cd ansible_collections/dai_continuous_testing/utilities
python tests/run_tests.py
```

### Run Specific Test Types
```bash
# Unit tests only
python tests/run_tests.py --type unit

# Integration tests only
python tests/run_tests.py --type integration
```

### Run with Validation Checks
```bash
# Run all validation checks and tests
python tests/run_tests.py --all-checks

# Individual checks
python tests/run_tests.py --validate    # Module structure validation
python tests/run_tests.py --coverage    # Test coverage analysis
python tests/run_tests.py --lint        # Syntax and linting checks
```

### Verbose Output
```bash
python tests/run_tests.py --verbose
```

## Test Coverage Requirements

- **Unit Tests**: Each module should have comprehensive unit tests covering:
  - Normal operation scenarios
  - Error handling and edge cases
  - Input validation
  - Platform-specific behavior (where applicable)

- **Integration Tests**: Test complete workflows including:
  - Module execution in Ansible context
  - Cross-module interactions
  - Error propagation and handling
  - Platform compatibility

## Test Dependencies

- Python 3.6 or higher
- unittest (standard library)
- unittest.mock (standard library)
- tempfile (standard library)

## Writing New Tests

### Unit Test Template
```python
import unittest
from unittest.mock import patch, Mock

class TestYourModule(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        pass
    
    def tearDown(self):
        """Clean up after each test method."""
        pass
    
    def test_normal_operation(self):
        """Test normal operation scenario."""
        pass
    
    def test_error_handling(self):
        """Test error handling scenarios."""
        pass
```

### Integration Test Guidelines
- Test real-world usage scenarios
- Mock external dependencies (network calls, file system operations)
- Validate module return values and side effects
- Test error recovery and resilience

## Continuous Integration

The test suite is designed to be run in CI/CD pipelines:

```yaml
# Example CI step
- name: Run Collection Tests
  run: |
    cd ansible_collections/dai_continuous_testing/utilities
    python tests/run_tests.py --all-checks
```

## Test Data and Fixtures

Test data is created dynamically using Python's tempfile module to ensure:
- Isolation between tests
- Clean test environment
- Cross-platform compatibility
- No dependency on external test files
