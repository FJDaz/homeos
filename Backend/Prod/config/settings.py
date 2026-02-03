"""Configuration settings using Pydantic Settings."""
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # API Keys
    deepseek_api_key: str = Field(
        default="",
        alias="DEEPSEEK_API_KEY",
        description="DeepSeek API key for code generation"
    )
    
    mistral_api_key: str = Field(
        default="",
        alias="MISTRAL_API_KEY",
        description="Mistral API key for Codestral"
    )
    
    google_api_key: str = Field(
        default="",
        alias="GOOGLE_API_KEY",
        description="Google API key for Gemini"
    )
    
    groq_api_key: str = Field(
        default="",
        alias="GROQ_API_KEY",
        description="Groq API key"
    )
    
    anthropic_api_key: str = Field(
        default="",
        alias="ANTHROPIC_API_KEY",
        description="Anthropic API key for Claude validation (automatic)"
    )

    kimi_api_key: str = Field(
        default="",
        alias="KIMI_KEY",
        description="KIMI (Moonshot) API key for gate-keeper validation"
    )

    kimi_api_url: str = Field(
        default="https://api.moonshot.cn/v1/chat/completions",
        alias="KIMI_API_URL",
        description="KIMI (Moonshot) API endpoint URL"
    )

    kimi_model: str = Field(
        default="moonshot-v1-8k",
        alias="KIMI_MODEL",
        description="KIMI model to use (moonshot-v1-8k, moonshot-v1-32k, moonshot-v1-128k)"
    )
    
    # API Configuration
    deepseek_api_url: str = Field(
        default="https://api.deepseek.com/v1/chat/completions",
        alias="DEEPSEEK_API_URL",
        description="DeepSeek API endpoint URL"
    )
    
    deepseek_model: str = Field(
        default="deepseek-coder",
        alias="DEEPSEEK_MODEL",
        description="DeepSeek model to use"
    )
    
    codestral_model: str = Field(
        default="codestral-latest",
        alias="CODESTRAL_MODEL",
        description="Codestral model to use"
    )
    
    gemini_model: str = Field(
        default="gemini-2.5-flash",  # Stable model - best price-performance ratio
        alias="GEMINI_MODEL",
        description="Gemini model to use. Stable: gemini-2.5-flash (recommended), gemini-2.5-flash-lite (fastest), gemini-2.5-pro (most capable). Experimental: gemini-2.0-flash-exp"
    )
    
    groq_model: str = Field(
        default="llama-3.3-70b-versatile",
        alias="GROQ_MODEL",
        description="Groq model to use"
    )
    
    default_provider: str = Field(
        default="deepseek",
        alias="DEFAULT_PROVIDER",
        description="Default provider for code generation"
    )
    
    # Request Parameters
    max_tokens: int = Field(
        default=4000,
        alias="MAX_TOKENS",
        description="Maximum tokens per request"
    )
    
    temperature: float = Field(
        default=0.7,
        alias="TEMPERATURE",
        description="Temperature for API requests"
    )
    
    timeout: int = Field(
        default=120,
        alias="TIMEOUT",
        description="Request timeout in seconds (increased from 60s to handle longer requests)"
    )
    
    max_retries: int = Field(
        default=3,
        alias="MAX_RETRIES",
        description="Maximum number of retry attempts"
    )
    
    # Paths
    plan_file_path: str = Field(
        default="plan.json",
        alias="PLAN_FILE_PATH",
        description="Path to the plan JSON file"
    )
    
    output_dir: Path = Field(
        default=Path("output"),
        alias="OUTPUT_DIR",
        description="Directory for output files"
    )
    
    logs_dir: Path = Field(
        default=Path("logs"),
        alias="LOGS_DIR",
        description="Directory for log files"
    )
    
    error_log_dir: Path = Field(
        default=Path("output/aetherflow_error_log"),
        alias="AETHERFLOW_ERROR_LOG_DIR",
        description="Directory for error/correction survey (errors Aetherflow + corrections Cursor/Claude)"
    )
    
    # Logging
    log_level: str = Field(
        default="INFO",
        alias="LOG_LEVEL",
        description="Logging level"
    )
    
    # Cost Tracking
    deepseek_input_cost_per_1k: float = Field(
        default=0.00014,
        alias="DEEPSEEK_INPUT_COST_PER_1K",
        description="Cost per 1K input tokens (USD)"
    )
    
    deepseek_output_cost_per_1k: float = Field(
        default=0.00028,
        alias="DEEPSEEK_OUTPUT_COST_PER_1K",
        description="Cost per 1K output tokens (USD)"
    )
    
    deepseek_max_tokens: int = Field(
        default=4096,
        alias="DEEPSEEK_MAX_TOKENS",
        description="Maximum output tokens for DeepSeek API (deepseek-coder limit: 4096-8192, using conservative 4096)"
    )
    
    # API URLs (for future providers)
    mistral_api_url: str = Field(
        default="https://api.mistral.ai/v1/chat/completions",
        alias="MISTRAL_API_URL",
        description="Mistral API endpoint URL"
    )
    
    gemini_api_url: str = Field(
        default="https://generativelanguage.googleapis.com/v1/models",
        alias="GEMINI_API_URL",
        description="Gemini API endpoint URL"
    )
    
    groq_api_url: str = Field(
        default="https://api.groq.com/openai/v1/chat/completions",
        alias="GROQ_API_URL",
        description="Groq API endpoint URL"
    )
    
    # Validation Settings (Claude Code validation - manual, no API)
    enable_claude_validation: bool = Field(
        default=False,
        alias="ENABLE_CLAUDE_VALIDATION",
        description="Enable Claude Code validation (manual, via files)"
    )
    
    # Balance Check Settings
    enable_balance_check: bool = Field(
        default=True,
        alias="ENABLE_BALANCE_CHECK",
        description="Enable balance check before API requests (if API supports it)"
    )
    
    min_balance_threshold: float = Field(
        default=0.10,
        alias="MIN_BALANCE_THRESHOLD",
        description="Minimum balance threshold (USD) - Request will fail if balance is below this"
    )
    
    # Mistral Cost Tracking
    mistral_input_cost_per_1k: float = Field(
        default=0.0003,
        alias="MISTRAL_INPUT_COST_PER_1K",
        description="Cost per 1K input tokens for Mistral/Codestral (USD)"
    )

    mistral_output_cost_per_1k: float = Field(
        default=0.0003,
        alias="MISTRAL_OUTPUT_COST_PER_1K",
        description="Cost per 1K output tokens for Mistral/Codestral (USD)"
    )

    # Gemini Cost Tracking (free tier with quota)
    gemini_input_cost_per_1k: float = Field(
        default=0.0,
        alias="GEMINI_INPUT_COST_PER_1K",
        description="Cost per 1K input tokens for Gemini (USD) - Free tier"
    )

    gemini_output_cost_per_1k: float = Field(
        default=0.0,
        alias="GEMINI_OUTPUT_COST_PER_1K",
        description="Cost per 1K output tokens for Gemini (USD) - Free tier"
    )

    # Groq Cost Tracking (Llama 3.3 70B pricing)
    groq_input_cost_per_1k: float = Field(
        default=0.00059,
        alias="GROQ_INPUT_COST_PER_1K",
        description="Cost per 1K input tokens for Groq (USD)"
    )

    groq_output_cost_per_1k: float = Field(
        default=0.00079,
        alias="GROQ_OUTPUT_COST_PER_1K",
        description="Cost per 1K output tokens for Groq (USD)"
    )
    
    # Execution Mode Settings
    default_execution_mode: str = Field(
        default="BUILD",
        alias="DEFAULT_EXECUTION_MODE",
        description="Default execution mode: FAST, BUILD, or DOUBLE-CHECK"
    )
    
    # Rate Limiting Settings (per provider)
    max_concurrent_requests_deepseek: int = Field(
        default=5,
        alias="MAX_CONCURRENT_REQUESTS_DEEPSEEK",
        description="Maximum concurrent requests for DeepSeek"
    )
    
    max_concurrent_requests_groq: int = Field(
        default=10,
        alias="MAX_CONCURRENT_REQUESTS_GROQ",
        description="Maximum concurrent requests for Groq"
    )
    
    max_concurrent_requests_gemini: int = Field(
        default=10,
        alias="MAX_CONCURRENT_REQUESTS_GEMINI",
        description="Maximum concurrent requests for Gemini"
    )
    
    max_concurrent_requests_codestral: int = Field(
        default=5,
        alias="MAX_CONCURRENT_REQUESTS_CODESTRAL",
        description="Maximum concurrent requests for Codestral"
    )
    
    # Planner Settings
    default_planner: str = Field(
        default="auto",
        alias="DEFAULT_PLANNER",
        description="Default planner: claude_code|claude_api|gemini|deepseek|auto"
    )
    
    enable_planner_fallback: bool = Field(
        default=True,
        alias="ENABLE_PLANNER_FALLBACK",
        description="Enable automatic fallback to cheaper planner on failure"
    )

    def __init__(self, **kwargs):
        """Initialize settings and create directories."""
        super().__init__(**kwargs)
        # Ensure output and logs directories exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.error_log_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
