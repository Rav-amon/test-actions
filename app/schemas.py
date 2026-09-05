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


class DateInfo(BaseModel):
    """Календарные сведения о дате, не зависящие от часового пояса."""

    date: str = Field(..., description='Дата в формате ISO 8601', examples=['2026-09-03'])
    year: int = Field(..., description='Год', examples=[2026])
    month: int = Field(..., description='Номер месяца, 1-12', examples=[9])
    day: int = Field(..., description='День месяца, 1-31', examples=[3])
    weekday: int = Field(..., description='День недели по ISO: 1 — понедельник, 7 — воскресенье', examples=[4])
    weekday_name: str = Field(..., description='Название дня недели', examples=['Thursday'])
    month_name: str = Field(..., description='Название месяца', examples=['September'])
    iso_week: int = Field(..., description='Номер недели по ISO 8601', examples=[36])
    day_of_year: int = Field(..., description='Порядковый номер дня в году', examples=[246])
    is_leap_year: bool = Field(..., description='Является ли год високосным', examples=[False])


class ServerDate(DateInfo):
    """Текущая дата сервера в заданном часовом поясе."""

    timezone: str = Field(..., description='Имя часового пояса', examples=['UTC'])


class HealthStatus(BaseModel):
    """Состояние сервиса для health-check."""

    status: str = Field(..., description='Статус сервиса', examples=['ok'])
    version: str = Field(..., description='Версия приложения', examples=['1.0.0'])
