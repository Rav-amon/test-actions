"""Pydantic-схемы запросов и ответов API."""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

TData = TypeVar('TData')


class ErrorDetail(BaseModel):
    """Единый формат ошибки: код, сообщение, детали."""

    code: str = Field(..., description='Машиночитаемый код ошибки', examples=['INVALID_TIMEZONE'])
    message: str = Field(..., description='Человекочитаемое описание ошибки')
    details: dict[str, object] | None = Field(
        default=None,
        description='Дополнительный контекст ошибки',
    )


class ApiResponse(BaseModel, Generic[TData]):
    """Единый формат ответа API: data, error, message."""

    data: TData | None = Field(default=None, description='Полезная нагрузка ответа')
    error: ErrorDetail | None = Field(default=None, description='Описание ошибки, если она есть')
    message: str = Field(default='', description='Короткое пояснение результата')


class ServerTime(BaseModel):
    """Текущее время сервера в разных представлениях."""

    iso: str = Field(..., description='Время в формате ISO 8601', examples=['2026-09-03T04:34:00+00:00'])
    timezone: str = Field(..., description='Имя часового пояса', examples=['UTC'])
    unix_ms: int = Field(..., description='Unix-время в миллисекундах', examples=[1772512440000])
    utc_offset_minutes: int = Field(..., description='Смещение от UTC в минутах', examples=[0])


class HealthStatus(BaseModel):
    """Состояние сервиса для health-check."""

    status: str = Field(..., description='Статус сервиса', examples=['ok'])
    version: str = Field(..., description='Версия приложения', examples=['1.0.0'])
