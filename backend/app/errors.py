"""RFC 7807 Problem Details Error Contracts and Exception Handlers.

Ensures all API errors follow a predictable, RFC 7807 compliant structure
with request correlation IDs, ISO 8601 timestamps, and typed fields.
"""

import datetime

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.logging import correlation_id_ctx, logger


class ErrorFieldDetail(BaseModel):
    """Specific field-level validation error."""

    field: str | None = None
    message: str
    code: str | None = None


class ProblemDetails(BaseModel):
    """RFC 7807 Problem Details model."""

    type: str = Field(
        default="about:blank", description="URI reference identifying the problem type"
    )
    title: str = Field(description="Short human-readable summary of problem")
    status: int = Field(description="HTTP status code")
    detail: str = Field(description="Human-readable explanation specific to this occurrence")
    instance: str | None = Field(
        default=None, description="URI reference of this specific occurrence"
    )
    request_id: str = Field(description="Correlation ID for tracing this request in logs")
    timestamp: str = Field(description="ISO 8601 UTC timestamp of error occurrence")
    errors: list[ErrorFieldDetail] | None = Field(default=None, description="Detailed field errors")


class AppException(Exception):
    """Base application exception for domain errors."""

    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        title: str = "Internal Server Error",
        detail: str = "An unexpected domain error occurred.",
        type_uri: str = "about:blank",
        errors: list[ErrorFieldDetail] | None = None,
    ) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.title = title
        self.detail = detail
        self.type_uri = type_uri
        self.errors = errors


def register_error_handlers(app: FastAPI) -> None:
    """Register RFC 7807 exception handlers on the FastAPI application."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        req_id = correlation_id_ctx.get()
        problem = ProblemDetails(
            type=exc.type_uri,
            title=exc.title,
            status=exc.status_code,
            detail=exc.detail,
            instance=str(request.url.path),
            request_id=req_id,
            timestamp=datetime.datetime.now(datetime.UTC).isoformat(),
            errors=exc.errors,
        )
        logger.warning(
            f"AppException: {exc.title} ({exc.status_code}) - {exc.detail}",
            extra={"extra_fields": {"status_code": exc.status_code, "path": str(request.url.path)}},
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=problem.model_dump(),
            headers={"Content-Type": "application/problem+json"},
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        req_id = correlation_id_ctx.get()
        title_map = {
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            409: "Conflict",
            422: "Unprocessable Entity",
            500: "Internal Server Error",
            503: "Service Unavailable",
        }
        title = title_map.get(exc.status_code, "HTTP Error")
        problem = ProblemDetails(
            type="about:blank",
            title=title,
            status=exc.status_code,
            detail=str(exc.detail),
            instance=str(request.url.path),
            request_id=req_id,
            timestamp=datetime.datetime.now(datetime.UTC).isoformat(),
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=problem.model_dump(),
            headers={"Content-Type": "application/problem+json"},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        req_id = correlation_id_ctx.get()
        field_errors: list[ErrorFieldDetail] = []
        for err in exc.errors():
            loc = " -> ".join(str(item) for item in err.get("loc", []))
            field_errors.append(
                ErrorFieldDetail(
                    field=loc,
                    message=err.get("msg", "Validation error"),
                    code=err.get("type", "value_error"),
                )
            )

        problem = ProblemDetails(
            type="https://api.sambal.gov.in/errors/validation-error",
            title="Request Validation Error",
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The incoming request failed schema validation.",
            instance=str(request.url.path),
            request_id=req_id,
            timestamp=datetime.datetime.now(datetime.UTC).isoformat(),
            errors=field_errors,
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=problem.model_dump(),
            headers={"Content-Type": "application/problem+json"},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        req_id = correlation_id_ctx.get()
        logger.exception(f"Unhandled exception on {request.method} {request.url.path}: {exc}")
        problem = ProblemDetails(
            type="about:blank",
            title="Internal Server Error",
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected internal server error occurred. Our team has been notified.",
            instance=str(request.url.path),
            request_id=req_id,
            timestamp=datetime.datetime.now(datetime.UTC).isoformat(),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=problem.model_dump(),
            headers={"Content-Type": "application/problem+json"},
        )
