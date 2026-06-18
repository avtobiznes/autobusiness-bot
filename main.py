import logging
import asyncio
import os
import sqlite3
from datetime import datetime

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

load_dotenv()

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
PROXY_URL = os.environ.get("PROXY_URL")

if PROXY_URL:
    bot = Bot(token=BOT_TOKEN, proxy=PROXY_URL)
else:
    bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

DB_PATH = "applications.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS applications
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  username TEXT,
                  brand_model TEXT,
                  phone_username TEXT,
                  created_at TEXT)''')
    conn.commit()
    conn.close()

def save_application(user_id: int, username: str, brand_model: str, phone_username: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO applications (user_id, username, brand_model, phone_username, created_at) VALUES (?, ?, ?, ?, ?)",
              (user_id, username, brand_model, phone_username, datetime.now().isoformat()))
    conn.commit()
    conn.close()

class Form(StatesGroup):
    brand_model = State()
    name_phone = State()

@router.message(CommandStart())
async def start_command(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Оставьте заявку! Напишите, пожалуйста, марку или модель:")
    await state.set_state(Form.brand_model)

@router.message(Form.brand_model)
async def process_brand_model(message: types.Message, state: FSMContext):
    await state.update_data(brand_model=message.text)
    await state.set_state(Form.name_phone)
    await message.answer("Введите ваше имя и номер телефона или юзернейм:")

@router.message(Form.name_phone)
async def process_name_phone(message: types.Message, state: FSMContext):
    data = await state.get_data()
    brand_model = data.get("brand_model", "")
    name_phone = message.text
    user_id = message.from_user.id
    username = message.from_user.username or ""

    save_application(user_id, username, brand_model, name_phone)

    if CHAT_ID:
        await bot.send_message(
            CHAT_ID,
            f"📥 <b>Новая заявка из ТГ Бота!</b>\n\n"
            f"👤 <b>Пользователь:</b> {f'@{username}' if username else 'Нет username'}\n"
            f"🆔 <b>ID:</b> <code>{user_id}</code>\n\n"
            f"📱 <b>Марка/Модель:</b>\n{brand_model}\n\n"
            f"📞 <b>Имя и контакт:</b>\n{name_phone}\n\n"
            f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M')}",
            parse_mode="HTML"
        )

    await message.answer("✅ Ваша заявка отправлена! Ожидайте ответа.")
    await state.clear()

async def main():
    dp.include_router(router)
    init_db()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())