import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from config import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

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
            }
        )

        return response
