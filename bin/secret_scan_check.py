"""
This program is to retrieve GitHub code scanning findings for all repositories with a given prefix.
Prerequisites:
The following environment variables need to be set prior running it:
 - GITHUB_TOKEN
 - GITHUB_ORGANISATION
Update prefix by setting:
 - REPO_PREFIX
In order to run this program, in your terminal, type:
```python3 secret_scan_check.py```
"""

import requests
import os

# -----------------------
# Configuration
# -----------------------
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")            # Set the token as an environment variable
GITHUB_ORGANISATION = os.getenv("GITHUB_OWNER")     # Set the organisation as an environment variable
REPO_PREFIX = "modernisation-platform"              # Set the repository prefix here
PER_PAGE = 100

# -----------------------
# Headers for GitHub API
# -----------------------
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

def get_repos():
    """Fetch all repositories in the org that start with the given prefix."""
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/orgs/{GITHUB_ORGANISATION}/repos?per_page={PER_PAGE}&page={page}"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        if not data:
            break
        for repo in data:
            if repo["name"].startswith(REPO_PREFIX):
                repos.append(repo["name"])
        page += 1
    return repos

def get_secret_scanning_alerts(repo_name):
    """Fetch default secret scanning alerts for a given repository."""
    alerts = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{GITHUB_ORGANISATION}/{repo_name}/secret-scanning/alerts?per_page={PER_PAGE}&page={page}"
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 404:
            print(f"Secret scanning not enabled for {repo_name}")
            break
        response.raise_for_status()
        data = response.json()
        if not data:
            break
        alerts.extend(data)
        page += 1
    return alerts

def get_generic_secret_scanning_alerts(repo_name):
    """Fetch generic secret scanning alerts for a given repository."""
    alerts = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{GITHUB_ORGANISATION}/{repo_name}/security/secret-scanning?query=is%3Aopen+results%3Ageneric/alerts?per_page={PER_PAGE}&page={page}"
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 404:
            print(f"Secret scanning not enabled for {repo_name}")
            break
        response.raise_for_status()
        data = response.json()
        if not data:
            break
        alerts.extend(data)
        page += 1
    return alerts

def main():
    repos = get_repos()
    print(f"\n🔍 Found {len(repos)} repositories starting with '{REPO_PREFIX}':\n")

    for repo in repos:
        print(f"📘 Checking repo: {repo}")
        alerts = get_secret_scanning_alerts(repo)
        generic_alerts = get_generic_secret_scanning_alerts(repo)
        if alerts:
            print(f"⚠️  {len(alerts)} alerts found in {repo}")
            for alert in alerts:
                print(f"  - Type: {alert['secret_type']}, State: {alert['state']}, Created: {alert['created_at']}")
        else:
            print("✅ No alerts found.\n")
        if generic_alerts:
            print(f"⚠️  {len(generic_alerts)} alerts found in {repo}")
            for alert in generic_alerts:
                print(f"  - Type: {alert['secret_type']}, State: {alert['state']}, Created: {alert['created_at']}")
        else:
            print("✅ No alerts found.\n")

if __name__ == "__main__":
    if not GITHUB_TOKEN or not GITHUB_ORGANISATION:
        print("❌ Error: Please set the GITHUB_TOKEN and the GITHUB_OWNER environment variable.")
    else:
        main()
