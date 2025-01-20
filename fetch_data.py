import requests
import config

GITHUB_API_URL = "https://api.github.com"
HEADERS = {"Authorization": f"token {config.GITHUB_TOKEN}"}


class GitHubDataFetcher:
    """Handles GitHub API interactions."""

    def __init__(self):
        self.headers = HEADERS

    def get_repos(self):
        """Fetch all repositories the user has access to."""
        response = requests.get(f"{GITHUB_API_URL}/user/repos", headers=self.headers)
        if response.status_code != 200:
            print(f"Failed to fetch repositories: {response.status_code} - {response.json().get('message')}")
            return []
        return [repo["full_name"] for repo in response.json()]

    def fetch_commit_data(self, repo_name, start_date):
        """Fetch commits authored by the user and their file information."""
        url = f"{GITHUB_API_URL}/repos/{repo_name}/commits"
        params = {"since": start_date}
        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code != 200:
            print(f"Failed to fetch commits for {repo_name}: {response.status_code} - {response.json().get('message')}")
            return []

        commits = response.json()
        result = []
        for commit in commits:
            if commit["author"] and commit["author"]["login"] == config.GITHUB_USERNAME:
                commit_sha = commit["sha"]
                file_info = self.get_file_info(repo_name, commit_sha)

                result.append({
                    "sha": commit_sha,
                    "date": commit["commit"]["author"]["date"],
                    "author": commit["commit"]["author"]["name"],
                    "message": commit["commit"]["message"],
                    "file_info": file_info
                })
        return result
    
    def get_file_info(self, repo_name, commit_sha):
        """Retrieve detailed file information for a specific commit."""
        url = f"{GITHUB_API_URL}/repos/{repo_name}/commits/{commit_sha}"
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            print(f"Failed to fetch file details for commit {commit_sha}: {response.status_code} - {response.json().get('message')}")
            return []

        files = response.json().get("files", [])
        file_info = []
        for file in files:
            status = file["status"]
            if status == "added":
                status = "created"
            file_info.append({
                "file_path": file["filename"],
                "status": status,
                "lines_added": file.get("additions", 0),
                "lines_removed": file.get("deletions", 0)
            })
        return file_info

    def fetch_prs_submitted(self, repo_name):
        """Fetch PRs submitted by the authenticated user."""
        url = f"{GITHUB_API_URL}/repos/{repo_name}/pulls"
        params = {"state": "all"}  # Fetch all PRs (open, closed, merged)
        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code != 200:
            print(f"Failed to fetch PRs for {repo_name}: {response.status_code} - {response.json().get('message')}")
            return []

        prs = response.json()
        return [
            {
                "pr_id": pr["id"],
                "date": pr["created_at"],
                "title": pr["title"],
                "status": "merged" if pr.get("merged_at") else "open" if pr["state"] == "open" else "closed"
            }
            for pr in prs
            if pr["user"]["login"] == config.GITHUB_USERNAME
        ]

    def fetch_pr_comments(self, repo_name):
        """Fetch PR comments authored by the user."""
        url = f"{GITHUB_API_URL}/repos/{repo_name}/pulls/comments"
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            print(f"Failed to fetch PR comments for {repo_name}: {response.status_code} - {response.json().get('message')}")
            return []

        comments = response.json()
        return [
            {
                "pr_id": comment["pull_request_url"].split("/")[-1],
                "date": comment["created_at"],
                "comment": comment["body"],
                "pr_url": comment["html_url"]
            }
            for comment in comments
            if comment["user"]["login"] == config.GITHUB_USERNAME
        ]
