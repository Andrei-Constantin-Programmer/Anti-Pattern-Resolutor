# JaCoCo Coverage Anlysis Tool

This module runs JaCoCo (Java Code Coverage) analysis on cloned repositories to ensure that only thoroughly tested code (100% coverage) is processed for anti-pattern analysis and refactoring.

## Overview

The JaCoCo tool follows a three-step process:

1. **Clone Java repositories** from a list of GitHub URLs
2. **Run JaCoCo coverage analysis** on each repository to generate coverage reports
3. **Filter files with 100% coverage** and save the file paths in a .txt file

### Required Tools

- **Java Development Kit (JDK)** 8 or higher (tested on JAVA 17)
- **Maven** Apache Maven 3.9.11+ or **Gradle (optional)** 6.0+ (depending on the project structure)
- **Python** Tested with Python 3.12.9, should be able to run with 3.8+
- **Git** for repository cloning


## Usage

```bash
# Test with a single repository
python jacoco_workflow.py --single-repo https://github.com/apache/commons-lang

# Process multiple repositories from a file
python jacoco_workflow.py --repos repos_list.txt
```