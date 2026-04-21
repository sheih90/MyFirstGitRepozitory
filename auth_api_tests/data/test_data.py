from config.settings import Settings


class TestData:
    """Тестовые данные для API тестов"""
    
    @staticmethod
    def get_valid_registration_data() -> dict:
        """Валидные данные для регистрации"""
        settings = Settings()
        return {
            "email": settings.test_user_email,
            "fullName": settings.test_user_fullname,
            "password": settings.test_user_password,
            "passwordRepeat": settings.test_user_password
        }
    
    @staticmethod
    def get_invalid_email_data() -> dict:
        """Невалидный email"""
        return {
            "email": "invalid-email",
            "fullName": "Test User",
            "password": "12345678Aa",
            "passwordRepeat": "12345678Aa"
        }
    
    @staticmethod
    def get_weak_password_data() -> dict:
        """Слабый пароль"""
        return {
            "email": "test@email.com",
            "fullName": "Test User",
            "password": "123",
            "passwordRepeat": "123"
        }
    
    @staticmethod
    def get_mismatched_passwords_data() -> dict:
        """Пароли не совпадают"""
        return {
            "email": "test@email.com",
            "fullName": "Test User",
            "password": "12345678Aa",
            "passwordRepeat": "87654321Aa"
        }
    
    @staticmethod
    def get_valid_login_data() -> dict:
        """Валидные данные для входа"""
        settings = Settings()
        return {
            "email": settings.test_user_email,
            "password": settings.test_user_password
        }
    
    @staticmethod
    def get_admin_credentials() -> dict:
        """Учетные данные администратора"""
        settings = Settings()
        return {
            "email": settings.admin_email,
            "password": settings.admin_password
        }
    
    @staticmethod
    def get_invalid_login_data() -> dict:
        """Невалидные данные для входа"""
        return {
            "email": "nonexistent@email.com",
            "password": "wrongpassword"
        }
