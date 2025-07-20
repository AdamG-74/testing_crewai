"""
Agent definitions for the Autonomous Agent-Based Testing Framework
"""

from typing import List, Dict, Any, Optional, Set
from pathlib import Path
import ast
import networkx as nx
from crewai import Agent, Task
from .llm_config import llm_config, Provider
from .models import (
    CodeUnit, TestCase, QualityMetrics, MutationResults, 
    CodeType, TestType, AuditReport
)


class CodeMapperAgent:
    """Agent responsible for mapping codebase structure and dependencies"""
    
    def __init__(self, llm: Optional[Any] = None, provider: Optional[Provider] = None):
        self.llm = llm or llm_config.create_llm(provider=provider, temperature=0.1)
        self.agent = Agent(
            role="Code Structure Analyst",
            goal="Analyze and map the complete structure of a Python codebase including modules, classes, functions, and their dependencies",
            backstory="""You are an expert Python code analyst with deep knowledge of AST parsing, 
            dependency analysis, and code structure mapping. You can identify complex relationships 
            between code units and create comprehensive dependency graphs.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def map_codebase(self, source_path: Path) -> List[CodeUnit]:
        """Map the entire codebase structure"""
        code_units = []
        
        for py_file in source_path.rglob("*.py"):
            if "test" not in py_file.name.lower() and "__pycache__" not in str(py_file):
                units = self._parse_file(py_file)
                code_units.extend(units)
        
        return code_units
    
    def _parse_file(self, file_path: Path) -> List[CodeUnit]:
        """Parse a single Python file and extract code units"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            units = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    unit = CodeUnit(
                        name=node.name,
                        type=CodeType.FUNCTION,
                        file_path=file_path,
                        line_start=node.lineno,
                        line_end=node.end_lineno,
                        docstring=ast.get_docstring(node),
                        signature=self._get_function_signature(node),
                        ast_node=node
                    )
                    units.append(unit)
                
                elif isinstance(node, ast.ClassDef):
                    unit = CodeUnit(
                        name=node.name,
                        type=CodeType.CLASS,
                        file_path=file_path,
                        line_start=node.lineno,
                        line_end=node.end_lineno,
                        docstring=ast.get_docstring(node),
                        ast_node=node
                    )
                    units.append(unit)
                    
                    # Add methods
                    for child in node.body:
                        if isinstance(child, ast.FunctionDef):
                            method = CodeUnit(
                                name=f"{node.name}.{child.name}",
                                type=CodeType.METHOD,
                                file_path=file_path,
                                line_start=child.lineno,
                                line_end=child.end_lineno,
                                docstring=ast.get_docstring(child),
                                signature=self._get_function_signature(child),
                                ast_node=child
                            )
                            units.append(method)
            
            return units
            
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return []
    
    def _get_function_signature(self, node: ast.FunctionDef) -> str:
        """Extract function signature from AST node"""
        args = []
        for arg in node.args.args:
            args.append(arg.arg)
        
        return f"{node.name}({', '.join(args)})"
    
    def build_dependency_graph(self, code_units: List[CodeUnit]) -> nx.DiGraph:
        """Build a dependency graph from code units"""
        graph = nx.DiGraph()
        
        for unit in code_units:
            graph.add_node(unit.name, unit=unit)
            
            # Add dependencies based on imports and function calls
            if unit.ast_node:
                dependencies = self._extract_dependencies(unit.ast_node)
                for dep in dependencies:
                    graph.add_edge(unit.name, dep)
        
        return graph
    
    def _extract_dependencies(self, node: ast.AST) -> Set[str]:
        """Extract dependencies from an AST node"""
        dependencies = set()
        
        for child in ast.walk(node):
            if isinstance(child, ast.Import):
                for alias in child.names:
                    dependencies.add(alias.name)
            elif isinstance(child, ast.ImportFrom):
                if child.module:
                    dependencies.add(child.module)
            elif isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    dependencies.add(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    if isinstance(child.func.value, ast.Name):
                        dependencies.add(f"{child.func.value.id}.{child.func.attr}")
        
        return dependencies


class TestDiscoveryAgent:
    """Agent responsible for discovering and analyzing existing test cases"""
    
    def __init__(self, llm: Optional[Any] = None, provider: Optional[Provider] = None):
        self.llm = llm or llm_config.create_llm(provider=provider, temperature=0.1)
        self.agent = Agent(
            role="Test Discovery Specialist",
            goal="Discover, analyze, and classify existing test cases in the codebase",
            backstory="""You are an expert in test discovery and analysis. You can identify 
            test patterns, classify test types, and map test cases to the code they cover.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def discover_tests(self, test_path: Path) -> List[TestCase]:
        """Discover all test cases in the test directory"""
        test_cases = []
        
        for py_file in test_path.rglob("test_*.py"):
            cases = self._parse_test_file(py_file)
            test_cases.extend(cases)
        
        return test_cases
    
    def _parse_test_file(self, file_path: Path) -> List[TestCase]:
        """Parse a test file and extract test cases"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            test_cases = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                    test_case = TestCase(
                        name=node.name,
                        type=self._classify_test_type(node),
                        file_path=file_path,
                        line_start=node.lineno,
                        line_end=node.end_lineno,
                        docstring=ast.get_docstring(node),
                        source_code=ast.unparse(node),
                        assertions=self._count_assertions(node),
                        mocks=self._count_mocks(node),
                        complexity=self._calculate_complexity(node)
                    )
                    test_cases.append(test_case)
            
            return test_cases
            
        except Exception as e:
            print(f"Error parsing test file {file_path}: {e}")
            return []
    
    def _classify_test_type(self, node: ast.FunctionDef) -> TestType:
        """Classify the type of test based on its content and name"""
        name = node.name.lower()
        docstring = ast.get_docstring(node) or ""
        
        if "integration" in name or "integration" in docstring.lower():
            return TestType.INTEGRATION
        elif "functional" in name or "functional" in docstring.lower():
            return TestType.FUNCTIONAL
        else:
            return TestType.UNIT
    
    def _count_assertions(self, node: ast.FunctionDef) -> int:
        """Count the number of assertions in a test function"""
        count = 0
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name) and child.func.id.startswith('assert'):
                    count += 1
                elif isinstance(child.func, ast.Attribute) and child.func.attr.startswith('assert'):
                    count += 1
        return count
    
    def _count_mocks(self, node: ast.FunctionDef) -> int:
        """Count the number of mocks in a test function"""
        count = 0
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name) and 'mock' in child.func.id.lower():
                    count += 1
                elif isinstance(child.func, ast.Attribute) and 'mock' in child.func.attr.lower():
                    count += 1
        return count
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a test function"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
        
        return complexity


class TestAssessorAgent:
    """Agent responsible for assessing test quality and coverage"""
    
    def __init__(self, llm: Optional[Any] = None, provider: Optional[Provider] = None):
        self.llm = llm or llm_config.create_llm(provider=provider, temperature=0.1)
        self.agent = Agent(
            role="Test Quality Assessor",
            goal="Assess the quality, coverage, and effectiveness of existing test cases",
            backstory="""You are an expert in test quality assessment with deep knowledge 
            of coverage analysis, mutation testing, and test effectiveness metrics.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def assess_quality(self, code_units: List[CodeUnit], test_cases: List[TestCase]) -> QualityMetrics:
        """Assess the overall quality of the test suite"""
        metrics = QualityMetrics()
        
        # Calculate coverage
        covered_units = set()
        for test in test_cases:
            covered_units.update(test.tested_units)
        
        metrics.uncovered_units = {unit.name for unit in code_units} - covered_units
        metrics.coverage_percentage = (len(covered_units) / len(code_units)) * 100 if code_units else 0
        
        # Calculate assertion density
        total_assertions = sum(test.assertions for test in test_cases)
        metrics.total_assertions = total_assertions
        metrics.assertion_density = total_assertions / len(test_cases) if test_cases else 0
        
        # Calculate mock coverage
        total_mocks = sum(test.mocks for test in test_cases)
        metrics.total_mocks = total_mocks
        metrics.mock_coverage = total_mocks / len(test_cases) if test_cases else 0
        
        # Calculate complexity score
        total_complexity = sum(test.complexity for test in test_cases)
        metrics.complexity_score = total_complexity / len(test_cases) if test_cases else 0
        
        # Assess test clarity using LLM
        metrics.test_clarity_score = self._assess_test_clarity(test_cases)
        
        # Identify low quality tests
        metrics.low_quality_tests = self._identify_low_quality_tests(test_cases)
        
        metrics.total_tests = len(test_cases)
        
        return metrics
    
    def _assess_test_clarity(self, test_cases: List[TestCase]) -> float:
        """Assess test clarity using LLM analysis"""
        if not test_cases:
            return 0.0
        
        total_score = 0.0
        for test in test_cases[:10]:  # Sample first 10 tests for efficiency
            if test.source_code:
                prompt = f"""
                Analyze the following test case for clarity, readability, and best practices.
                Score from 0-10 where 10 is excellent:
                
                Test: {test.name}
                Code: {test.source_code}
                
                Consider:
                - Clear naming and structure
                - Proper setup and teardown
                - Meaningful assertions
                - Good documentation
                - Follows testing best practices
                
                Return only a number between 0-10:
                """
                
                try:
                    response = self.llm.invoke(prompt)
                    score = float(response.content.strip())
                    total_score += min(max(score, 0), 10)  # Clamp between 0-10
                except:
                    total_score += 5.0  # Default score on error
        
        return total_score / min(len(test_cases), 10)
    
    def _identify_low_quality_tests(self, test_cases: List[TestCase]) -> List[str]:
        """Identify tests that need improvement"""
        low_quality = []
        
        for test in test_cases:
            issues = []
            
            if test.assertions == 0:
                issues.append("no assertions")
            if test.complexity > 5:
                issues.append("high complexity")
            if not test.docstring:
                issues.append("no documentation")
            if test.mocks == 0 and test.assertions > 0:
                issues.append("no mocking")
            
            if issues:
                low_quality.append(f"{test.name} ({', '.join(issues)})")
        
        return low_quality


class TestGeneratorAgent:
    """Agent responsible for generating new test cases using LLM"""
    
    def __init__(self, llm: Optional[Any] = None, provider: Optional[Provider] = None):
        self.llm = llm or llm_config.create_llm(provider=provider, temperature=0.3)
        self.agent = Agent(
            role="Test Generation Specialist",
            goal="Generate high-quality test cases for uncovered or poorly tested code units",
            backstory="""You are an expert test developer with deep knowledge of testing 
            patterns, best practices, and effective test case design. You can create 
            comprehensive test suites that improve coverage and quality.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def generate_tests(self, code_unit: CodeUnit, existing_tests: List[TestCase]) -> List[TestCase]:
        """Generate test cases for a specific code unit"""
        prompt = self._create_test_generation_prompt(code_unit, existing_tests)
        
        try:
            response = self.llm.invoke(prompt)
            generated_code = self._extract_test_code(response.content)
            
            if generated_code:
                test_case = TestCase(
                    name=f"test_{code_unit.name}",
                    type=TestType.UNIT,
                    file_path=Path(f"tests/test_{code_unit.name}.py"),
                    line_start=1,
                    line_end=len(generated_code.split('\n')),
                    tested_units={code_unit.name},
                    source_code=generated_code,
                    assertions=self._count_assertions_in_code(generated_code),
                    mocks=self._count_mocks_in_code(generated_code)
                )
                return [test_case]
        
        except Exception as e:
            print(f"Error generating tests for {code_unit.name}: {e}")
        
        return []
    
    def _create_test_generation_prompt(self, code_unit: CodeUnit, existing_tests: List[TestCase]) -> str:
        """Create a prompt for test generation"""
        existing_test_info = ""
        if existing_tests:
            existing_test_info = f"\nExisting tests: {[t.name for t in existing_tests]}"
        
        return f"""
        Generate comprehensive test cases for the following Python code unit:
        
        Name: {code_unit.name}
        Type: {code_unit.type.value}
        File: {code_unit.file_path}
        Lines: {code_unit.line_start}-{code_unit.line_end}
        Signature: {code_unit.signature or 'N/A'}
        Docstring: {code_unit.docstring or 'N/A'}
        {existing_test_info}
        
        Requirements:
        1. Use pytest framework
        2. Include multiple test scenarios (happy path, edge cases, error cases)
        3. Use descriptive test names
        4. Include proper setup and teardown if needed
        5. Use mocking for external dependencies
        6. Add docstrings to test functions
        7. Follow testing best practices
        
        Generate only the test code (no explanations):
        """
    
    def _extract_test_code(self, response: str) -> str:
        """Extract test code from LLM response"""
        # Simple extraction - look for code blocks
        if "```python" in response:
            start = response.find("```python") + 9
            end = response.find("```", start)
            return response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            return response[start:end].strip()
        else:
            return response.strip()
    
    def _count_assertions_in_code(self, code: str) -> int:
        """Count assertions in generated code"""
        return code.count("assert ") + code.count(".assert")
    
    def _count_mocks_in_code(self, code: str) -> int:
        """Count mocks in generated code"""
        return code.count("mock") + code.count("Mock") + code.count("patch")


class TestJudgeAgent:
    """Agent responsible for judging and validating generated tests"""
    
    def __init__(self, llm: Optional[Any] = None, provider: Optional[Provider] = None):
        self.llm = llm or llm_config.create_llm(provider=provider, temperature=0.1)
        self.agent = Agent(
            role="Test Quality Judge",
            goal="Evaluate and validate generated test cases for quality and effectiveness",
            backstory="""You are an expert test reviewer with deep knowledge of testing 
            standards, quality metrics, and best practices. You can identify issues and 
            suggest improvements for test cases.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def judge_test(self, test_case: TestCase, code_unit: CodeUnit) -> Dict[str, Any]:
        """Judge the quality of a generated test case"""
        prompt = f"""
        Evaluate the following test case for quality and effectiveness:
        
        Test Case:
        Name: {test_case.name}
        Code: {test_case.source_code}
        
        Code Unit Being Tested:
        Name: {code_unit.name}
        Type: {code_unit.type.value}
        Signature: {code_unit.signature or 'N/A'}
        Docstring: {code_unit.docstring or 'N/A'}
        
        Evaluate on a scale of 1-10 for each criterion:
        1. Coverage completeness
        2. Test case variety (happy path, edge cases, error cases)
        3. Assertion quality
        4. Mocking effectiveness
        5. Code readability
        6. Documentation quality
        
        Provide scores and specific feedback for improvement.
        """
        
        try:
            response = self.llm.invoke(prompt)
            return self._parse_judgment_response(response.content)
        except Exception as e:
            print(f"Error judging test {test_case.name}: {e}")
            return {"overall_score": 5.0, "feedback": ["Error in evaluation"]}
    
    def _parse_judgment_response(self, response: str) -> Dict[str, Any]:
        """Parse the judgment response from LLM"""
        # Simple parsing - in a real implementation, you'd want more sophisticated parsing
        lines = response.split('\n')
        scores = {}
        feedback = []
        
        for line in lines:
            if any(criterion in line.lower() for criterion in ['coverage', 'variety', 'assertion', 'mocking', 'readability', 'documentation']):
                try:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        criterion = parts[0].strip()
                        score_text = parts[1].strip()
                        score = float(score_text.split()[0])
                        scores[criterion] = score
                except:
                    pass
            elif line.strip() and not line.startswith('#'):
                feedback.append(line.strip())
        
        overall_score = sum(scores.values()) / len(scores) if scores else 5.0
        
        return {
            "overall_score": overall_score,
            "criterion_scores": scores,
            "feedback": feedback
        }


class AuditReporterAgent:
    """Agent responsible for generating comprehensive audit reports"""
    
    def __init__(self, llm: Optional[Any] = None, provider: Optional[Provider] = None):
        self.llm = llm or llm_config.create_llm(provider=provider, temperature=0.1)
        self.agent = Agent(
            role="Audit Report Specialist",
            goal="Generate comprehensive before/after audit reports with actionable insights",
            backstory="""You are an expert technical writer and analyst specializing in 
            test quality assessment and improvement reporting. You can create clear, 
            actionable reports that highlight improvements and recommendations.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def generate_report(self, audit_data: AuditReport) -> str:
        """Generate a comprehensive audit report"""
        prompt = self._create_report_prompt(audit_data)
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            print(f"Error generating report: {e}")
            return self._generate_fallback_report(audit_data)
    
    def _create_report_prompt(self, audit_data: AuditReport) -> str:
        """Create a prompt for report generation"""
        improvements = audit_data.get_improvement_summary()
        
        before_coverage = f"{audit_data.before_metrics.coverage_percentage:.1f}%" if audit_data.before_metrics else 'N/A'
        before_mutation = f"{audit_data.before_metrics.mutation_score:.1f}%" if audit_data.before_metrics else 'N/A'
        before_tests = audit_data.before_metrics.total_tests if audit_data.before_metrics else 'N/A'
        before_assertions = audit_data.before_metrics.total_assertions if audit_data.before_metrics else 'N/A'
        
        after_coverage = f"{audit_data.after_metrics.coverage_percentage:.1f}%" if audit_data.after_metrics else 'N/A'
        after_mutation = f"{audit_data.after_metrics.mutation_score:.1f}%" if audit_data.after_metrics else 'N/A'
        after_tests = audit_data.after_metrics.total_tests if audit_data.after_metrics else 'N/A'
        after_assertions = audit_data.after_metrics.total_assertions if audit_data.after_metrics else 'N/A'
        
        improvements_text = chr(10).join(f"- {k}: {v:.2f}" for k, v in improvements.items())
        
        return f"""
        Generate a comprehensive audit report for the testing framework improvement project.
        
        Project: {audit_data.project_name}
        Timestamp: {audit_data.timestamp}
        
        Before Metrics:
        - Coverage: {before_coverage}
        - Mutation Score: {before_mutation}
        - Total Tests: {before_tests}
        - Total Assertions: {before_assertions}
        
        After Metrics:
        - Coverage: {after_coverage}
        - Mutation Score: {after_mutation}
        - Total Tests: {after_tests}
        - Total Assertions: {after_assertions}
        
        Improvements:
        {improvements_text}
        
        Generated Tests: {len(audit_data.generated_tests)}
        Modified Tests: {len(audit_data.modified_tests)}
        
        Recommendations: {audit_data.recommendations}
        
        Create a professional markdown report with:
        1. Executive Summary
        2. Detailed Metrics Comparison
        3. Key Improvements
        4. Recommendations
        5. Next Steps
        
        Format as clean markdown:
        """
    
    def _generate_fallback_report(self, audit_data: AuditReport) -> str:
        """Generate a fallback report if LLM fails"""
        improvements = audit_data.get_improvement_summary()
        
        before_coverage = f"{audit_data.before_metrics.coverage_percentage:.1f}%" if audit_data.before_metrics else 'N/A'
        before_mutation = f"{audit_data.before_metrics.mutation_score:.1f}%" if audit_data.before_metrics else 'N/A'
        before_tests = audit_data.before_metrics.total_tests if audit_data.before_metrics else 'N/A'
        
        after_coverage = f"{audit_data.after_metrics.coverage_percentage:.1f}%" if audit_data.after_metrics else 'N/A'
        after_mutation = f"{audit_data.after_metrics.mutation_score:.1f}%" if audit_data.after_metrics else 'N/A'
        after_tests = audit_data.after_metrics.total_tests if audit_data.after_metrics else 'N/A'
        
        report = f"""
# Testing Framework Audit Report

## Project: {audit_data.project_name}
**Generated:** {audit_data.timestamp}

## Executive Summary
This report details the improvements made to the testing framework through autonomous agent-based analysis and enhancement.

## Metrics Comparison

### Before Enhancement
- Coverage: {before_coverage}
- Mutation Score: {before_mutation}
- Total Tests: {before_tests}

### After Enhancement
- Coverage: {after_coverage}
- Mutation Score: {after_mutation}
- Total Tests: {after_tests}

## Key Improvements
"""
        
        for metric, value in improvements.items():
            report += f"- **{metric.replace('_', ' ').title()}**: {value:+.2f}\n"
        
        report += f"""
## Generated Tests
- New test cases created: {len(audit_data.generated_tests)}
- Modified test cases: {len(audit_data.modified_tests)}

## Recommendations
"""
        
        for rec in audit_data.recommendations:
            report += f"- {rec}\n"
        
        return report 