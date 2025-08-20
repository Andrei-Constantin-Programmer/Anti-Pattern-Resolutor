# Temporary main file
import argparse
import os

from github_handler.clone_repos import clone_repos_from_file
from sonarqube_tool.cloning_processing import delete_sonarqube_output_if_updated
from sonarqube_tool.scan_repos import scan_repos

# If path is absolute, set the base as the root of the Anti-Pattern Resolutor.
def _resolve_path(base_dir: str, path: str) -> str:
    return path if os.path.isabs(path) else os.path.join(base_dir, path)


def main():
    parser = argparse.ArgumentParser(description="Run SonarQube on a list of repositories.")
    parser.add_argument(
        "--token",
        help="""
            SonarQube token. If not provided, will read from SONARQUBE_TOKEN environment variable. 
            To get this: run Docker on your PC, then: `docker run -d --name sonarqube -p 9000:9000 sonarqube:community`. 
            Use "admin" as the username and the password you set during the setup. 
            Log into 'http://localhost:9000', then My Account > Security, and generate a "User Token" type token to use. 
            It will have the necessary permissions for analysis.
        """
    )
    parser.add_argument(
        "--repos",
        nargs="?",
        default="repos.txt",
        help="Text file with GitHub repo URLs (default: repos.txt)"
    )
    parser.add_argument(
        "--clone-dir",
        default="clones",
        help="Output folder to clone into (default: clones)"
    )
    parser.add_argument(
        "--force-scan",
        action="store_true",
        help="Force repository SonarQube scan even if output file exists"
    )
    args = parser.parse_args()

    # Get token from argument or environment variable
    token = args.token or os.getenv('SONARQUBE_TOKEN')
    if not token:
        print("Error: SonarQube token is required. Provide it via --token argument or set SONARQUBE_TOKEN environment variable.")
        return

    base_dir = os.path.dirname(os.path.abspath(__file__))

    repos_file = _resolve_path(base_dir, args.repos)
    clone_dir = _resolve_path(base_dir, args.clone_dir)

    clone_repos_from_file(repos_file, clone_dir, post_pull_hook=delete_sonarqube_output_if_updated)
    scan_repos(token, clone_dir, args.force_scan)


if __name__ == "__main__":
    main()
