# Anti-Pattern Resolutor

[![CI](https://github.com/Andrei-Constantin-Programmer/Legacy-Code-Migration/actions/workflows/python.yml/badge.svg?branch=main)](https://github.com/Andrei-Constantin-Programmer/Legacy-Code-Migration/actions/workflows/python.yml)
[![DevBlog](https://img.shields.io/badge/Live-Blog-blue?style=flat-square&logo=githubpages)](https://andrei-constantin-programmer.github.io/IBM-UCL-Blog)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Status](https://img.shields.io/badge/status-research-orange.svg)

A cutting-edge research project developed in collaboration with **IBM Research** and **University College London (UCL)** to automatically migrate legacy Java codebases to modern, maintainable solutions using AI-powered antipattern detection and intelligent refactoring suggestions.

## 🚀 Overview

This tool leverages the power of Large Language Models (LLMs) and vector-based knowledge retrieval to provide comprehensive analysis of Java code, automatically detecting common antipatterns and suggesting concrete refactoring strategies. It represents a significant advancement in automated code modernization and technical debt reduction.

## ✨ Key Features

- 🔍 **Intelligent Antipattern Detection**: Automatically identifies 20+ common Java antipatterns including God Object, Long Method, Feature Envy, and more
- 🤖 **AI-Powered Analysis**: Utilizes state-of-the-art LLMs (Granite, Llama, etc.) for deep semantic code understanding
- 📊 **Context-Aware Analysis**: Vector database enables intelligent knowledge retrieval for more accurate assessments
- 🛠️ **Actionable Refactoring Recommendations**: Provides step-by-step refactoring guidance with effort estimates
- 🏗️ **Modular Agent Architecture**: Extensible design with specialized agents for different analysis tasks
- 📈 **Comprehensive Reporting**: Detailed analysis reports with confidence scores and impact assessments

## 🏛️ Architecture

The tool follows a modular, agent-based architecture:

```
AntiPattern_Remediator/
├── 📁 src/                           # Core source code
│   ├── 📁 core/                      # Analysis engine
│   │   ├── 📁 agents/               # Specialized analysis agents
│   │   │   ├── 🔧 base_agent.py     # Agent interface foundation
│   │   │   ├── 🔍 antipattern_scanner.py  # Pattern detection agent
│   │   │   ├── 🔄 code_transformer.py     # Code transformation agent
│   │   │   └── 🛠️ refactoring_agent.py    # Refactoring strategy agent
│   │   ├── 📁 graph/                # Workflow orchestration
│   │   │   ├── 🌐 create_graph.py   # Main workflow builder
│   │   │   └── ⚡ enhanced_workflow.py     # Advanced pipeline
│   │   ├── 📋 state.py              # Shared state management
│   │   └── 🔄 workflow.py           # Basic workflow definitions
│   └── 📁 data/                     # Data management layer
│       └── 📁 database/             # Vector database components
│           └── 💾 vector_db.py      # Vector DB operations
├── ⚙️ config/                       # Configuration management
│   └── 📝 settings.py              # Application settings
├── 🔧 scripts/                     # Utility scripts
│   ├── 🚀 setup_db.py             # Database initialization
│   └── ▶️ run_analysis.py          # Standalone analysis runner
├── 📊 static/                      # Static resources
│   ├── 📖 ap.txt                  # Antipattern knowledge base
│   └── 💾 vector_db/              # Vector database storage
├── 🎯 main.py                      # Main application entry point
└── 📦 requirements.txt             # Python dependencies
```

## 🛠️ Installation & Setup

### Prerequisites

- **Python 3.8+** 
- **Ollama** (for LLM support)
- **Git**

### Step-by-Step Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-repo/Legacy-Code-Migration.git
   cd Legacy-Code-Migration
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install & Configure Ollama**
   ```bash
   # Install Ollama (visit https://ollama.ai for platform-specific instructions)
   
   # Pull required models
   ollama pull granite3.3:8b          # Main analysis model
   ollama pull nomic-embed-text       # Embedding model for vector search
   ```

5. **Initialize Vector Database**
   ```bash
   python scripts/setup_db.py
   ```

6. **Verify Installation**
   ```bash
   python main.py
   ```

## 📖 Usage Guide

### 🎯 Quick Start

**Analyze Sample Code:**
```bash
python main.py
```

**Custom Analysis:**
```bash
python scripts/run_analysis.py
```

### 💻 Programmatic Usage

```python
from src.core.graph import CreateGraph
from src.data.database import VectorDBManager

# Initialize components
vector_db = VectorDBManager()
workflow = CreateGraph(db_manager=vector_db.get_db()).workflow

# Analyze your Java code
java_code = """
public class UserManager {
    private List<User> users = new ArrayList<>();
    private List<String> logs = new ArrayList<>();
    
    public void addUser(User user) {
        users.add(user);
        logs.add("User added: " + user.getName());
        // Send email notification
        EmailService.sendWelcomeEmail(user);
        // Update analytics
        AnalyticsService.trackUserRegistration(user);
    }
    
    public void generateReport() {
        // Complex report generation logic...
    }
}
"""

# Run analysis
result = workflow.invoke({
    "code": java_code,
    "context": None,
    "answer": None
})

print("Analysis Results:", result["answer"])
```


## ⚙️ Configuration

Edit `config/settings.py` to customize behavior:

```python
# Model Configuration
LLM_MODEL = "granite3.3:8b"           # Primary analysis model
EMBEDDING_MODEL = "nomic-embed-text"   # Vector embedding model

# Analysis Parameters
CHUNK_SIZE = 1000                      # Text chunking for vector DB
CHUNK_OVERLAP = 200                    # Overlap between chunks
CONFIDENCE_THRESHOLD = 0.7             # Minimum confidence for pattern detection

# Database Settings
VECTOR_DB_DIR = "static/vector_db"     # Vector database location
```

## 🧠 Supported Antipatterns

The tool currently detects and provides refactoring guidance for:

| Category | Antipatterns |
|----------|-------------|
| **Structural** | God Object, Long Method, Large Class, Data Class |
| **Behavioral** | Feature Envy, Message Chains, Inappropriate Intimacy |
| **Creational** | Singleton Abuse, Factory Abuse |
| **Architectural** | Circular Dependencies, Tight Coupling |
| **Performance** | N+1 Queries, Premature Optimization |

## 🔧 Core Components

### 🤖 Analysis Agents

- **`AntipatternScanner`**: Identifies code smells and antipatterns using pattern matching and ML techniques
- **`CodeTransformer`**: Applies automated code transformations and suggests improvements
- **`RefactoringAgent`**: Generates comprehensive refactoring strategies with effort estimates

### 🌐 Workflow Engine

- **`CreateGraph`**: Orchestrates the complete analysis pipeline using LangGraph
- **`EnhancedWorkflow`**: Advanced multi-step analysis with context-aware processing

### 💾 Data Management

- **`VectorDBManager`**: Manages vector database operations for knowledge retrieval
- **Settings System**: Centralized configuration with environment-specific overrides

## 📊 Sample Output

```
🚀 Legacy Code Migration Tool - Analysis Results
================================================================

📋 ANTIPATTERN ANALYSIS RESULTS
================================================================

1. **God Object Detected**
   - Location: UserManager class
   - Issue: Class handles user management, logging, email notifications, and analytics
   - Impact: High coupling, difficult to test and maintain
   - Refactoring: Split into UserService, LoggingService, NotificationService
   - Effort Estimate: 4-6 hours

2. **Feature Envy Detected**
   - Location: addUser() method
   - Issue: Method heavily uses EmailService and AnalyticsService
   - Impact: Poor cohesion, violation of Single Responsibility Principle
   - Refactoring: Move email/analytics logic to respective services
   - Effort Estimate: 2-3 hours

3. **Long Method**
   - Location: generateReport() method
   - Issue: Method contains 45 lines of complex logic
   - Impact: Difficult to understand and modify
   - Refactoring: Extract smaller, focused methods
   - Effort Estimate: 3-4 hours

================================================================
📊 Analysis Summary: 3 antipatterns detected
🎯 Estimated Total Refactoring Effort: 9-13 hours
📈 Code Quality Impact: High improvement expected
================================================================
```

## 🤝 Contributing

This is an active research project. We welcome contributions in several areas:

- 🐛 **Bug Reports**: Submit issues via GitHub
- 🔧 **Feature Requests**: Suggest new antipatterns or analysis capabilities
- 📖 **Documentation**: Improve setup guides and usage examples
- 🧪 **Testing**: Add test cases for edge scenarios

### Development Setup

```bash
# Clone with development dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Code formatting
black src/
isort src/
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 Acknowledgments

- **IBM Research** - For providing technical expertise and computational resources
- **University College London (UCL)** - For research guidance and academic support
- **LangChain Community** - For the foundational LLM orchestration framework
- **Ollama Project** - For making LLM deployment accessible and efficient

<!-- ## 📞 Support & Contact

- 📧 **Email**: [project-email@domain.com]
- 🐛 **Issues**: [GitHub Issues](https://github.com/your-repo/Legacy-Code-Migration/issues)
- 📖 **Documentation**: [Wiki](https://github.com/your-repo/Legacy-Code-Migration/wiki)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/your-repo/Legacy-Code-Migration/discussions) -->

---

<div align="center">

**Built with ❤️ for the developer community**

[⭐ Star this repo](https://github.com/your-repo/Legacy-Code-Migration) | [🔧 Report Bug](https://github.com/your-repo/Legacy-Code-Migration/issues) | [💡 Request Feature](https://github.com/your-repo/Legacy-Code-Migration/issues)

</div>
