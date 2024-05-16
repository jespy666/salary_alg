from functools import wraps

from aiogram.types import Message

from utils import exceptions as e


def errors_handler(func):
    @wraps(func)
    async def wrapper(message: Message):
        try:
            return await func(message)
        except e.WrongTimeFormat:
            await message.answer(
                'The time format of the entered data does not comply with ISO'
            )
        except e.WrongGroupType:
            await message.answer(
                'Invalid sorted type'
            )
        except e.WrongInputFormat:
            await message.answer(
                'The input data cannot be interpreted as JSON'
            )
    return wrapper
