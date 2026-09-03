# Server Time API

Простой тестовый бэкенд на FastAPI, возвращающий текущее время сервера.

## Возможности

- Текущее время сервера в ISO 8601, Unix-миллисекундах и со смещением от UTC
- Конвертация в любой часовой пояс IANA через query-параметр `tz`
- Единый формат ответа `{ data, error, message }` и единый формат ошибки `{ code, message, details }`
- Автогенерируемая OpenAPI-спецификация и Swagger UI
- Health-check эндпоинт

## Требования

- Python 3.11+ (проверено на 3.12)

## Установка

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
```

## Запуск

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- Swagger UI: http://127.0.0.1:8000/docs
- OpenAPI JSON: http://127.0.0.1:8000/openapi.json

## Эндпоинты

### `GET /api/v1/time`

Возвращает текущее время сервера.

| Параметр | Тип | По умолчанию | Описание |
| --- | --- | --- | --- |
| `tz` | string | `UTC` | Часовой пояс IANA, например `Europe/Moscow` |

Пример запроса:

```bash
curl "http://127.0.0.1:8000/api/v1/time?tz=Europe/Moscow"
```

Пример ответа `200 OK`:

```json
{
  "data": {
    "iso": "2026-09-03T07:34:00.123456+03:00",
    "timezone": "Europe/Moscow",
    "unix_ms": 1772512440123,
    "utc_offset_minutes": 180
  },
  "error": null,
  "message": "Текущее время сервера"
}
```

Пример ответа `400 Bad Request` при неизвестном поясе:

```json
{
  "data": null,
  "error": {
    "code": "INVALID_TIMEZONE",
    "message": "Неизвестный часовой пояс: Mars/Olympus",
    "details": { "timezone": "Mars/Olympus" }
  },
  "message": "Неизвестный часовой пояс: Mars/Olympus"
}
```

### `GET /api/v1/health`

Возвращает статус сервиса и версию приложения.

```json
{
  "data": { "status": "ok", "version": "1.0.0" },
  "error": null,
  "message": "Сервис работает"
}
```

## Коды ошибок

| Код | HTTP | Когда возникает |
| --- | --- | --- |
| `INVALID_TIMEZONE` | 400 | Передан неизвестный часовой пояс |
| `VALIDATION_ERROR` | 422 | Некорректные параметры запроса |
| `NOT_FOUND` | 404 | Запрошен несуществующий маршрут |
| `INTERNAL_ERROR` | 500 | Непредвиденная ошибка сервера |

## Тесты

```bash
pytest -q
```

## Структура проекта

```
app/
  api/v1/routes.py       — HTTP-маршруты версии 1
  services/time_service.py — логика работы со временем
  schemas.py             — Pydantic-схемы запросов и ответов
  errors.py              — доменные исключения
  main.py                — сборка приложения и обработчики ошибок
tests/                   — тесты сервиса и API
```

## Заметки по реализации

- Время всегда вычисляется в UTC и приводится к нужному поясу только при отдаче.
- `build_server_time` — чистая функция, поэтому легко тестируется на фиксированном моменте.
- Пакет `tzdata` нужен на Windows: там нет системной базы часовых поясов IANA.
