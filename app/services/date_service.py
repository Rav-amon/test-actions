"""Сервис работы с календарными датами.

Названия дней недели и месяцев заданы явными константами, а не через
``strftime``: так ответ API не зависит от локали, установленной в системе.
"""

import calendar
from datetime import date, datetime, timezone as dt_timezone
from zoneinfo import ZoneInfo

from app.errors import InvalidDateError
from app.schemas import DateInfo, ServerDate
from app.services.time_service import DEFAULT_TIMEZONE, resolve_timezone

DATE_FORMAT = '%Y-%m-%d'

WEEKDAY_NAMES = (
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday',
    'Sunday',
)

MONTH_NAMES = (
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December',
)

MONTH_INDEX_OFFSET = 1


def parse_date(raw_date: str) -> date:
    """Разбирает дату из строки формата ``YYYY-MM-DD``.

    Args:
        raw_date: Строка с датой, например ``2026-09-03``.

    Returns:
        Разобранная дата.

    Raises:
        InvalidDateError: Если строка не соответствует формату или дата не существует.
    """
    try:
        return datetime.strptime(raw_date, DATE_FORMAT).date()
    except ValueError as exc:
        raise InvalidDateError(raw_date) from exc


def build_date_info(value: date) -> DateInfo:
    """Собирает календарные сведения о дате.

    Чистая функция: одинаковый аргумент всегда даёт одинаковый результат.

    Args:
        value: Дата, о которой нужны сведения.

    Returns:
        Календарные сведения о дате.
    """
    iso_calendar = value.isocalendar()

    return DateInfo(
        date=value.isoformat(),
        year=value.year,
        month=value.month,
        day=value.day,
        weekday=iso_calendar.weekday,
        weekday_name=WEEKDAY_NAMES[value.weekday()],
        month_name=MONTH_NAMES[value.month - MONTH_INDEX_OFFSET],
        iso_week=iso_calendar.week,
        day_of_year=value.timetuple().tm_yday,
        is_leap_year=calendar.isleap(value.year),
    )


def build_server_date(moment: datetime, target_timezone: ZoneInfo) -> ServerDate:
    """Определяет дату, наступившую в заданном часовом поясе на момент ``moment``.

    Чистая функция: одинаковые аргументы всегда дают одинаковый результат.

    Args:
        moment: Момент времени с указанным часовым поясом (aware datetime).
        target_timezone: Пояс, в котором нужно определить дату.

    Returns:
        Дата сервера в этом часовом поясе.

    Raises:
        ValueError: Если ``moment`` не содержит информации о часовом поясе.
    """
    if moment.tzinfo is None:
        raise ValueError('Ожидается datetime с часовым поясом (aware datetime)')

    localized_date = moment.astimezone(target_timezone).date()
    info = build_date_info(localized_date)

    return ServerDate(**info.model_dump(), timezone=str(target_timezone))


def get_server_date(timezone_name: str = DEFAULT_TIMEZONE) -> ServerDate:
    """Возвращает текущую дату сервера в запрошенном часовом поясе.

    Args:
        timezone_name: Имя часового пояса IANA. По умолчанию ``UTC``.

    Returns:
        Текущая дата сервера.

    Raises:
        InvalidTimezoneError: Если пояс неизвестен.
    """
    target_timezone = resolve_timezone(timezone_name)
    return build_server_date(datetime.now(dt_timezone.utc), target_timezone)


def get_date_info(raw_date: str) -> DateInfo:
    """Возвращает календарные сведения о произвольной дате.

    Args:
        raw_date: Дата в формате ``YYYY-MM-DD``.

    Returns:
        Календарные сведения о дате.

    Raises:
        InvalidDateError: Если дату не удалось разобрать.
    """
    return build_date_info(parse_date(raw_date))
