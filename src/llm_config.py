"""
LLM Configuration for Provider-Agnostic Language Model Support
"""

import os
from typing import Optional, Dict, Any
from enum import Enum
from dotenv import load_dotenv
from litellm import completion
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun

# litellm._turn_on_debug()


class Provider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    COHERE = "cohere"
    CUSTOM = "custom"


class LiteLLMWrapper(LLM):
    """Wrapper for LiteLLM to work with LangChain"""
    model: str
    provider: Provider = Provider.OPENAI
    temperature: float = 0.1
    max_tokens: Optional[int] = None
    kwargs: dict = {}

    def _call(self, 
              prompt: str, 
              stop: Optional[list] = None,
              run_manager: Optional[CallbackManagerForLLMRun] = None,
              **kwargs) -> str:
        """Make a call to the LLM"""
        try:
            # Prepare parameters
            params = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.temperature,
                **self.kwargs
            }
            
            if self.max_tokens:
                params["max_tokens"] = self.max_tokens
            
            if stop:
                params["stop"] = stop
            
            # Make the call
            response = completion(**params)
            
            # Extract the content - handle different response formats
            try:
                if hasattr(response, 'choices') and response.choices:
                    choice = response.choices[0]
                    if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                        content = choice.message.content
                        if content is not None:
                            return content
                        else:
                            return ""
                    else:
                        return str(choice)
                else:
                    return str(response)
            except (AttributeError, IndexError):
                # Fallback for different response formats
                return str(response)
                
        except Exception as e:
            raise Exception(f"LLM call failed: {e}")
    
    @property
    def _llm_type(self) -> str:
        """Return the LLM type"""
        return f"litellm_{self.provider.value}"


class LLMConfig:
    """Configuration manager for LLM providers"""
    
    def __init__(self):
        """Initialize LLM configuration"""
        load_dotenv()
        self._setup_environment()
    
    def _setup_environment(self):
        """Set up environment variables for different providers"""
        # Azure OpenAI Configuration
        azure_key = os.getenv("AZURE_API_KEY")
        if azure_key:
            os.environ["AZURE_API_KEY"] = azure_key
            azure_endpoint = os.getenv("AZURE_API_BASE")
            if azure_endpoint:
                os.environ["AZURE_API_BASE"] = azure_endpoint
            azure_version = os.getenv("AZURE_API_VERSION")
            if azure_version:
                os.environ["AZURE_API_VERSION"] = azure_version
        
        # OpenAI Configuration
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            os.environ["OPENAI_API_KEY"] = openai_key
        
        # Anthropic Configuration
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            os.environ["ANTHROPIC_API_KEY"] = anthropic_key
        
        # Google Configuration
        google_key = os.getenv("GOOGLE_API_KEY")
        if google_key:
            os.environ["GOOGLE_API_KEY"] = google_key
        
        # Cohere Configuration
        cohere_key = os.getenv("COHERE_API_KEY")
        if cohere_key:
            os.environ["COHERE_API_KEY"] = cohere_key
    
    def get_available_providers(self) -> Dict[Provider, bool]:
        """Get available providers based on environment variables"""
        return {
            Provider.OPENAI: bool(os.getenv("OPENAI_API_KEY")),
            Provider.AZURE_OPENAI: bool(os.getenv("AZURE_API_KEY")),
            Provider.ANTHROPIC: bool(os.getenv("ANTHROPIC_API_KEY")),
            Provider.GOOGLE: bool(os.getenv("GOOGLE_API_KEY")),
            Provider.COHERE: bool(os.getenv("COHERE_API_KEY")),
        }
    
    def get_default_provider(self) -> Provider:
        """Get the default provider based on available credentials"""
        available = self.get_available_providers()
        
        # Priority order
        priority = [
            Provider.AZURE_OPENAI,
            Provider.OPENAI,
            Provider.ANTHROPIC,
            Provider.GOOGLE,
            Provider.COHERE
        ]
        
        for provider in priority:
            if available[provider]:
                return provider
        
        raise ValueError("No LLM provider credentials found. Please set up at least one provider.")
    
    def get_default_model(self, provider: Provider) -> str:
        """Get the default model for a provider"""
        defaults = {
            Provider.OPENAI: "gpt-4",
            Provider.AZURE_OPENAI: "gpt-4",
            Provider.ANTHROPIC: "claude-3-sonnet-20240229",
            Provider.GOOGLE: "gemini-pro",
            Provider.COHERE: "command",
        }
        return defaults.get(provider, "gpt-4")
    
    def create_llm(self, 
                   provider: Optional[Provider] = None,
                   model: Optional[str] = None,
                   temperature: float = 0.1,
                   **kwargs) -> LiteLLMWrapper:
        """
        Create an LLM instance
        
        Args:
            provider: LLM provider (auto-detected if not specified)
            model: Model name (auto-detected if not specified)
            temperature: Sampling temperature
            **kwargs: Additional arguments for LiteLLM
            
        Returns:
            Configured LLM instance
        """
        if provider is None:
            provider = self.get_default_provider()
        
        if model is None:
            model = self.get_default_model(provider)
        
        # Validate provider availability
        available = self.get_available_providers()
        if not available[provider]:
            raise ValueError(f"Provider {provider.value} is not available. "
                           f"Please set up the required credentials.")
        
        return LiteLLMWrapper(
            model=model,
            provider=provider,
            temperature=temperature,
            **kwargs
        )
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about configured providers"""
        available = self.get_available_providers()
        default = self.get_default_provider()
        
        info = {
            "available_providers": [p.value for p, available in available.items() if available],
            "default_provider": default.value,
            "default_model": self.get_default_model(default),
            "credentials_configured": any(available.values())
        }
        
        return info 

llm_config = LLMConfig() 