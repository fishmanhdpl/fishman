import openai,logging, time, os, sqlite3, threading
from datetime import datetime
from config import token_api
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import api_key

logging.basicConfig(level=logging.INFO)
curr_path = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(curr_path, 'dialogs.db')

connection = threading.local()
openai.api_key = api_key  # api OpenaAI
logging.basicConfig(level=logging.INFO)
bot = Bot(token_api)  # api TelegramBot
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

last_message_time = 0
directory = os.path.join(curr_path, "requests")
os.makedirs(directory, exist_ok=True)
LOG_FILE = os.path.join(directory, "user_requests.txt")
now = datetime.now()
files = os.listdir(directory)
mesage = """
<b>/launch</b> - <em>для входа в режим общения с ChatGPT</em>
<b>/help</b> - <em>для дополнительной информации</em>
<b>/stop</b> - <em>для остановки бота</em>
<b>/clear</b> - <em>для отчистки предыдущих запросов</em>"""
messagess = [
             {"role": 'system','content': "You are a useful assistant who can help answer most of the questions. Your developer's telegram account: @salttorch"},# Информация о роботе
             {'role': 'user', 'content': 'Who won the world series in 2020?'},  # Информация о пользователе
            {'role': 'assistant', 'content': '"The Los Angeles Dodgers won the World Series in 2020."'}  # ответ робота
]