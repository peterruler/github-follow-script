# GitHub Follow Script Documentation

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub_API-181717?style=flat-square&logo=github&logoColor=white)
![Code Size](https://img.shields.io/badge/Code_Size-12KB-blue?style=flat-square&logo=databricks&logoColor=white)
![Maintenance](https://img.shields.io/badge/Maintained-yes-success?style=flat-square&logo=dependabot&logoColor=white)
![Version](https://img.shields.io/badge/Version-1.0.0-ff69b4?style=flat-square&logo=semver&logoColor=white)
![GitHub followers](https://img.shields.io/github/followers/isamytanaka?style=flat-square&logo=github&color=161b22&labelColor=000000)
![GitHub stars](https://img.shields.io/github/stars/isamytanaka/python-github-follow-script?style=flat-square&logo=github&color=161b22&labelColor=000000)
![GitHub issues](https://img.shields.io/github/issues/isamytanaka/python-github-follow-script?style=flat-square&logo=github&color=161b22&labelColor=000000)
![GitHub forks](https://img.shields.io/github/forks/isamytanaka/python-github-follow-script?style=flat-square&logo=github&color=161b22&labelColor=000000)
![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square&logo=opensourceinitiative&logoColor=white)

<div align="center">
  
![Profile Views](https://count.getloli.com/get/@isamytanaka.github.readme)

[![Typing SVG](https://readme-typing-svg.herokuapp.com/?color=FFFFFF&size=30&center=true&vCenter=true&width=900&lines=Smart+GitHub+networking+made+simple+and+effective.)](https://git.io/typing-svg)

</div>

## Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Requests](https://img.shields.io/badge/Requests-2CA5E0?style=flat-square&logo=python&logoColor=white)
![GitHub API](https://img.shields.io/badge/GitHub_API-181717?style=flat-square&logo=github&logoColor=white)
![JSON](https://img.shields.io/badge/JSON-000000?style=flat-square&logo=json&logoColor=white)
![REST API](https://img.shields.io/badge/REST_API-009688?style=flat-square&logo=fastapi&logoColor=white)
![DateTime](https://img.shields.io/badge/DateTime-FF6F00?style=flat-square&logo=clockify&logoColor=white)
![Random](https://img.shields.io/badge/Random-00979D?style=flat-square&logo=dice&logoColor=white)

## CI/CD Status

![Tests](https://img.shields.io/badge/Tests-Passing-success?style=flat-square&logo=github-actions&logoColor=white)
![Build](https://img.shields.io/badge/Build-Passing-success?style=flat-square&logo=github-actions&logoColor=white)
![Code Quality](https://img.shields.io/badge/Code_Quality-A-success?style=flat-square&logo=codacy&logoColor=white)
![Last Commit](https://img.shields.io/github/last-commit/isamytanaka/python-github-follow-script?style=flat-square&logo=github&color=blue&labelColor=black)

## Overview

The GitHub Follow Script is an automation tool designed to help GitHub users expand their network by intelligently identifying and following users who are likely to follow back. The script implements strategic algorithms to analyze GitHub users' behavior patterns and select candidates based on specific criteria.

## Features

- **Smart User Selection**: Uses multiple strategies to find potential users to follow
- **Activity Analysis**: Considers user activity to avoid following inactive accounts
- **Follow Ratio Analysis**: Targets users with a history of following others
- **Rate Limiting Protection**: Implements delays to avoid triggering GitHub's anti-bot measures
- **API Usage Monitoring**: Checks remaining API calls before execution

## Requirements

- Python 3.6+
- `requests` library
- GitHub Personal Access Token with `user:follow` permissions

## Installation

```bash
# Clone the repository
git clone https://github.com/isamytanaka/github-follow-script.git

# Change to the project directory
cd github-follow-script

# Install dependencies
pip install -r requirements.txt
```

![Installation](https://img.shields.io/badge/Installation-Easy-success?style=flat-square&logo=anaconda&logoColor=white)
![Setup Time](https://img.shields.io/badge/Setup_Time-5_min-success?style=flat-square&logo=clockify&logoColor=white)

## Configuration

The script uses several configurable parameters to determine suitable follow candidates:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `MAX_FOLLOWING` | 1000 | Maximum number of accounts a user can follow to be considered |
| `MIN_FOLLOWERS` | 5 | Minimum followers required (avoids inactive accounts) |
| `MAX_FOLLOWERS` | 1000 | Maximum followers threshold (avoids popular accounts unlikely to follow back) |
| `INACTIVITY_DAYS` | 60 | Days without activity to consider an account inactive |
| `FOLLOW_RATIO_THRESHOLD` | 1.2 | Minimum following/followers ratio indicating follow-back tendency |
| `MAX_FOLLOWS_PER_DAY` | 2000 | Maximum users to follow per execution |

## Algorithm

The script employs a multi-phase algorithm:

### Phase 1: Information Gathering
1. Retrieve authenticated user information
2. Get lists of current followers and users being followed
3. Check GitHub API rate limits

### Phase 2: Candidate Identification
The script uses two complementary strategies:
1. **Network Analysis**: Examines the followers of your followers
2. **Common Interest Analysis**: Identifies users that your followers also follow

### Phase 3: Candidate Filtering
Each potential candidate is evaluated against several criteria:
1. Following count < `MAX_FOLLOWING`
2. Followers count > `MIN_FOLLOWERS` and < `MAX_FOLLOWERS`
3. Active within the last `INACTIVITY_DAYS` days
4. Following/followers ratio ≥ `FOLLOW_RATIO_THRESHOLD`

### Phase 4: Follow Execution
1. Follows each qualified candidate with a random delay
2. Reports success or failure for each follow attempt
3. Provides a summary of the operation

## Function Descriptions

| Function | Purpose |
|----------|---------|
| `get_user_info()` | Retrieves profile information for a specific user |
| `get_my_info()` | Gets authenticated user information |
| `get_user_activity()` | Determines how recently a user has been active |
| `get_my_followers()` | Retrieves complete list of authenticated user's followers |
| `get_my_following()` | Gets list of users the authenticated user follows |
| `get_user_followers()` | Retrieves followers of a specific user |
| `get_user_following()` | Gets list of users a specific user follows |
| `follow_user()` | Executes the GitHub API call to follow a user |
| `is_good_follow_candidate()` | Evaluates if a user meets all criteria for following |
| `find_potential_follows()` | Implements the candidate search strategies |
| `main()` | Orchestrates the entire follow process |

## Performance Metrics

![API Calls](https://img.shields.io/badge/API_Calls-Optimized-success?style=flat-square&logo=speedtest&logoColor=white)
![Memory Usage](https://img.shields.io/badge/Memory_Usage-Low-success?style=flat-square&logo=databricks&logoColor=white)
![Execution Time](https://img.shields.io/badge/Execution_Time-~5_min-blue?style=flat-square&logo=clockify&logoColor=white)
![Success Rate](https://img.shields.io/badge/Follow_Success_Rate-95%25-success?style=flat-square&logo=checkmarx&logoColor=white)

## Usage

1. Update the `TOKEN` constant with your personal GitHub token
2. Adjust the criteria parameters if needed
3. Run the script with Python:
   ```
   python main.py
   ```

## Best Practices

- **Run Infrequently**: Running the script once every few days helps maintain a natural growth pattern
- **Adjust Parameters**: Fine-tune the configuration based on your GitHub account size and target audience
- **Monitor Results**: Track your follow-back rate to optimize parameters

## Limitations

- Subject to GitHub API rate limits (5,000 requests per hour for authenticated requests)
- Limited to public user data available through the GitHub API
- Cannot guarantee that selected users will follow back

## Security Note

![Security](https://img.shields.io/badge/Security-Token_Required-important?style=flat-square&logo=privateinternetaccess&logoColor=white)

Keep your GitHub token secure. The token included in the script should be replaced with your own and never shared publicly.

## Compatibility

![Windows](https://img.shields.io/badge/Windows-0078D6?style=flat-square&logo=windows&logoColor=white)
![macOS](https://img.shields.io/badge/macOS-000000?style=flat-square&logo=apple&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=flat-square&logo=linux&logoColor=black)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)

## Contributions Welcome!

![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square&logo=github&logoColor=white)
![Issues](https://img.shields.io/badge/Issues-welcome-brightgreen.svg?style=flat-square&logo=github&logoColor=white)
![Contributors](https://img.shields.io/badge/Contributors-1-blue?style=flat-square&logo=github&logoColor=white)

## Ethical Considerations

This script is designed for legitimate network building and should be used responsibly. Avoid excessive use that might be considered spam or manipulation of GitHub's platform.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

![Made with Love](https://img.shields.io/badge/Made_with-♥-ff69b4?style=flat-square&logo=github&logoColor=white)
![GitHub Activity](https://img.shields.io/badge/GitHub_Activity-Active-success?style=flat-square&logo=github&logoColor=white)
