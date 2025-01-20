from fetch_data import GitHubDataFetcher
from data_manager import DataManager
from report_generator import ReportController
from interactive_selector import select_repos_curses
from datetime import datetime


def main():
    """Main controller for the GitHub Contribution Tracker."""
    fetcher = GitHubDataFetcher()
    manager = DataManager()

    print("\nWelcome to the GitHub Contribution Tracker!")
    print("1. Fetch and update data")
    print("2. Generate report")
    print("3. Exit")
    choice = input("Enter your choice (1, 2, or 3): ")

    if choice == "1":
        print("\nWhat would you like to do?")
        print("1. Update existing repositories")
        print("2. Add a new repository")
        sub_choice = input("Enter your choice (1 or 2): ")

        # Update existing repositories
        if sub_choice == "1":            
            managed_repos = manager.get_managed_repos()
            if not managed_repos:
                print("No managed repositories found. Add a repository first.")
                return

            selected_repos = select_repos_curses(managed_repos)
            if not selected_repos:
                print("No repositories selected.")
                return

            print("\nDefault behavior will fetch data from the last pull date.")
            start_date = input("Enter a new starting date (YYYY-MM-DD) to reset data, or press Enter to keep the current: ").strip()

            if start_date:
                try:
                    datetime.strptime(start_date, "%Y-%m-%d")
                except ValueError:
                    print("Invalid date format. Please use YYYY-MM-DD.")
                    return

            for repo in selected_repos:
                if start_date:
                    # Replace start date and clear repo data
                    print(f"Resetting start date for {repo} to {start_date} and clearing existing data...")
                else:
                    # Keep current start date, fetch new data
                    start_date = manager.data["repos"][repo]["start_date"]
                    print(f"Using current start date ({start_date}) for {repo}...")

                last_pull_date = manager.data["repos"][repo]["last_pull_date"]
                print(f"Fetching data for {repo} from {last_pull_date} to now...")

                commits = fetcher.fetch_commit_data(repo, last_pull_date)
                prs_submitted = fetcher.fetch_prs_submitted(repo)
                pr_comments = fetcher.fetch_pr_comments(repo)


                if not commits and not prs_submitted and not pr_comments:
                    print(f"No changes to report for {repo} since the last update.")
                else:
                    manager.update_repo_data(repo, start_date, commits, prs_submitted, pr_comments)

            manager.save_data()
            print("Repositories updated successfully!")

        # Add a new repository
        elif sub_choice == "2":
            available_repos = fetcher.get_repos()
            new_repos = select_repos_curses(available_repos)

            for repo in new_repos:
                manager.add_managed_repo(repo)

                while True:
                    start_date = input(f"Enter the starting date for {repo} (YYYY-MM-DD): ")
                    try:
                        datetime.strptime(start_date, "%Y-%m-%d")
                        break
                    except ValueError:
                        print("Invalid date format. Please use YYYY-MM-DD.")

                print(f"Fetching data for repo: {repo} from {start_date} to now...")
                commits = fetcher.fetch_commit_data(repo, start_date)
                prs_submitted = fetcher.fetch_prs_submitted(repo)
                pr_comments = fetcher.fetch_prs_submitted(repo)

                manager.update_repo_data(repo, start_date, commits, prs_submitted, pr_comments)

            manager.save_data()
            print("Data updated successfully!")

        else:
            print("Invalid choice. Please enter 1 or 2.")

    elif choice == "2":
        print("\nGenerating the report...")
        controller = ReportController()
        controller.server_app("GitHub Contribution Tracker", 65244)
    
    elif choice == "3":
        print("Exiting. Goodbye!")
    
    else:
        print("Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()