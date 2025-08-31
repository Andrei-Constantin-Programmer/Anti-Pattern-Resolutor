# Anti-Pattern Resolutor

[![CI](https://github.com/Andrei-Constantin-Programmer/Legacy-Code-Migration/actions/workflows/python.yml/badge.svg?branch=main)](https://github.com/Andrei-Constantin-Programmer/Legacy-Code-Migration/actions/workflows/python.yml)
[![DevBlog](https://img.shields.io/badge/Live-Blog-blue?style=flat-square&logo=githubpages)](https://andrei-constantin-programmer.github.io/IBM-UCL-Blog)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Status](https://img.shields.io/badge/status-research-orange.svg)

Local-first, agentic refactoring pipeline for Java that pairs SonarQube findings with LLM-based reasoning to detect smells/anti-patterns and propose file-scoped, behaviour-preserving edits. Changes are gated by compile + tests; public interfaces are preserved; static analysis is re-run for reporting only. Run artefacts (plans, diffs, logs) are persisted for auditability.

Project made in collaboration with **UCL** and **IBM**.

## What it does
- Interprets rule-based static analysis (SonarQube) as signals, not ground truth.
- Coordinates single-responsibility agents (Scanner -> Strategist -> Transformer -> Reviewer -> Explainer) with a shared context.
- Enforces compile+test acceptance; tests are never modified.
- Java, file scope only (no cross-file/architectural refactors).
- Provider-agnostic LLM layer (e.g., local Ollama; hosted options supported) with externalised prompts.
- Uses a keyed document Trove (definitions, symptoms, safe remedies) for deterministic retrieval.

## Requirements
- **Python 3.8+** 
- An LLM backend (e.g., [Ollama](https://ollama.ai) locally)
- SonarQube access ([local](https://docs.sonarsource.com/sonarqube-server/10.6/try-out-sonarqube/)) for static analysis
- **Git**
- **Java JDK** (11 recommended)
- **Maven** (3.9.11 recommended)

## Installation & Configuration

```bash
# 1. Clone
git clone https://github.com/Andrei-Constantin-Programmer/Anti-Pattern-Resolutor.git
cd Anti-Pattern-Resolutor

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
python install_requirements.py # pip install -r requirements.txt works on Unix, 
                               # but not Windows due to incompatible libraries.
```

Optional (Ollama locally):
```bash
ollama pull granite3.3:8b
ollama pull nomic-embed-text
```

Further LangChain configurations can be changed by modifying `AntiPattern_Remediator/config/settings.py`.

## Usage

### Prepare coverage candidates
This stage clones repos, runs tests with JaCoCo, and writes a list of files with 100% line coverage to safely target.

Create `repos.txt` in the repository root:
```
https://github.com/org/repo-one
https://github.com/org/repo-two
```

Run:
```bash
# From repository root
python jacoco_tool/jacoco_analysis.py --repos repos.txt

# Useful flags:
#   --single-repo https://github.com/user/repo
#   --clone-dir clones
#   --output-dir jacoco_results
#   --force-jacoco
#   --timeout 600
#   --verbose
```

Outputs:
- Cloned sources under `clones/` (default)
- Coverage artefacts and a combined file list under `jacoco_results/`
(path is printed at the end of the run)

### Provide a SonarQube token
Generate a **user token** in SonarQube (My Account -> Security), then set it as `SONARQUBE_TOKEN`.
- Docs: https://docs.sonarsource.com/sonarqube-server/latest/user-guide/managing-tokens/#generating-a-token

Unix:
```bash
export SONARQUBE_TOKEN="paste-your-token"
```

Windows PowerShell (temporary):
```powershell
$env:SONARQUBE_TOKEN = "paste-your-token"
```

Windows (persist):
```powershell
setx SONARQUBE_TOKEN "paste-your-token"
# Restart the terminal afterwards
```

### Run SonarQube
```bash
python remediate_repos.py
        --token SONARQUBE_TOKEN # If you haven't added a token in the environment
```

### Run the Remediator
```bash
python AntiPattern_Remediator/main.py
```

The pipeline selects 100%-covered files, proposes minimal, behaviour-preserving edits, and gates them behind compile + test.  

SonarQube is re-run for reporting.  

Plans, diffs, logs, and summaries are written to the run output directory (path shown in the console).

### Troubleshooting
- **"No coverage results found"**  
Ensure `mvn -q -DskipTests=false test` succeeds in each repo; consider `--timeout` and `--force-jacoco` when running the JaCoCo tool.
- **Auth errors with SonarQube**  
Confirm `SONARQUBE_TOKEN` is set in your current shell and your SonarQube URL is reachable.
- **Java/Maven not found**  
Verify JDK 11 and Maven are on `PATH`.

## Acknowledgments
- **IBM** - For providing technical expertise and computational resources, and mentorship from Dr Amrin Maria Khan and Prof. John McNamara
- **University College London (UCL)** - For research guidance and academic support, under the supervision of Dr Jens Krinke
- **LangChain Community** - For the foundational LLM orchestration framework
- **Ollama Project** - For making LLM deployment accessible and efficient
