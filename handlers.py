from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from keyboards import *
from peremen import *


for file in files:
    creation_time = datetime.fromtimestamp(os.path.getctime(os.path.join(directory, file)))
    if (now - creation_time).days > 0:
        os.remove(os.path.join(directory, file))


db = sqlite3.connect(DB_PATH, check_same_thread=False)
c = db.cursor()
c.execute(
    'CREATE TABLE IF NOT EXISTS dialogs (id integer primary key, user_id TEXT DEFAULT "", question TEXT DEFAULT "", answer TEXT DEFAULT "")')


def updates(messagess, role, content):
    messagess.append({'role': role, 'content': content})
    return messagess


async def make_text(message: types.Message):
    model_engine = 'gpt-3.5-turbo'
    updates(messagess, 'user', message.text)
    response = openai.ChatCompletion.create(
    model=model_engine,
    messages=messagess
    )
    response = response['choices'][0]['message']['content']
    return response


async def save_messages_db(user_id, question, answer):
    if not hasattr(connection, 'conn'):
        connection.conn = sqlite3.connect(DB_PATH, check_same_thread=False)

    c = connection.conn.cursor()
    c.execute("INSERT INTO dialogs (user_id, question, answer) VALUES (?, ?, ?)", (user_id, question, answer))
    connection.conn.commit()


async def get_question_history_userid(user_id):
    if not hasattr(connection, 'conn'):
        connection.conn = sqlite3.connect(DB_PATH, check_same_thread=False)

    c = connection.conn.cursor()
    c.execute("SELECT question, answer FROM dialogs WHERE user_id = ?", (user_id,))
    response = c.fetchall()
    prompt = ""
    for question, answer in response:
        prompt += f"Question: {question}\nAnswer: {answer}"
    return prompt


async def clear_user_messages(user_id):
    if not hasattr(connection, 'conn'):
        connection.conn = sqlite3.connect(DB_PATH, check_same_thread=False)

    c = connection.conn.cursor()
    c.execute("DELETE FROM dialogs WHERE user_id = ?", (user_id,))
    connection.conn.commit()


class Conversation(StatesGroup):
    waiting_for_input = State()


async def save_to_file(user_id, messages):
    with open(os.path.join(directory, f"{user_id}.txt"), "a") as f:
        for message in messages:
            f.write(f"{message}\n")


@dp.message_handler(commands=["launch"])
async def cmd_start(message: types.Message, state: FSMContext):
    global last_message_time
    current_time = time.time()
    if current_time - last_message_time < 3:
        await message.answer(f'Слишком частые запросы.')
        await message.delete()
        return
    last_message_time = current_time
    user_id = str(message.from_user.id)
    user_data = await state.get_data()
    if user_id not in user_data:
        user_data[user_id] = {"username": message.from_user.username, "messages": []}
    await message.answer("<em>Введите свой вопрос, для отмены введите</em> <b>/stop</b>", parse_mode='HTML', reply_markup=kb_menu)
    await message.delete()
    await Conversation.waiting_for_input.set()


@dp.message_handler(commands='help')
async def cmd_help(message: types.Message):
    global last_message_time
    current_time = time.time()
    if current_time - last_message_time < 3:
        await message.answer(f'Слишком частые запросы.')
        await message.delete()
        return
    last_message_time = current_time
    await message.answer(
        f"<em>Я ещё сырой. На данный момент вы можете использовать меня как помощника. Если у тебя есть что предложить в плане моего улучшения, отпиши моему разработчику -  <b>@salttorch</b>\nЗапросы лучше делать на английском языке, после чего переводить.</em>", parse_mode='HTML', reply_markup=kb_menu)
    await message.delete()
    return


@dp.message_handler(commands='clear')
async def cmd_clear(message: types.Message):
    global last_message_time
    current_time = time.time()
    if current_time - last_message_time < 3:
        await message.answer(f'Слишком частые запросы. Подождите {int(current_time - last_message_time)} sec.')
        await message.delete()
        return
    last_message_time = current_time
    user_id = str(message.from_user.id)
    user_name = message.from_user.username or message.from_user.first_name or f"{message.from_user.id}"
    await clear_user_messages(user_id=str(user_id))
    await message.answer(f"<em> База предыдущих вопросов для {user_name} ({user_id}) очищена.</em>", parse_mode='HTML', reply_markup=kb_menu)
    await message.delete()
    return


@dp.message_handler()
async def echo_unrecognized(message: types.Message):
    global last_message_time
    current_time = time.time()
    if current_time - last_message_time < 3:
        await message.answer(f'Слишком частые запросы.')
        await message.delete()
        return
    last_message_time = current_time
    await message.answer(text=mesage, parse_mode='HTML')
    await message.delete()
    return


@dp.message_handler(commands=['stop'], state="*")
async def cmd_stop(message: types.Message, state: FSMContext):
    global last_message_time
    current_time = time.time()
    if current_time - last_message_time < 3:
        await message.answer(f'Слишком частые запросы.')
        await message.delete()
        return
    last_message_time = current_time
    current_state = await state.get_state()
    if current_state:
        await state.finish()
    await message.answer("<em>Общение с ChatGPT завершено</em>", parse_mode='HTML', reply_markup=kb_menu)
    await message.delete()


@dp.message_handler(state=Conversation.waiting_for_input)
async def handle_message(message: types.Message, state: FSMContext):
    global last_message_time
    current_time = time.time()
    if current_time - last_message_time < 5:
            await message.answer(f'Слишком частые запросы.')
            await message.delete()
            return


    last_message_time = current_time
    if not hasattr(connection, 'conn'):
        connection.conn = sqlite3.connect(DB_PATH, check_same_thread=False)

    user_name = message.from_user.username or message.from_user.first_name or f"{message.from_user.id}"
    user_id = message.from_user.id
    with open(LOG_FILE, "a") as f:
        f.write(f"{user_name} ({user_id}): {message.text}\n")

    user_id = str(message.from_user.id)

    user_data = await state.get_data()
    if user_id not in user_data:
        user_data[user_id] = {"username": message.from_user.username, "messages": []}
    user_data[user_id]["messages"].append(message.text)
    await save_to_file(user_id, user_data[user_id]["messages"])

    sent_message = await message.answer("Обработка запроса...")

    response = await make_text(message)

    await sent_message.edit_text(response)