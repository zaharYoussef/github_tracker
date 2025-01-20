import os
import json
from datetime import datetime


class DataManager:
    """Handles loading, saving, and updating local JSON data."""

    def __init__(self, data_file="github_data.json"):
        self.data_file = data_file
        self.data = self._load_data()

    def _initialize_json(self):
        """Initialize the JSON file if it doesn't exist."""
        if not os.path.exists(self.data_file):
            with open(self.data_file, "w") as f:
                json.dump({"managed_repos": [], "repos": {}}, f, indent=4)

    def _load_data(self):
        """Load the JSON file."""
        self._initialize_json()
        with open(self.data_file, "r") as f:
            return json.load(f)

    def save_data(self):
        """Save the current data to the JSON file."""
        with open(self.data_file, "w") as f:
            json.dump(self.data, f, indent=4)

    def get_managed_repos(self):
        """Get the list of managed repositories."""
        return self.data.get("managed_repos", [])

    def add_managed_repo(self, repo_name):
        """Add a new repository to the list of managed repositories."""
        if repo_name not in self.data["managed_repos"]:
            self.data["managed_repos"].append(repo_name)
            print(f"Added '{repo_name}' to managed repositories.")
        else:
            print(f"'{repo_name}' is already a managed repository.")

    def update_repo_data(self, repo_name, start_date, commits, prs_submitted, pr_comments):
        """Update data for a specific repository."""
        now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        # Initialize new repo data if not already present
        if repo_name not in self.data["repos"]:            
            self.data["repos"][repo_name] = {
                "start_date": start_date,
                "last_pull_date": now,
                "commits": [],
                "pr_submitted": [],
                "pr_comments": []
            }
        # Update the repository
        else:
            if start_date and start_date != self.data["repos"][repo_name]["start_date"]:
                # Replace start date and clear existing data
                self.data["repos"][repo_name]["start_date"] = start_date
                self.data["repos"][repo_name]["commits"] = []
                self.data["repos"][repo_name]["pr_submitted"] = []
                self.data["repos"][repo_name]["pr_comments"] = []

        # Add new data and update the last pull date
        self.data["repos"][repo_name]["commits"].extend(commits)
        self.data["repos"][repo_name]["pr_submitted"].extend(prs_submitted)
        self.data["repos"][repo_name]["pr_comments"].extend(pr_comments)
        self.data["repos"][repo_name]["last_pull_date"] = now