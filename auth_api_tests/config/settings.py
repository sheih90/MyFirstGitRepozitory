from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Настройки для тестов API авторизации"""
    
    base_url: str = "https://auth.dev-cinescope.coconutqa.ru"
    
    # Тестовые данные
    test_user_email: str = "test_automation@email.com"
    test_user_password: str = "12345678Aa"
    test_user_fullname: str = "Test Automation User"
    
    # Admin credentials
    admin_email: str = "api1@gmail.com"
    admin_password: str = "asdqwe123Q"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
