"""Тесты HTTP-эндпоинтов."""

from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_should_return_server_time_when_request_is_valid(client: TestClient) -> None:
    response = client.get('/api/v1/time')
    body = response.json()

    assert response.status_code == HTTPStatus.OK
    assert body['error'] is None
    assert body['data']['timezone'] == 'UTC'
    assert body['data']['utc_offset_minutes'] == 0


def test_should_return_localized_time_when_timezone_is_provided(client: TestClient) -> None:
    response = client.get('/api/v1/time', params={'tz': 'Europe/Moscow'})
    body = response.json()

    assert response.status_code == HTTPStatus.OK
    assert body['data']['timezone'] == 'Europe/Moscow'
    assert body['data']['iso'].endswith('+03:00')


def test_should_return_error_when_timezone_is_unknown(client: TestClient) -> None:
    response = client.get('/api/v1/time', params={'tz': 'Mars/Olympus'})
    body = response.json()

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert body['data'] is None
    assert body['error']['code'] == 'INVALID_TIMEZONE'
    assert body['error']['details']['timezone'] == 'Mars/Olympus'


def test_should_return_server_date_when_request_is_valid(client: TestClient) -> None:
    response = client.get('/api/v1/date')
    body = response.json()

    assert response.status_code == HTTPStatus.OK
    assert body['error'] is None
    assert body['data']['timezone'] == 'UTC'
    assert len(body['data']['date']) == len('YYYY-MM-DD')


def test_should_return_date_info_when_date_is_valid(client: TestClient) -> None:
    response = client.get('/api/v1/date/2026-09-03')
    body = response.json()

    assert response.status_code == HTTPStatus.OK
    assert body['data']['weekday_name'] == 'Thursday'
    assert body['data']['month_name'] == 'September'
    assert body['data']['day_of_year'] == 246


def test_should_return_error_when_date_is_malformed(client: TestClient) -> None:
    response = client.get('/api/v1/date/2026-02-30')
    body = response.json()

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert body['data'] is None
    assert body['error']['code'] == 'INVALID_DATE'
    assert body['error']['details']['date'] == '2026-02-30'


def test_should_return_ok_status_when_health_is_requested(client: TestClient) -> None:
    response = client.get('/api/v1/health')
    body = response.json()

    assert response.status_code == HTTPStatus.OK
    assert body['data']['status'] == 'ok'


def test_should_return_not_found_error_when_route_is_unknown(client: TestClient) -> None:
    response = client.get('/api/v1/unknown')
    body = response.json()

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert body['error']['code'] == 'NOT_FOUND'
