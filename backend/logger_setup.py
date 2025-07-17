import logging
import json
import sys
import os

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "level": record.levelname,
            "message": record.getMessage(),
            "time": self.formatTime(record, self.datefmt),
            "name": record.name,
        }

        # Incluir datos extra si están presentes
        if hasattr(record, "extra_data"):
            log_record["extra"] = record.extra_data

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_record)


class CustomLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        extra = kwargs.get("extra", {})
        kwargs["extra"] = {"extra_data": extra}
        return msg, kwargs


def get_logger(name: str = "app") -> logging.Logger:
    base_logger = logging.getLogger(name)

    if not any(isinstance(h, logging.StreamHandler) for h in base_logger.handlers):
        handler = logging.StreamHandler(sys.stderr)
        formatter = JsonFormatter()
        handler.setFormatter(formatter)

        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        base_logger.setLevel(log_level)
        handler.setLevel(log_level)

        base_logger.addHandler(handler)
        base_logger.propagate = False

    return CustomLoggerAdapter(base_logger, {})
