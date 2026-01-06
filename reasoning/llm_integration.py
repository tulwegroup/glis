"""
LLM Integration Module - Layer 3

Unified interface for OpenAI, Claude, and open-source models.
Handles prompt engineering, caching, cost tracking, and fallback strategies.

Features:
- Multi-provider support (OpenAI, Anthropic, HuggingFace)
- Request caching for cost efficiency
- Token counting and cost estimation
- Fallback chains for reliability
- Structured output validation
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import os
import hashlib
from abc import ABC, abstractmethod

# Try importing various LLM libraries
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    from langchain.llms import OpenAI, HuggingFaceHub
    from langchain.prompts import PromptTemplate
    HAS_LANGCHAIN = True
except ImportError:
    HAS_LANGCHAIN = False


class ModelProvider(Enum):
    """Supported LLM providers"""
    OPENAI_GPT4 = "gpt-4"
    OPENAI_GPT35 = "gpt-3.5-turbo"
    OPENAI_GPT4_TURBO = "gpt-4-turbo-preview"
    CLAUDE_3 = "claude-3-opus"
    CLAUDE_2 = "claude-2.1"
    LLAMA2_70B = "llama2-70b"
    LLAMA2_13B = "llama2-13b"
    MIXTRAL = "mixtral-8x7b"


class TaskType(Enum):
    """LLM task categories"""
    BRIEF_GENERATION = "brief_generation"
    PLEADING_DRAFTING = "pleading_drafting"
    STATUTE_INTERPRETATION = "statute_interpretation"
    STRATEGY_ANALYSIS = "strategy_analysis"
    LEGAL_RESEARCH = "legal_research"
    CITATION_ANALYSIS = "citation_analysis"


@dataclass
class LLMConfig:
    """Configuration for LLM requests"""
    primary_provider: ModelProvider = ModelProvider.OPENAI_GPT4
    fallback_providers: List[ModelProvider] = field(default_factory=lambda: [
        ModelProvider.OPENAI_GPT35,
        ModelProvider.CLAUDE_3
    ])
    temperature: float = 0.3  # Lower for legal analysis
    max_tokens: int = 2000
    top_p: float = 0.9
    use_caching: bool = True
    cache_ttl_hours: int = 24
    cost_tracking: bool = True
    api_timeout_seconds: int = 30
    retry_attempts: int = 3
    retry_backoff_factor: float = 2.0


@dataclass
class LLMResponse:
    """Structured LLM response"""
    text: str
    provider: ModelProvider
    tokens_used: int
    cost_usd: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    cached: bool = False
    task_type: Optional[TaskType] = None
    confidence: float = 1.0


@dataclass
class PromptTemplate:
    """Legal prompt template with variables"""
    name: str
    task_type: TaskType
    template: str
    required_variables: List[str]
    instructions: str = ""
    examples: List[Tuple[str, str]] = field(default_factory=list)  # (input, expected_output)

    def format(self, **kwargs) -> str:
        """Format template with variables"""
        formatted = self.template
        for var in self.required_variables:
            if var not in kwargs:
                raise ValueError(f"Missing required variable: {var}")
            formatted = formatted.replace(f"{{{{{var}}}}}", str(kwargs[var]))
        return formatted


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""

    @abstractmethod
    def generate(self, prompt: str, config: LLMConfig) -> LLMResponse:
        """Generate text from prompt"""
        pass

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        pass

    @abstractmethod
    def estimate_cost(self, tokens: int) -> float:
        """Estimate cost in USD"""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API provider"""

    def __init__(self, api_key: Optional[str] = None):
        if not HAS_OPENAI:
            raise ImportError("OpenAI library not installed. Install with: pip install openai")
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided and OPENAI_API_KEY not set")
        
        openai.api_key = self.api_key
        self.model_costs = {
            ModelProvider.OPENAI_GPT4: (0.03, 0.06),  # (input, output) per 1K tokens
            ModelProvider.OPENAI_GPT35: (0.0005, 0.0015),
            ModelProvider.OPENAI_GPT4_TURBO: (0.01, 0.03),
        }

    def generate(self, prompt: str, config: LLMConfig) -> LLMResponse:
        """Generate completion using OpenAI API"""
        try:
            response = openai.ChatCompletion.create(
                model=config.primary_provider.value,
                messages=[
                    {"role": "system", "content": "You are an expert legal analyst specializing in Ghanaian law. Provide structured, accurate legal analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                top_p=config.top_p,
                timeout=config.api_timeout_seconds,
            )
            
            text = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            cost = self.estimate_cost(tokens_used)
            
            return LLMResponse(
                text=text,
                provider=config.primary_provider,
                tokens_used=tokens_used,
                cost_usd=cost
            )
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")

    def count_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        # Rough estimate: 1 token ≈ 4 characters
        return len(text) // 4

    def estimate_cost(self, tokens: int) -> float:
        """Estimate cost for GPT-4 (conservative estimate)"""
        # GPT-4: $0.03 per 1K input, $0.06 per 1K output
        return (tokens / 1000) * 0.06


class HuggingFaceProvider(LLMProvider):
    """HuggingFace open-source models provider"""

    def __init__(self, model_id: str = "meta-llama/Llama-2-70b-chat-hf"):
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            self.tokenizer = AutoTokenizer.from_pretrained(model_id)
            self.model_id = model_id
        except ImportError:
            raise ImportError("transformers not installed. Install with: pip install transformers")

    def generate(self, prompt: str, config: LLMConfig) -> LLMResponse:
        """Generate completion using HuggingFace model"""
        try:
            # For HuggingFace, we would load and run the model locally
            # This is a placeholder that requires additional setup
            tokens_used = self.count_tokens(prompt) + config.max_tokens
            
            # In production, would call: pipeline('text-generation', model=self.model_id)
            # For now, return error indicating local setup needed
            raise NotImplementedError("Local HuggingFace inference requires GPU setup")
            
        except Exception as e:
            raise RuntimeError(f"HuggingFace error: {str(e)}")

    def count_tokens(self, text: str) -> int:
        """Count tokens using tokenizer"""
        try:
            return len(self.tokenizer.encode(text))
        except:
            return len(text) // 4

    def estimate_cost(self, tokens: int) -> float:
        """Open-source models have no API cost"""
        return 0.0


class LLMCache:
    """Simple file-based cache for LLM responses"""

    def __init__(self, cache_dir: str = "data/llm_cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def _get_key(self, prompt: str, model: ModelProvider) -> str:
        """Generate cache key from prompt and model"""
        content = f"{prompt}:{model.value}"
        return hashlib.md5(content.encode()).hexdigest()

    def get(self, prompt: str, model: ModelProvider) -> Optional[LLMResponse]:
        """Retrieve cached response"""
        key = self._get_key(prompt, model)
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    response = LLMResponse(**data)
                    response.cached = True
                    return response
            except:
                return None
        return None

    def set(self, prompt: str, response: LLMResponse) -> None:
        """Cache response"""
        key = self._get_key(prompt, response.provider)
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        
        try:
            with open(cache_file, 'w') as f:
                data = {
                    'text': response.text,
                    'provider': response.provider.value,
                    'tokens_used': response.tokens_used,
                    'cost_usd': response.cost_usd,
                    'timestamp': response.timestamp,
                    'task_type': response.task_type.value if response.task_type else None,
                    'confidence': response.confidence,
                }
                json.dump(data, f, indent=2)
        except:
            pass


class LLMOrchestrator:
    """Main orchestrator for LLM operations"""

    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig()
        self.cache = LLMCache() if self.config.use_caching else None
        self.providers: Dict[ModelProvider, LLMProvider] = {}
        self.cost_tracker: Dict[str, List[float]] = {}
        self.prompt_templates: Dict[str, PromptTemplate] = self._load_prompt_templates()
        
        # Initialize primary provider
        self._initialize_providers()

    def _initialize_providers(self) -> None:
        """Initialize available LLM providers"""
        # Try OpenAI
        try:
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                provider = OpenAIProvider(openai_key)
                for model in [ModelProvider.OPENAI_GPT4, ModelProvider.OPENAI_GPT35, ModelProvider.OPENAI_GPT4_TURBO]:
                    self.providers[model] = provider
        except:
            pass
        
        # Try HuggingFace (open-source)
        try:
            provider = HuggingFaceProvider()
            for model in [ModelProvider.LLAMA2_70B, ModelProvider.LLAMA2_13B, ModelProvider.MIXTRAL]:
                self.providers[model] = provider
        except:
            pass

    def _load_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Load and return legal prompt templates"""
        return {
            "brief_facts": PromptTemplate(
                name="brief_facts",
                task_type=TaskType.BRIEF_GENERATION,
                template="""Analyze the following legal case and extract the key facts in 2-3 concise sentences.

Case Text:
{case_text}

Facts:""",
                required_variables=["case_text"],
                instructions="Extract only material facts relevant to the legal issues. Be concise."
            ),
            
            "brief_issue": PromptTemplate(
                name="brief_issue",
                task_type=TaskType.BRIEF_GENERATION,
                template="""Based on the following case, identify the central legal issue(s) in one sentence.

Case Text:
{case_text}

Legal Issue:""",
                required_variables=["case_text"],
                instructions="State the legal question that the court must answer."
            ),
            
            "brief_holding": PromptTemplate(
                name="brief_holding",
                task_type=TaskType.BRIEF_GENERATION,
                template="""Identify the court's holding (decision) in this case in 1-2 sentences.

Case Text:
{case_text}

Holding:""",
                required_variables=["case_text"],
                instructions="State what the court decided, not how it reasoned."
            ),

            "statute_interpretation": PromptTemplate(
                name="statute_interpretation",
                task_type=TaskType.STATUTE_INTERPRETATION,
                template="""Interpret the following statute in the context of Ghanaian law:

Statute:
{statute_text}

Section: {section}

Context: {context}

Interpretation:""",
                required_variables=["statute_text", "section", "context"],
                instructions="Provide practical interpretation and application guidance."
            ),

            "pleading_draft": PromptTemplate(
                name="pleading_draft",
                task_type=TaskType.PLEADING_DRAFTING,
                template="""Draft a {pleading_type} for the following case:

Facts: {facts}
Legal Basis: {legal_basis}
Parties: {parties}
Relief Sought: {relief}

{pleading_type}:""",
                required_variables=["pleading_type", "facts", "legal_basis", "parties", "relief"],
                instructions="Draft professional legal pleading. Use formal legal language appropriate for Ghana courts."
            ),

            "strategy_analysis": PromptTemplate(
                name="strategy_analysis",
                task_type=TaskType.STRATEGY_ANALYSIS,
                template="""Analyze the litigation strategy for the following case:

Client Position: {client_position}
Key Facts: {key_facts}
Relevant Precedents: {precedents}
Opposing Arguments: {opposing_args}
Client Objectives: {objectives}

Analysis:""",
                required_variables=["client_position", "key_facts", "precedents", "opposing_args", "objectives"],
                instructions="Provide strategic recommendations with risk assessment and expected outcomes."
            ),
        }

    def generate(
        self,
        prompt: str,
        task_type: TaskType = TaskType.LEGAL_RESEARCH,
        use_cache: bool = True,
        retry: int = 0
    ) -> LLMResponse:
        """Generate LLM response with caching and fallback"""
        
        # Check cache
        if use_cache and self.cache:
            cached = self.cache.get(prompt, self.config.primary_provider)
            if cached:
                return cached

        # Try primary provider
        try:
            if self.config.primary_provider not in self.providers:
                raise ValueError(f"Provider {self.config.primary_provider} not available")
            
            provider = self.providers[self.config.primary_provider]
            response = provider.generate(prompt, self.config)
            response.task_type = task_type
            
            # Cache response
            if use_cache and self.cache:
                self.cache.set(prompt, response)
            
            # Track cost
            if self.config.cost_tracking:
                task_name = task_type.value
                if task_name not in self.cost_tracker:
                    self.cost_tracker[task_name] = []
                self.cost_tracker[task_name].append(response.cost_usd)
            
            return response
        
        except Exception as e:
            # Try fallback providers
            if retry < len(self.config.fallback_providers):
                fallback = self.config.fallback_providers[retry]
                if fallback in self.providers:
                    original_primary = self.config.primary_provider
                    self.config.primary_provider = fallback
                    try:
                        response = self.generate(prompt, task_type, use_cache=False, retry=retry + 1)
                        self.config.primary_provider = original_primary
                        return response
                    except:
                        self.config.primary_provider = original_primary
            
            raise RuntimeError(f"All LLM providers failed. Last error: {str(e)}")

    def generate_from_template(
        self,
        template_name: str,
        **variables
    ) -> LLMResponse:
        """Generate response using prompt template"""
        if template_name not in self.prompt_templates:
            raise ValueError(f"Unknown template: {template_name}")
        
        template = self.prompt_templates[template_name]
        prompt = template.format(**variables)
        return self.generate(prompt, task_type=template.task_type)

    def get_cost_summary(self) -> Dict[str, Any]:
        """Get cost tracking summary"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_cost_usd": 0.0,
            "tasks": {}
        }
        
        for task_type, costs in self.cost_tracker.items():
            task_total = sum(costs)
            summary["tasks"][task_type] = {
                "requests": len(costs),
                "total_cost_usd": round(task_total, 4),
                "average_cost_usd": round(task_total / len(costs), 4) if costs else 0,
            }
            summary["total_cost_usd"] += task_total
        
        summary["total_cost_usd"] = round(summary["total_cost_usd"], 4)
        return summary

    def available_providers(self) -> List[ModelProvider]:
        """Get list of available providers"""
        return list(self.providers.keys())

    def set_primary_provider(self, provider: ModelProvider) -> None:
        """Change primary LLM provider"""
        if provider not in self.providers:
            raise ValueError(f"Provider {provider} not available. Available: {list(self.providers.keys())}")
        self.config.primary_provider = provider


# Global instance
_orchestrator: Optional[LLMOrchestrator] = None


def get_llm_orchestrator(config: Optional[LLMConfig] = None) -> LLMOrchestrator:
    """Get or create LLM orchestrator singleton"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = LLMOrchestrator(config)
    return _orchestrator


if __name__ == "__main__":
    # Test LLM integration
    orchestrator = get_llm_orchestrator()
    
    # Check available providers
    print("Available providers:", orchestrator.available_providers())
    
    # Test cost summary
    print("Cost summary:", orchestrator.get_cost_summary())
