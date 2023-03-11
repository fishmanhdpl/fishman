import asyncio
from aiogram import Bot, Dispatcher, executor
from config import token_api, api_key
from aiogram.contrib.fsm_storage.memory import MemoryStorage

openai_key = api_key
storage = MemoryStorage()
loop = asyncio.new_event_loop()
bot = Bot(token_api, parse_mode='HTML')
dp = Dispatcher(bot, storage=storage)


if __name__ == '__main__':
    from handlers import dp
    executor.start_polling(dp, skip_updates=True)