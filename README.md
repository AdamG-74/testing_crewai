# Autonomous Agent-Based Testing Framework

A comprehensive Python framework that uses AI agents to autonomously analyze, assess, and improve test quality through dependency mapping, mutation testing, and intelligent test generation.

## 🎯 Overview

This framework implements a fully autonomous testing improvement system that:

1. **Maps Codebase Structure** - Uses AST parsing to create comprehensive dependency graphs
2. **Discovers Existing Tests** - Analyzes and classifies current test coverage
3. **Assesses Test Quality** - Evaluates coverage, assertions, mocking, and mutation scores
4. **Generates New Tests** - Uses LLM agents to create high-quality test cases
5. **Runs Mutation Testing** - Validates test effectiveness through fault injection
6. **Produces Audit Reports** - Generates detailed before/after comparisons

## 🏗️ Architecture

### Agent Roles

| Agent | Responsibility |
|-------|---------------|
| **CodeMapperAgent** | AST parsing, dependency analysis, code structure mapping |
| **TestDiscoveryAgent** | Test file analysis, test classification, coverage mapping |
| **TestAssessorAgent** | Quality metrics calculation, coverage analysis |
| **TestGeneratorAgent** | LLM-powered test generation with best practices |
| **TestJudgeAgent** | Test quality evaluation and validation |
| **AuditReporterAgent** | Comprehensive reporting and recommendations |

### Quality Metrics

- **Coverage Percentage** - Lines of code exercised by tests
- **Mutation Score** - Fault detection rate through mutation testing
- **Assertion Density** - Number of assertions per test case
- **Test Clarity Score** - LLM-based readability assessment
- **Complexity Score** - Cyclomatic complexity analysis
- **Mock Coverage** - Dependency isolation effectiveness

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd crewai_testing

# Install dependencies
poetry install

# Set up environment variables in .env file
# For Azure OpenAI:
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_ENDPOINT=your-endpoint
AZURE_OPENAI_API_VERSION=2023-07-01-preview

# For OpenAI:
OPENAI_API_KEY=your-key

# For Anthropic:
ANTHROPIC_API_KEY=your-key
```

### Basic Usage

```python
from src import TestingFramework
from pathlib import Path

# Initialize framework (auto-detects provider)
framework = TestingFramework(
    project_path=Path("./your-project"),
    model="gpt-4"  # Optional, auto-detected based on provider
)

# Run full audit
audit_report = framework.run_full_audit(
    generate_tests=True,
    run_mutation_testing=True,
    max_iterations=3
)

# View results
print(f"Coverage improved by: {audit_report.get_improvement_summary()}")
```

### Command Line Interface

```bash
# Run full audit
python -m src audit ./your-project --verbose

# Analyze without making changes
python -m src analyze ./your-project

# Generate tests for uncovered code
python -m src generate ./your-project

# Custom options
python -m src audit ./your-project \
    --provider azure_openai \
    --model gpt-4 \
    --no-mutation \
    --iterations 5 \
    --verbose
```

## 📊 Example Output

```
🚀 Starting Autonomous Testing Framework Audit
📁 Project: /path/to/your-project

📊 Stage 1: Mapping Codebase Structure
   Found 15 code units

🔍 Stage 2: Discovering Existing Tests
   Found 8 existing test cases

📈 Stage 3: Assessing Initial Test Quality
   📊 Before Metrics:
      Coverage: 45.2%
      Total Tests: 8
      Total Assertions: 24
      Assertion Density: 3.00
      Test Clarity Score: 7.2/10
      Uncovered Units: 7

🧬 Stage 4: Running Initial Mutation Testing
   🧬 Before Mutation Results:
      Total Mutations: 42
      Killed: 28
      Survived: 14
      Mutation Score: 66.7%

🤖 Stage 5: Autonomous Test Generation and Improvement
   🔄 Iteration 1/3
   🎯 Targeting 7 units for improvement
   ✅ Generated high-quality test for calculate_compound_interest
   ✅ Generated high-quality test for AdvancedCalculator.sin

📊 Stage 6: Final Quality Assessment
   📊 After Metrics:
      Coverage: 78.9%
      Total Tests: 12
      Total Assertions: 41
      Assertion Density: 3.42
      Test Clarity Score: 8.1/10
      Uncovered Units: 2

🧬 Stage 7: Running Final Mutation Testing
   🧬 After Mutation Results:
      Total Mutations: 42
      Killed: 35
      Survived: 7
      Mutation Score: 83.3%

📋 Stage 8: Generating Audit Report
   📄 Report saved: reports/audit_report_20241201_143022.md
   📊 Data saved: reports/audit_data_20241201_143022.json

✅ Audit Complete! Report saved to: reports/
```

## 🔧 Configuration

### Environment Variables

```bash
# Azure OpenAI (recommended)
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_ENDPOINT=your-endpoint
AZURE_OPENAI_API_VERSION=2023-07-01-preview

# OpenAI
OPENAI_API_KEY=your-key

# Anthropic
ANTHROPIC_API_KEY=your-key

# Google
GOOGLE_API_KEY=your-key

# Cohere
COHERE_API_KEY=your-key
```

### Project Structure

```
your-project/
├── src/                    # Source code
├── tests/                  # Test files
├── reports/                # Generated reports
├── pyproject.toml         # Project configuration
└── .env                   # Environment variables
```

### Framework Configuration

```python
framework = TestingFramework(
    project_path=Path("./project"),
    provider=Provider.AZURE_OPENAI,  # Optional, auto-detected
    model="gpt-4",                   # Optional, auto-detected
    temperature=0.1                  # Default: 0.1
)
```

## 📈 Quality Metrics Explained

### Coverage Percentage
- **Calculation**: (Lines covered / Total lines) × 100
- **Target**: ≥80% for production code
- **Tool**: coverage.py

### Mutation Score
- **Calculation**: (Killed mutations / Total mutations) × 100
- **Target**: ≥70% for effective tests
- **Tool**: mutmut

### Assertion Density
- **Calculation**: Total assertions / Total test cases
- **Target**: ≥2.0 assertions per test
- **Purpose**: Ensures comprehensive validation

### Test Clarity Score
- **Calculation**: LLM-based assessment (0-10 scale)
- **Target**: ≥7.0 for readability
- **Factors**: Naming, structure, documentation, best practices

## 🤖 Agent Capabilities

### CodeMapperAgent
- AST-based code parsing
- Dependency graph construction
- Function/class/method identification
- Import and call analysis

### TestDiscoveryAgent
- Test file pattern recognition
- Test function classification
- Coverage mapping
- Assertion and mock counting

### TestAssessorAgent
- Coverage calculation
- Quality metric computation
- Low-quality test identification
- LLM-based clarity assessment

### TestGeneratorAgent
- Context-aware test generation
- Best practice adherence
- Edge case consideration
- Mock and assertion optimization

### TestJudgeAgent
- Quality validation
- Best practice checking
- Improvement suggestions
- Score-based filtering

### AuditReporterAgent
- Comprehensive reporting
- Before/after comparison
- Actionable recommendations
- Multiple output formats

## 🧪 Testing the Framework

The framework includes example code and tests to demonstrate its capabilities:

```bash
# Run the example tests
pytest tests/test_calculator_basic.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run mutation testing
mutmut run
```

## 📋 Requirements

- Python 3.11+
- OpenAI API key
- Poetry (for dependency management)

### Dependencies

- **Core**: crewai, langchain, litellm
- **Testing**: pytest, pytest-cov, coverage, mutmut
- **Analysis**: networkx, graphviz, radon
- **CLI**: click, rich
- **Utilities**: pyyaml, markdown, pydantic

## 🔄 Workflow Stages

1. **Codebase Mapping** - Extract dependency graph
2. **Test Discovery** - Locate and classify existing tests
3. **Quality Assessment** - Calculate metrics and identify gaps
4. **Test Generation** - Create new tests using LLM agents
5. **Quality Validation** - Judge and filter generated tests
6. **Mutation Testing** - Validate test effectiveness
7. **Re-assessment** - Calculate improved metrics
8. **Reporting** - Generate comprehensive audit report

## 🎯 Best Practices

### For Framework Users
- Set appropriate quality thresholds
- Review generated tests before committing
- Use mutation testing for critical code
- Monitor improvement trends over time

### For Framework Developers
- Extend agent capabilities with domain-specific logic
- Add custom quality metrics
- Implement additional test generation strategies
- Create specialized agents for specific testing needs

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📞 Support

For questions, issues, or contributions:
- Open an issue on GitHub
- Check the documentation
- Review example implementations

---

**Built with ❤️ using CrewAI and LangChain** 