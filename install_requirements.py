import os
import platform
import subprocess
import sys
import tempfile
from typing import Callable, List

def _skip_rule(dependency: str, os: str) -> Callable[[str], bool]:
    return (lambda line: platform.system() == os and line.strip().startswith(dependency))

def _filter_dependencies(lines: List[str]) -> List[str]:
    rules = [
        _skip_rule("uvloop", "Windows")
    ]
    return [line for line in lines if not any(rule(line) for rule in rules)]


def install_requirements(requirements_path="requirements.txt"):
    try:
        with open(requirements_path, "r", encoding="utf-8") as f:
            filtered_lines = _filter_dependencies(f.readlines())

        with tempfile.NamedTemporaryFile(mode="w+", delete=False, encoding="utf-8") as tmp:
            tmp.writelines(filtered_lines)
            tmp.flush()
            temp_file_path = tmp.name

        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", temp_file_path],
            check=True
        )

        print("Requirements installed successfully.")

    except subprocess.CalledProcessError as e:
        print(f"pip install failed: {e}")
    except FileNotFoundError:
        print(f"Requirements file at '{requirements_path}' not found.")
    finally:
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.remove(temp_file_path)


if __name__ == "__main__":
    install_requirements()
