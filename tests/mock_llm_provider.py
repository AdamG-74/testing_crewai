"""
Mock LLM Provider for Testing Framework Validation

This module provides a mock LLM provider that integrates with the existing
src/llm_config.py to enable testing without making actual API calls.
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun

# Import existing components
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from src.llm_config import Provider, LLMConfig, LiteLLMWrapper
except ImportError:
    # Fallback for direct imports
    import llm_config as llm_config_module
    Provider = llm_config_module.Provider
    LLMConfig = llm_config_module.LLMConfig
    LiteLLMWrapper = llm_config_module.LiteLLMWrapper


class MockResponse:
    """Mock response object that mimics LiteLLM response structure"""
    
    def __init__(self, content: str):
        self.content = content
        self.choices = [MockChoice(content)]
    
    def __str__(self):
        return self.content


class MockChoice:
    """Mock choice object for response structure"""
    
    def __init__(self, content: str):
        self.message = MockMessage(content)
    
    def __str__(self):
        return self.message.content


class MockMessage:
    """Mock message object for response structure"""
    
    def __init__(self, content: str):
        self.content = content


class MockLLMProvider:
    """
    Mock LLM provider that generates realistic responses for testing
    
    This provider provides the same interface as LiteLLMWrapper
    and provides mock responses for different types of prompts used by agents.
    """
    
    def __init__(self, **kwargs):
        self.model = kwargs.get("model", "mock-gpt-4")
        self.provider = kwargs.get("provider", Provider.CUSTOM)
        self.temperature = kwargs.get("temperature", 0.1)
        self.max_tokens = kwargs.get("max_tokens", None)
        self.kwargs = kwargs.get("kwargs", {})
        
        self.call_count = 0
        self.call_history = []
        
        # Mock responses for different prompt types
        self.response_templates = {
            "test_generation": self._generate_mock_test_code,
            "test_judgment": self._generate_mock_judgment,
            "test_clarity": self._generate_mock_clarity_score,
            "audit_report": self._generate_mock_report,
            "code_analysis": self._generate_mock_code_analysis,
            "default": self._generate_default_response
        }
    
    def invoke(self, prompt: str) -> MockResponse:
        """Invoke method that agents expect - returns MockResponse with content attribute"""
        content = self._call(prompt)
        return MockResponse(content)
    
    def _call(self, 
              prompt: str, 
              stop: Optional[list] = None,
              run_manager: Optional[CallbackManagerForLLMRun] = None,
              **kwargs) -> str:
        """Override parent _call method to provide mock responses"""
        self.call_count += 1
        self.call_history.append(prompt)
        
        # Determine response type based on prompt content
        response_type = self._classify_prompt(prompt)
        response_generator = self.response_templates.get(response_type, self.response_templates["default"])
        
        return response_generator(prompt)
    
    @property
    def _llm_type(self) -> str:
        """Return the LLM type"""
        return f"mock_{self.provider.value}"
    
    def _classify_prompt(self, prompt: str) -> str:
        """Classify the prompt type to generate appropriate mock response"""
        prompt_lower = prompt.lower()
        
        if "generate" in prompt_lower and "test" in prompt_lower:
            return "test_generation"
        elif "evaluate" in prompt_lower or "judge" in prompt_lower or "quality" in prompt_lower:
            return "test_judgment"
        elif "clarity" in prompt_lower or "readability" in prompt_lower:
            return "test_clarity"
        elif "report" in prompt_lower or "audit" in prompt_lower:
            return "audit_report"
        elif "analyze" in prompt_lower or "structure" in prompt_lower:
            return "code_analysis"
        else:
            return "default"
    
    def _generate_mock_test_code(self, prompt: str) -> str:
        """Generate mock test code based on the prompt"""
        # Extract function/class name from prompt if possible
        function_name = "example_function"
        class_name = "ExampleClass"
        
        # Try to extract actual names from prompt
        if "Name:" in prompt:
            lines = prompt.split('\n')
            for line in lines:
                if line.strip().startswith("Name:"):
                    name = line.split("Name:")[1].strip()
                    if "." in name:
                        class_name, function_name = name.split(".", 1)
                    else:
                        function_name = name
                    break
        
        # Generate realistic test code
        test_code = f'''"""
Test cases for {function_name}
"""

import pytest
from unittest.mock import Mock, patch


class Test{function_name.title().replace("_", "")}:
    """Test cases for {function_name} function"""
    
    def test_{function_name}_happy_path(self):
        """Test {function_name} with valid inputs"""
        # Arrange
        expected_result = "expected_value"
        
        # Act
        result = {function_name}("test_input")
        
        # Assert
        assert result is not None
        assert isinstance(result, (str, int, float, bool, list, dict))
    
    def test_{function_name}_edge_cases(self):
        """Test {function_name} with edge case inputs"""
        # Test empty input
        result = {function_name}("")
        assert result is not None
        
        # Test None input
        with pytest.raises((ValueError, TypeError)):
            {function_name}(None)
    
    def test_{function_name}_error_handling(self):
        """Test {function_name} error handling"""
        with pytest.raises((ValueError, TypeError)):
            {function_name}("invalid_input")
    
    @patch('module.dependency')
    def test_{function_name}_with_mocks(self, mock_dependency):
        """Test {function_name} with mocked dependencies"""
        # Arrange
        mock_dependency.return_value = "mocked_result"
        
        # Act
        result = {function_name}("test_input")
        
        # Assert
        assert result is not None
        mock_dependency.assert_called_once()
'''
        
        return test_code
    
    def _generate_mock_judgment(self, prompt: str) -> str:
        """Generate mock judgment response for test quality evaluation"""
        return """
Coverage completeness: 8/10 - Good coverage of main functionality
Test case variety: 7/10 - Includes happy path and error cases, could use more edge cases
Assertion quality: 8/10 - Clear and specific assertions
Mocking effectiveness: 6/10 - Basic mocking present, could be more comprehensive
Code readability: 9/10 - Well-structured and documented
Documentation quality: 8/10 - Good docstrings and comments

Overall Score: 7.7/10

Feedback:
- Consider adding more edge case scenarios
- Improve mock setup for external dependencies
- Add parameterized tests for multiple input scenarios
- Consider testing performance characteristics
"""
    
    def _generate_mock_clarity_score(self, prompt: str) -> str:
        """Generate mock clarity score response"""
        return """
Test Clarity Assessment:

Readability Score: 8.5/10
- Clear test names that describe what is being tested
- Good use of Arrange-Act-Assert pattern
- Descriptive variable names

Documentation Score: 8.0/10
- Comprehensive docstrings for test methods
- Clear comments explaining test logic
- Good class-level documentation

Structure Score: 9.0/10
- Logical test organization
- Proper use of test fixtures
- Clean separation of concerns

Overall Clarity Score: 8.5/10
"""
    
    def _generate_mock_report(self, prompt: str) -> str:
        """Generate mock audit report content"""
        return """
# Test Quality Audit Report

## Executive Summary
The codebase shows good testing practices with room for improvement in coverage and test variety.

## Key Metrics
- Test Coverage: 75%
- Assertion Density: 3.2 assertions per test
- Mock Usage: 45% of tests use mocking
- Average Test Quality Score: 7.8/10

## Recommendations
1. Increase test coverage for edge cases
2. Add more integration tests
3. Improve error handling test scenarios
4. Consider adding performance tests

## Detailed Analysis
The test suite demonstrates solid understanding of testing principles with consistent use of pytest conventions and good documentation practices.
"""
    
    def _generate_mock_code_analysis(self, prompt: str) -> str:
        """Generate mock code analysis response"""
        return """
Code Structure Analysis:

Complexity: Medium
- Cyclomatic complexity: 4.2 average
- Function length: 15 lines average
- Class cohesion: High

Dependencies:
- External dependencies: 3 modules
- Internal coupling: Low to medium
- Circular dependencies: None detected

Quality Indicators:
- Documentation coverage: 80%
- Type hints usage: 60%
- Error handling: Present but could be improved

Recommendations:
- Add more type hints for better code clarity
- Consider breaking down larger functions
- Improve error handling consistency
"""
    
    def _generate_default_response(self, prompt: str) -> str:
        """Generate default mock response"""
        return """
This is a mock response from the MockLLMProvider.
The prompt was classified as a general query.

Key points:
- Mock provider is functioning correctly
- Response generated based on prompt analysis
- Suitable for testing framework validation

Response generated for testing purposes.
"""
    
    def reset_call_history(self):
        """Reset call history for clean testing"""
        self.call_count = 0
        self.call_history.clear()
    
    def get_call_statistics(self) -> Dict[str, Any]:
        """Get statistics about mock LLM usage"""
        return {
            "total_calls": self.call_count,
            "call_history_length": len(self.call_history),
            "last_prompt_length": len(self.call_history[-1]) if self.call_history else 0,
            "prompt_types": [self._classify_prompt(prompt) for prompt in self.call_history]
        }


class MockLLMConfig(LLMConfig):
    """
    Mock configuration that extends existing LLMConfig
    
    This class provides a way to configure the testing framework
    to use the mock provider instead of real LLM providers.
    """
    
    def __init__(self):
        # Don't call parent __init__ to avoid loading real environment
        self.mock_provider = None
        self.original_methods = {}
    
    def setup_mock_provider(self) -> MockLLMProvider:
        """Set up and return a mock LLM provider"""
        self.mock_provider = MockLLMProvider()
        return self.mock_provider
    
    def get_available_providers(self) -> Dict[Provider, bool]:
        """Override to return mock provider as available"""
        return {
            Provider.OPENAI: False,
            Provider.AZURE_OPENAI: False,
            Provider.ANTHROPIC: False,
            Provider.GOOGLE: False,
            Provider.COHERE: False,
            Provider.CUSTOM: True,  # Mock provider is always available
        }
    
    def get_default_provider(self) -> Provider:
        """Override to return custom provider for mock"""
        return Provider.CUSTOM
    
    def get_default_model(self, provider: Provider) -> str:
        """Override to return mock model"""
        if provider == Provider.CUSTOM:
            return "mock-gpt-4"
        return super().get_default_model(provider)
    
    def create_llm(self, 
                   provider: Optional[Provider] = None,
                   model: Optional[str] = None,
                   temperature: float = 0.1,
                   **kwargs) -> MockLLMProvider:
        """Override to return mock LLM provider"""
        if self.mock_provider is None:
            self.setup_mock_provider()
        
        # Update mock provider settings
        if model:
            self.mock_provider.model = model
        if provider:
            self.mock_provider.provider = provider
        self.mock_provider.temperature = temperature
        
        return self.mock_provider
    
    def patch_existing_config(self, llm_config_instance: LLMConfig) -> MockLLMProvider:
        """Patch an existing LLMConfig instance to use mock provider"""
        # Store original methods
        self.original_methods = {
            'create_llm': llm_config_instance.create_llm,
            'get_default_provider': llm_config_instance.get_default_provider,
            'get_available_providers': llm_config_instance.get_available_providers
        }
        
        # Create mock provider
        mock_provider = self.setup_mock_provider()
        
        # Patch methods
        llm_config_instance.create_llm = self.create_llm
        llm_config_instance.get_default_provider = self.get_default_provider
        llm_config_instance.get_available_providers = self.get_available_providers
        
        return mock_provider
    
    def restore_config(self, llm_config_instance: LLMConfig):
        """Restore original LLMConfig functionality"""
        if self.original_methods:
            for method_name, original_method in self.original_methods.items():
                setattr(llm_config_instance, method_name, original_method)
            self.original_methods.clear()
    
    @staticmethod
    def create_test_environment():
        """Create a test environment with mock LLM provider"""
        # Set mock environment variables to avoid real API calls
        test_env_vars = {
            "MOCK_LLM_PROVIDER": "true",
            "OPENAI_API_KEY": "mock-key-for-testing",
            "AZURE_API_KEY": "",
            "ANTHROPIC_API_KEY": "",
            "GOOGLE_API_KEY": "",
            "COHERE_API_KEY": ""
        }
        
        # Store original values
        original_values = {}
        for key, value in test_env_vars.items():
            original_values[key] = os.environ.get(key)
            os.environ[key] = value
        
        return original_values
    
    @staticmethod
    def restore_environment(original_values: Dict[str, Optional[str]]):
        """Restore original environment variables"""
        for key, value in original_values.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


# Convenience functions for test setup
def setup_mock_llm() -> MockLLMProvider:
    """Set up mock LLM provider for testing"""
    mock_config = MockLLMConfig()
    return mock_config.setup_mock_provider()


def patch_framework_with_mock(framework_instance) -> MockLLMProvider:
    """Patch a TestingFramework instance to use mock LLM"""
    mock_config = MockLLMConfig()
    mock_provider = mock_config.setup_mock_provider()
    
    # Patch the framework's LLM config
    if hasattr(framework_instance, 'llm_config'):
        mock_config.patch_existing_config(framework_instance.llm_config)
    
    # Patch individual agents
    agents = ['code_mapper', 'test_discovery', 'test_assessor', 
              'test_generator', 'test_judge', 'audit_reporter']
    
    for agent_name in agents:
        if hasattr(framework_instance, agent_name):
            agent = getattr(framework_instance, agent_name)
            if agent and hasattr(agent, 'llm'):
                agent.llm = mock_provider
    
    # Also patch the main framework LLM
    if hasattr(framework_instance, 'llm'):
        framework_instance.llm = mock_provider
    
    return mock_provider


def patch_global_llm_config() -> MockLLMProvider:
    """Patch the global llm_config instance to use mock provider"""
    try:
        from src.llm_config import llm_config
        mock_config = MockLLMConfig()
        return mock_config.patch_existing_config(llm_config)
    except ImportError:
        # Fallback if import fails
        return setup_mock_llm()


# Test utilities
def create_mock_llm_for_agent(agent_class, **kwargs):
    """Create an agent instance with mock LLM"""
    mock_llm = setup_mock_llm()
    return agent_class(llm=mock_llm, **kwargs)


def configure_mock_environment():
    """Configure environment for mock testing"""
    # Set environment variable to indicate mock mode
    os.environ["TESTING_MODE"] = "mock"
    os.environ["MOCK_LLM_PROVIDER"] = "true"
    
    # Set mock API keys to avoid real provider detection
    test_env = {
        "OPENAI_API_KEY": "mock-openai-key",
        "AZURE_API_KEY": "",
        "ANTHROPIC_API_KEY": "",
        "GOOGLE_API_KEY": "",
        "COHERE_API_KEY": ""
    }
    
    original_values = {}
    for key, value in test_env.items():
        original_values[key] = os.environ.get(key)
        if value:
            os.environ[key] = value
        elif key in os.environ:
            del os.environ[key]
    
    return original_values


def restore_environment(original_values: Dict[str, Optional[str]]):
    """Restore original environment variables"""
    for key, value in original_values.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
    
    # Clean up testing mode variables
    os.environ.pop("TESTING_MODE", None)
    os.environ.pop("MOCK_LLM_PROVIDER", None)