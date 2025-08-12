import os
import sys
import json

from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

PROJ_ROOT = Path(__file__).resolve().parents[1]
LOGS_DIR = os.getenv("LOGS_DIR", PROJ_ROOT / "logs")
ASSETS_DIR = os.getenv("ASSETS_DIR", PROJ_ROOT / "assets")
MODELS_DIR = os.getenv("MODELS_DIR", PROJ_ROOT / "models")


def _format_message(record):
    # process record to generate
    t = record["time"]
    level = record["level"]

    name = record["name"]
    function = record["function"]
    line = record["line"]

    message = record["message"]

    # escape tags in message, tags are "<some_tag>"
    if function.startswith("<") and function.endswith(">"):
        function = rf"\{function}"

    message = message.replace("{", "{{").replace("}", "}}")

    # strip the path to the project root and replace it with a dot for brevity in both file and message
    message = message.replace(str(PROJ_ROOT), ".")

    final = (
        f"<green>{t:YYYY-MM-DD HH:mm:ss.SSS!UTC}</green> | "
        f"<level>{level: <8}</level> | "
        f"<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

    if extra := record["extra"]:
        extra = json.dumps(extra)
        extra = extra.replace("{", "{{").replace("}", "}}").replace('"', "")
        final += f" | <level>{extra}</level>\n"
    else:
        final += "\n"

    return final


def _request_serialize(record):
    if type(record["message"]) is not str:
        # If the message is not a string, we assume it's a dictionary
        record["message"] = json.dumps(record["message"])

    # Convert the message to a JSON object
    # and replace single quotes with double quotes for valid JSON
    if isinstance(record["message"], str):
        record["message"] = record["message"].replace("'", '"')
    if not record["message"].startswith("{"):
        # If the message is not a JSON object, we assume it's a string
        record["message"] = json.dumps({"message": record["message"]})

    # Create a log object with the time and message
    try:
        record["message"] = json.loads(record["message"])
    except json.JSONDecodeError:
        # If the message is not a valid JSON, we log it as a string
        record["message"] = {"message": record["message"]}

    if not isinstance(record["message"], dict):
        # If the message is not a dictionary, we convert it to a dictionary
        record["message"] = {"message": record["message"]}

    return _log_serialize(record)


def _log_serialize(record):
    log_object = {
        "time": f"{record['time']:YYYY-MM-DD HH:mm:ss.SSS!UTC}",
        "level": record["level"].name,
        "name": record["name"],
        "function": record["function"],
        "line": record["line"],
        "message": record["message"],
        "extra": record["extra"],
    }
    return json.dumps(log_object)


def _json_message(record):
    if record["extra"].get("type") != "request":
        record["extra"]["serialized"] = _log_serialize(record)
    else:
        record["extra"]["serialized"] = _request_serialize(record)
    return "{extra[serialized]}\n"


logger.remove(0)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# If tqdm is installed, configure loguru with tqdm.write
# https://github.com/Delgan/loguru/issues/135
try:
    from tqdm import tqdm

    logger.add(
        lambda msg: tqdm.write(msg, end=""),
        format=_format_message,
        colorize=True,
        level=LOG_LEVEL,
        filter=lambda record: record["extra"].get("type") != "request",
    )
except ModuleNotFoundError:
    logger.add(sys.stderr, format=_format_message, colorize=True, level=LOG_LEVEL)

# Request log file (only logs tagged with type="request")
logger.add(
    LOGS_DIR / "requests.log",
    format=_json_message,
    rotation="5 MB",
    retention="14 days",
    compression="zip",
    filter=lambda record: record["extra"].get("type") == "request",
    colorize=False,
    serialize=False,
)

# System log file (anything NOT tagged as "request")
logger.add(
    LOGS_DIR / "system.log",
    format=_json_message,
    rotation="10 MB",
    retention="7 days",
    compression="zip",
    filter=lambda record: record["extra"].get("type") != "request",
    colorize=False,
    serialize=False,
)

logger.info(f"LOG_LEVEL is: {LOG_LEVEL}")

# Paths
logger.info(f"PROJ_ROOT path is: {PROJ_ROOT}")
logger.info(f"LOGS_DIR path is: {LOGS_DIR}")
logger.info(f"MODELS_DIR path is: {MODELS_DIR}")

NUM_WORKERS = int(os.getenv("NUM_WORKERS", 2))
