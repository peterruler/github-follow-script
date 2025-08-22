import requests
import random
import time
import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('github_follow.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Custom exceptions
class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors"""
    def __init__(self, message, status_code=None, response_text=None):
        self.message = message
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(self.message)

class RateLimitError(GitHubAPIError):
    """Exception for API rate limit exceeded"""
    pass

class AuthenticationError(GitHubAPIError):
    """Exception for authentication failures"""
    pass

# Constants and configuration
GITHUB_API = "https://api.github.com"
# You'll need to create a personal access token at https://github.com/settings/tokens
# with 'user:follow' permissions
TOKEN = os.getenv('GITHUB_TOKEN')
if not TOKEN:
    raise ValueError("GITHUB_TOKEN environment variable is required. Please check your .env file.")

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Follow criteria settings
MAX_FOLLOWING = 1000  # People with more following than this are less likely to follow back
MIN_FOLLOWERS = 5     # Too few followers may indicate inactive account
MAX_FOLLOWERS = 1000  # Too many followers may indicate that the person doesn't follow back
INACTIVITY_DAYS = 60  # Days without activity to consider account potentially inactive
FOLLOW_RATIO_THRESHOLD = 1.2  # Following/followers ratio (>1 indicates person tends to follow)
MAX_FOLLOWS_PER_DAY = 200  # Limit to avoid appearing as spam/bot

# Helper functions
def handle_api_response(response, context="API request"):
    """Handle API response and raise appropriate exceptions"""
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 204:
        return True  # Success for operations like follow
    elif response.status_code == 401:
        logger.error(f"Authentication failed: {context}")
        raise AuthenticationError("Invalid or expired GitHub token", response.status_code, response.text)
    elif response.status_code == 403:
        if 'rate limit' in response.text.lower():
            logger.error(f"Rate limit exceeded: {context}")
            raise RateLimitError("GitHub API rate limit exceeded", response.status_code, response.text)
        else:
            logger.error(f"Forbidden access: {context}")
            raise GitHubAPIError("Access forbidden", response.status_code, response.text)
    elif response.status_code == 404:
        logger.warning(f"Resource not found: {context}")
        return None
    else:
        logger.error(f"API error {response.status_code}: {context}")
        raise GitHubAPIError(f"API request failed", response.status_code, response.text)

def get_user_info(username):
    """Gets information about a GitHub user"""
    try:
        logger.debug(f"Fetching user info for: {username}")
        response = requests.get(f"{GITHUB_API}/users/{username}", headers=HEADERS, timeout=10)
        return handle_api_response(response, f"get user info for {username}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error while fetching user info for {username}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching user info for {username}: {e}")
        return None

def get_my_info():
    """Gets information about the authenticated user"""
    try:
        logger.debug("Fetching authenticated user info")
        response = requests.get(f"{GITHUB_API}/user", headers=HEADERS, timeout=10)
        return handle_api_response(response, "get authenticated user info")
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error while fetching user info: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching user info: {e}")
        return None

def get_user_activity(username):
    """Checks the date of the user's last activity"""
    try:
        logger.debug(f"Fetching activity for user: {username}")
        response = requests.get(f"{GITHUB_API}/users/{username}/events/public", headers=HEADERS, timeout=10)
        events = handle_api_response(response, f"get activity for {username}")
        
        if events and len(events) > 0:
            try:
                latest_event_date = datetime.strptime(events[0]['created_at'], "%Y-%m-%dT%H:%M:%SZ")
                days_since_activity = (datetime.now() - latest_event_date).days
                return days_since_activity
            except (KeyError, ValueError) as e:
                logger.warning(f"Error parsing activity date for {username}: {e}")
                return None
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error while fetching activity for {username}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching activity for {username}: {e}")
        return None

def get_my_followers():
    """Gets list of followers of the authenticated user"""
    followers = []
    page = 1
    try:
        while True:
            logger.debug(f"Fetching followers page {page}")
            response = requests.get(f"{GITHUB_API}/user/followers?page={page}&per_page=100", 
                                  headers=HEADERS, timeout=10)
            page_followers = handle_api_response(response, f"get followers page {page}")
            
            if not page_followers:
                break
            followers.extend([follower['login'] for follower in page_followers])
            page += 1
            
            # Safety limit to prevent infinite loops
            if page > 100:
                logger.warning("Reached maximum page limit for followers")
                break
                
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error while fetching followers: {e}")
    except Exception as e:
        logger.error(f"Unexpected error fetching followers: {e}")
    
    return followers

def get_my_following():
    """Gets list of who the authenticated user follows"""
    following = []
    page = 1
    try:
        while True:
            logger.debug(f"Fetching following page {page}")
            response = requests.get(f"{GITHUB_API}/user/following?page={page}&per_page=100", 
                                  headers=HEADERS, timeout=10)
            page_following = handle_api_response(response, f"get following page {page}")
            
            if not page_following:
                break
            following.extend([follow['login'] for follow in page_following])
            page += 1
            
            # Safety limit to prevent infinite loops
            if page > 100:
                logger.warning("Reached maximum page limit for following")
                break
                
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error while fetching following list: {e}")
    except Exception as e:
        logger.error(f"Unexpected error fetching following list: {e}")
    
    return following

def get_user_followers(username):
    """Gets some followers of a specific user"""
    try:
        logger.debug(f"Fetching followers for user: {username}")
        response = requests.get(f"{GITHUB_API}/users/{username}/followers?per_page=100", 
                              headers=HEADERS, timeout=10)
        followers_data = handle_api_response(response, f"get followers for {username}")
        
        if followers_data:
            return [follower['login'] for follower in followers_data]
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error while fetching followers for {username}: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching followers for {username}: {e}")
        return []

def get_user_following(username):
    """Gets who a specific user follows"""
    try:
        logger.debug(f"Fetching following list for user: {username}")
        response = requests.get(f"{GITHUB_API}/users/{username}/following?per_page=100", 
                              headers=HEADERS, timeout=10)
        following_data = handle_api_response(response, f"get following for {username}")
        
        if following_data:
            return [follow['login'] for follow in following_data]
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error while fetching following for {username}: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching following for {username}: {e}")
        return []

def follow_user(username):
    """Follows a specific user"""
    try:
        logger.debug(f"Attempting to follow user: {username}")
        response = requests.put(f"{GITHUB_API}/user/following/{username}", headers=HEADERS, timeout=10)
        result = handle_api_response(response, f"follow user {username}")
        if result:
            logger.info(f"Successfully followed: {username}")
        return result is True
    except RateLimitError:
        logger.error(f"Rate limit exceeded while trying to follow {username}")
        raise
    except AuthenticationError:
        logger.error(f"Authentication failed while trying to follow {username}")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error while following {username}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error following {username}: {e}")
        return False

def is_good_follow_candidate(username):
    """Determines if a user is a good candidate to follow"""
    try:
        user_info = get_user_info(username)
        if not user_info:
            logger.debug(f"No user info available for {username}")
            return False
        
        # Validate required fields
        required_fields = ['following', 'followers']
        for field in required_fields:
            if field not in user_info:
                logger.warning(f"Missing required field '{field}' for user {username}")
                return False
        
        # Check basic criteria
        following_count = user_info['following']
        followers_count = user_info['followers']
        
        # Validate numeric values
        if not isinstance(following_count, int) or not isinstance(followers_count, int):
            logger.warning(f"Invalid follower counts for user {username}")
            return False
        
        if following_count > MAX_FOLLOWING:
            logger.debug(f"{username} follows too many people ({following_count} > {MAX_FOLLOWING})")
            return False
        if followers_count < MIN_FOLLOWERS:
            logger.debug(f"{username} has too few followers ({followers_count} < {MIN_FOLLOWERS})")
            return False
        if followers_count > MAX_FOLLOWERS:
            logger.debug(f"{username} has too many followers ({followers_count} > {MAX_FOLLOWERS})")
            return False
        
        # Check recent activity
        try:
            days_inactive = get_user_activity(username)
            if days_inactive and days_inactive > INACTIVITY_DAYS:
                logger.debug(f"{username} is inactive ({days_inactive} days > {INACTIVITY_DAYS})")
                return False
        except Exception as e:
            logger.warning(f"Could not check activity for {username}: {e}")
            # Continue evaluation without activity check
        
        # Check follow ratio
        if followers_count > 0:
            follow_ratio = following_count / followers_count
            if follow_ratio >= FOLLOW_RATIO_THRESHOLD:
                logger.debug(f"{username} has bad follow ratio ({follow_ratio:.2f} >= {FOLLOW_RATIO_THRESHOLD})")
                return False  # Bad ratio - follows too many compared to followers
        
        logger.debug(f"{username} is a good follow candidate")
        return True  # All criteria passed
        
    except Exception as e:
        logger.error(f"Error evaluating follow candidate {username}: {e}")
        return False

def find_potential_follows():
    """Finds potential people to follow"""
    try:
        logger.info("Starting search for potential follows")
        my_info = get_my_info()
        if not my_info:
            logger.error("Could not get authenticated user information. Check your token.")
            return []
        
        my_username = my_info.get('login')
        if not my_username:
            logger.error("No username found in user info")
            return []
        
        logger.info(f"Authenticated as: {my_username}")
        
        my_followers = get_my_followers()
        my_following = get_my_following()
        
        logger.info(f"You have {len(my_followers)} followers and follow {len(my_following)} users")
        
        # Strategy 1: Check followers of your followers
        potential_users = set()
        
        # Get some random followers for analysis
        sample_followers = random.sample(my_followers, min(10, len(my_followers))) if my_followers else []
        logger.info(f"Analyzing {len(sample_followers)} sample followers")
        
        for follower in sample_followers:
            try:
                follower_following = get_user_following(follower)
                for user in follower_following:
                    if user != my_username and user not in my_following and user not in my_followers:
                        potential_users.add(user)
            except Exception as e:
                logger.warning(f"Error analyzing follower {follower}: {e}")
                continue
        
        # Strategy 2: Check who your followers also follow
        for follower in sample_followers:
            try:
                follower_followers = get_user_followers(follower)
                for user in follower_followers:
                    if user != my_username and user not in my_following and user not in my_followers:
                        potential_users.add(user)
            except Exception as e:
                logger.warning(f"Error analyzing follower's followers for {follower}: {e}")
                continue
        
        logger.info(f"Found {len(potential_users)} potential users to evaluate")
        
        # Filter and limit candidates
        good_candidates = []
        evaluated_count = 0
        
        for user in potential_users:
            try:
                evaluated_count += 1
                if evaluated_count % 10 == 0:
                    logger.info(f"Evaluated {evaluated_count}/{len(potential_users)} candidates")
                
                if is_good_follow_candidate(user):
                    good_candidates.append(user)
                    if len(good_candidates) >= MAX_FOLLOWS_PER_DAY:
                        logger.info(f"Reached maximum candidates limit: {MAX_FOLLOWS_PER_DAY}")
                        break
            except Exception as e:
                logger.warning(f"Error evaluating candidate {user}: {e}")
                continue
        
        logger.info(f"Found {len(good_candidates)} good candidates after evaluation")
        return good_candidates
        
    except Exception as e:
        logger.error(f"Unexpected error in find_potential_follows: {e}")
        return []

def main():
    """Main function to execute the GitHub follow process"""
    try:
        logger.info("Starting GitHub follow process...")
        
        # Check GitHub API limits
        try:
            response = requests.get(f"{GITHUB_API}/rate_limit", headers=HEADERS, timeout=10)
            rate_limit_data = handle_api_response(response, "check rate limit")
            
            if rate_limit_data:
                remaining = rate_limit_data['resources']['core']['remaining']
                reset_time = datetime.fromtimestamp(rate_limit_data['resources']['core']['reset'])
                logger.info(f"API requests remaining: {remaining}")
                logger.info(f"Rate limit resets at: {reset_time}")
                
                if remaining < 100:
                    logger.warning("Few API requests remaining. Consider waiting for rate limit reset.")
                    print(f"Only {remaining} API requests remaining. Rate limit resets at {reset_time}")
                    return
            else:
                logger.warning("Could not check rate limit, proceeding with caution")
                
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            print("Could not check API rate limit. Proceeding with caution...")
        
        # Find potential candidates
        try:
            candidates = find_potential_follows()
        except RateLimitError:
            logger.error("Rate limit exceeded during candidate search")
            print("Rate limit exceeded. Please try again later.")
            return
        except AuthenticationError:
            logger.error("Authentication failed during candidate search")
            print("Authentication failed. Please check your GitHub token.")
            return
        except Exception as e:
            logger.error(f"Error finding candidates: {e}")
            print(f"Error occurred while finding candidates: {e}")
            return
        
        if not candidates:
            logger.info("No suitable candidates to follow were found")
            print("No suitable candidates to follow were found.")
            return
        
        logger.info(f"Found {len(candidates)} potential candidates to follow")
        print(f"Found {len(candidates)} potential candidates to follow.")
        
        # Follow candidates with interval between requests
        followed_count = 0
        failed_count = 0
        
        for i, username in enumerate(candidates, 1):
            try:
                logger.info(f"Processing candidate {i}/{len(candidates)}: {username}")
                success = follow_user(username)
                
                if success:
                    print(f"✓ Successfully followed: {username}")
                    followed_count += 1
                else:
                    print(f"✗ Failed to follow: {username}")
                    failed_count += 1
                
                # Pause to avoid request rate limits (only if not the last user)
                if i < len(candidates):
                    sleep_time = random.uniform(2, 5)
                    logger.debug(f"Sleeping for {sleep_time:.2f} seconds")
                    time.sleep(sleep_time)
                    
            except RateLimitError:
                logger.error("Rate limit exceeded during following process")
                print(f"Rate limit exceeded after following {followed_count} users. Stopping.")
                break
            except AuthenticationError:
                logger.error("Authentication failed during following process")
                print("Authentication failed. Please check your GitHub token.")
                break
            except KeyboardInterrupt:
                logger.info("Process interrupted by user")
                print(f"\nProcess interrupted. Followed {followed_count} users so far.")
                break
            except Exception as e:
                logger.error(f"Unexpected error following {username}: {e}")
                print(f"✗ Error following {username}: {e}")
                failed_count += 1
                continue
        
        # Final summary
        logger.info(f"Process completed. Followed: {followed_count}, Failed: {failed_count}")
        print(f"\n🎉 Process completed!")
        print(f"✓ Successfully followed: {followed_count} users")
        if failed_count > 0:
            print(f"✗ Failed to follow: {failed_count} users")
        
    except KeyboardInterrupt:
        logger.info("GitHub follow process interrupted by user")
        print("\nProcess interrupted by user.")
    except Exception as e:
        logger.error(f"Unexpected error in main process: {e}")
        print(f"An unexpected error occurred: {e}")
        print("Check the log file 'github_follow.log' for more details.")

if __name__ == "__main__":
    main()
