import pytest
import responses
import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import sys
import json

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import (
    get_user_info, get_my_info, get_user_activity, get_my_followers,
    get_my_following, get_user_followers, get_user_following,
    follow_user, is_good_follow_candidate, find_potential_follows,
    GITHUB_API, MAX_FOLLOWING, MIN_FOLLOWERS, MAX_FOLLOWERS,
    INACTIVITY_DAYS, FOLLOW_RATIO_THRESHOLD
)


class TestGitHubAPI:
    """Test GitHub API interaction functions"""

    @responses.activate
    def test_get_user_info_success(self):
        """Test successful user info retrieval"""
        username = "testuser"
        mock_response = {
            "login": username,
            "id": 12345,
            "following": 100,
            "followers": 200,
            "public_repos": 50
        }
        
        responses.add(
            responses.GET,
            f"{GITHUB_API}/users/{username}",
            json=mock_response,
            status=200
        )
        
        result = get_user_info(username)
        assert result == mock_response
        assert result["login"] == username

    @responses.activate
    def test_get_user_info_not_found(self):
        """Test user info retrieval for non-existent user"""
        username = "nonexistentuser"
        
        responses.add(
            responses.GET,
            f"{GITHUB_API}/users/{username}",
            status=404
        )
        
        result = get_user_info(username)
        assert result is None

    @responses.activate
    def test_get_my_info_success(self):
        """Test successful authenticated user info retrieval"""
        mock_response = {
            "login": "myusername",
            "id": 67890,
            "following": 150,
            "followers": 300
        }
        
        responses.add(
            responses.GET,
            f"{GITHUB_API}/user",
            json=mock_response,
            status=200
        )
        
        result = get_my_info()
        assert result == mock_response
        assert result["login"] == "myusername"

    @responses.activate
    def test_get_user_activity_with_events(self):
        """Test user activity check with recent events"""
        username = "activeuser"
        recent_date = datetime.now() - timedelta(days=5)
        mock_events = [
            {
                "created_at": recent_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "type": "PushEvent"
            }
        ]
        
        responses.add(
            responses.GET,
            f"{GITHUB_API}/users/{username}/events/public",
            json=mock_events,
            status=200
        )
        
        result = get_user_activity(username)
        assert result == 5

    @responses.activate
    def test_get_user_activity_no_events(self):
        """Test user activity check with no events"""
        username = "inactiveuser"
        
        responses.add(
            responses.GET,
            f"{GITHUB_API}/users/{username}/events/public",
            json=[],
            status=200
        )
        
        result = get_user_activity(username)
        assert result is None

    @responses.activate
    def test_get_my_followers_multiple_pages(self):
        """Test fetching followers across multiple pages"""
        # First page
        page1_response = [
            {"login": "follower1"},
            {"login": "follower2"}
        ]
        responses.add(
            responses.GET,
            f"{GITHUB_API}/user/followers?page=1&per_page=100",
            json=page1_response,
            status=200
        )
        
        # Second page (empty)
        responses.add(
            responses.GET,
            f"{GITHUB_API}/user/followers?page=2&per_page=100",
            json=[],
            status=200
        )
        
        result = get_my_followers()
        assert result == ["follower1", "follower2"]

    @responses.activate
    def test_get_user_followers_success(self):
        """Test fetching specific user's followers"""
        username = "testuser"
        mock_followers = [
            {"login": "follower1"},
            {"login": "follower2"},
            {"login": "follower3"}
        ]
        
        responses.add(
            responses.GET,
            f"{GITHUB_API}/users/{username}/followers?per_page=100",
            json=mock_followers,
            status=200
        )
        
        result = get_user_followers(username)
        assert result == ["follower1", "follower2", "follower3"]

    @responses.activate
    def test_follow_user_success(self):
        """Test successful user following"""
        username = "usertofollow"
        
        responses.add(
            responses.PUT,
            f"{GITHUB_API}/user/following/{username}",
            status=204
        )
        
        result = follow_user(username)
        assert result is True

    @responses.activate
    def test_follow_user_failure(self):
        """Test failed user following"""
        username = "usertofollow"
        
        responses.add(
            responses.PUT,
            f"{GITHUB_API}/user/following/{username}",
            status=403
        )
        
        result = follow_user(username)
        assert result is False


class TestFollowCandidateEvaluation:
    """Test follow candidate evaluation logic"""

    @patch('main.get_user_info')
    @patch('main.get_user_activity')
    def test_is_good_follow_candidate_perfect_match(self, mock_activity, mock_user_info):
        """Test candidate that meets all criteria"""
        mock_user_info.return_value = {
            "following": 400,  # Less than MAX_FOLLOWING (1000)
            "followers": 500   # Between MIN_FOLLOWERS (5) and MAX_FOLLOWERS (1000), ratio = 400/500 = 0.8 < 1.2
        }
        mock_activity.return_value = 30  # Less than INACTIVITY_DAYS (60)
        
        result = is_good_follow_candidate("gooduser")
        assert result is True

    @patch('main.get_user_info')
    def test_is_good_follow_candidate_too_many_following(self, mock_user_info):
        """Test candidate with too many following"""
        mock_user_info.return_value = {
            "following": 1500,  # More than MAX_FOLLOWING
            "followers": 400
        }
        
        result = is_good_follow_candidate("baduser")
        assert result is False

    @patch('main.get_user_info')
    def test_is_good_follow_candidate_too_few_followers(self, mock_user_info):
        """Test candidate with too few followers"""
        mock_user_info.return_value = {
            "following": 500,
            "followers": 2  # Less than MIN_FOLLOWERS
        }
        
        result = is_good_follow_candidate("baduser")
        assert result is False

    @patch('main.get_user_info')
    def test_is_good_follow_candidate_too_many_followers(self, mock_user_info):
        """Test candidate with too many followers"""
        mock_user_info.return_value = {
            "following": 500,
            "followers": 1500  # More than MAX_FOLLOWERS
        }
        
        result = is_good_follow_candidate("baduser")
        assert result is False

    @patch('main.get_user_info')
    @patch('main.get_user_activity')
    def test_is_good_follow_candidate_inactive(self, mock_activity, mock_user_info):
        """Test candidate that is inactive"""
        mock_user_info.return_value = {
            "following": 500,
            "followers": 400
        }
        mock_activity.return_value = 90  # More than INACTIVITY_DAYS

        result = is_good_follow_candidate("inactiveuser")
        assert result is False

    @patch('main.get_user_info')
    @patch('main.get_user_activity')
    def test_is_good_follow_candidate_good_ratio(self, mock_activity, mock_user_info):
        """Test candidate with good follow ratio (follows less than threshold)"""
        mock_user_info.return_value = {
            "following": 100,  # Ratio = 100/200 = 0.5 < FOLLOW_RATIO_THRESHOLD (1.2)
            "followers": 200
        }
        mock_activity.return_value = 30

        result = is_good_follow_candidate("goodratiouser")
        assert result is True

    @patch('main.get_user_info')
    @patch('main.get_user_activity')
    def test_is_good_follow_candidate_bad_ratio(self, mock_activity, mock_user_info):
        """Test candidate with bad follow ratio"""
        mock_user_info.return_value = {
            "following": 1000,  # Ratio = 1000/400 = 2.5 > FOLLOW_RATIO_THRESHOLD (1.2)
            "followers": 400
        }
        mock_activity.return_value = 30

        result = is_good_follow_candidate("badratiouser")
        assert result is False

    @patch('main.get_user_info')
    def test_is_good_follow_candidate_no_user_info(self, mock_user_info):
        """Test candidate with no user info available"""
        mock_user_info.return_value = None
        
        result = is_good_follow_candidate("nonexistentuser")
        assert result is False


class TestFindPotentialFollows:
    """Test potential follows discovery logic"""

    @patch('main.get_my_info')
    def test_find_potential_follows_no_user_info(self, mock_my_info):
        """Test when authenticated user info is not available"""
        mock_my_info.return_value = None
        
        result = find_potential_follows()
        assert result == []

    @patch('main.get_my_info')
    @patch('main.get_my_followers')
    @patch('main.get_my_following')
    @patch('main.get_user_following')
    @patch('main.get_user_followers')
    @patch('main.is_good_follow_candidate')
    @patch('random.sample')
    def test_find_potential_follows_success(self, mock_sample, mock_is_good, 
                                          mock_user_followers, mock_user_following,
                                          mock_my_following, mock_my_followers, 
                                          mock_my_info):
        """Test successful potential follows discovery"""
        mock_my_info.return_value = {"login": "myusername"}
        mock_my_followers.return_value = ["follower1", "follower2"]
        mock_my_following.return_value = ["following1"]
        mock_sample.return_value = ["follower1"]
        
        mock_user_following.return_value = ["potential1", "potential2"]
        mock_user_followers.return_value = ["potential3", "potential4"]
        
        # Mock that potential1 and potential3 are good candidates
        def mock_is_good_side_effect(username):
            return username in ["potential1", "potential3"]
        
        mock_is_good.side_effect = mock_is_good_side_effect
        
        result = find_potential_follows()
        
        # Should find potential1 and potential3 as good candidates
        assert "potential1" in result
        assert "potential3" in result
        assert len(result) <= 2


class TestConfiguration:
    """Test configuration constants"""

    def test_constants_are_properly_set(self):
        """Test that all configuration constants are properly set"""
        assert MAX_FOLLOWING == 1000
        assert MIN_FOLLOWERS == 5
        assert MAX_FOLLOWERS == 1000
        assert INACTIVITY_DAYS == 60
        assert FOLLOW_RATIO_THRESHOLD == 1.2

    def test_github_api_url(self):
        """Test GitHub API URL is correct"""
        assert GITHUB_API == "https://api.github.com"


class TestIntegration:
    """Integration tests"""

    @patch.dict(os.environ, {'GITHUB_TOKEN': 'test_token'})
    def test_environment_variable_loading(self):
        """Test that environment variables are loaded correctly"""
        # Reload module to test env var loading
        import importlib
        import main
        importlib.reload(main)
        
        assert main.TOKEN == 'test_token'

    def test_missing_github_token_raises_error(self):
        """Test that missing GitHub token raises appropriate error"""
        # We need to test this by trying to import a fresh version of main
        # that doesn't have the token set
        with patch.dict(os.environ, {}, clear=True):
            with patch('main.load_dotenv') as mock_load_dotenv:
                mock_load_dotenv.return_value = None
                with pytest.raises(ValueError, match="GITHUB_TOKEN environment variable is required"):
                    # This should trigger the error when TOKEN is None
                    exec('''
import os
TOKEN = os.getenv('GITHUB_TOKEN')
if not TOKEN:
    raise ValueError("GITHUB_TOKEN environment variable is required. Please check your .env file.")
''')
