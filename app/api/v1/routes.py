"""Маршруты API версии 1."""

from fastapi import APIRouter, Query

from app import __version__
from app.schemas import ApiResponse, HealthStatus, ServerTime
from app.services.time_service import DEFAULT_TIMEZONE, get_server_time

router = APIRouter(prefix='/api/v1', tags=['time'])


@router.get(
    '/time',
    response_model=ApiResponse[ServerTime],
    summary='Текущее время сервера',
)
def read_server_time(
    tz: str = Query(
        default=DEFAULT_TIMEZONE,
        description='Часовой пояс IANA, например Europe/Moscow',
        examples=['UTC'],
    ),
) -> ApiResponse[ServerTime]:
    """Возвращает текущее время сервера в запрошенном часовом поясе."""
    return ApiResponse[ServerTime](
        data=get_server_time(tz),
        message='Текущее время сервера',
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
