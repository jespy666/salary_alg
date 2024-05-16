import asyncio

from loguru import logger

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Message


from bot.wrappers import errors_handler
from utils.aggregator import SalaryAggregator

from config import BOT_TOKEN


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

router = Router()


@router.message(Command('start'))
async def start(message: Message) -> None:
    logger.info('User: {} tap a start command', message.from_user.id)
    await message.answer('Hello, there is a start command')


@router.message()
@errors_handler
async def handle(message: Message) -> None:
    request = message.text
    logger.info(
        'User: {} send a new message: {}',
        message.from_user.id,
        request,
    )
    agr = SalaryAggregator(request)
    response: dict = await agr.get_response()
    await message.answer(str(response))


dp.include_router(router)


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        logger.success('Bot starts')
        asyncio.run(main())
    finally:
        logger.critical('Bot has been shutdown')
