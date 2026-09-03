"""Доменные исключения приложения."""

from http import HTTPStatus


class AppError(Exception):
    """Базовая ошибка приложения с кодом, сообщением и деталями."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = HTTPStatus.BAD_REQUEST,
        details: dict[str, object] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details


class InvalidTimezoneError(AppError):
    """Передан неизвестный или некорректный часовой пояс."""

    def __init__(self, timezone_name: str) -> None:
        super().__init__(
            code='INVALID_TIMEZONE',
            message=f'Неизвестный часовой пояс: {timezone_name}',
            status_code=HTTPStatus.BAD_REQUEST,
            details={'timezone': timezone_name},
        )
