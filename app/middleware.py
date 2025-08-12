import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from config import logger

SENSITIVE_FIELDS = {"password", "token", "secret"}


def filter_sensitive(data):
    return {k: ("***" if k in SENSITIVE_FIELDS else v) for k, v in data.items()}


def summarize_upload_file(upload_file):
    return {
        "filename": upload_file.filename,
        "size": upload_file.size,
        "content_type": upload_file.content_type,
    }


class RequestLoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Extract URL variables
        url_vars = dict(request.query_params)

        # Extract form data if present
        form_data = {}
        if request.headers.get("content-type", "").startswith(
            ("application/x-www-form-urlencoded", "multipart/form-data")
        ):
            form = await request.form()
            form_data = filter_sensitive(dict(form))

        # Process the request
        response = await call_next(request)

        process_time = round(time.time() - start_time, 4)
        content_length = response.headers.get("content-length")

        # Structured log for requests
        logger.bind(type="request").info(
            {
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time": process_time,
                "client": request.client.host,
                "content_length": content_length,
                "url_vars": url_vars,
                "form_data": {
                    k: summarize_upload_file(v) if hasattr(v, "filename") else v
                    for k, v in form_data.items()
                },
            }
        )

        return response
