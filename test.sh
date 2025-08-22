#!/bin/bash

# GitHub Follow Script - Test Runner
# This script sets up the environment and runs all tests

set -e  # Exit on any error

echo "🚀 GitHub Follow Script - Test Runner"
echo "=====================================\n"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "src/main.py" ]; then
    print_error "main.py not found. Please run this script from the project root directory."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_warning "Please edit .env file and add your GitHub token before running the main script."
    else
        print_error ".env.example not found. Cannot create .env file."
        exit 1
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
print_status "Installing dependencies..."
if [ -f "src/requirements.txt" ]; then
    pip install -r src/requirements.txt
    print_success "Dependencies installed"
else
    print_error "requirements.txt not found in src/ directory"
    exit 1
fi

# Set test environment variables
export GITHUB_TOKEN="test_token_for_testing"

# Run linting (if flake8 is available)
if command -v flake8 &> /dev/null; then
    print_status "Running code linting..."
    flake8 src/ tests/ --max-line-length=100 --ignore=E501,W503 || print_warning "Linting found some issues"
fi

# Run tests
print_status "Running tests..."
echo ""

# Run pytest with coverage
pytest tests/ \
    --verbose \
    --cov=src \
    --cov-report=html \
    --cov-report=term-missing \
    --cov-fail-under=70 \
    || {
        print_error "Tests failed!"
        exit 1
    }

echo ""
print_success "All tests passed!"

# Generate coverage report
if [ -d "htmlcov" ]; then
    print_status "Coverage report generated in htmlcov/index.html"
fi

# Check if main script can be imported without errors
print_status "Testing main script import..."
python3 -c "
import sys
sys.path.insert(0, 'src')
try:
    import main
    print('✓ main.py imports successfully')
except Exception as e:
    print(f'✗ Import error: {e}')
    sys.exit(1)
" || {
    print_error "main.py has import issues"
    exit 1
}

print_success "Script validation complete!"

echo ""
echo "📊 Test Summary:"
echo "==============="
echo "• All unit tests passed"
echo "• Code coverage report available"
echo "• main.py imports without errors"
echo ""
echo "To run the main script:"
echo "1. Edit .env file with your GitHub token"
echo "2. Run: python3 src/main.py"
echo ""
echo "🎉 Testing complete!"
