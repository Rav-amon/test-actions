"""Тесты сервиса работы с датами."""

from datetime import date, datetime, timezone as dt_timezone
from zoneinfo import ZoneInfo

import pytest

from app.errors import InvalidDateError
from app.services.date_service import build_date_info, build_server_date, parse_date

LEAP_YEAR_DAY_OF_YEAR = 60
THURSDAY_ISO_WEEKDAY = 4
SUNDAY_ISO_WEEKDAY = 7


def test_should_return_calendar_fields_when_date_is_valid() -> None:
    result = build_date_info(date(2026, 9, 3))

    assert result.date == '2026-09-03'
    assert result.year == 2026
    assert result.month == 9
    assert result.day == 3
    assert result.weekday == THURSDAY_ISO_WEEKDAY
    assert result.weekday_name == 'Thursday'
    assert result.month_name == 'September'
    assert result.day_of_year == 246
    assert result.is_leap_year is False


def test_should_mark_sunday_as_seventh_weekday() -> None:
    result = build_date_info(date(2026, 9, 6))

    assert result.weekday == SUNDAY_ISO_WEEKDAY
    assert result.weekday_name == 'Sunday'


def test_should_detect_leap_year_when_february_has_29_days() -> None:
    result = build_date_info(date(2024, 2, 29))

    assert result.is_leap_year is True
    assert result.day_of_year == LEAP_YEAR_DAY_OF_YEAR


def test_should_return_iso_week_from_previous_year_when_date_is_january_first() -> None:
    result = build_date_info(date(2027, 1, 1))

    assert result.iso_week == 53


def test_should_parse_date_when_format_is_iso() -> None:
    assert parse_date('2026-09-03') == date(2026, 9, 3)


@pytest.mark.parametrize('raw_date', ['03-09-2026', '2026-13-01', '2026-02-30', 'вчера', ''])
def test_should_raise_invalid_date_error_when_string_is_malformed(raw_date: str) -> None:
    with pytest.raises(InvalidDateError):
        parse_date(raw_date)


def test_should_return_next_day_when_timezone_is_ahead_of_utc() -> None:
    late_utc_evening = datetime(2026, 9, 3, 22, 30, tzinfo=dt_timezone.utc)

    utc_date = build_server_date(late_utc_evening, ZoneInfo('UTC'))
    tokyo_date = build_server_date(late_utc_evening, ZoneInfo('Asia/Tokyo'))

    assert utc_date.date == '2026-09-03'
    assert tokyo_date.date == '2026-09-04'
    assert tokyo_date.timezone == 'Asia/Tokyo'


def test_should_raise_value_error_when_moment_is_naive() -> None:
    naive_moment = datetime(2026, 9, 3, 12, 0)

    with pytest.raises(ValueError):
        build_server_date(naive_moment, ZoneInfo('UTC'))
