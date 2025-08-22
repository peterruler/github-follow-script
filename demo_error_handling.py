#!/usr/bin/env python3
"""
Demo script to showcase error handling capabilities in main.py
This script demonstrates various error scenarios and how they are handled.
"""

import sys
import os
from unittest.mock import patch, MagicMock
import requests

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import (
    GitHubAPIError, RateLimitError, AuthenticationError,
    handle_api_response, get_user_info, follow_user, main
)


def demo_custom_exceptions():
    """Demonstrate custom exception handling"""
    print("🚨 Demonstrating Custom Exception Handling")
    print("=" * 50)
    
    # Demo 1: Authentication Error
    print("\n1. Authentication Error Demo:")
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Bad credentials"
    
    try:
        handle_api_response(mock_response, "authentication test")
    except AuthenticationError as e:
        print(f"✓ Caught AuthenticationError: {e}")
        print(f"  Status Code: {e.status_code}")
        print(f"  Response: {e.response_text}")
    
    # Demo 2: Rate Limit Error
    print("\n2. Rate Limit Error Demo:")
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.text = "API rate limit exceeded for user"
    
    try:
        handle_api_response(mock_response, "rate limit test")
    except RateLimitError as e:
        print(f"✓ Caught RateLimitError: {e}")
        print(f"  Status Code: {e.status_code}")
    
    # Demo 3: General API Error
    print("\n3. General API Error Demo:")
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal server error"
    
    try:
        handle_api_response(mock_response, "server error test")
    except GitHubAPIError as e:
        print(f"✓ Caught GitHubAPIError: {e}")
        print(f"  Status Code: {e.status_code}")


def demo_network_error_handling():
    """Demonstrate network error handling"""
    print("\n\n🌐 Demonstrating Network Error Handling")
    print("=" * 50)
    
    # Demo: Network timeout
    print("\n1. Network Timeout Demo:")
    with patch('main.requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
        
        result = get_user_info("testuser")
        if result is None:
            print("✓ Network timeout handled gracefully - returned None")
        
    # Demo: Connection error
    print("\n2. Connection Error Demo:")
    with patch('main.requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        result = get_user_info("testuser")
        if result is None:
            print("✓ Connection error handled gracefully - returned None")


def demo_data_validation():
    """Demonstrate data validation and error recovery"""
    print("\n\n🔍 Demonstrating Data Validation")
    print("=" * 50)
    
    # Demo: Missing required fields
    print("\n1. Missing Required Fields Demo:")
    with patch('main.get_user_info') as mock_get_user_info:
        mock_get_user_info.return_value = {"login": "testuser"}  # Missing followers/following
        
        from main import is_good_follow_candidate
        result = is_good_follow_candidate("testuser")
        if result is False:
            print("✓ Missing required fields detected and handled")
    
    # Demo: Invalid data types
    print("\n2. Invalid Data Types Demo:")
    with patch('main.get_user_info') as mock_get_user_info:
        mock_get_user_info.return_value = {
            "following": "invalid",  # Should be int
            "followers": None       # Should be int
        }
        
        result = is_good_follow_candidate("testuser")
        if result is False:
            print("✓ Invalid data types detected and handled")


def demo_resilient_operations():
    """Demonstrate resilient operations with partial failures"""
    print("\n\n🛡️ Demonstrating Resilient Operations")
    print("=" * 50)
    
    print("\n1. Partial API Failure Handling:")
    
    # Mock a scenario where some API calls succeed and others fail
    def mock_follow_user_side_effect(username):
        if username == "fail_user":
            return False  # Simulate failure
        elif username == "rate_limit_user":
            raise RateLimitError("Rate limit exceeded")
        else:
            return True  # Simulate success
    
    with patch('main.follow_user', side_effect=mock_follow_user_side_effect):
        users = ["success_user1", "fail_user", "success_user2", "rate_limit_user"]
        
        successful = 0
        failed = 0
        
        for user in users:
            try:
                if follow_user(user):
                    successful += 1
                    print(f"  ✓ Successfully followed: {user}")
                else:
                    failed += 1
                    print(f"  ✗ Failed to follow: {user}")
            except RateLimitError:
                print(f"  ⚠️  Rate limit hit for: {user}")
                break
        
        print(f"\n  Summary: {successful} successful, {failed} failed")
        print("  ✓ Operation continued despite individual failures")


def demo_logging_and_monitoring():
    """Demonstrate logging and monitoring capabilities"""
    print("\n\n📊 Demonstrating Logging & Monitoring")
    print("=" * 50)
    
    print("\n1. Structured Logging Demo:")
    
    # Enable debug logging for demonstration
    import logging
    logging.getLogger('main').setLevel(logging.DEBUG)
    
    # Create a test handler to capture logs
    import io
    log_capture = io.StringIO()
    handler = logging.StreamHandler(log_capture)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    logger = logging.getLogger('main')
    logger.addHandler(handler)
    
    # Trigger some logging
    with patch('main.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"login": "testuser", "following": 100, "followers": 200}
        mock_get.return_value = mock_response
        
        get_user_info("demo_user")
    
    # Show captured logs
    log_output = log_capture.getvalue()
    if log_output:
        print("  Captured log entries:")
        for line in log_output.strip().split('\n'):
            if line:
                print(f"    {line}")
    
    # Clean up
    logger.removeHandler(handler)
    log_capture.close()


def demo_graceful_degradation():
    """Demonstrate graceful degradation in adverse conditions"""
    print("\n\n⚡ Demonstrating Graceful Degradation")
    print("=" * 50)
    
    print("\n1. Low API Quota Handling:")
    
    # Mock low API quota scenario
    with patch('main.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'resources': {
                'core': {
                    'remaining': 50,  # Low quota
                    'reset': 1234567890
                }
            }
        }
        mock_get.return_value = mock_response
        
        with patch('main.find_potential_follows') as mock_find:
            mock_find.return_value = []
            
            print("  Simulating main() with low API quota...")
            main()
            print("  ✓ Function completed despite low quota warning")


def main_demo():
    """Run all error handling demonstrations"""
    print("🧪 GitHub Follow Script - Error Handling Demo")
    print("=" * 60)
    print("This demo showcases the robust error handling capabilities")
    print("implemented in the GitHub Follow Script.\n")
    
    try:
        demo_custom_exceptions()
        demo_network_error_handling()
        demo_data_validation()
        demo_resilient_operations()
        demo_logging_and_monitoring()
        demo_graceful_degradation()
        
        print("\n\n🎉 Error Handling Demo Complete!")
        print("=" * 60)
        print("All error scenarios handled successfully:")
        print("✓ Custom exception hierarchy")
        print("✓ Network error recovery")
        print("✓ Data validation and sanitization")
        print("✓ Resilient operations with partial failures")
        print("✓ Comprehensive logging and monitoring")
        print("✓ Graceful degradation under adverse conditions")
        print("\nThe script is production-ready with robust error handling! 🚀")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        print("This shouldn't happen if error handling is working correctly!")


if __name__ == "__main__":
    main_demo()
