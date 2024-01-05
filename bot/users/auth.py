from sqlalchemy import select, delete
from telebot.types import Message, ReplyKeyboardRemove, CallbackQuery
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from bot.loader import bot, auth_sts, user_sts
from database import User, UserSessions
from utils.utils import check_phone_number
from .markups import confirmation, owner_or_user
from .markups.buttons import *
from database.connection import Session


# regexp="Ro'yxatdan o'tish🗒", state=auth_sts.init
async def signup_handler(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    await bot.send_message(chat_id, "Ism Familyangizni yuboring.", reply_to_message_id=message.message_id,
                           reply_markup=ReplyKeyboardRemove())
    await bot.set_state(user_id, auth_sts.name, chat_id)


# content_types=["text"], state=auth_sts.name
async def name_handler(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["name"] = message.text
    await bot.send_message(chat_id, "Telefon raqamingizni yuboring", reply_to_message_id=message.message_id,
                           reply_markup=number_request())
    await bot.set_state(user_id, auth_sts.number, chat_id)


# content_types=["text", "contact"], state=auth_sts.number
async def number_handler(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["number"] = message.text if message.content_type == "text" else message.contact.phone_number
    if message.content_type == "text" and check_phone_number(message.text):

        await bot.send_message(chat_id, "Siz foydalanuvchimisiz yoki Stadion egasi",
                               reply_to_message_id=message.message_id,
                               reply_markup=owner_or_user())
        await bot.set_state(user_id, auth_sts.type, chat_id)
    elif message.content_type == "contact":
        await bot.send_message(chat_id, "Siz foydalanuvchimisiz yoki Stadion egasi",
                               reply_to_message_id=message.message_id,
                               reply_markup=owner_or_user())
        await bot.set_state(user_id, auth_sts.type, chat_id)
    else:
        await bot.send_message(chat_id,
                               "Noto'g'ri raqam kiritdingiz!\nTo'gri raqam formati: <b>+998901234567</b>\nqaytadan urinib ko'ring",
                               parse_mode="html", reply_to_message_id=message.message_id)


async def user_type(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    call_data = bool(int(callback.data.split("|")[1]))
    utype = "Stadion Egasi" if call_data else "Foydalanuvchi"
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["is_owner"] = call_data
    await bot.answer_callback_query(callback.id, f"{utype}")
    await bot.send_message(chat_id, "Akountingiz uchun parolni kiriting", reply_markup=ReplyKeyboardRemove())
    await bot.set_state(user_id, auth_sts.password, chat_id)


# content_types=["text"], state=auth_sts.password
async def password_handler(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    async with bot.retrieve_data(user_id, chat_id) as data:
        data["password"] = message.text
        name = data["name"]
        number = data["number"]
        text = f"""<b>Malumotni Tasdiqlang:</b>" 
<b>Ismi:</b> <code>{name}</code>" 
<b>Telefon raqami:</b> <code>{number}</code>
<b>Parol:</b> <code>{message.text}</code>"""

    await bot.send_message(chat_id, text, reply_markup=confirmation(), parse_mode="html")
    await bot.set_state(user_id, auth_sts.confirm, chat_id)


# , func=lambda x: True, state=auth_sts.confirm
async def confirmation_inline(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    user_data = {}
    password = ""
    if callback.data == "confirm":
        async with bot.retrieve_data(user_id, chat_id) as data:
            password += data["password"]
            user_data["password"] = generate_password_hash(data['password'])
            user_data["number"] = data['number']
            user_data["is_owner"] = data["is_owner"]
            user_data["username"] = data['name'].lower().replace(" ", "_") + data["number"][9:-2]
            print(user_data)
        try:
            async with Session() as db:
                new_user = User(**user_data)
                db.add(new_user)

                await db.commit()
                await db.refresh(new_user)
                user_data["user_id"] = new_user.id
                new_session = UserSessions(telegram_id=user_id, user_id=new_user.id)
                db.add(new_session)
                await db.commit()
                q = select(User).join(UserSessions, User.id == UserSessions.user_id).where(
                    UserSessions.telegram_id == user_id)
                user_owner = (await db.execute(q)).scalar().is_owner
                await bot.answer_callback_query(callback.id, "Tasiqlandi")
                await bot.send_message(chat_id,
                                       f"Bu ma\'lumotlarni saqlab qoying\n<code>username: {user_data['username']}\npassword: {password}</code>",
                                       parse_mode="html", reply_markup=main_menu_markup(user_owner))
            async with bot.retrieve_data(user_id, chat_id) as data:
                data["user_id"] = user_data["user_id"]
                await bot.set_state(user_id, user_sts.main, chat_id)
        except IntegrityError as e:
            print(e)
            await bot.send_message(chat_id, "Hatolik yuz berdi\nBu raqam ro\'yxatdan o\'tkazilgan ",
                                   reply_markup=login_signup())
            await bot.set_state(user_id, auth_sts.init, chat_id)
        except Exception as e:
            print(e)
            await bot.send_message(chat_id, "Hatolik yuz berdi\nQaytadan urinib ko\'ring",
                                   reply_markup=login_signup())
            await bot.set_state(user_id, auth_sts.init, chat_id)

    if callback.data == "reject":
        await bot.send_message(chat_id, "Ismingizni kiriting.")
        await bot.set_state(user_id, auth_sts.name, chat_id)


# regexp="Kirish↙️", state=auth_sts.init
async def login_handler(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    await bot.send_message(chat_id, "Usernameni kiriting!", reply_to_message_id=message.message_id,
                           reply_markup=ReplyKeyboardRemove())
    await bot.set_state(user_id, auth_sts.username, chat_id)


# content_types=["text"], state=auth_sts.username
async def login_username(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    async with Session() as db:
        user_q = select(User).where(User.username == message.text)
        user = (await db.execute(user_q)).scalar()
        if user is None:
            await bot.send_message(chat_id, "Bunday Username mavjud emas!", reply_markup=login_signup())
            await bot.set_state(user_id, auth_sts.init, chat_id)
        else:
            async with bot.retrieve_data(user_id, chat_id) as data:
                data["username"] = message.text
                data["attempts"] = 0
                data["is_admin"] = user.is_staff
            await bot.send_message(chat_id, "Parolni kiriting!")
            await bot.set_state(user_id, auth_sts.login_password, chat_id)


# content_types=["text"], state=auth_sts.login_password,is_admin=False
async def login_password_(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    password = message.text
    async with bot.retrieve_data(user_id, chat_id) as data:
        user_q = select(User).where(User.username == data["username"])

    async with Session() as db:
        user = (await db.execute(user_q)).scalar()
        data["user_id"] = user.id
        is_owner = user.is_owner
        if user and check_password_hash(user.password, password):
            try:
                new_session = UserSessions(user_id=user.id, telegram_id=user_id)
                db.add(new_session)
                await db.commit()
            except IntegrityError as e:
                print(e)

            await bot.send_message(chat_id, "Tizimga kirdingiz!", reply_markup=main_menu_markup(is_owner))
            await bot.set_state(user_id, user_sts.main, chat_id)
        else:
            await bot.send_message(chat_id, "Parol noto\'g\'ri!")
            async with bot.retrieve_data(user_id, chat_id) as data:
                data["attempts"] += 1
                if data["attempts"] >= 3:
                    await bot.send_message(chat_id, "Iltimos keyinroq urinib koring!", reply_markup=login_signup())
                    await bot.set_state(user_id, auth_sts.init, chat_id)
                    data["attempts"] = 0


# commands=["logout"], state='*'
async def logout_handler(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    try:
        async with Session.begin() as db:
            user_q = select(UserSessions.user_id).where(UserSessions.telegram_id == user_id)
            user = (await db.execute(user_q)).scalar()
            del_query = delete(UserSessions).where(UserSessions.user_id == user)
            await db.execute(del_query)
            await db.commit()
            await bot.send_message(chat_id, "Tizimdan chiqdingiz", reply_markup=login_signup())
            await bot.set_state(user_id, auth_sts.init, chat_id)
    except Exception as e:
        print(e)
