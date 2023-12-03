from telebot.types import Message

from bot.loader import bot


@bot.message_handler(regexp="ℹ️Yordam")
@bot.message_handler(commands=['help'])
async def help_handler(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    await bot.send_message(chat_id, "Yordam yoki buglar haqida ogohlantirish uchun '' ga murojat qiling ")