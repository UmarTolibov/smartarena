from sqlalchemy import select, exists
from telebot.types import Message, CallbackQuery
from bot.loader import bot, auth_sts, user_sts
from .markups import accounts_inline
from .markups.buttons import login_signup, main_menu_markup
from database import Session, User, UserSessions


@bot.message_handler(commands=["start"])
async def greeting(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    markup = login_signup()
    try:
        async with Session.begin() as db:
            user_check_q = select(User.username, User.id).join(UserSessions, User.id == UserSessions.user_id).where(
                UserSessions.telegram_id == user_id)
            user_check = (await db.execute(user_check_q)).fetchall()
            if len(user_check) >= 2:
                markup = accounts_inline(user_check)
                await bot.send_message(chat_id, "Qaysi akkaunt bilan davom ettirmoqchisiz?", reply_markup=markup)
                await bot.set_state(user_id, chat_id)
            else:
                async with bot.retrieve_data(user_id, chat_id) as data:
                    data["user_id"] = user_check.first().id
                await bot.send_message(chat_id, f"Salom {user_check[0].username}", reply_markup=main_menu_markup())
                await bot.set_state(user_id, user_sts.main, chat_id)
    except Exception as e:
        print(e)
        await bot.send_message(chat_id, f"Salom {message.from_user.first_name}", reply_to_message_id=message.message_id,
                               reply_markup=markup)
        await bot.set_state(user_id, auth_sts.init, chat_id)


@bot.callback_query_handler(func=lambda call: "account" in call.data.split("|"))
async def choose_account_handler(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    user_db_id = int(call.data.split("|")[1])
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["user_id"] = user_db_id
        await bot.delete_message(chat_id, call.message.message_id)
        await bot.send_message(chat_id, f"Tizimga kirildi", reply_markup=main_menu_markup())
        await bot.set_state(user_id, user_sts.main, chat_id)

