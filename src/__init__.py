"""
Autonomous Agent-Based Testing Framework

A comprehensive framework that uses AI agents to analyze, assess, and improve
test quality through dependency mapping, mutation testing, and autonomous
test generation.
"""

__version__ = "0.1.0"
__author__ = "AdamG-74"

from .framework import TestingFramework
from .agents import (
    CodeMapperAgent,
    TestDiscoveryAgent,
    TestAssessorAgent,
    TestGeneratorAgent,
    TestJudgeAgent,
    AuditReporterAgent
)
from .models import (
    CodeUnit,
    TestCase,
    QualityMetrics,
    MutationResults,
    AuditReport
)

__all__ = [
    "TestingFramework",
    "CodeMapperAgent",
    "TestDiscoveryAgent", 
    "TestAssessorAgent",
    "TestGeneratorAgent",
    "TestJudgeAgent",
    "AuditReporterAgent",
    "CodeUnit",
    "TestCase",
    "QualityMetrics",
    "MutationResults",
    "AuditReport"
] 