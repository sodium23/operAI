from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Execution OS Backend Prototype"
    claude_api_key: str = ""
    claude_model: str = "claude-3-5-sonnet-20241022"
    mock_llm: bool = True
    stability_threshold: float = 0.9
    max_refinement_iterations: int = 5
    governance_log_path: str = "governance.log"
    token_cost_per_1k: float = 0.02

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)


settings = Settings()
