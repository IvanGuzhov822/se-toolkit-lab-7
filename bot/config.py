from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_token: str = ""
    lms_api_base_url: str = "http://localhost:42002"
    lms_api_key: str = ""
    llm_api_key: str = ""
    llm_api_base_url: str = "http://localhost:42005"
    llm_api_model: str = "qwen-coder"

    class Config:
        env_file = ".env.bot.secret"
        env_file_encoding = "utf-8"


settings = Settings()
