from loguru import logger

from config import BASE_DIR


logger.add(
    f'{BASE_DIR}/logs.log',
    format="{time} | {level: <8} | {name: ^15} | {function: ^15} | {line: >3} | {message}",  # noqa: E501
    rotation="9:00",
    compression="zip",
    level="INFO",
)
