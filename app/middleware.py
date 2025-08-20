import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from .config import logger

SENSITIVE_FIELDS = {"password", "token", "secret"}


def filter_sensitive(data):
    return {k: ("***" if k in SENSITIVE_FIELDS else v) for k, v in data.items()}


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        url_vars = dict(request.query_params)
        form_data_summary = {}

        # Only inspect form fields safely
        content_type = request.headers.get("content-type", "")
        if content_type.startswith("application/x-www-form-urlencoded"):
            form_data_summary["form_data"] = (
                "Present (application/x-www-form-urlencoded)"
            )
        elif content_type.startswith("multipart/form-data"):
            form_data_summary["form_data"] = "Present (multipart/form-data)"
        elif content_type.startswith("application/json"):
            form_data_summary["form_data"] = "Present (application/json)"
        else:
            form_data_summary = {"form_data": "Not present or unsupported content type"}

        response = await call_next(request)

        process_time = round(time.time() - start_time, 4)
        content_length = response.headers.get("content-length")

        logger.bind(type="request").info(
            {
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time": process_time,
                "client": request.client.host,
                "content_length": content_length,
                "url_vars": url_vars,
                "form_data": form_data_summary,
            }
        )

        return response
