from telebot.types import Message
from sqlalchemy.sql import select

from database.connection import Session
from bot.loader import bot, sts
from bot.common.markups import *
from database import User


@bot.message_handler(commands=['start'])
async def greeting(msg: Message):
    print("ASDASDA")
    chat_id = msg.chat.id
    user_id = msg.from_user.id
    async with Session.begin() as conn:
        user = (await conn.execute(select(User).where(User.telegram_id == user_id))).scalar()

        if user is None:
            await bot.send_message(chat_id, f"Hello {msg.from_user.first_name}", reply_markup=login())
            await bot.set_state(user_id, sts.log_in, chat_id)
        else:
            await bot.send_message(chat_id, f"Welcome back {user.username}", reply_markup=menu())
            await bot.delete_state(user_id, chat_id)
