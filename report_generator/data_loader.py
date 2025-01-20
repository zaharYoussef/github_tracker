# data_loader.py
import json
import os
import pandas as pd
from datetime import datetime


EXTENSION_TO_LANGUAGE = {
    "py": "Python",
    "tf": "Terraform",
    "js": "JavaScript",
    "md": "Markdown",
    "ts": "TypeScript",
    "yml": "yaml",
    "sh": "Shell Script"
}

class DataLoader:
    """
    Handles data processing and transformations for the report generator.
    """

    def __init__(self, data_file="github_data.json"):
        self.data_file = data_file
        self.data = self._load_data()
        
        # Build and cache DataFrames for each data type.
        self._commits_df = self._create_commits_dataframe()
        self._prs_submitted_df = self._create_prs_submitted_dataframe()
        self._prs_comments_df = self._create_prs_comments_dataframe()

    def _load_data(self):
        """Load the JSON file containing GitHub data."""
        if not os.path.exists(self.data_file):
            raise FileNotFoundError(f"Data file '{self.data_file}' not found.")

        with open(self.data_file, "r") as f:
            return json.load(f)

    def _create_commits_dataframe(self):
        """
        Transform all commits into a single DataFrame with the following columns:
        [repo_name, sha, date, file_path, file_type, ...].
        """
        rows = []
        for repo_name, repo_data in self.data["repos"].items():
            commits = repo_data.get("commits", [])
            for commit in commits:
                commit_sha = commit.get("sha")
                commit_date_str = commit.get("date")
                commit_date = None
                if commit_date_str:
                    try:
                        commit_date = datetime.strptime(commit_date_str, "%Y-%m-%dT%H:%M:%SZ")
                    except ValueError:
                        pass

                file_info_list = commit.get("file_info", [])
                if not file_info_list:
                    rows.append({
                        "repo_name": repo_name,
                        "sha": commit_sha,
                        "date": commit_date,
                        "file_path": None,
                        "file_type": None,
                    })
                else:
                    for fi in file_info_list:
                        file_path = fi.get("file_path")
                        if file_path:
                            file_type = file_path.split(".")[-1] if "." in file_path else "unknown"
                        else:
                            file_type = None

                        rows.append({
                            "repo_name": repo_name,
                            "sha": commit_sha,
                            "date": commit_date,
                            "file_path": file_path,
                            "file_type": file_type,
                        })

        if rows:
            return pd.DataFrame(rows)
        else:
            # return empty DF with consistent columns if no data
            return pd.DataFrame(columns=["repo_name","sha","date","file_path","file_type"])

    def _create_prs_submitted_dataframe(self):
        """
        Flatten all "pr_submitted" data into a DataFrame with columns like:
        [repo_name, pr_id, created_at, ...].
        """
        rows = []
        for repo_name, repo_data in self.data["repos"].items():
            prs_submitted = repo_data.get("pr_submitted", [])
            for pr in prs_submitted:
                rows.append({
                    "repo_name": repo_name,
                    "pr_id": pr.get("pr_id"),
                    "created_at": pr.get("created_at"),
                })
        if rows:
            return pd.DataFrame(rows)
        else:
            return pd.DataFrame(columns=["repo_name","pr_id","created_at"])

    def _create_prs_comments_dataframe(self):
        """
        Flatten all "pr_comments" data into a DataFrame with columns like:
        [repo_name, comment_id, created_at, ...].
        """
        rows = []
        for repo_name, repo_data in self.data["repos"].items():
            pr_comments = repo_data.get("pr_comments", [])
            for comment in pr_comments:
                rows.append({
                    "repo_name": repo_name,
                    "comment_id": comment.get("comment_id"),
                    "created_at": comment.get("created_at"),
                })
        if rows:
            return pd.DataFrame(rows)
        else:
            return pd.DataFrame(columns=["repo_name","comment_id","created_at"])

    def get_overall_metrics(self):
        """Aggregate metrics for all repositories."""
        total_commits = len(self._commits_df)
        total_prs_submitted = len(self._prs_submitted_df)
        total_prs_comments = len(self._prs_comments_df)

        return {
            "total_commits": total_commits,
            "total_prs_submitted": total_prs_submitted,
            "total_prs_comments": total_prs_comments,
        }

    def get_file_type_breakdown(self):
        """Calculate the breakdown of file types across all repositories."""
        if self._commits_df.empty:
            return {}
        breakdown_series = self._commits_df["file_type"].value_counts(dropna=False)
        return breakdown_series.to_dict()

    def get_repo_specific_metrics(self, repo_name):
        """Retrieve metrics for a specific repository."""
        if repo_name not in self.data["repos"]:
            raise ValueError(f"Repository '{repo_name}' not found in data.")

        # Filter commits by repo
        repo_commits = self._commits_df[self._commits_df["repo_name"] == repo_name]
        repo_prs_submitted = self._prs_submitted_df[self._prs_submitted_df["repo_name"] == repo_name]
        repo_prs_comments = self._prs_comments_df[self._prs_comments_df["repo_name"] == repo_name]

        total_commits = len(repo_commits)
        total_prs_submitted = len(repo_prs_submitted)
        total_prs_comments = len(repo_prs_comments)
        file_types = self.get_file_type_breakdown_by_repo(repo_name)

        return {
            "total_commits": total_commits,
            "total_prs_submitted": total_prs_submitted,
            "total_prs_comments": total_prs_comments,
            "file_types": file_types,
        }

    def get_file_type_breakdown_by_repo(self, repo_name):
        """Calculate the breakdown of file types for a specific repository."""
        if repo_name not in self.data["repos"]:
            raise ValueError(f"Repository '{repo_name}' not found in data.")

        repo_commits = self._commits_df[self._commits_df["repo_name"] == repo_name]
        if repo_commits.empty:
            return {}

        breakdown_series = repo_commits["file_type"].value_counts(dropna=False)
        return breakdown_series.to_dict()
    
    def get_top_languages(self, n=5):
        """Get the top N languages by file type contributions across all repositories."""
        if self._commits_df.empty:
            return {}

        language_series = self._commits_df["file_type"].apply(
            lambda ft: EXTENSION_TO_LANGUAGE.get(ft, ft)
        )

        language_series = language_series[language_series != "unknown"]

        language_counts = language_series.value_counts()
        return language_counts.head(n).to_dict()


    def get_repo_contributions_summary(self):
        """Get a summary of contributions for each repository."""
        summary = []
        for repo_name, repo_data in self.data["repos"].items():
            total_commits = len(self._commits_df[self._commits_df["repo_name"] == repo_name])
            total_prs = len(self._prs_submitted_df[self._prs_submitted_df["repo_name"] == repo_name])
            last_commit_date = (
                self._commits_df[self._commits_df["repo_name"] == repo_name]["date"].max()
            )
            summary.append({
                "Repository Name": repo_name,
                "Total Commits": total_commits,
                "Total PRs": total_prs,
                "Last Contribution Date": last_commit_date,
            })

        return pd.DataFrame(summary).reset_index(drop=True)