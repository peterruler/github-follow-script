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
└── test_main.py          # Comprehensive test suite
```

## Test Coverage

Our test suite covers:

- ✅ **API Functions** - All GitHub API interactions
- ✅ **Follow Logic** - Candidate evaluation algorithms  
- ✅ **Error Handling** - Edge cases and error scenarios
- ✅ **Configuration** - Environment variable loading
- ✅ **Integration** - End-to-end workflow testing

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

### 🔌 API Tests (`TestGitHubAPI`)
- User info retrieval
- Authentication
- Pagination handling
- Error responses

### 🎯 Logic Tests (`TestFollowCandidateEvaluation`)
- Follow criteria validation
- Ratio calculations
- Activity thresholds
- Edge cases

### 🔍 Discovery Tests (`TestFindPotentialFollows`)
- Candidate discovery algorithms
- Filtering logic
- Rate limiting

### ⚙️ Configuration Tests (`TestConfiguration`)
- Environment variables
- Default values
- Error handling

## Mock Testing

We use `responses` library to mock GitHub API calls:

```python
@responses.activate
def test_api_function():
    responses.add(responses.GET, "...", json={...})
    # Test your function
```

## Coverage Goals

- **Target**: 80%+ coverage
- **Current**: Run `./test.sh` to see current coverage
- **Reports**: Generated in `htmlcov/` directory

## Continuous Integration

The test script can be easily integrated into CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Run tests
  run: ./test.sh
```
