import pytest
import allure
import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.api_client import APIClient
from utils.assertions import assert_status_code, assert_field_exists


@pytest.fixture(scope="function")
def api_client():
    """Фикстура для создания клиента API"""
    client = APIClient()
    yield client


@pytest.fixture(scope="function")
def authenticated_client(api_client):
    """Фикстура для создания аутентифицированного клиента"""
    import random
    # Сначала регистрируем пользователя с уникальным email
    random_id = random.randint(10000, 99999)
    test_email = f"testuser{random_id}@gmail.com"
    test_password = "12345678Aa"
    test_fullname = "Test User"
    
    register_response = api_client.register(
        email=test_email,
        full_name=test_fullname,
        password=test_password,
        password_repeat=test_password
    )
    
    # Если пользователь уже существует (400 или 409), просто логинимся
    if register_response.status_code in [400, 409]:
        login_response = api_client.login(email=test_email, password=test_password)
        # Если логин не удался, создаем нового пользователя с другим email
        if login_response.status_code != 200:
            random_id = random.randint(10000, 99999)
            test_email = f"testuser{random_id}_new@gmail.com"
            register_response = api_client.register(
                email=test_email,
                full_name=test_fullname,
                password=test_password,
                password_repeat=test_password
            )
            assert_status_code(register_response, 201)
            login_response = api_client.login(email=test_email, password=test_password)
    else:
        assert_status_code(register_response, 201)
        login_response = api_client.login(email=test_email, password=test_password)
    
    assert_status_code(login_response, 200)
    yield api_client


class TestUserManagement:
    """Тесты на управление пользователями"""
    
    @allure.feature("Пользователь")
    @allure.story("Получение информации о пользователе")
    @allure.title("Получение информации о текущем пользователе")
    def test_get_current_user(self, authenticated_client):
        """Проверка получения информации о текущем пользователе"""
        # Получаем email текущего пользователя из сессии
        # После логина мы должны иметь доступ к своему профилю
        pass  # Требуется доработка API клиента для получения текущего user_id
    
    @allure.feature("Пользователь")
    @allure.story("Получение списка пользователей")
    @allure.title("Получение списка пользователей без авторизации")
    def test_get_users_without_auth(self, api_client):
        """Проверка получения списка пользователей без авторизации"""
        with allure.step("Выполнение запроса на получение списка пользователей"):
            response = api_client.get_all_users()
        
        with allure.step("Проверка кода ответа 401"):
            assert_status_code(response, 401)
    
    @allure.feature("Пользователь")
    @allure.story("Создание пользователя")
    @allure.title("Создание пользователя без авторизации")
    def test_create_user_without_auth(self, api_client):
        """Проверка создания пользователя без авторизации"""
        with allure.step("Выполнение запроса на создание пользователя"):
            response = api_client.create_user(
                full_name="New User",
                email="newuser@email.com",
                password="12345678Aa"
            )
        
        with allure.step("Проверка кода ответа 401"):
            assert_status_code(response, 401)
