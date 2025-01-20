# github_tracker
This is a simple GitHub tracker that generates a report about my github contributions. I also used this project to get some experience with using [panel](https://panel.holoviz.org/).

## Requirements
- Python 3.11
- A GitHub Personal Access Token (PAT) with read access.

## Setup
1. Create and activate a virtual environment:

    ```sh
    python -m venv ./.venv
    source .venv/bin/activate
    ```

2. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

3. Create a config.py file. Add your GitHub credentials to config.py in the following format:
    ```python
    GITHUB_TOKEN = "your_github_pat_token"
    GITHUB_USERNAME = "your_github_user"
    ```

4. Run the application with:
    ```python
    python app.py
    ```