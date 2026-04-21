import pytest
import allure
import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.api_client import APIClient
from data.test_data import TestData
from utils.assertions import assert_status_code, assert_field_exists, assert_field_value


@pytest.fixture(scope="function")
def api_client():
    """Фикстура для создания клиента API"""
    client = APIClient()
    yield client


@pytest.fixture(scope="function")
def registered_user(api_client):
    """Фикстура для создания зарегистрированного пользователя"""
    import random
    random_id = random.randint(10000, 99999)
    test_email = f"testuser{random_id}@gmail.com"
    test_password = "12345678Aa"
    test_fullname = "Test Automation User"
    
    # Регистрируем нового пользователя
    response = api_client.register(
        email=test_email,
        full_name=test_fullname,
        password=test_password,
        password_repeat=test_password
    )
    
    # Если пользователь уже существует (400 или 409), просто логинимся
    if response.status_code in [400, 409]:
        login_response = api_client.login(
            email=test_email,
            password=test_password
        )
        # Если логин не удался, создаем нового пользователя с другим email
        if login_response.status_code != 200:
            random_id = random.randint(10000, 99999)
            test_email = f"testuser{random_id}_new@gmail.com"
            response = api_client.register(
                email=test_email,
                full_name=test_fullname,
                password=test_password,
                password_repeat=test_password
            )
            assert_status_code(response, 201)
            login_response = api_client.login(
                email=test_email,
                password=test_password
            )
        assert_status_code(login_response, 200)
    else:
        assert_status_code(response, 201)
        # Логинимся после регистрации
        login_response = api_client.login(
            email=test_email,
            password=test_password
        )
        assert_status_code(login_response, 200)
    
    yield {
        "email": test_email,
        "password": test_password,
        "fullName": test_fullname
    }


@pytest.fixture(scope="function")
def admin_client():
    """Фикстура для создания клиента API с правами администратора"""
    client = APIClient()
    
    # Логинимся под администратором
    login_response = client.login_as_admin()
    assert_status_code(login_response, 200, 
        f"Не удалось войти под администратором. Проверьте креды. Ответ: {login_response.text}")
    
    yield client


class TestRegistration:
    """Тесты на регистрацию пользователя"""
    
    @allure.feature("Авторизация")
    @allure.story("Регистрация пользователя")
    @allure.title("Успешная регистрация нового пользователя")
    def test_successful_registration(self, api_client):
        """Проверка успешной регистрации нового пользователя"""
        import random
        random_id = random.randint(1000, 9999)
        test_data = {
            "email": f"newuser{random_id}@email.com",
            "fullName": "New Test User",
            "password": "12345678Aa",
            "passwordRepeat": "12345678Aa"
        }
        
        with allure.step("Выполнение запроса на регистрацию"):
            response = api_client.register(
                email=test_data["email"],
                full_name=test_data["fullName"],
                password=test_data["password"],
                password_repeat=test_data["passwordRepeat"]
            )
        
        with allure.step("Проверка кода ответа 201"):
            assert_status_code(response, 201)
        
        with allure.step("Проверка наличия полей в ответе"):
            response_data = response.json()
            assert_field_exists(response_data, "id")
            assert_field_exists(response_data, "email")
            assert_field_exists(response_data, "fullName")
            assert_field_value(response_data, "email", test_data["email"])
    
    @allure.feature("Авторизация")
    @allure.story("Регистрация пользователя")
    @allure.title("Регистрация с невалидным email")
    def test_registration_with_invalid_email(self, api_client):
        """Проверка регистрации с невалидным email"""
        test_data = TestData.get_invalid_email_data()
        
        with allure.step("Выполнение запроса на регистрацию с невалидным email"):
            response = api_client.register(
                email=test_data["email"],
                full_name=test_data["fullName"],
                password=test_data["password"],
                password_repeat=test_data["passwordRepeat"]
            )
        
        with allure.step("Проверка кода ответа 400"):
            assert_status_code(response, 400)
    
    @allure.feature("Авторизация")
    @allure.story("Регистрация пользователя")
    @allure.title("Регистрация с несоответствующими паролями")
    def test_registration_with_mismatched_passwords(self, api_client):
        """Проверка регистрации с несоответствующими паролями"""
        test_data = TestData.get_mismatched_passwords_data()
        
        with allure.step("Выполнение запроса на регистрацию с разными паролями"):
            response = api_client.register(
                email=test_data["email"],
                full_name=test_data["fullName"],
                password=test_data["password"],
                password_repeat=test_data["passwordRepeat"]
            )
        
        with allure.step("Проверка кода ответа 400"):
            assert_status_code(response, 400)
    
    @allure.feature("Авторизация")
    @allure.story("Регистрация пользователя")
    @allure.title("Регистрация существующего пользователя")
    def test_registration_existing_user(self, api_client, registered_user):
        """Проверка регистрации уже существующего пользователя"""
        with allure.step("Выполнение запроса на регистрацию существующего пользователя"):
            response = api_client.register(
                email=registered_user["email"],
                full_name=registered_user["fullName"],
                password=registered_user["password"],
                password_repeat=registered_user["password"]
            )
        
        # API возвращает 409 (Conflict) или 400 с сообщением о существующем пользователе
        with allure.step("Проверка кода ответа 409 или 400"):
            assert response.status_code in [400, 409], f"Ожидался статус 400 или 409, получен: {response.status_code}"


class TestLogin:
    """Тесты на аутентификацию пользователя"""
    
    @allure.feature("Авторизация")
    @allure.story("Аутентификация пользователя")
    @allure.title("Успешная аутентификация")
    def test_successful_login(self, api_client, registered_user):
        """Проверка успешной аутентификации пользователя"""
        with allure.step("Выполнение запроса на вход"):
            response = api_client.login(
                email=registered_user["email"],
                password=registered_user["password"]
            )
        
        with allure.step("Проверка кода ответа 200"):
            assert_status_code(response, 200)
    
    @allure.feature("Авторизация")
    @allure.story("Аутентификация пользователя")
    @allure.title("Аутентификация с неверным паролем")
    def test_login_with_wrong_password(self, api_client, registered_user):
        """Проверка аутентификации с неверным паролем"""
        with allure.step("Выполнение запроса на вход с неверным паролем"):
            response = api_client.login(
                email=registered_user["email"],
                password="wrongpassword123"
            )
        
        with allure.step("Проверка кода ответа 401"):
            assert_status_code(response, 401)
    
    @allure.feature("Авторизация")
    @allure.story("Аутентификация пользователя")
    @allure.title("Аутентификация несуществующего пользователя")
    def test_login_nonexistent_user(self, api_client):
        """Проверка аутентификации несуществующего пользователя"""
        test_data = TestData.get_invalid_login_data()
        
        with allure.step("Выполнение запроса на вход несуществующего пользователя"):
            response = api_client.login(
                email=test_data["email"],
                password=test_data["password"]
            )
        
        # API возвращает 401 для несуществующих пользователей (не разглашает информацию)
        with allure.step("Проверка кода ответа 401"):
            assert_status_code(response, 401)


class TestAdminOperations:
    """Тесты на операции администратора"""
    
    @allure.feature("Администрирование")
    @allure.story("Вход администратора")
    @allure.title("Успешный вход администратора")
    def test_admin_login(self, api_client):
        """Проверка успешного входа под учетной записью администратора"""
        with allure.step("Выполнение запроса на вход администратора"):
            response = api_client.login_as_admin()
        
        with allure.step("Проверка кода ответа 200"):
            assert_status_code(response, 200)
        
        with allure.step("Проверка наличия токенов в ответе"):
            assert api_client.access_token is not None, "Access token не получен"
            assert api_client.refresh_token is not None, "Refresh token не получен"
    
    @allure.feature("Администрирование")
    @allure.story("Получение списка пользователей")
    @allure.title("Получение списка пользователей администратором")
    def test_get_all_users_as_admin(self, admin_client):
        """Проверка получения списка пользователей администратором"""
        with allure.step("Выполнение запроса на получение списка пользователей"):
            response = admin_client.get_all_users()
        
        with allure.step("Проверка кода ответа 200"):
            assert_status_code(response, 200)
        
        with allure.step("Проверка наличия данных в ответе"):
            response_data = response.json()
            # API возвращает 'users' вместо 'items'
            assert_field_exists(response_data, "users")
            assert isinstance(response_data["users"], list)
    
    @allure.feature("Администрирование")
    @allure.story("Создание пользователя")
    @allure.title("Создание пользователя администратором")
    def test_create_user_as_admin(self, admin_client):
        """Проверка создания пользователя администратором"""
        import random
        random_id = random.randint(10000, 99999)
        test_email = f"admin_created_{random_id}@email.com"
        test_password = "12345678Aa"
        test_fullname = "User Created by Admin"
        
        with allure.step("Выполнение запроса на создание пользователя"):
            response = admin_client.create_user(
                full_name=test_fullname,
                email=test_email,
                password=test_password,
                verified=True,
                banned=False
            )
        
        with allure.step("Проверка кода ответа 201"):
            assert_status_code(response, 201)
        
        with allure.step("Проверка наличия полей в ответе"):
            response_data = response.json()
            assert_field_exists(response_data, "id")
            assert_field_exists(response_data, "email")
            assert_field_value(response_data, "email", test_email)
    
    @allure.feature("Администрирование")
    @allure.story("Получение информации о пользователе")
    @allure.title("Получение информации о пользователе по email")
    def test_get_user_by_email_as_admin(self, admin_client):
        """Проверка получения информации о пользователе по email администратором"""
        # Сначала создаем пользователя
        import random
        random_id = random.randint(10000, 99999)
        test_email = f"get_user_{random_id}@email.com"
        test_password = "12345678Aa"
        test_fullname = "Get User Test"
        
        create_response = admin_client.create_user(
            full_name=test_fullname,
            email=test_email,
            password=test_password,
            verified=True,
            banned=False
        )
        assert_status_code(create_response, 201)
        
        with allure.step("Выполнение запроса на получение информации о пользователе"):
            response = admin_client.get_user(test_email)
        
        with allure.step("Проверка кода ответа 200"):
            assert_status_code(response, 200)
        
        with allure.step("Проверка данных пользователя"):
            response_data = response.json()
            assert_field_exists(response_data, "email")
            assert_field_value(response_data, "email", test_email)
    
    @allure.feature("Администрирование")
    @allure.story("Изменение роли пользователя")
    @allure.title("Изменение роли пользователя администратором")
    def test_edit_user_role_as_admin(self, admin_client):
        """Проверка изменения роли пользователя администратором"""
        import random
        random_id = random.randint(10000, 99999)
        test_email = f"edit_role_{random_id}@email.com"
        test_password = "12345678Aa"
        test_fullname = "Edit Role Test"
        
        # Создаем пользователя
        create_response = admin_client.create_user(
            full_name=test_fullname,
            email=test_email,
            password=test_password,
            verified=True,
            banned=False
        )
        assert_status_code(create_response, 201)
        user_id = create_response.json()["id"]
        
        with allure.step("Выполнение запроса на изменение роли пользователя"):
            response = admin_client.edit_user(
                user_id=user_id,
                roles=["USER"],  # Устанавливаем роль USER
                verified=True,
                banned=False
            )
        
        with allure.step("Проверка кода ответа 200"):
            assert_status_code(response, 200)
    
    @allure.feature("Администрирование")
    @allure.story("Удаление пользователя")
    @allure.title("Удаление пользователя администратором")
    def test_delete_user_as_admin(self, admin_client):
        """Проверка удаления пользователя администратором"""
        import random
        random_id = random.randint(10000, 99999)
        test_email = f"delete_user_{random_id}@email.com"
        test_password = "12345678Aa"
        test_fullname = "Delete User Test"
        
        # Создаем пользователя
        create_response = admin_client.create_user(
            full_name=test_fullname,
            email=test_email,
            password=test_password,
            verified=True,
            banned=False
        )
        assert_status_code(create_response, 201)
        user_id = create_response.json()["id"]
        
        with allure.step("Выполнение запроса на удаление пользователя"):
            response = admin_client.delete_user(user_id)
        
        with allure.step("Проверка кода ответа 200"):
            assert_status_code(response, 200)
        
        with allure.step("Проверка что пользователь удален (возвращается пустой объект)"):
            get_response = admin_client.get_user(user_id)
            # API возвращает 200 с пустым объектом {} для удаленного пользователя
            assert get_response.status_code == 200
            response_data = get_response.json()
            # Проверяем что ответ пустой или не содержит данных пользователя
            assert len(response_data) == 0 or "id" not in response_data, \
                f"Ожидался пустой ответ, но получен: {response_data}"


class TestLogout:
    """Тесты на выход из учётной записи"""
    
    @allure.feature("Авторизация")
    @allure.story("Выход из учётной записи")
    @allure.title("Успешный выход из учётной записи")
    def test_successful_logout(self, api_client, registered_user):
        """Проверка успешного выхода из учётной записи"""
        with allure.step("Выполнение запроса на выход"):
            response = api_client.logout()
        
        with allure.step("Проверка кода ответа 200"):
            assert_status_code(response, 200)
