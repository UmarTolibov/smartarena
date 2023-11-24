from telebot.types import Message
from sqlalchemy.sql import select, update

from database.connection import Session
from bot.loader import bot, sts, reg_state
from bot.keyboards.default import *
from database import User, UserSessions
from bot.common.bot_config import __


@bot.message_handler(commands=['start'])
async def greeting(msg: Message):
    chat_id = msg.chat.id
    user_id = msg.from_user.id
    async with Session.begin() as db:
        tg_user = (await db.execute(select(UserSessions).where(UserSessions.telegram_id == user_id))).scalar()
        db_user = (await db.execute(select(User).where(User.id == tg_user.user_id))).scalar()
        if tg_user is None:
            await bot.send_message(chat_id, f"Hello {msg.from_user.first_name}", reply_markup=registrate())
            await bot.set_state(user_id, reg_state.register, chat_id)
        elif tg_user and not tg_user.logged:
            await bot.send_message(chat_id, f"Hello {msg.from_user.first_name}", reply_markup=login())
            await bot.set_state(user_id, sts.log_in, chat_id)
        else:
            await bot.send_message(chat_id, f"Welcome back {db_user.username}",
                                   reply_markup=main_menu(lang=db_user.lang))
            await bot.delete_state(user_id, chat_id)


@bot.message_handler(commands=["logout"])
async def logout(msg: Message):
    chat_id = msg.chat.id
    user_id = msg.from_user.id

    async with Session.begin() as db:
        tg_user_query = select(UserSessions).where(UserSessions.telegram_id == user_id)
        tg_user = (await db.execute(tg_user_query)).scalar()
        db_user_query = select(User).where(User.id == tg_user.id)
        db_user = (await db.execute(db_user_query)).scalar()
        if tg_user.logged:
            query = update(UserSessions).where(UserSessions.telegram_id == user_id).values(logged=False)
            await db.execute(query)
            await db.commit()
            await bot.send_message("Logged out!", reply_markup=login(), reply_to_message_id=msg.message_id)
            await bot.set_state(user_id, sts.log_in, chat_id)
        else:
            await bot.send_message("You are not logged in", reply_markup=login(), reply_to_message_id=msg.message_id)
