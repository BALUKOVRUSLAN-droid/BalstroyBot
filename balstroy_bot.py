print("🚀 БАЛСТРОЙ ПРОДАЮЩИЙ БОТ!")
import asyncio
import os
import sqlite3
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "566254565"))
AVITO_URL = os.getenv("AVITO_URL", "https://www.avito.ru/brands/f707e786468e325dd4b7ada38832c0e7/all?sellerId=7e5f44c8bc596cfe2ac22cddcbc4475c")
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/balstroy10")
PHONE = os.getenv("PHONE", "+7 906 206-53-50")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

conn = sqlite3.connect('leads.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS leads (id INTEGER PRIMARY KEY, user_id INTEGER, username TEXT, phone TEXT, params TEXT, status TEXT, created TEXT)''')
conn.commit()

class OrderStates(StatesGroup):
    waiting_height = State()
    waiting_width = State()
    waiting_material = State()
    waiting_phone = State()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📞 Заказать лестницу", callback_data="order_stairs")],
        [InlineKeyboardButton(text="📱 Связаться с менеджером", callback_data="contact_manager")],
        [InlineKeyboardButton(text="🔗 Наш Avito", url=AVITO_URL)],
        [InlineKeyboardButton(text="📢 Канал Балстрой", url=CHANNEL_URL)]
    ])
    await message.answer(
        "🏠 Добро пожаловать в Балстрой!\n\n"
        "Мы изготавливаем лестницы любой сложности под ключ!\n\n"
        "Выберите действие:", reply_markup=keyboard
    )

async def on_startup(bot):
    webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_URL')}/webhook"
    print(f"🚀 Устанавливаем webhook: {webhook_url}")
    await bot.set_webhook(webhook_url)
    print("✅ Webhook установлен!")

async def on_shutdown(bot):
    print("🛑 Удаляем webhook...")
    await bot.delete_webhook()
    print("✅ Webhook удален!")

async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
    setup_application(app, dp, bot=bot)
    
    port = int(os.getenv("PORT", 10000))
    host = "0.0.0.0"
    
    print(f"🚀 Запуск сервера на {host}:{port}")
    await web._run_app(app, host=host, port=port)

if __name__ == "__main__":
    asyncio.run(main())
