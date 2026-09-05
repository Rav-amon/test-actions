"""Маршруты API версии 1."""

from fastapi import APIRouter, Path, Query

from app import __version__
from app.schemas import ApiResponse, DateInfo, HealthStatus, ServerDate, ServerTime
from app.services.date_service import get_date_info, get_server_date
from app.services.time_service import DEFAULT_TIMEZONE, get_server_time

router = APIRouter(prefix='/api/v1', tags=['time'])

TIMEZONE_QUERY = Query(
    default=DEFAULT_TIMEZONE,
    description='Часовой пояс IANA, например Europe/Moscow',
    examples=['UTC'],
)


@router.get(
    '/time',
    response_model=ApiResponse[ServerTime],
    summary='Текущее время сервера',
)
def read_server_time(tz: str = TIMEZONE_QUERY) -> ApiResponse[ServerTime]:
    """Возвращает текущее время сервера в запрошенном часовом поясе."""
    return ApiResponse[ServerTime](
        data=get_server_time(tz),
        message='Текущее время сервера',
    )


@router.get(
    '/date',
    response_model=ApiResponse[ServerDate],
    summary='Текущая дата сервера',
    tags=['date'],
)
def read_server_date(tz: str = TIMEZONE_QUERY) -> ApiResponse[ServerDate]:
    """Возвращает текущую дату сервера в запрошенном часовом поясе."""
    return ApiResponse[ServerDate](
        data=get_server_date(tz),
        message='Текущая дата сервера',
    )


@router.get(
    '/date/{target_date}',
    response_model=ApiResponse[DateInfo],
    summary='Сведения о произвольной дате',
    tags=['date'],
)
def read_date_info(
    target_date: str = Path(
        ...,
        description='Дата в формате YYYY-MM-DD',
        examples=['2026-09-03'],
    ),
) -> ApiResponse[DateInfo]:
    """Возвращает календарные сведения о переданной дате."""
    return ApiResponse[DateInfo](
        data=get_date_info(target_date),
        message='Сведения о дате',
    )


@router.get(
    '/health',
    response_model=ApiResponse[HealthStatus],
    summary='Проверка работоспособности',
    tags=['health'],
)
def read_health() -> ApiResponse[HealthStatus]:
    """Возвращает статус сервиса и версию приложения."""
    return ApiResponse[HealthStatus](
        data=HealthStatus(status='ok', version=__version__),
        message='Сервис работает',
    )
