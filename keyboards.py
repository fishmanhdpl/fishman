from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from main import dp

kb_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='/help'),
            KeyboardButton(text='/stop'),
            KeyboardButton(text='/clear')
        ]
    ],
    resize_keyboard=True
)

# Keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
# b1 = KeyboardButton('/help')
# b2 = KeyboardButton('/stop')
# b3 = KeyboardButton('/clear')
# # b4 = KeyboardButton('/start')
# Keyboard.insert(b1)
# Keyboard.insert(b2)
# Keyboard.insert(b3)
# # Keyboard.insert(b4)