import re
import time
import json

from fastapi import Request
from urllib.parse import parse_qs
from starlette.middleware.base import BaseHTTPMiddleware

from ..config import logger

SENSITIVE_FIELDS = {"password", "token", "secret"}


def filter_sensitive(data):
    if isinstance(data, dict):
        return {
            k: ("***" if k in SENSITIVE_FIELDS else filter_sensitive(v))
            for k, v in data.items()
        }
    return data


class MultipartParser:
    @staticmethod
    def parse_multipart_form_data(body: bytes, content_type: str):
        """Parse multipart/form-data manually with improved boundary handling"""
        # Extract boundary from content-type
        boundary_match = re.search(r"boundary=([^;]+)", content_type)
        if not boundary_match:
            raise ValueError("No boundary found in content-type")

        boundary = boundary_match.group(1).strip('"')
        boundary_line = b"--" + boundary.encode()
        end_boundary = boundary_line + b"--"

        # Split body by boundary lines
        body_str = body.decode("latin-1")  # Use latin-1 to preserve binary data
        parts = body_str.split(boundary_line.decode())

        parsed_parts = []

        for part in parts:
            part = part.strip()
            if not part or part.endswith("--"):  # Skip empty parts and end boundary
                continue

            # Split headers from content
            if "\r\n\r\n" in part:
                headers_str, content = part.split("\r\n\r\n", 1)
            else:
                headers_str, content = part, ""

            # Parse headers
            headers = {}
            for header_line in headers_str.split("\r\n"):
                if ":" in header_line:
                    header_name, header_value = header_line.split(":", 1)
                    headers[header_name.strip()] = header_value.strip()

            parsed_parts.append(
                {
                    "headers": headers,
                    "content": content.encode("latin-1"),  # Convert back to bytes
                }
            )

        return parsed_parts

    @staticmethod
    def extract_form_data_from_parts(parts):
        """Extract form field data from multipart parts."""
        form_data = {}

        for part in parts:
            headers = part.get("headers", {})
            content_disposition = headers.get("Content-Disposition", "")

            if not content_disposition or "form-data" not in content_disposition:
                continue

            # Parse content disposition parameters
            field_name = None
            filename = None

            # Extract parameters from content disposition
            params = content_disposition.split(";")
            for param in params:
                param = param.strip()
                if param.startswith("name="):
                    field_name = param[5:].strip("\"'")
                elif param.startswith("filename="):
                    filename = param[9:].strip("\"'")

            if field_name:
                content = part.get("content", b"")

                if filename:
                    # It's a file upload - always store as list
                    file_info = {
                        "filename": filename,
                        "content_type": headers.get(
                            "Content-Type", "application/octet-stream"
                        ),
                        "size": len(content),
                        "type": "file",
                    }

                    # If field already exists, append to the list
                    if field_name in form_data:
                        # If it's already a list, append to it
                        if isinstance(form_data[field_name], list):
                            form_data[field_name].append(file_info)
                        # If it's a single file (from previous iteration), convert to list
                        elif (
                            isinstance(form_data[field_name], dict)
                            and form_data[field_name].get("type") == "file"
                        ):
                            existing_file = form_data[field_name]
                            form_data[field_name] = [existing_file, file_info]
                        # If it's some other type, create a new list (shouldn't happen normally)
                        else:
                            form_data[field_name] = [file_info]
                    else:
                        # First file for this field - start with a list
                        form_data[field_name] = [file_info]
                else:
                    # It's a regular form field - decode content
                    try:
                        # Remove trailing \r\n if present (common in multipart)
                        content_str = content.decode("utf-8").strip()
                        if content_str.endswith("\r\n"):
                            content_str = content_str[:-2]
                        elif content_str.endswith("\n"):
                            content_str = content_str[:-1]

                        form_data[field_name] = content_str
                    except UnicodeDecodeError:
                        # If it's not valid UTF-8, treat as binary data
                        form_data[field_name] = f"Binary data ({len(content)} bytes)"

        return form_data


class RequestLoggingMiddleware(BaseHTTPMiddleware):

    async def _parse_form_data(self, request: Request, body: bytes):
        content_type = request.headers.get("content-type", "")

        if not body:
            return "No body"

        try:
            if content_type.startswith("application/x-www-form-urlencoded"):
                # Parse URL-encoded form data
                form_data = parse_qs(body.decode("utf-8"))
                # Convert lists to single values for simplicity
                simplified = {
                    k: v[0] if len(v) == 1 else v for k, v in form_data.items()
                }
                return filter_sensitive(simplified)

            elif content_type.startswith("application/json"):
                # Parse JSON data
                json_data = json.loads(body.decode("utf-8"))
                return filter_sensitive(json_data)

            elif content_type.startswith("multipart/form-data"):
                # Parse multipart form data with boundary handling
                parts = MultipartParser.parse_multipart_form_data(body, content_type)
                form_data = MultipartParser.extract_form_data_from_parts(parts)

                # Format for logging - summarize files, show regular fields
                formatted_data = {}
                for field_name, value in form_data.items():
                    # Files are already lists, so no special handling needed
                    formatted_data[field_name] = value

                return filter_sensitive(formatted_data)

            else:
                # For other content types, just show basic info
                if len(body) > 1024:  # 1KB limit for logging
                    return f"Body data ({len(body)} bytes - truncated)"
                try:
                    return f"Body: {body.decode('utf-8')[:500]}..."
                except UnicodeDecodeError:
                    return f"Binary data ({len(body)} bytes)"

        except Exception as e:
            return f"Error parsing form data: {str(e)}"

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Store original body for potential re-use
        body = await request.body()

        # Parse form data from raw body for logging
        form_data_summary = await self._parse_form_data(request, body)

        # Create a new request with the original body to avoid consumption issues
        request = Request(request.scope, request.receive)
        setattr(request, "_body", body)  # Store body for potential re-use

        response = await call_next(request)

        process_time = round(time.time() - start_time, 4)
        content_length = response.headers.get("content-length")
        url_vars = dict(request.query_params)

        logger.bind(type="request").info(
            {
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time": process_time,
                "client": request.client.host if request.client else None,
                "content_length": content_length,
                "url_vars": url_vars,
                "form_data": form_data_summary,
            }
        )

        return response
