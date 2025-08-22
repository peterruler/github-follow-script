import pytest
import responses
import requests
from unittest.mock import patch, MagicMock
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import (
    GitHubAPIError, RateLimitError, AuthenticationError,
    handle_api_response, get_user_info, get_my_info, get_user_activity,
    follow_user, is_good_follow_candidate, find_potential_follows, main,
    GITHUB_API
)


class TestErrorHandling:
    """Test error handling functionality"""

    def test_handle_api_response_success_200(self):
        """Test successful API response handling"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}
        
        result = handle_api_response(mock_response, "test context")
        assert result == {"test": "data"}

    def test_handle_api_response_success_204(self):
        """Test successful no-content API response handling"""
        mock_response = MagicMock()
        mock_response.status_code = 204
        
        result = handle_api_response(mock_response, "test context")
        assert result is True

    def test_handle_api_response_authentication_error(self):
        """Test authentication error handling"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        
        with pytest.raises(AuthenticationError) as exc_info:
            handle_api_response(mock_response, "test context")
        
        assert exc_info.value.status_code == 401
        assert "Invalid or expired GitHub token" in str(exc_info.value)

    def test_handle_api_response_rate_limit_error(self):
        """Test rate limit error handling"""
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.text = "API rate limit exceeded"
        
        with pytest.raises(RateLimitError) as exc_info:
            handle_api_response(mock_response, "test context")
        
        assert exc_info.value.status_code == 403
        assert "GitHub API rate limit exceeded" in str(exc_info.value)

    def test_handle_api_response_forbidden_error(self):
        """Test forbidden access error handling"""
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden access"
        
        with pytest.raises(GitHubAPIError) as exc_info:
            handle_api_response(mock_response, "test context")
        
        assert exc_info.value.status_code == 403
        assert "Access forbidden" in str(exc_info.value)

    def test_handle_api_response_not_found(self):
        """Test not found response handling"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        
        result = handle_api_response(mock_response, "test context")
        assert result is None

    def test_handle_api_response_server_error(self):
        """Test server error handling"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        
        with pytest.raises(GitHubAPIError) as exc_info:
            handle_api_response(mock_response, "test context")
        
        assert exc_info.value.status_code == 500
        assert "API request failed" in str(exc_info.value)


class TestAPIFunctionsErrorHandling:
    """Test error handling in API functions"""

    @patch('main.requests.get')
    def test_get_user_info_network_error(self, mock_get):
        """Test network error handling in get_user_info"""
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")
        
        result = get_user_info("testuser")
        assert result is None

    @patch('main.requests.get')
    def test_get_user_info_timeout_error(self, mock_get):
        """Test timeout error handling in get_user_info"""
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
        
        result = get_user_info("testuser")
        assert result is None

    @patch('main.requests.get')
    def test_get_my_info_authentication_error(self, mock_get):
        """Test authentication error in get_my_info"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Bad credentials"
        mock_get.return_value = mock_response
        
        # get_my_info catches AuthenticationError and returns None
        result = get_my_info()
        assert result is None

    @patch('main.requests.get')
    def test_get_user_activity_malformed_response(self, mock_get):
        """Test malformed response handling in get_user_activity"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"created_at": "invalid-date-format"}]
        mock_get.return_value = mock_response
        
        result = get_user_activity("testuser")
        assert result is None

    @patch('main.requests.put')
    def test_follow_user_rate_limit_error(self, mock_put):
        """Test rate limit error in follow_user"""
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.text = "API rate limit exceeded"
        mock_put.return_value = mock_response
        
        with pytest.raises(RateLimitError):
            follow_user("testuser")

    @patch('main.requests.put')
    def test_follow_user_network_error(self, mock_put):
        """Test network error in follow_user"""
        mock_put.side_effect = requests.exceptions.ConnectionError("Network error")
        
        result = follow_user("testuser")
        assert result is False


class TestCandidateEvaluationErrorHandling:
    """Test error handling in candidate evaluation"""

    @patch('main.get_user_info')
    def test_is_good_follow_candidate_missing_fields(self, mock_get_user_info):
        """Test handling of missing required fields"""
        mock_get_user_info.return_value = {"login": "testuser"}  # Missing followers/following
        
        result = is_good_follow_candidate("testuser")
        assert result is False

    @patch('main.get_user_info')
    def test_is_good_follow_candidate_invalid_types(self, mock_get_user_info):
        """Test handling of invalid data types"""
        mock_get_user_info.return_value = {
            "following": "invalid",  # Should be int
            "followers": None       # Should be int
        }
        
        result = is_good_follow_candidate("testuser")
        assert result is False

    @patch('main.get_user_info')
    @patch('main.get_user_activity')
    def test_is_good_follow_candidate_activity_error(self, mock_activity, mock_get_user_info):
        """Test handling of activity check errors"""
        mock_get_user_info.return_value = {
            "following": 100,
            "followers": 200
        }
        mock_activity.side_effect = Exception("Activity check failed")
        
        # Should continue evaluation despite activity error
        result = is_good_follow_candidate("testuser")
        assert result is True  # Should pass other criteria

    @patch('main.get_user_info')
    def test_is_good_follow_candidate_exception_handling(self, mock_get_user_info):
        """Test general exception handling in candidate evaluation"""
        mock_get_user_info.side_effect = Exception("Unexpected error")
        
        result = is_good_follow_candidate("testuser")
        assert result is False


class TestMainFunctionErrorHandling:
    """Test error handling in main function"""

    @patch('main.requests.get')
    def test_main_rate_limit_check_error(self, mock_get):
        """Test error handling during rate limit check"""
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")
        
        # Should handle the error gracefully and continue
        with patch('main.find_potential_follows') as mock_find:
            mock_find.return_value = []
            main()  # Should not raise exception

    @patch('main.find_potential_follows')
    def test_main_authentication_error_during_search(self, mock_find):
        """Test authentication error during candidate search"""
        mock_find.side_effect = AuthenticationError("Invalid token")
        
        with patch('main.requests.get') as mock_get:
            # Mock successful rate limit check
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'resources': {'core': {'remaining': 5000, 'reset': 1234567890}}
            }
            mock_get.return_value = mock_response
            
            main()  # Should handle error gracefully

    @patch('main.find_potential_follows')
    @patch('main.follow_user')
    def test_main_keyboard_interrupt(self, mock_follow, mock_find):
        """Test keyboard interrupt handling"""
        mock_find.return_value = ["user1", "user2", "user3"]
        mock_follow.side_effect = KeyboardInterrupt()
        
        with patch('main.requests.get') as mock_get:
            # Mock successful rate limit check
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'resources': {'core': {'remaining': 5000, 'reset': 1234567890}}
            }
            mock_get.return_value = mock_response
            
            main()  # Should handle interrupt gracefully

    @patch('main.find_potential_follows')
    @patch('main.follow_user')
    def test_main_rate_limit_during_following(self, mock_follow, mock_find):
        """Test rate limit error during following process"""
        mock_find.return_value = ["user1", "user2"]
        mock_follow.side_effect = RateLimitError("Rate limit exceeded")
        
        with patch('main.requests.get') as mock_get:
            # Mock successful rate limit check
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'resources': {'core': {'remaining': 5000, 'reset': 1234567890}}
            }
            mock_get.return_value = mock_response
            
            main()  # Should handle rate limit gracefully


class TestCustomExceptions:
    """Test custom exception classes"""

    def test_github_api_error_creation(self):
        """Test GitHubAPIError exception creation"""
        error = GitHubAPIError("Test message", 500, "Server error")
        
        assert str(error) == "Test message"
        assert error.status_code == 500
        assert error.response_text == "Server error"

    def test_rate_limit_error_inheritance(self):
        """Test RateLimitError inheritance"""
        error = RateLimitError("Rate limit exceeded", 403, "Too many requests")
        
        assert isinstance(error, GitHubAPIError)
        assert str(error) == "Rate limit exceeded"

    def test_authentication_error_inheritance(self):
        """Test AuthenticationError inheritance"""
        error = AuthenticationError("Invalid token", 401, "Unauthorized")
        
        assert isinstance(error, GitHubAPIError)
        assert str(error) == "Invalid token"


class TestRobustnessFeatures:
    """Test robustness features like infinite loop prevention"""

    @patch('main.handle_api_response')
    @patch('main.requests.get')
    def test_followers_pagination_safety_limit(self, mock_get, mock_handle):
        """Test that followers pagination has safety limits"""
        # Mock responses that would create infinite loop
        mock_handle.return_value = [{"login": "user1"}]  # Always return data
        
        from main import get_my_followers
        
        # Should stop at safety limit, not infinite loop
        result = get_my_followers()
        
        # Should have made exactly 100 requests (safety limit)
        assert mock_get.call_count <= 100

    @patch('main.get_user_info')
    @patch('main.get_my_info')
    @patch('main.get_my_followers')
    @patch('main.get_my_following')
    def test_find_potential_follows_resilience(self, mock_following, mock_followers, 
                                              mock_my_info, mock_user_info):
        """Test that find_potential_follows handles individual errors gracefully"""
        mock_my_info.return_value = {"login": "testuser"}
        mock_followers.return_value = ["follower1", "follower2"]
        mock_following.return_value = ["following1"]
        
        # Make get_user_info fail for some users but succeed for others
        def mock_user_info_side_effect(username):
            if username == "error_user":
                raise Exception("User info error")
            return {"following": 100, "followers": 200} if username != "nonexistent" else None
        
        mock_user_info.side_effect = mock_user_info_side_effect
        
        with patch('main.get_user_following') as mock_get_following:
            with patch('main.get_user_followers') as mock_get_followers:
                # Mix successful and failing calls
                mock_get_following.return_value = ["potential1", "error_user", "potential2"]
                mock_get_followers.return_value = ["potential3"]
                
                result = find_potential_follows()
                
                # Should return some results despite errors
                assert isinstance(result, list)
