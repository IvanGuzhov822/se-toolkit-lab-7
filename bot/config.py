from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_token: str = ""
    lms_api_base_url: str = "https://lms.innopolis.university"
    lms_api_key: str = ""
    llm_api_key: str = ""

    class Config:
        env_file = ".env.bot.secret"
        env_file_encoding = "utf-8"


settings = Settings()
