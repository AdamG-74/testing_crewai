"""
Data models for the Autonomous Agent-Based Testing Framework
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any
from enum import Enum
from datetime import datetime
import ast
from pathlib import Path


class CodeType(Enum):
    """Types of code units"""
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"


class TestType(Enum):
    """Types of test cases"""
    UNIT = "unit"
    INTEGRATION = "integration"
    FUNCTIONAL = "functional"
    MUTATION = "mutation"


@dataclass
class CodeUnit:
    """Represents a code unit (module, class, function, method)"""
    name: str
    type: CodeType
    file_path: Path
    line_start: int
    line_end: int
    complexity: int = 0
    dependencies: Set[str] = field(default_factory=set)
    docstring: Optional[str] = None
    signature: Optional[str] = None
    ast_node: Optional[ast.AST] = None
    
    def __hash__(self):
        return hash((self.name, self.file_path, self.line_start))
    
    def __eq__(self, other):
        if not isinstance(other, CodeUnit):
            return False
        return (self.name, self.file_path, self.line_start) == (other.name, other.file_path, other.line_start)


@dataclass
class TestCase:
    """Represents a test case"""
    name: str
    type: TestType
    file_path: Path
    line_start: int
    line_end: int
    tested_units: Set[str] = field(default_factory=set)
    assertions: int = 0
    mocks: int = 0
    complexity: int = 0
    docstring: Optional[str] = None
    source_code: Optional[str] = None
    
    def __hash__(self):
        return hash((self.name, self.file_path, self.line_start))
    
    def __eq__(self, other):
        if not isinstance(other, TestCase):
            return False
        return (self.name, self.file_path, self.line_start) == (other.name, other.file_path, other.line_start)


@dataclass
class QualityMetrics:
    """Quality metrics for test assessment"""
    coverage_percentage: float = 0.0
    mutation_score: float = 0.0
    assertion_density: float = 0.0
    test_clarity_score: float = 0.0
    complexity_score: float = 0.0
    mock_coverage: float = 0.0
    total_tests: int = 0
    total_assertions: int = 0
    total_mocks: int = 0
    uncovered_units: Set[str] = field(default_factory=set)
    low_quality_tests: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "coverage_percentage": self.coverage_percentage,
            "mutation_score": self.mutation_score,
            "assertion_density": self.assertion_density,
            "test_clarity_score": self.test_clarity_score,
            "complexity_score": self.complexity_score,
            "mock_coverage": self.mock_coverage,
            "total_tests": self.total_tests,
            "total_assertions": self.total_assertions,
            "total_mocks": self.total_mocks,
            "uncovered_units": list(self.uncovered_units),
            "low_quality_tests": self.low_quality_tests
        }


@dataclass
class MutationResults:
    """Results from mutation testing"""
    total_mutations: int = 0
    killed_mutations: int = 0
    survived_mutations: int = 0
    timeout_mutations: int = 0
    mutation_score: float = 0.0
    mutation_details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def calculate_score(self) -> float:
        """Calculate mutation score as percentage of killed mutations"""
        if self.total_mutations == 0:
            return 0.0
        return (self.killed_mutations / self.total_mutations) * 100


@dataclass
class AuditReport:
    """Before/after audit report"""
    project_name: str
    timestamp: datetime = field(default_factory=datetime.now)
    before_metrics: Optional[QualityMetrics] = None
    after_metrics: Optional[QualityMetrics] = None
    before_mutation: Optional[MutationResults] = None
    after_mutation: Optional[MutationResults] = None
    improvements: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    generated_tests: List[TestCase] = field(default_factory=list)
    modified_tests: List[TestCase] = field(default_factory=list)
    
    def get_improvement_summary(self) -> Dict[str, float]:
        """Calculate improvement deltas"""
        if not self.before_metrics or not self.after_metrics:
            return {}
        
        return {
            "coverage_delta": self.after_metrics.coverage_percentage - self.before_metrics.coverage_percentage,
            "mutation_score_delta": self.after_metrics.mutation_score - self.before_metrics.mutation_score,
            "assertion_density_delta": self.after_metrics.assertion_density - self.before_metrics.assertion_density,
            "test_clarity_delta": self.after_metrics.test_clarity_score - self.before_metrics.test_clarity_score,
            "complexity_score_delta": self.after_metrics.complexity_score - self.before_metrics.complexity_score,
            "mock_coverage_delta": self.after_metrics.mock_coverage - self.before_metrics.mock_coverage,
            "tests_added": self.after_metrics.total_tests - self.before_metrics.total_tests,
            "assertions_added": self.after_metrics.total_assertions - self.before_metrics.total_assertions
        } 