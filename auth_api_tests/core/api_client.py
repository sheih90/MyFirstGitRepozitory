import requests
from typing import Optional, Dict, Any
from config.settings import settings


class APIClient:
    """Клиент для работы с Auth API"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.base_url
        self.session = requests.Session()
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.current_user_email: Optional[str] = None
    
    def _get_headers(self, include_auth: bool = False) -> Dict[str, str]:
        """Получение заголовков запроса"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if include_auth and self.access_token:
            # Используем Bearer токен из тела ответа
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers
    
    def register(self, email: str, full_name: str, password: str, password_repeat: str) -> requests.Response:
        """Регистрация пользователя"""
        payload = {
            "email": email,
            "fullName": full_name,
            "password": password,
            "passwordRepeat": password_repeat
        }
        return self.session.post(
            f"{self.base_url}/register",
            json=payload,
            headers=self._get_headers()
        )
    
    def login(self, email: str, password: str) -> requests.Response:
        """Аутентификация пользователя"""
        payload = {
            "email": email,
            "password": password
        }
        response = self.session.post(
            f"{self.base_url}/login",
            json=payload,
            headers=self._get_headers()
        )
        
        # Сохраняем токены если они есть в ответе
        if response.status_code == 200:
            try:
                response_data = response.json()
                # Токены могут быть в теле ответа или в cookies
                self.access_token = response_data.get('accessToken') or response.cookies.get('accessToken')
                self.refresh_token = response_data.get('refreshToken') or response.cookies.get('refreshToken')
            except:
                cookies = response.cookies
                self.access_token = cookies.get('accessToken')
                self.refresh_token = cookies.get('refreshToken')
            # Также сохраняем email текущего пользователя
            self.current_user_email = email
        
        return response
    
    def login_as_admin(self) -> requests.Response:
        """Вход под учетной записью администратора"""
        from data.test_data import TestData
        admin_creds = TestData.get_admin_credentials()
        return self.login(admin_creds["email"], admin_creds["password"])
    
    def logout(self) -> requests.Response:
        """Выход из учётной записи"""
        return self.session.get(
            f"{self.base_url}/logout",
            headers=self._get_headers(include_auth=True)
        )
    
    def refresh_tokens(self) -> requests.Response:
        """Обновление токенов"""
        return self.session.get(
            f"{self.base_url}/refresh-tokens",
            headers=self._get_headers(include_auth=True)
        )
    
    def get_user(self, id_or_email: str) -> requests.Response:
        """Получение информации о пользователе"""
        return self.session.get(
            f"{self.base_url}/user/{id_or_email}",
            headers=self._get_headers(include_auth=True)
        )
    
    def get_all_users(self, page_size: int = 10, page: int = 1, 
                      roles: list = None, created_at: str = "asc") -> requests.Response:
        """Получение списка пользователей"""
        params = {
            "pageSize": page_size,
            "page": page,
            "createdAt": created_at
        }
        if roles:
            params["roles"] = roles
        
        return self.session.get(
            f"{self.base_url}/user",
            params=params,
            headers=self._get_headers(include_auth=True)
        )
    
    def create_user(self, full_name: str, email: str, password: str, 
                    verified: bool = True, banned: bool = False) -> requests.Response:
        """Создание пользователя (требует прав ADMIN/SUPER_ADMIN)"""
        payload = {
            "fullName": full_name,
            "email": email,
            "password": password,
            "verified": verified,
            "banned": banned
        }
        return self.session.post(
            f"{self.base_url}/user",
            json=payload,
            headers=self._get_headers(include_auth=True)
        )
    
    def delete_user(self, user_id: str) -> requests.Response:
        """Удаление пользователя"""
        return self.session.delete(
            f"{self.base_url}/user/{user_id}",
            headers=self._get_headers(include_auth=True)
        )
    
    def edit_user(self, user_id: str, roles: list = None, 
                  verified: bool = None, banned: bool = None) -> requests.Response:
        """Изменение данных пользователя"""
        payload = {}
        if roles is not None:
            payload["roles"] = roles
        if verified is not None:
            payload["verified"] = verified
        if banned is not None:
            payload["banned"] = banned
        
        return self.session.patch(
            f"{self.base_url}/user/{user_id}",
            json=payload,
            headers=self._get_headers(include_auth=True)
        )
