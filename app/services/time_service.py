"""Сервис работы со временем сервера.

Время всегда вычисляется в UTC и только затем приводится к запрошенному
часовому поясу — так представление не влияет на исходное значение.
"""

from datetime import datetime, timezone as dt_timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.errors import InvalidTimezoneError
from app.schemas import ServerTime

DEFAULT_TIMEZONE = 'UTC'
MILLISECONDS_IN_SECOND = 1000
SECONDS_IN_MINUTE = 60


def resolve_timezone(timezone_name: str) -> ZoneInfo:
    """Преобразует имя часового пояса в объект ZoneInfo.

    Args:
        timezone_name: Имя пояса из базы IANA, например ``Europe/Moscow``.

    Returns:
        Объект часового пояса.

    Raises:
        InvalidTimezoneError: Если пояс неизвестен.
    """
    try:
        return ZoneInfo(timezone_name)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise InvalidTimezoneError(timezone_name) from exc


def build_server_time(moment: datetime, target_timezone: ZoneInfo) -> ServerTime:
    """Формирует представление момента времени в заданном часовом поясе.

    Чистая функция: одинаковые аргументы всегда дают одинаковый результат.

    Args:
        moment: Момент времени с указанным часовым поясом (aware datetime).
        target_timezone: Пояс, в котором нужно показать время.

    Returns:
        Представление времени сервера.

    Raises:
        ValueError: Если ``moment`` не содержит информации о часовом поясе.
    """
    if moment.tzinfo is None:
        raise ValueError('Ожидается datetime с часовым поясом (aware datetime)')

    localized = moment.astimezone(target_timezone)
    offset = localized.utcoffset()
    offset_minutes = 0 if offset is None else int(offset.total_seconds() // SECONDS_IN_MINUTE)

    return ServerTime(
        iso=localized.isoformat(),
        timezone=str(target_timezone),
        unix_ms=int(localized.timestamp() * MILLISECONDS_IN_SECOND),
        utc_offset_minutes=offset_minutes,
    )


def get_server_time(timezone_name: str = DEFAULT_TIMEZONE) -> ServerTime:
    """Возвращает текущее время сервера в запрошенном часовом поясе.

    Args:
        timezone_name: Имя часового пояса IANA. По умолчанию ``UTC``.

    Returns:
        Текущее время сервера.

    Raises:
        InvalidTimezoneError: Если пояс неизвестен.
    """
    target_timezone = resolve_timezone(timezone_name)
    return build_server_time(datetime.now(dt_timezone.utc), target_timezone)
