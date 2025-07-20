# Technology Stack & Build System

## Core Technologies

### Python Environment
- **Python Version**: 3.11+ (supports up to 3.13)
- **Package Manager**: Poetry (primary) with pip fallback via requirements.txt
- **Virtual Environment**: Managed by Poetry

### AI/ML Framework Stack
- **CrewAI**: Multi-agent orchestration framework
- **LangChain**: LLM integration and chaining
- **LiteLLM**: Universal LLM API interface
- **Supported LLM Providers**: OpenAI, Azure OpenAI, Anthropic, Google, Cohere

### Testing & Analysis Tools
- **pytest**: Primary testing framework with coverage support
- **coverage.py**: Code coverage analysis
- **mutmut**: Mutation testing framework
- **radon**: Code complexity analysis

### Code Analysis & Visualization
- **networkx**: Dependency graph construction
- **graphviz**: Graph visualization
- **AST**: Built-in Python AST parsing for code structure analysis

### CLI & UI
- **click**: Command-line interface framework
- **rich**: Terminal formatting and progress displays
- **jinja2**: Template engine for report generation

### Data & Configuration
- **pydantic**: Data validation and serialization
- **python-dotenv**: Environment variable management
- **PyYAML**: YAML configuration parsing
- **markdown**: Report generation

## Common Commands

### Development Setup
```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Install dev dependencies
poetry install --with dev
```

### Testing
```bash
# Run tests with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_calculator_basic.py -v

# Run mutation testing
mutmut run
```

### Framework Usage
```bash
# Run full audit
python -m src audit ./project-path --verbose

# Analyze without changes
python -m src analyze ./project-path

# Generate tests only
python -m src generate ./project-path

# Custom provider/model
python -m src audit ./project-path --provider azure_openai --model gpt-4
```

### Code Quality
```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## Environment Configuration

### Required Environment Variables
```bash
# Choose one provider:
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_ENDPOINT=your-endpoint
AZURE_OPENAI_API_VERSION=2023-07-01-preview

# OR
OPENAI_API_KEY=your-key

# OR
ANTHROPIC_API_KEY=your-key
```

### Project Structure Requirements
- Source code in `src/` directory
- Tests in `tests/` directory
- Reports generated in `reports/` directory
- Configuration via `.env` file