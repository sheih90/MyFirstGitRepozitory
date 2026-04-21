# Auth API Test Framework

Фреймворк для тестирования Auth API сервиса Cinescope.

## Структура проекта

```
auth_api_tests/
├── config/                 # Конфигурация
│   ├── __init__.py
│   ├── settings.py         # Настройки через pydantic
│   └── .env.example        # Пример переменных окружения
├── core/                   # Ядро фреймворка
│   ├── __init__.py
│   └── api_client.py       # Клиент для работы с API
├── data/                   # Тестовые данные
│   ├── __init__.py
│   └── test_data.py        # Классы с тестовыми данными
├── tests/                  # Тесты
│   ├── __init__.py
│   ├── test_auth.py        # Тесты авторизации
│   └── test_users.py       # Тесты пользователей
├── utils/                  # Утилиты
│   ├── __init__.py
│   └── assertions.py       # Пользовательские ассерты
├── allure-results/         # Отчёты Allure (генерируются автоматически)
├── pytest.ini              # Конфигурация pytest
├── requirements.txt        # Зависимости
└── README.md               # Этот файл
```

## Установка

1. Клонируйте репозиторий или создайте директорию проекта

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` на основе `.env.example`:
```bash
cp config/.env.example config/.env
```

5. При необходимости измените настройки в `config/.env`

## Запуск тестов

### Все тесты:
```bash
pytest
```

### Тесты с отчётом Allure:
```bash
pytest --alluredir=allure-results
```

### Открыть отчёт Allure:
```bash
allure serve allure-results
```

### Запуск конкретных тестов:
```bash
# Только тесты регистрации
pytest tests/test_auth.py::TestRegistration -v

# Только smoke тесты
pytest -m smoke -v

# Тесты по метке auth
pytest -m auth -v
```

### Генерация отчёта HTML:
```bash
pytest --html=report.html --self-contained-html
```

## Доступные API эндпоинты

### Авторизация:
- `POST /register` - Регистрация пользователя
- `POST /login` - Аутентификация пользователя
- `GET /logout` - Выход из учётной записи
- `GET /refresh-tokens` - Обновление токенов

### Пользователи:
- `GET /user/{idOrEmail}` - Получение информации о пользователе
- `DELETE /user/{id}` - Удаление пользователя
- `PATCH /user/{id}` - Изменение данных пользователя
- `POST /user` - Создание пользователя (ADMIN/SUPER_ADMIN)
- `GET /user` - Получение списка пользователей (ADMIN/SUPER_ADMIN)

## Добавление новых тестов

1. Создайте новый файл теста в директории `tests/` с префиксом `test_`

2. Используйте фикстуры:
   - `api_client` - клиент API без авторизации
   - `registered_user` - зарегистрированный пользователь
   - `authenticated_client` - аутентифицированный клиент

3. Используйте декораторы Allure для документирования:
```python
@allure.feature("Название функции")
@allure.story("Название истории")
@allure.title("Название теста")
def test_example(api_client):
    with allure.step("Шаг 1"):
        # действие
        pass
    
    with allure.step("Шаг 2"):
        # проверка
        pass
```

## Особенности

- **Pydantic** для валидации настроек
- **Requests** для HTTP запросов
- **Pytest** как тестовый фреймворк
- **Allure** для красивых отчётов
- **Фикстуры** для переиспользования кода
- **Page Object**-подобная архитектура через `APIClient`

## Требования к паролю

Пароль должен содержать:
- Минимум 8 символов
- Хотя бы одну заглавную букву
- Хотя бы одну строчную букву
- Хотя бы одну цифру

Пример: `12345678Aa`
