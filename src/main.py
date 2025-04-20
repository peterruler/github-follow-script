import requests
import random
import time
from datetime import datetime, timedelta

# Constants and configuration
GITHUB_API = "https://api.github.com"
# You'll need to create a personal access token at https://github.com/settings/tokens
# with 'user:follow' permissions
TOKEN = "YOUR_TOKEN"
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
MAX_FOLLOWS_PER_DAY = 20  # Limit to avoid appearing as spam/bot

# Helper functions
def get_user_info(username):
    """Gets information about a GitHub user"""
    response = requests.get(f"{GITHUB_API}/users/{username}", headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    return None

def get_my_info():
    """Gets information about the authenticated user"""
    response = requests.get(f"{GITHUB_API}/user", headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    return None

def get_user_activity(username):
    """Checks the date of the user's last activity"""
    response = requests.get(f"{GITHUB_API}/users/{username}/events/public", headers=HEADERS)
    if response.status_code == 200:
        events = response.json()
        if events:  # If there are events
            latest_event_date = datetime.strptime(events[0]['created_at'], "%Y-%m-%dT%H:%M:%SZ")
            days_since_activity = (datetime.now() - latest_event_date).days
            return days_since_activity
    return None

def get_my_followers():
    """Gets list of followers of the authenticated user"""
    followers = []
    page = 1
    while True:
        response = requests.get(f"{GITHUB_API}/user/followers?page={page}&per_page=100", headers=HEADERS)
        if response.status_code == 200:
            page_followers = response.json()
            if not page_followers:
                break
            followers.extend([follower['login'] for follower in page_followers])
            page += 1
        else:
            break
    return followers

def get_my_following():
    """Gets list of who the authenticated user follows"""
    following = []
    page = 1
    while True:
        response = requests.get(f"{GITHUB_API}/user/following?page={page}&per_page=100", headers=HEADERS)
        if response.status_code == 200:
            page_following = response.json()
            if not page_following:
                break
            following.extend([follow['login'] for follow in page_following])
            page += 1
        else:
            break
    return following

def get_user_followers(username):
    """Gets some followers of a specific user"""
    followers = []
    response = requests.get(f"{GITHUB_API}/users/{username}/followers?per_page=100", headers=HEADERS)
    if response.status_code == 200:
        followers = [follower['login'] for follower in response.json()]
    return followers

def get_user_following(username):
    """Gets who a specific user follows"""
    following = []
    response = requests.get(f"{GITHUB_API}/users/{username}/following?per_page=100", headers=HEADERS)
    if response.status_code == 200:
        following = [follow['login'] for follow in response.json()]
    return following

def follow_user(username):
    """Follows a specific user"""
    response = requests.put(f"{GITHUB_API}/user/following/{username}", headers=HEADERS)
    return response.status_code == 204  # 204 No Content means success

def is_good_follow_candidate(username):
    """Determines if a user is a good candidate to follow"""
    user_info = get_user_info(username)
    if not user_info:
        return False
    
    # Check basic criteria
    following_count = user_info['following']
    followers_count = user_info['followers']
    
    if following_count > MAX_FOLLOWING:
        return False
    if followers_count < MIN_FOLLOWERS:
        return False
    if followers_count > MAX_FOLLOWERS:
        return False
    
    # Check recent activity
    days_inactive = get_user_activity(username)
    if days_inactive and days_inactive > INACTIVITY_DAYS:
        return False
    
    # Check follow ratio
    if followers_count > 0:
        follow_ratio = following_count / followers_count
        if follow_ratio >= FOLLOW_RATIO_THRESHOLD:
            return True
    
    return False

def find_potential_follows():
    """Finds potential people to follow"""
    my_info = get_my_info()
    if not my_info:
        print("Could not get your information. Check your token.")
        return []
    
    my_username = my_info['login']
    my_followers = get_my_followers()
    my_following = get_my_following()
    
    # Strategy 1: Check followers of your followers
    potential_users = set()
    
    # Get some random followers for analysis
    sample_followers = random.sample(my_followers, min(10, len(my_followers))) if my_followers else []
    
    for follower in sample_followers:
        follower_following = get_user_following(follower)
        for user in follower_following:
            if user != my_username and user not in my_following and user not in my_followers:
                potential_users.add(user)
    
    # Strategy 2: Check who your followers also follow
    for follower in sample_followers:
        follower_followers = get_user_followers(follower)
        for user in follower_followers:
            if user != my_username and user not in my_following and user not in my_followers:
                potential_users.add(user)
    
    # Filter and limit candidates
    good_candidates = []
    for user in potential_users:
        if is_good_follow_candidate(user):
            good_candidates.append(user)
            if len(good_candidates) >= MAX_FOLLOWS_PER_DAY:
                break
    
    return good_candidates

def main():
    print("Starting GitHub follow process...")
    
    # Check GitHub API limits
    rate_limit = requests.get(f"{GITHUB_API}/rate_limit", headers=HEADERS).json()
    remaining = rate_limit['resources']['core']['remaining']
    print(f"Remaining API requests: {remaining}")
    
    if remaining < 100:
        print("Few requests available. Try again later.")
        return
    
    # Find potential candidates
    candidates = find_potential_follows()
    if not candidates:
        print("No suitable candidates to follow were found.")
        return
    
    print(f"Found {len(candidates)} potential candidates to follow.")
    
    # Follow candidates with interval between requests
    followed_count = 0
    for username in candidates:
        success = follow_user(username)
        if success:
            print(f"Successfully followed: {username}")
            followed_count += 1
        else:
            print(f"Failed to follow: {username}")
        
        # Pause to avoid request rate limits
        time.sleep(random.uniform(2, 5))
    
    print(f"Process completed. Followed {followed_count} new users.")

if __name__ == "__main__":
    main()
