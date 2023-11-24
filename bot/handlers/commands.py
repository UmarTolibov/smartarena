from telebot.types import Message
from sqlalchemy.sql import select, update

from database.connection import Session
from bot.loader import bot, sts
from bot.common.markups import *
from database import User


@bot.message_handler(commands=['start'])
async def greeting(msg: Message):
    chat_id = msg.chat.id
    user_id = msg.from_user.id
    async with Session.begin() as conn:
        user = (await conn.execute(select(User).where(User.telegram_id == user_id))).scalar()

        if user is None or not user.logged:
            await bot.send_message(chat_id, f"Hello {msg.from_user.first_name}", reply_markup=login())
            await bot.set_state(user_id, sts.log_in, chat_id)
        else:
            await bot.send_message(chat_id, f"Welcome back {user.username}", reply_markup=menu())
            await bot.delete_state(user_id, chat_id)


@bot.message_handler(commands=["logout"])
async def logout(msg: Message):
    chat_id = msg.chat.id
    user_id = msg.from_user.id

    async with Session.begin() as db:
        user = (await db.execute(select(User).where(User.telegram_id == user_id))).scalar()
        query = update(User).where(User.telegram_id == user_id).values(telegram_id=0, logged=False)
    await bot.send_message("Logged out!", reply_markup=login(), reply_to_message_id=msg.message_id)
