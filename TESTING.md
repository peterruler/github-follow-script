# 🧪 Testing Setup Guide

## Quick Start

1. **Copy environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your GitHub token:**
   ```bash
   nano .env
   # Add your token: GITHUB_TOKEN=ghp_your_token_here
   ```

3. **Run all tests:**
   ```bash
   ./test.sh
   ```

## Test Structure

```
tests/
├── __init__.py
├── test_main.py               # Core functionality tests
├── test_error_handling.py     # Error scenarios & edge cases
└── test_full_coverage.py      # 100% coverage completeness tests
```

## Test Coverage

Our test suite achieves **100% code coverage** and includes:

- ✅ **API Functions** - All GitHub API interactions (success & failure paths)
- ✅ **Follow Logic** - Candidate evaluation algorithms  
- ✅ **Error Handling** - Comprehensive exception handling & recovery
- ✅ **Configuration** - Environment variable loading & validation
- ✅ **Integration** - End-to-end workflow testing
- ✅ **Edge Cases** - Network errors, rate limits, malformed responses
- ✅ **Safety Limits** - Infinite loop prevention, pagination boundaries
- ✅ **Main Entry** - Script execution and keyboard interrupts

## Manual Test Execution

```bash
# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r src/requirements.txt

# Run tests with coverage
pytest tests/ --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Test Categories

### 🔌 API Tests (`TestGitHubAPI` in `test_main.py`)
- User info retrieval (success & not found)
- Authentication validation
- Pagination handling (multiple pages)
- Error responses (404, 403, etc.)
- Activity tracking

### 🎯 Logic Tests (`TestFollowCandidateEvaluation` in `test_main.py`)
- Follow criteria validation
- Ratio calculations (follow/follower thresholds)
- Activity thresholds (inactivity detection)
- Edge cases (missing data, invalid types)

### 🔍 Discovery Tests (`TestFindPotentialFollows` in `test_main.py`)
- Candidate discovery algorithms (strategy 1 & 2)
- Filtering logic
- Rate limiting awareness
- Sample size handling

### ⚙️ Configuration Tests (`TestConfiguration` in `test_main.py`)
- Environment variables
- Default values
- Token validation
- Missing token error handling

### 🚨 Error Handling Tests (`test_error_handling.py`)
**Core Response Handling:**
- HTTP status codes (200, 204, 401, 403, 404, 500)
- Rate limit detection
- Authentication errors
- Forbidden access

**API Function Errors:**
- Network errors (ConnectionError, Timeout)
- Malformed JSON responses
- Request exceptions
- Unexpected exceptions

**Candidate Evaluation Errors:**
- Missing required fields
- Invalid data types
- Activity check failures
- Exception recovery

**Main Function Errors:**
- Rate limit during search
- Authentication failures
- Keyboard interrupts
- Generic exception handling

**Robustness Features:**
- Pagination safety limits (prevents infinite loops)
- Individual error resilience in batch operations

### ✅ Full Coverage Tests (`test_full_coverage.py`)
**Module Import & Configuration:**
- Token requirement validation
- Environment variable handling
- Module reload behavior

**API Function Completeness:**
- All success paths
- All failure paths
- Network error handling
- Unexpected exceptions
- Empty/None responses
- Safety limits (100-page max for followers/following)

**Find Potential Follows Coverage:**
- Missing username handling
- Exception handling in follower analysis
- Exception handling in following analysis
- Progress logging (every 10th candidate)
- Daily limit enforcement (MAX_FOLLOWS_PER_DAY)
- Candidate evaluation exceptions
- Unexpected errors

**Main Function Coverage:**
- Low rate limit warning (<100 remaining)
- Rate limit data unavailable (None response)
- RateLimitError during candidate search
- AuthenticationError during search
- Generic exception during search
- Success/failure/exception during following
- AuthenticationError during following
- RateLimitError during following
- Outer keyboard interrupt
- Outer generic exception
- Script entry point (`if __name__ == "__main__"`)

**Test Statistics:**
- **Total Tests:** 83
- **Coverage:** 100.00%
- **Lines Covered:** 364/364
- **Test Files:** 3
- **Test Classes:** 10+

## Mock Testing

We use `responses` library and `unittest.mock` for comprehensive mocking:

**API Mocking (`responses`):**
```python
@responses.activate
def test_api_function():
    responses.add(responses.GET, "https://api.github.com/...", 
                  json={...}, status=200)
    # Test your function
```

**Function Mocking (`monkeypatch`):**
```python
def test_with_mocks(monkeypatch):
    monkeypatch.setattr(main, 'get_user_info', 
                       lambda u: {'following': 100, 'followers': 200})
    # Test with mocked function
```

**Exception Mocking:**
```python
def test_network_error(monkeypatch):
    monkeypatch.setattr(main.requests, 'get', 
                       MagicMock(side_effect=requests.exceptions.Timeout()))
    # Test error handling
```

## Coverage Goals

- **Target**: 100% coverage ✅
- **Current**: 100.00% (364/364 lines)
- **Threshold**: Tests fail if coverage drops below 100%
- **Reports**: Generated in `htmlcov/` directory

## Running Specific Test Files

```bash
# Run only main functionality tests
pytest tests/test_main.py -v

# Run only error handling tests
pytest tests/test_error_handling.py -v

# Run only coverage completion tests
pytest tests/test_full_coverage.py -v

# Run with coverage for specific file
pytest tests/test_full_coverage.py --cov=src/main.py --cov-report=term-missing
```

## Continuous Integration

The test script can be easily integrated into CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Run tests
  run: ./test.sh
  
# Expected output:
# ✅ 83 tests passed
# ✅ 100% code coverage
# ✅ All quality checks passed
```

## Test Development Guidelines

When adding new features to `src/main.py`:

1. **Write tests first** (TDD approach recommended)
2. **Maintain 100% coverage** - tests will fail if coverage drops
3. **Test all paths:**
   - Success cases
   - Error cases (network, validation, etc.)
   - Edge cases (empty data, None, invalid types)
   - Exception handling
4. **Use mocks** to avoid real API calls
5. **Run full test suite** before committing:
   ```bash
   ./test.sh
   ```

## Debugging Failed Tests

```bash
# Run with verbose output
pytest -vv

# Run specific test
pytest tests/test_full_coverage.py::test_main_rate_limit_low_remaining -v

# Run with print statements visible
pytest -s

# Stop at first failure
pytest -x

# Show local variables on failure
pytest -l
```

## Coverage Report Analysis

```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html

# View detailed report
open htmlcov/index.html

# Terminal report with missing lines
pytest --cov=src --cov-report=term-missing

# Check specific file coverage
coverage report --include=src/main.py
```

## Test File Descriptions

### `test_main.py` (23 tests)
Core functionality tests covering:
- GitHub API interactions (success paths)
- Follow candidate evaluation logic
- Configuration and constants
- Basic integration scenarios

### `test_error_handling.py` (26 tests)
Comprehensive error scenario coverage:
- HTTP error codes and API failures
- Network errors and timeouts
- Data validation errors
- Exception propagation and handling
- Robustness features

### `test_full_coverage.py` (34 tests)
Completeness tests ensuring 100% coverage:
- All remaining code branches
- Edge cases and rare scenarios
- Safety limit validations
- Script entry point testing
- Module import validation

**Total: 83 tests, 100% coverage, 0 failures**
