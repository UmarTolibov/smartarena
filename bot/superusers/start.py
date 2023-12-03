from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from telebot.types import Message, CallbackQuery
from werkzeug.security import check_password_hash

from bot.loader import bot, auth_sts, user_sts, admin_sts
from .markups import accounts_inline
from .markups.buttons import main_menu_markup
from database import Session, User, UserSessions
from ..users.markups import login_signup


@bot.message_handler(commands=["start"], is_admin=True)
async def greeting_admin(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    async with Session.begin() as db:
        user_check_q = select(User.username, User.id).join(UserSessions, User.id == UserSessions.user_id).where(
            UserSessions.telegram_id == user_id)
        user_check = (await db.execute(user_check_q)).fetchall()
        print(user_check)

        if len(user_check) >= 2:
            markup = accounts_inline(user_check)
            await bot.send_message(chat_id, "Qaysi akkaunt bilan davom ettirmoqchisiz?", reply_markup=markup)
            return
        else:
            await bot.send_message(chat_id, f"Salom {user_check[0].username}", reply_markup=main_menu_markup())
            await bot.set_state(user_id, admin_sts.menu, chat_id)
            async with bot.retrieve_data(user_id, chat_id) as data:
                data["user_id"] = user_check[0][1]


@bot.callback_query_handler(func=lambda call: "account" in call.data.split("|"))
async def choose_account_handler(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    user_db_id = int(call.data.split("|")[1])
    async with bot.retrieve_data(user_id, chat_id) as data:
        admin = data["is_admin"]
        if admin:
            data["user_id"] = user_db_id
            await bot.delete_message(chat_id, call.message.message_id)
            await bot.send_message(chat_id, f"Tizimga kirildi", reply_markup=main_menu_markup())
            await bot.set_state(user_id, admin_sts.main, chat_id)
        else:
            return


@bot.message_handler(content_types=["text"], state=auth_sts.login_password, is_admin=True)
async def admin_login_password(message: Message):
    print("working")
    user_id = message.from_user.id
    chat_id = message.chat.id
    password = message.text
    async with bot.retrieve_data(user_id, chat_id) as data:
        user_q = select(User).where(User.username == data["username"])

    async with Session() as db:
        user = (await db.execute(user_q)).scalar()
        data["user_id"] = user.id
        if user and check_password_hash(user.password, password):
            try:
                new_session = UserSessions(user_id=user.id, telegram_id=user_id)
                db.add(new_session)
                await db.commit()
            except IntegrityError as e:
                print(e)

            await bot.send_message(chat_id, "Tizimga kirdingiz!", reply_markup=main_menu_markup())
            await bot.set_state(user_id, admin_sts.menu, chat_id)
        else:
            await bot.send_message(chat_id, "Parol noto\'g\'ri!")
            async with bot.retrieve_data(user_id, chat_id) as data:
                data["attempts"] += 1
                if data["attempts"] >= 3:
                    await bot.send_message(chat_id, "Iltimos keyinroq urinib koring!", reply_markup=login_signup())
                    await bot.set_state(user_id, auth_sts.init, chat_id)
                    data["attempts"] = 0
