"""
Main framework for Autonomous Agent-Based Testing
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import yaml

from dotenv import load_dotenv

from .models import (
    CodeUnit, TestCase, QualityMetrics, MutationResults, 
    AuditReport, CodeType, TestType
)
from .agents import (
    CodeMapperAgent, TestDiscoveryAgent, TestAssessorAgent,
    TestGeneratorAgent, TestJudgeAgent, AuditReporterAgent
)
from .llm_config import LLMConfig, Provider


class TestingFramework:
    """
    Main framework for autonomous agent-based testing improvement
    """
    
    def __init__(self, 
                 project_path: Path,
                 provider: Optional[Provider] = None,
                 model: Optional[str] = None,
                 temperature: float = 0.1):
        """
        Initialize the testing framework
        
        Args:
            project_path: Path to the project root
            provider: LLM provider (auto-detected if not specified)
            model: LLM model to use (auto-detected if not specified)
            temperature: Temperature for LLM responses
        """
        load_dotenv()
        
        self.project_path = Path(project_path)
        self.source_path = self.project_path / "src"
        self.test_path = self.project_path / "tests"
        self.reports_path = self.project_path / "reports"
        
        # Create necessary directories
        self.reports_path.mkdir(exist_ok=True)
        self.test_path.mkdir(exist_ok=True)
        
        # Initialize LLMConfig after loading dotenv
        self.llm_config = LLMConfig()
        self.llm = self.llm_config.create_llm(
            provider=provider,
            model=model,
            temperature=temperature
        )
        # Initialize agents with the correct provider
        self.code_mapper = CodeMapperAgent(provider=provider)
        self.test_discovery = TestDiscoveryAgent(provider=provider)
        self.test_assessor = TestAssessorAgent(provider=provider)
        self.test_generator = TestGeneratorAgent(provider=provider)
        self.test_judge = TestJudgeAgent(provider=provider)
        self.audit_reporter = AuditReporterAgent(provider=provider)
        
        # State tracking
        self.code_units: List[CodeUnit] = []
        self.test_cases: List[TestCase] = []
        self.before_metrics: Optional[QualityMetrics] = None
        self.after_metrics: Optional[QualityMetrics] = None
        self.before_mutation: Optional[MutationResults] = None
        self.after_mutation: Optional[MutationResults] = None
        self.generated_tests: List[TestCase] = []
        self.modified_tests: List[TestCase] = []
    
    def run_full_audit(self, 
                      generate_tests: bool = True,
                      run_mutation_testing: bool = True,
                      max_iterations: int = 3) -> AuditReport:
        """
        Run the complete autonomous testing improvement workflow
        
        Args:
            generate_tests: Whether to generate new tests
            run_mutation_testing: Whether to run mutation testing
            max_iterations: Maximum iterations for test improvement
            
        Returns:
            AuditReport with before/after comparison
        """
        print("🚀 Starting Autonomous Testing Framework Audit")
        print(f"📁 Project: {self.project_path}")
        
        # Stage 1: Codebase Mapping
        print("\n📊 Stage 1: Mapping Codebase Structure")
        self.code_units = self.code_mapper.map_codebase(self.source_path)
        print(f"   Found {len(self.code_units)} code units")
        
        # Stage 2: Test Discovery
        print("\n🔍 Stage 2: Discovering Existing Tests")
        self.test_cases = self.test_discovery.discover_tests(self.test_path)
        print(f"   Found {len(self.test_cases)} existing test cases")
        
        # Stage 3: Initial Quality Assessment
        print("\n📈 Stage 3: Assessing Initial Test Quality")
        self.before_metrics = self.test_assessor.assess_quality(self.code_units, self.test_cases)
        self._print_metrics("Before", self.before_metrics)
        
        # Stage 4: Mutation Testing (Before)
        if run_mutation_testing:
            print("\n🧬 Stage 4: Running Initial Mutation Testing")
            self.before_mutation = self._run_mutation_testing()
            self._print_mutation_results("Before", self.before_mutation)
        
        # Stage 5: Autonomous Test Generation and Improvement
        if generate_tests:
            print("\n🤖 Stage 5: Autonomous Test Generation and Improvement")
            self._improve_tests_iteratively(max_iterations)
        
        # Stage 6: Final Assessment
        print("\n📊 Stage 6: Final Quality Assessment")
        self.after_metrics = self.test_assessor.assess_quality(self.code_units, self.test_cases)
        self._print_metrics("After", self.after_metrics)
        
        # Stage 7: Final Mutation Testing
        if run_mutation_testing:
            print("\n🧬 Stage 7: Running Final Mutation Testing")
            self.after_mutation = self._run_mutation_testing()
            self._print_mutation_results("After", self.after_mutation)
        
        # Stage 8: Generate Audit Report
        print("\n📋 Stage 8: Generating Audit Report")
        audit_report = self._generate_audit_report()
        
        # Save report
        self._save_audit_report(audit_report)
        
        print(f"\n✅ Audit Complete! Report saved to: {self.reports_path}")
        return audit_report
    
    def _improve_tests_iteratively(self, max_iterations: int):
        """Iteratively improve tests using autonomous agents"""
        for iteration in range(max_iterations):
            print(f"\n   🔄 Iteration {iteration + 1}/{max_iterations}")
            
            # Identify units that need better testing
            uncovered_units = self._identify_uncovered_units()
            low_quality_units = self._identify_low_quality_units()
            
            target_units = list(uncovered_units) + list(low_quality_units)
            
            if not target_units:
                print("   ✅ No units need improvement")
                break
            
            print(f"   🎯 Targeting {len(target_units)} units for improvement")
            
            improvements_made = False
            
            for unit_name in target_units[:5]:  # Limit to 5 units per iteration
                unit = self._find_code_unit(unit_name)
                if not unit:
                    continue
                
                # Generate new tests
                new_tests = self.test_generator.generate_tests(unit, self.test_cases)
                
                if new_tests:
                    # Judge the quality of generated tests
                    for test in new_tests:
                        judgment = self.test_judge.judge_test(test, unit)
                        
                        if judgment.get("overall_score", 0) >= 7.0:  # Quality threshold
                            # Save the test
                            self._save_test_case(test)
                            self.test_cases.append(test)
                            self.generated_tests.append(test)
                            improvements_made = True
                            print(f"   ✅ Generated high-quality test for {unit_name}")
                        else:
                            print(f"   ❌ Rejected low-quality test for {unit_name}")
            
            if not improvements_made:
                print("   ⚠️  No improvements made in this iteration")
                break
    
    def _identify_uncovered_units(self) -> set:
        """Identify code units that have no test coverage"""
        covered_units = set()
        for test in self.test_cases:
            covered_units.update(test.tested_units)
        
        all_units = {unit.name for unit in self.code_units}
        return all_units - covered_units
    
    def _identify_low_quality_units(self) -> set:
        """Identify units with low-quality tests"""
        low_quality_units = set()
        
        # Group tests by tested unit
        unit_tests = {}
        for test in self.test_cases:
            for unit_name in test.tested_units:
                if unit_name not in unit_tests:
                    unit_tests[unit_name] = []
                unit_tests[unit_name].append(test)
        
        # Identify units with low-quality tests
        for unit_name, tests in unit_tests.items():
            total_assertions = sum(test.assertions for test in tests)
            total_mocks = sum(test.mocks for test in tests)
            
            if total_assertions < 3 or total_mocks < 1:
                low_quality_units.add(unit_name)
        
        return low_quality_units
    
    def _find_code_unit(self, unit_name: str) -> Optional[CodeUnit]:
        """Find a code unit by name"""
        for unit in self.code_units:
            if unit.name == unit_name:
                return unit
        return None
    
    def _save_test_case(self, test_case: TestCase):
        """Save a generated test case to file"""
        test_file = self.test_path / test_case.file_path.name
        
        # Create test file content
        content = f"""import pytest
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

{test_case.source_code}
"""
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _run_mutation_testing(self) -> MutationResults:
        """Run mutation testing on the codebase"""
        try:
            # Create a temporary directory for mutation testing
            with tempfile.TemporaryDirectory() as temp_dir:
                # Copy project to temp directory
                import shutil
                temp_project = Path(temp_dir) / "project"
                shutil.copytree(self.project_path, temp_project, dirs_exist_ok=True)
                
                # Run mutmut
                result = subprocess.run(
                    ["mutmut", "run"],
                    cwd=temp_project,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                # Parse results
                return self._parse_mutmut_results(result.stdout, result.stderr)
                
        except Exception as e:
            print(f"   ⚠️  Mutation testing failed: {e}")
            return MutationResults()
    
    def _parse_mutmut_results(self, stdout: str, stderr: str) -> MutationResults:
        """Parse mutmut output to extract results"""
        results = MutationResults()
        
        # Simple parsing - in production you'd want more sophisticated parsing
        lines = stdout.split('\n')
        
        for line in lines:
            if "surviving" in line.lower():
                try:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part.isdigit():
                            results.survived_mutations = int(part)
                            break
                except:
                    pass
            elif "killed" in line.lower():
                try:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part.isdigit():
                            results.killed_mutations = int(part)
                            break
                except:
                    pass
        
        results.total_mutations = results.killed_mutations + results.survived_mutations
        results.mutation_score = results.calculate_score()
        
        return results
    
    def _generate_audit_report(self) -> AuditReport:
        """Generate the final audit report"""
        improvements = []
        recommendations = []
        
        # Calculate improvements
        if self.before_metrics and self.after_metrics:
            coverage_delta = self.after_metrics.coverage_percentage - self.before_metrics.coverage_percentage
            if coverage_delta > 0:
                improvements.append(f"Coverage improved by {coverage_delta:.1f}%")
            
            tests_added = self.after_metrics.total_tests - self.before_metrics.total_tests
            if tests_added > 0:
                improvements.append(f"Added {tests_added} new test cases")
        
        # Generate recommendations
        if self.after_metrics:
            if self.after_metrics.coverage_percentage < 80:
                recommendations.append("Increase test coverage to at least 80%")
            
            if self.after_metrics.mutation_score < 70:
                recommendations.append("Improve mutation score by adding more comprehensive assertions")
            
            if self.after_metrics.assertion_density < 2.0:
                recommendations.append("Increase assertion density for better test effectiveness")
        
        return AuditReport(
            project_name=self.project_path.name,
            before_metrics=self.before_metrics,
            after_metrics=self.after_metrics,
            before_mutation=self.before_mutation,
            after_mutation=self.after_mutation,
            improvements=improvements,
            recommendations=recommendations,
            generated_tests=self.generated_tests,
            modified_tests=self.modified_tests
        )
    
    def _save_audit_report(self, audit_report: AuditReport):
        """Save the audit report to file"""
        # Generate markdown report
        markdown_report = self.audit_reporter.generate_report(audit_report)
        
        # Save markdown
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        markdown_file = self.reports_path / f"audit_report_{timestamp}.md"
        
        with open(markdown_file, 'w', encoding='utf-8') as f:
            f.write(markdown_report)
        
        # Save JSON data
        json_file = self.reports_path / f"audit_data_{timestamp}.json"
        
        report_data = {
            "project_name": audit_report.project_name,
            "timestamp": audit_report.timestamp.isoformat(),
            "before_metrics": audit_report.before_metrics.to_dict() if audit_report.before_metrics else None,
            "after_metrics": audit_report.after_metrics.to_dict() if audit_report.after_metrics else None,
            "improvements": audit_report.get_improvement_summary(),
            "recommendations": audit_report.recommendations,
            "generated_tests_count": len(audit_report.generated_tests),
            "modified_tests_count": len(audit_report.modified_tests)
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"   📄 Report saved: {markdown_file}")
        print(f"   📊 Data saved: {json_file}")
    
    def _print_metrics(self, stage: str, metrics: QualityMetrics):
        """Print quality metrics"""
        print(f"   📊 {stage} Metrics:")
        print(f"      Coverage: {metrics.coverage_percentage:.1f}%")
        print(f"      Total Tests: {metrics.total_tests}")
        print(f"      Total Assertions: {metrics.total_assertions}")
        print(f"      Assertion Density: {metrics.assertion_density:.2f}")
        print(f"      Test Clarity Score: {metrics.test_clarity_score:.1f}/10")
        print(f"      Uncovered Units: {len(metrics.uncovered_units)}")
    
    def _print_mutation_results(self, stage: str, results: MutationResults):
        """Print mutation testing results"""
        print(f"   🧬 {stage} Mutation Results:")
        print(f"      Total Mutations: {results.total_mutations}")
        print(f"      Killed: {results.killed_mutations}")
        print(f"      Survived: {results.survived_mutations}")
        print(f"      Mutation Score: {results.mutation_score:.1f}%")
    
    def get_codebase_summary(self) -> Dict[str, Any]:
        """Get a summary of the codebase structure"""
        return {
            "total_code_units": len(self.code_units),
            "modules": len([u for u in self.code_units if u.type == CodeType.MODULE]),
            "classes": len([u for u in self.code_units if u.type == CodeType.CLASS]),
            "functions": len([u for u in self.code_units if u.type == CodeType.FUNCTION]),
            "methods": len([u for u in self.code_units if u.type == CodeType.METHOD]),
            "total_tests": len(self.test_cases),
            "test_types": {
                test_type.value: len([t for t in self.test_cases if t.type == test_type])
                for test_type in TestType
            }
        } 