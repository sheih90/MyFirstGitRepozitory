import pytest
import allure


@allure.step("Проверка кода статуса ответа")
def assert_status_code(response, expected_status: int, custom_message: str = None):
    """Проверка кода статуса HTTP ответа"""
    actual_status = response.status_code
    message = custom_message or (
        f"Ожидаемый статус код: {expected_status}, "
        f"фактический: {actual_status}. Ответ: {response.text}"
    )
    assert actual_status == expected_status, message


@allure.step("Проверка наличия поля в ответе")
def assert_field_exists(response_data: dict, field_name: str):
    """Проверка наличия поля в JSON ответе"""
    assert field_name in response_data, (
        f"Поле '{field_name}' отсутствует в ответе. Ответ: {response_data}"
    )


@allure.step("Проверка значения поля в ответе")
def assert_field_value(response_data: dict, field_name: str, expected_value):
    """Проверка значения поля в JSON ответе"""
    assert_field_exists(response_data, field_name)
    actual_value = response_data[field_name]
    assert actual_value == expected_value, (
        f"Ожидаемое значение поля '{field_name}': {expected_value}, "
        f"фактическое: {actual_value}"
    )


@allure.step("Проверка сообщения об ошибке")
def assert_error_message(response_data: dict, expected_message: str = None):
    """Проверка сообщения об ошибке в ответе"""
    if expected_message:
        assert "message" in response_data, "В ответе отсутствует поле 'message'"
        assert expected_message in response_data["message"], (
            f"Ожидаемое сообщение об ошибке: '{expected_message}', "
            f"фактическое: '{response_data.get('message', '')}'"
        )
