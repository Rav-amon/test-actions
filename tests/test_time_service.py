"""Тесты сервиса работы со временем."""

from datetime import datetime, timezone as dt_timezone
from zoneinfo import ZoneInfo

import pytest

from app.errors import InvalidTimezoneError
from app.services.time_service import (
    MILLISECONDS_IN_SECOND,
    build_server_time,
    get_server_time,
    resolve_timezone,
)

FIXED_MOMENT = datetime(2026, 9, 3, 4, 34, 0, tzinfo=dt_timezone.utc)
MOSCOW_OFFSET_MINUTES = 180


def test_should_return_utc_representation_when_timezone_is_utc() -> None:
    result = build_server_time(FIXED_MOMENT, ZoneInfo('UTC'))

    assert result.iso == '2026-09-03T04:34:00+00:00'
    assert result.timezone == 'UTC'
    assert result.utc_offset_minutes == 0


def test_should_convert_moment_when_timezone_is_moscow() -> None:
    result = build_server_time(FIXED_MOMENT, ZoneInfo('Europe/Moscow'))

    assert result.iso == '2026-09-03T07:34:00+03:00'
    assert result.utc_offset_minutes == MOSCOW_OFFSET_MINUTES


def test_should_keep_same_unix_ms_for_different_timezones() -> None:
    utc_time = build_server_time(FIXED_MOMENT, ZoneInfo('UTC'))
    moscow_time = build_server_time(FIXED_MOMENT, ZoneInfo('Europe/Moscow'))

    assert utc_time.unix_ms == moscow_time.unix_ms


def test_should_raise_value_error_when_moment_is_naive() -> None:
    naive_moment = datetime(2026, 9, 3, 4, 34, 0)

    with pytest.raises(ValueError):
        build_server_time(naive_moment, ZoneInfo('UTC'))


def test_should_raise_invalid_timezone_error_when_name_is_unknown() -> None:
    with pytest.raises(InvalidTimezoneError):
        resolve_timezone('Mars/Olympus')


def test_should_return_current_time_when_timezone_is_default() -> None:
    before_ms = int(datetime.now(dt_timezone.utc).timestamp() * MILLISECONDS_IN_SECOND)
    result = get_server_time()
    after_ms = int(datetime.now(dt_timezone.utc).timestamp() * MILLISECONDS_IN_SECOND)

    assert before_ms <= result.unix_ms <= after_ms
