import sys
from loguru import logger
from src.utils.config import settings

# Remove default handler
logger.remove()

# Console output - colourful and readable
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> — <level>{message}</level>",
    level="DEBUG" if settings.debug else "INFO",
    colorize=True,
)

# File output - rotates daily, keeps 14 days
log_path = settings.logs_dir / "app_{time:YYYY-MM-DD}.log"
logger.add(
    str(log_path),
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{line} | {message}",
    level="INFO",
    rotation="00:00",
    retention="14 days",
)

__all__ = ["logger"]