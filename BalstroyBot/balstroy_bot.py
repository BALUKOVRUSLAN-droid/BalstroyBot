print("🚀 БАЛСТРОЙ ПРОДАЮЩИЙ БОТ!")
import asyncio
import sqlite3
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

BOT_TOKEN = "8482592973:AAG0NbbGvs4Hf_GgfAL16smD9_OGYgb_wPg"
ADMIN_ID = 566254565
AVITO_URL = "https://www.avito.ru/brands/f707e786468e325dd4b7ada38832c0e7/all?sellerId=7e5f44c8bc596cfe2ac22cddcbc4475c"
CHANNEL_URL = "https://t.me/balstroy10"
PHONE = "+7 906 206-53-50"

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

def get_main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Все лестницы Авито", url=AVITO_URL)],
        [InlineKeyboardButton(text="🎁 Акция -15% СЕЙЧАС", callback_data="sale")],
        [InlineKeyboardButton(text="📐 КАЛЬКУЛЯТОР ЦЕНЫ", callback_data="calculator")],
        [InlineKeyboardButton(text="📞 МЕНЕДЖЕР 15мин", callback_data="manager")],
        [InlineKeyboardButton(text="👥 Отзывы 5⭐ (34)", url=CHANNEL_URL)]
    ])

def get_materials_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("🔩 Металл+Дерево", callback_data="mat_metal_wood")],
        [InlineKeyboardButton("🔩 Только Металл", callback_data="mat_metal")],
        [InlineKeyboardButton("🌳 Только Дерево", callback_data="mat_wood")],
        [InlineKeyboardButton("🔙 Главное меню", callback_data="back_main")]
    ])

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        "🔨 <b>БАЛСТРОЙ | Лестницы под ключ</b>\n\n"
        "✅ <b>34 отзыва 5⭐ на Авито</b>\n"
        "✅ Металл+дерево от 25 000₽\n"
        "✅ <b>СКИДКА 15% до 15 февраля</b>\n"
        "✅ Доставка + монтаж\n\n"
        "⚡ <b>Выберите действие:</b>", 
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "sale")
async def sale_callback(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("💰 КАЛЬКУЛЯТОР СКИДКИ", callback_data="calculator")],
        [InlineKeyboardButton("📞 ЗАКАЗАТЬ СКИДКУ", callback_data="manager")],
        [InlineKeyboardButton("🏠 Все лестницы", url=AVITO_URL)]
    ])
    await callback.message.edit_text(
        "🎉 <b>СУПЕР АКЦИЯ -15%!</b>\n\n"
        "⏰ <b>До 15 февраля 2026</b>\n\n"
        "💰 Прямые от 21 250₽ (было 25к)\n"
        "💰 Винтовые от 38 250₽ (было 45к)\n\n"
        "<b>⚡ Осталось 17 дней!</b>",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await callback.answer()

@dp.callback_query(F.data == "calculator")
async def calculator_start(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(OrderStates.waiting_height)
    await callback.message.edit_text(
        "📐 <b>КАЛЬКУЛЯТОР ЛЕСТНИЦЫ</b>\n\n"
        "📏 Введите высоту проема (метры):\n"
        "<i>Пример: 2.7 или 3.2</i>",
        parse_mode="HTML"
    )
    await callback.answer()

@dp.message(OrderStates.waiting_height)
async def process_height(message: types.Message, state: FSMContext):
    try:
        height = float(message.text.replace(',', '.'))
        await state.update_data(height=height)
        await state.set_state(OrderStates.waiting_width)
        await message.answer(
            "📐 Ширина марша (метры):\n"
            "<i>Пример: 1.0 или 1.2</i>",
            parse_mode="HTML"
        )
    except:
        await message.answer("❌ Введите число! Пример: 2.7")

@dp.message(OrderStates.waiting_width)
async def process_width(message: types.Message, state: FSMContext):
    try:
        width = float(message.text.replace(',', '.'))
        await state.update_data(width=width)
        await state.set_state(OrderStates.waiting_material)
        await message.answer("🔩 Выберите материал:", reply_markup=get_materials_kb())
    except:
        await message.answer("❌ Введите число! Пример: 1.0")

@dp.callback_query(F.data.startswith("mat_"))
async def process_material(callback: types.CallbackQuery, state: FSMContext):
    material = callback.data.split("_")[1]
    await state.update_data(material=material)
    await state.set_state(OrderStates.waiting_phone)
    
    data = await state.get_data()
    price = data['height'] * data['width'] * 15000 * (1.2 if material == "metal_wood" else 1.0 if material == "metal" else 1.5)
    
    await callback.message.edit_text(
        f"💰 <b>ПРЕДВАРИТЕЛЬНАЯ СМЕТА</b>\n\n"
        f"📏 Высота: {data['height']}м\n"
        f"📐 Ширина: {data['width']}м\n"
        f"🔩 Материал: {material.replace('_','+').title()}\n\n"
        f"💵 Стоимость: {price:,.0f} ₽\n"
        f"🎁 <b>Со скидкой 15%: {price*0.85:,.0f} ₽</b>\n\n"
        f"📞 Оставьте телефон для точного расчета:",
        parse_mode="HTML"
    )
    await callback.answer()

@dp.message(OrderStates.waiting_phone)
async def process_phone(message: types.Message, state: FSMContext):
    data = await state.get_data()
    price = data['height'] * data['width'] * 15000 * (1.2 if data['material'] == "metal_wood" else 1.0 if data['material'] == "metal" else 1.5)
    
    cursor.execute("INSERT INTO leads VALUES (NULL, ?, ?, ?, ?, 'hot_lead', ?)", 
                   (message.from_user.id, message.from_user.username or "no_name", message.text, str(data), datetime.now().isoformat()))
    conn.commit()
    
    await bot.send_message(ADMIN_ID, 
        f"🔥 <b>ГОРЯЧИЙ ЛИД!</b>\n\n"
        f"👤 @{message.from_user.username or 'no_name'}\n"
        f"🆔 {message.from_user.id}\n"
        f"📏 {data['height']}x{data['width']}м\n"
        f"🔩 {data['material'].replace('_','+')}\n"
        f"💰 {price*0.85:,.0f}₽\n"
        f"📞 {message.text}",
        parse_mode="HTML"
    )
    
    await message.answer(
        f"✅ <b>СМЕТА ОТПРАВЛЕНА!</b>\n\n"
        f"📞 Менеджер перезвонит <b>за 15 минут</b>\n\n"
        f"💰 <b>ИТОГО: {price*0.85:,.0f} ₽</b>",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )
    await state.clear()

@dp.callback_query(F.data == "manager")
async def manager_callback(callback: types.CallbackQuery):
    cursor.execute("INSERT INTO leads VALUES (NULL, ?, ?, ?, ?, 'manager', ?)", 
                   (callback.from_user.id, callback.from_user.username or "no_name", PHONE, "", datetime.now().isoformat()))
    conn.commit()
    
    await bot.send_message(ADMIN_ID, 
        f"📞 <b>ЗАЯВКА МЕНЕДЖЕР!</b>\n\n"
        f"👤 @{callback.from_user.username or 'no_name'}\n"
        f"🆔 {callback.from_user.id}\n"
        f"📱 {PHONE}"
    )
    
    await callback.message.edit_text(
        f"✅ <b>ЗАЯВКА ПРИНЯТА!</b>\n\n"
        f"📞 Перезвоню с <b>{PHONE}</b>\n"
        f"⏰ Будни 9:00-21:00",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )
    await callback.answer()

@dp.callback_query(F.data == "back_main")
async def back_main(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🔨 <b>БАЛСТРОЙ | Главное меню</b>",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )
    await callback.answer()

async def main():
    print("🚀 БАЛСТРОЙ БОТ 100% ГОТОВ!")
    print(f"✅ Админ: {ADMIN_ID}")
    print(f"✅ Телефон: {PHONE}")
    print("📱 ИДИТЕ В TELEGRAM: /start")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        conn.close()
