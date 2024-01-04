import io
import json

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from telebot.asyncio_handler_backends import ContinueHandling
from telebot.types import Message
from bot.loader import bot
from database import Stadium, Order, Session, User
from .markups.buttons import *


# regexp="👨‍💻Admin", is_admin=True
async def admin_menu_(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    async with bot.retrieve_data(user_id, chat_id) as data:
        admin = data["is_admin"]
    if admin:
        await bot.send_message(chat_id, "Admin menu:", reply_markup=admin_menu_markup())
    else:
        return ContinueHandling()


# regexp="Foydalanuvchilar👥"
async def admin_menu_users(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    q = select(User)
    async with bot.retrieve_data(user_id, chat_id) as data:
        admin = data["is_admin"]
    if admin:
        async with Session.begin() as db:
            orders = (await db.execute(q)).scalars().all()
            data = json.dumps(jsonable_encoder(orders))
            file = io.BytesIO(data.encode())
            file.name = "users.json"
            await bot.send_chat_action(chat_id, "UPLOAD_DOCUMENT")
            await bot.send_document(chat_id, file)
    else:
        return ContinueHandling()


# regexp="Stadionlar🏟"
async def admin_menu_stadiums(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    async with bot.retrieve_data(user_id, chat_id) as data:
        admin = data["is_admin"]
    if admin:
        stadiums_query = select(Stadium)
        async with Session.begin() as db:
            stadiums = (await db.execute(stadiums_query)).scalars().all()
            data = json.dumps(jsonable_encoder(stadiums))
            file = io.BytesIO(data.encode())
            file.name = "stadiums.json"
            await bot.send_chat_action(chat_id, "UPLOAD_DOCUMENT")
            await bot.send_document(chat_id, file)

    else:
        return ContinueHandling()


# regexp="Buyurtmalar🗒"
async def admin_menu_orders(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    orders_query = select(Order)
    async with bot.retrieve_data(user_id, chat_id) as data:
        admin = data["is_admin"]
    if admin:
        async with Session.begin() as db:

            orders = (await db.execute(orders_query)).scalars().all()
            data = json.dumps(jsonable_encoder(orders))
            file = io.BytesIO(data.encode())
            file.name = "orders.json"
            await bot.send_chat_action(chat_id, "UPLOAD_DOCUMENT")
            await bot.send_document(chat_id, file)

    else:
        return ContinueHandling()
