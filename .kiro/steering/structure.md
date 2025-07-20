# Project Structure & Organization

## Directory Layout

```
crewai-testing/
├── src/                          # Main source code
│   ├── __init__.py              # Package initialization & exports
│   ├── __main__.py              # Entry point for python -m src
│   ├── framework.py             # Core TestingFramework class
│   ├── agents.py                # AI agent implementations
│   ├── models.py                # Data models & enums
│   ├── llm_config.py           # LLM provider configuration
│   ├── cli.py                   # Command-line interface
│   ├── example_calculator.py    # Example code for testing
│   ├── reports/                 # Report generation modules
│   └── tests/                   # Internal framework tests
├── tests/                       # Project test suite
│   └── test_calculator_basic.py # Example test file
├── reports/                     # Generated audit reports
│   ├── audit_report_*.md       # Markdown reports
│   └── audit_data_*.json       # JSON data exports
├── .env                        # Environment variables
├── env.example                 # Environment template
├── pyproject.toml              # Poetry configuration
├── requirements.txt            # Pip fallback dependencies
├── setup.py                    # Package setup script
└── README.md                   # Project documentation
```

## Code Organization Patterns

### Agent Architecture
- **Single Responsibility**: Each agent has one specific role (CodeMapper, TestDiscovery, etc.)
- **Agent Base Pattern**: All agents follow similar initialization with LLM configuration
- **Composition**: Framework composes agents rather than inheriting from them

### Data Models
- **Dataclasses**: Use `@dataclass` for all data structures
- **Enums**: Type-safe enumerations for CodeType, TestType, Provider
- **Immutable Collections**: Use `Set[str]` with `field(default_factory=set)` for collections
- **Path Objects**: Use `pathlib.Path` instead of strings for file paths

### Error Handling
- **Graceful Degradation**: Framework continues operation when individual components fail
- **Fallback Mechanisms**: Default values and fallback implementations for LLM failures
- **Timeout Protection**: Subprocess calls include timeout parameters

### Configuration Management
- **Environment Variables**: Use python-dotenv for configuration
- **Auto-Detection**: LLM providers auto-detected based on available API keys
- **Validation**: Pydantic models for configuration validation

## Naming Conventions

### Files & Modules
- **Snake Case**: All Python files use snake_case (e.g., `llm_config.py`)
- **Descriptive Names**: File names clearly indicate purpose
- **Agent Suffix**: Agent classes end with "Agent" (e.g., `CodeMapperAgent`)

### Classes & Functions
- **PascalCase**: Class names use PascalCase (e.g., `TestingFramework`)
- **Snake Case**: Function and method names use snake_case
- **Verb-Noun Pattern**: Methods use action verbs (e.g., `map_codebase`, `assess_quality`)

### Constants & Enums
- **UPPER_CASE**: Constants use UPPER_CASE
- **Descriptive Values**: Enum values are lowercase strings matching their purpose

## Import Organization
```python
# Standard library imports first
import os
from pathlib import Path
from typing import List, Dict, Optional

# Third-party imports second
from crewai import Agent
from pydantic import BaseModel

# Local imports last
from .models import CodeUnit, TestCase
from .llm_config import LLMConfig
```

## Testing Structure
- **Mirror Source Structure**: Test files mirror the src/ directory structure
- **Test Prefix**: All test files start with `test_`
- **Descriptive Test Names**: Test functions clearly describe what they test
- **Pytest Conventions**: Follow pytest naming and organization patterns

## Report Generation
- **Timestamped Files**: All reports include timestamp in filename
- **Multiple Formats**: Generate both Markdown and JSON versions
- **Structured Data**: JSON exports contain structured data for programmatic access