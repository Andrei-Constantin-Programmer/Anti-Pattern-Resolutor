from pathlib import Path
import platform
import shutil
import subprocess

SONARQUBE_URL = "http://localhost:9000"
SONARQUBE_FILE_NAME = "sonarqube_output.txt"
PROPERTIES_FILE_NAME = "sonar-project.properties"

# Setup the SonarQube properties file for a repository.
def _setup_properties(token, repo_dir, project_key):
    properties_file = repo_dir / PROPERTIES_FILE_NAME
    properties = f"""
sonar.projectKey={project_key}
sonar.projectName={repo_dir.name}
sonar.projectVersion=1.0
sonar.sources=.
sonar.host.url={SONARQUBE_URL}
sonar.token={token}
""".strip()

    properties_file.write_text(properties)
    return properties_file


def _scan_repo(repo_dir, token, force_scan):
    project_key = repo_dir.name.replace(" ", "_")
    output_file = repo_dir / SONARQUBE_FILE_NAME

    if not force_scan and output_file.exists():
        print(f"Skipping {repo_dir.name}; repository already scanned.")
        return

    properties_file = _setup_properties(token, repo_dir, project_key)

    print(f"Running SonarQube on {repo_dir.name}...")

    try:
        use_shell = platform.system() == "Windows"
        result = subprocess.run(
            ["sonar-scanner"],
            cwd=repo_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=True,
            text=True,
            shell=use_shell
        )
        output_file.write_text(result.stdout)
        print(f"Scan complete. Output saved to {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"SonarQube scan failed for {repo_dir.name}: {e}")
        output_file.write_text(e.stdout or "No output captured.")

    properties_file.unlink(missing_ok=True)
    

def scan_repos(token: str, clone_root: str = "clones", force_scan: bool = False) -> None:

    if not shutil.which("sonar-scanner"):
        print("'sonar-scanner' not found in PATH. Please add it or specify manually.")
        return
    
    root = Path(clone_root)
    
    if not root.exists():
        print(f"Clone root {root} does not exist.")
        return
    
    for repo_dir in root.iterdir():
        if not repo_dir.is_dir():
            continue
        _scan_repo(repo_dir, token, force_scan)

        