"""Точка входа FastAPI-приложения."""

import logging
from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import __version__
from app.api.v1 import router as api_v1_router
from app.errors import AppError
from app.schemas import ApiResponse, ErrorDetail

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title='Server Time API',
    description='Тестовый бэкенд, возвращающий текущее время сервера.',
    version=__version__,
    docs_url='/docs',
    openapi_url='/openapi.json',
)

app.include_router(api_v1_router)


def _error_response(status_code: int, error: ErrorDetail, message: str) -> JSONResponse:
    """Собирает ответ с ошибкой в едином формате API."""
    payload = ApiResponse[None](data=None, error=error, message=message)
    return JSONResponse(status_code=status_code, content=payload.model_dump())


@app.exception_handler(AppError)
async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
    """Преобразует доменную ошибку в ответ API."""
    logger.warning(
        'Доменная ошибка',
        extra={'code': exc.code, 'path': request.url.path, 'details': exc.details},
    )
    error = ErrorDetail(code=exc.code, message=exc.message, details=exc.details)
    return _error_response(exc.status_code, error, exc.message)


@app.exception_handler(RequestValidationError)
async def handle_validation_error(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Преобразует ошибку валидации запроса в ответ API."""
    error = ErrorDetail(
        code='VALIDATION_ERROR',
        message='Некорректные параметры запроса',
        details={'errors': exc.errors()},
    )
    return _error_response(
        HTTPStatus.UNPROCESSABLE_ENTITY,
        error,
        'Некорректные параметры запроса',
    )


@app.exception_handler(StarletteHTTPException)
async def handle_http_error(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Преобразует стандартную HTTP-ошибку в ответ API."""
    code = HTTPStatus(exc.status_code).name
    error = ErrorDetail(code=code, message=str(exc.detail), details=None)
    return _error_response(exc.status_code, error, str(exc.detail))


@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    """Логирует непредвиденную ошибку и скрывает детали от клиента."""
    logger.exception('Непредвиденная ошибка', extra={'path': request.url.path})
    error = ErrorDetail(
        code='INTERNAL_ERROR',
        message='Внутренняя ошибка сервера',
        details=None,
    )
    return _error_response(
        HTTPStatus.INTERNAL_SERVER_ERROR,
        error,
        'Внутренняя ошибка сервера',
    )
