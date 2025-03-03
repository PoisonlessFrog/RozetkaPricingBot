from aiogram import Bot
from config import TELEGRAM_BOT_TOKEN

bot = Bot(token=TELEGRAM_BOT_TOKEN)

async def notify_user(chat_id, message):
    await bot.send_message(chat_id, message)
