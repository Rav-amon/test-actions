# Server Time API

Простой тестовый бэкенд на FastAPI, возвращающий текущее время сервера.

## Возможности

- Текущее время сервера в ISO 8601, Unix-миллисекундах и со смещением от UTC
- Текущая дата сервера с днём недели, номером ISO-недели и днём года
- Календарные сведения о произвольной дате
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

## Запуск в Docker

```bash
docker build -t server-time-api .
docker run -d --name server-time-api -p 8000:8000 server-time-api
```

Приложение будет доступно на http://127.0.0.1:8000. Состояние контейнера видно
в `docker ps`: встроенный HEALTHCHECK опрашивает `/api/v1/health` и переводит
контейнер в статус `healthy`.

Остановка и удаление контейнера:

```bash
docker rm -f server-time-api
```

## CI/CD

Workflow `.github/workflows/deploy.yml` при пуше в `main` собирает образ,
публикует его в GitHub Container Registry и разворачивает на сервере по SSH.

Секреты репозитория (Settings → Secrets and variables → Actions):

| Секрет | Описание |
| --- | --- |
| `SSH_HOST` | Адрес сервера |
| `SSH_USER` | Пользователь SSH, состоящий в группе `docker` |
| `SSH_PRIVATE_KEY` | Приватный ключ целиком, включая строки BEGIN/END |
| `SSH_PORT` | Порт SSH, обычно `22` |

Токен `GITHUB_TOKEN` для доступа к реестру создаётся автоматически, отдельный
секрет для него заводить не нужно.

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

### `GET /api/v1/date`

Возвращает текущую дату сервера. Принимает тот же параметр `tz`, что и `/time`.
Обратите внимание: при разнице часовых поясов дата может отличаться от UTC-даты.

```bash
curl "http://127.0.0.1:8000/api/v1/date?tz=Asia/Tokyo"
```

```json
{
  "data": {
    "date": "2026-09-04",
    "year": 2026,
    "month": 9,
    "day": 4,
    "weekday": 5,
    "weekday_name": "Friday",
    "month_name": "September",
    "iso_week": 36,
    "day_of_year": 247,
    "is_leap_year": false,
    "timezone": "Asia/Tokyo"
  },
  "error": null,
  "message": "Текущая дата сервера"
}
```

### `GET /api/v1/date/{target_date}`

Возвращает календарные сведения о произвольной дате. Часовой пояс здесь не
используется — данные зависят только от самой даты.

| Параметр | Тип | Формат | Описание |
| --- | --- | --- | --- |
| `target_date` | string | `YYYY-MM-DD` | Дата, о которой нужны сведения |

```bash
curl "http://127.0.0.1:8000/api/v1/date/2024-02-29"
```

```json
{
  "data": {
    "date": "2024-02-29",
    "year": 2024,
    "month": 2,
    "day": 29,
    "weekday": 4,
    "weekday_name": "Thursday",
    "month_name": "February",
    "iso_week": 9,
    "day_of_year": 60,
    "is_leap_year": true
  },
  "error": null,
  "message": "Сведения о дате"
}
```

Несуществующая или неверно отформатированная дата даёт `400 Bad Request` с кодом
`INVALID_DATE`.

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
| `INVALID_DATE` | 400 | Дата не разобрана или не существует |
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
  services/date_service.py — логика работы с датами
  schemas.py             — Pydantic-схемы запросов и ответов
  errors.py              — доменные исключения
  main.py                — сборка приложения и обработчики ошибок
tests/                   — тесты сервиса и API
```

## Заметки по реализации

- Время всегда вычисляется в UTC и приводится к нужному поясу только при отдаче.
- `build_server_time` — чистая функция, поэтому легко тестируется на фиксированном моменте.
- Пакет `tzdata` нужен на Windows: там нет системной базы часовых поясов IANA.
