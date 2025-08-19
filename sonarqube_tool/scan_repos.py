from pathlib import Path
import platform
import shutil
import subprocess
from .sonarqube_api import SonarQubeAPI

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
sonar.sources=src/main/java
sonar.java.binaries=target/classes
sonar.host.url={SONARQUBE_URL}
sonar.token={token}
""".strip()

    properties_file.write_text(properties)
    return properties_file

def _compile_java_sources(repo_dir):
    """
    Compile Java sources using Maven, supporting both Windows and Linux.
    Skips Apache RAT license checking with -Drat.skip=true.
    """
    # Check if it's a Maven project
    pom_file = repo_dir / "pom.xml"
    if not pom_file.exists():
        print(f"No pom.xml found in {repo_dir.name}, skipping compilation.")
        return
    
    # Check if already compiled (target directory exists)
    target_dir = repo_dir / "target"
    if target_dir.exists():
        print(f"Target directory already exists for {repo_dir.name}, skipping compilation.")
        return
    
    print(f"Compiling Java sources for {repo_dir.name}...")
    
    try:
        # Determine the Maven command based on platform
        if platform.system() == "Windows":
            maven_cmd = ["mvn.cmd", "clean", "compile", "-Drat.skip=true"]
        else:
            maven_cmd = ["mvn", "clean", "compile", "-Drat.skip=true"]
        
        # Run Maven compilation
        result = subprocess.run(
            maven_cmd,
            cwd=repo_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=True
        )
        print(f"Successful! Compilation successful for {repo_dir.name}")

    except subprocess.CalledProcessError as e:
        print(f"Error: Compilation failed for {repo_dir.name}: {e}")
        print(f"Maven output: {e.stdout}")
    except FileNotFoundError:
        print(f"Error: Maven not found in PATH. Please install Maven to compile {repo_dir.name}")
    except Exception as e:
        print(f"Error: Unexpected error during compilation of {repo_dir.name}: {e}")
    

def _scan_repo(repo_dir, token, force_scan):
    project_key = repo_dir.name.replace(" ", "_")
    output_file = repo_dir / SONARQUBE_FILE_NAME

    if not force_scan and output_file.exists():
        print(f"Skipping {repo_dir.name}; repository already scanned.")
        return

    properties_file = _setup_properties(token, repo_dir, project_key)

    # Compile Java sources before scanning, defaulting to Maven
    _compile_java_sources(repo_dir)

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
        api = SonarQubeAPI()
        if api.is_scan_successful(project_key):
            issues_path = repo_dir / "issues.json"
            api.save_all_issues(project_key, issues_path)
            print(f"All issues saved for {repo_dir.name}.")
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
