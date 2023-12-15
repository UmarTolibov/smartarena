from telebot.types import Message

from bot.loader import bot


async def help_handler(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    await bot.send_message(chat_id, "Yordam yoki buglar haqida ogohlantirish uchun '' ga murojat qiling ")
