import os
from sonarqube_tool.scan_repos import SONARQUBE_FILE_NAME

# Cloning post-processing step, delete SonarQube output if the repo is updated.
def delete_sonarqube_output_if_updated(repo_path: str, repo_name: str, old_commit: str, new_commit: str) -> None:
    if old_commit != new_commit:
        print(f"{repo_name} updated. Deleting old SonarQube output.")
        output_file = os.path.join(repo_path, SONARQUBE_FILE_NAME)
        if os.path.exists(output_file):
            os.remove(output_file)
    else:
        print(f"{repo_name} is already up to date.")
