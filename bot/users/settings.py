from sqlalchemy import select, update
from telebot.types import Message
from werkzeug.security import generate_password_hash, check_password_hash

from bot.loader import bot, user_sts, settings_sts, auth_sts
from database import Session, User
from .markups.buttons import *


# regexp="⚙️Sozlanmalar"
async def settings_handler(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    await bot.send_message(chat_id, "Sozlanmalar:", reply_markup=account_settings_markup())
    await bot.set_state(user_id, settings_sts.init, chat_id)


# regexp="✏️Username", state=settings_sts.init
async def settings_username(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    await bot.send_message(chat_id, "yangi *Username*ni jo'nating")
    await bot.set_state(user_id, settings_sts.username, chat_id)


# content_types=["text"],state=settings_sts.username
async def settings_set_username(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    new_username = message.text
    try:
        async with bot.retrieve_data(user_id, chat_id) as data:
            tg_user = data["user_id"]
            db_user_query = update(User).where(User.id == tg_user).values(username=new_username)

        async with Session.begin() as db:
            await db.execute(db_user_query)
            await db.commit()
        await bot.send_message(chat_id, "Username yangilandi")
        await bot.set_state(user_id, settings_sts.init, chat_id)

    except Exception as e:
        await bot.send_message(chat_id, "Hatolik boldi", reply_markup=login_signup())
        await bot.set_state(user_id, auth_sts.init, chat_id)


# regexp="✏️Password", state=settings_sts.init
async def settings_password(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    await bot.send_message(chat_id, "Eski parolni kiriting")
    await bot.set_state(user_id, settings_sts.old_password, chat_id)


# content_types=["text"],state=settings_sts.old_password
async def settings_old_password(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    old_password = message.text
    async with bot.retrieve_data(user_id, chat_id) as data:
        query = select(User.password).where(User.id == data["user_id"])
    async with Session.begin() as db:
        password = (await db.execute(query)).scalar()
        password_check = check_password_hash(password, old_password)
        if password_check:
            await bot.send_message(chat_id, "Yangi parolni jo'nating")
            await bot.set_state(user_id, settings_sts.new_password, chat_id)
        else:
            await bot.send_message(chat_id, "Parol noto'gri qaytadan urinib ko'ring")


# content_types=["text"],state=settings_sts.new_password
async def settings_new_password(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    new_password = generate_password_hash(message.text)
    async with bot.retrieve_data(user_id, chat_id) as data:
        q = update(User).where(User.id == data["user_id"]).values(password=new_password)
    async with Session.begin() as db:
        await db.execute(q)
        await db.commit()
    await bot.send_message(chat_id, "Parol yangilandi", reply_markup=account_settings_markup())
    await bot.set_state(user_id, settings_sts.init, chat_id)
