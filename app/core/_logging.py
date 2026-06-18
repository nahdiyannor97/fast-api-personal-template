import logging
import sys
from socket import gethostname
from typing import Any

import structlog

from app.core.config import settings


def redact_sensitive_fields(_, __, event_dict) -> Any:
    """
    Redact sensitive fields in log events.
    """
    sensitive_fields = ["password", "token", "secret", "api_key", "authorization"]
    for field in sensitive_fields:
        if field in event_dict:
            event_dict[field] = "[REDACTED]"
    return event_dict


def add_app_context(_, __, event_dict) -> Any:
    """
    Add application context (project name, environment, hostname) to log events.
    """
    event_dict["app_name"] = settings.project_name
    event_dict["environment"] = settings.environment
    event_dict["hostname"] = gethostname()
    return event_dict


def filter_callsite_info(_, __, event_dict) -> Any:
    """
    Filter out callsite information from log events unless the level is 'error'.
    """
    if event_dict.get("level") != "error":
        event_dict.pop("lineno", None)
    return event_dict


def configure_structlog() -> None:
    """
    Configure structlog for structured logging with JSON format.
    """
    structlog.configure_once(
        processors=[
            structlog.contextvars.merge_contextvars,
            redact_sensitive_fields,
            add_app_context,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.CallsiteParameterAdder(
                {
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.LINENO,
                }
            ),
            filter_callsite_info,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def add_console_handler(root_logger) -> None:
    """
    Add a console handler to the root logger for colored stream output.
    """
    console_handler = logging.StreamHandler(stream=sys.stderr)
    console_handler.setFormatter(
        fmt=structlog.stdlib.ProcessorFormatter(
            processor=structlog.dev.ConsoleRenderer(colors=True)
        )
    )
    root_logger.addHandler(console_handler)


def add_file_handler(root_logger) -> None:
    """
    Add a file handler to the root logger that rotates hourly.
    """
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename="./logs/app.log",
        when="H",
        interval=1,
        backupCount=48,
        encoding="utf-8",
    )
    file_handler.setFormatter(
        fmt=structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.JSONRenderer(sort_keys=True)
        )
    )
    root_logger.addHandler(file_handler)


def get_structlog_logger(name: str | None = None) -> Any:
    """
    Initialize and return a structlog logger with both console and file handlers.
    """
    root_logger = logging.getLogger(name=name)
    root_logger.setLevel(level=logging.INFO)
    root_logger.handlers.clear()
    root_logger.propagate = False

    add_console_handler(root_logger=root_logger)
    add_file_handler(root_logger=root_logger)

    return structlog.getLogger(name)


configure_structlog()
logger = get_structlog_logger(name=__name__)
