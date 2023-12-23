import datetime

from sqlalchemy import select, func, exists, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased
from telebot.types import Message, CallbackQuery
from werkzeug.security import check_password_hash

from bot.loader import bot, auth_sts, user_sts, admin_sts, stadium_sts
from .markups import accounts_inline
from .markups.buttons import main_menu_markup
from database import Session, User, UserSessions, Stadium, Order
from ..users.markups import login_signup, your_stadiums_markup, back, stadiums_inline, book_inline


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
            async with bot.retrieve_data(user_id) as data:
                data["user_id"] = user_check[0][1]


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
        else:
            return


async def admin_login_password(message: Message):
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


async def ad_stadium_confirmation_handler(callback: CallbackQuery):
    print("_")
    chat_id = callback.message.chat.id
    user_id = callback.from_user.id
    if callback.data == "confirm":
        async with bot.retrieve_data(user_id, chat_id) as data:
            print(data)
            new_stadium = Stadium(name=data["stadium_name"], description=data["stadium_description"],
                                  price=int(data["stadium_price"]), opening_time=data["stadium_open_time"],
                                  closing_time=data["stadium_close_time"], region=data["region_name"],
                                  district=data["district_name"], location=data["location_data"],
                                  user_id=data["user_id"])
            new_stadium.set_image_urls(data["stadium_photo"])

        try:
            async with Session() as db:
                db.add(new_stadium)
                await db.commit()
            await bot.send_message(chat_id, "Stadion qo'shildi.", reply_markup=main_menu_markup())
        except Exception as e:
            print(e)
            await bot.send_message(chat_id, "Hatolik yuz berdi, qayta urinib ko'ring:(",
                                   reply_markup=your_stadiums_markup())
            await bot.set_state(chat_id, stadium_sts.init, user_id)
    if callback.data == "reject":
        await bot.send_message(chat_id, "Stadion nomini kiriting", reply_markup=back())
        await bot.set_state(user_id, stadium_sts.name, chat_id)


async def admin_proceed_yes_no(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    answer = bool(int(call.data.split("|")[1]))
    if answer is True:
        await bot.answer_callback_query(call.id, "Malumotlarni kirishda hushyor bo'lishingizni so'rab qolamiz",
                                        show_alert=True)
        await bot.send_message(chat_id, "Stadion nomini kiriting")
        await bot.set_state(user_id, stadium_sts.name, chat_id)
    else:
        await bot.answer_callback_query(call.id, "Bekor qilindi", )
        await bot.send_message(chat_id, "Bosh sahifa", reply_markup=main_menu_markup())


async def admin_hour_choose(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    hour = int(call.data.split("|")[1])
    async with bot.retrieve_data(user_id, chat_id) as data:
        print(data)
        data["hour"] = hour
        region_filter = data["region_name"]
        district_filter = data["district_name"]
        start_time_str = data["start_time"]
        date_str = data["date"]
        date_object = datetime.datetime.strptime(date_str.replace(":", "-"), "%Y-%m-%d")
        start_time_delta = datetime.datetime.strptime(start_time_str, "%H:%M").time()
        combined_datetime = datetime.datetime.combine(date_object, start_time_delta)
        hour_filter = data["hour"]
        markup = main_menu_markup()
    await bot.answer_callback_query(call.id, "Stadionlar")
    async with Session() as session:
        order_alias = aliased(Order)
        query = (
            select(Stadium)
            .filter(func.lower(Stadium.region).ilike(func.lower(region_filter)))
            .filter(func.lower(Stadium.district).ilike(func.lower(district_filter)))
            .filter(~exists().where(
                and_(
                    order_alias.stadium_id == Stadium.id,
                    order_alias.start_time == combined_datetime,
                    order_alias.hour == hour_filter
                )
            ))
        )

        # Execute the query asynchronously to get the result
        result = await session.execute(query)
        stadiums = result.scalars().all()
        await bot.send_message(chat_id, "Stadionlar", reply_markup=markup)
        await bot.send_message(chat_id, "Tanlang", reply_markup=stadiums_inline(stadiums))


async def admin_location_book(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    data = call.data
    if data == "book_now":
        # format_string = "%Y-%m-%d %H:%M:%S"
        async with bot.retrieve_data(user_id, chat_id) as data:
            start_time_str = data["start_time"]
            date_str = data["date"]
            date_object = datetime.datetime.strptime(date_str.replace(":", "-"), "%Y-%m-%d")
            start_time_delta = datetime.datetime.strptime(start_time_str, "%H:%M").time()
            combined_datetime = datetime.datetime.combine(date_object, start_time_delta)
            hour = data["hour"]
            new_order = Order(status="Ko'rib chiqilmoqda", start_time=combined_datetime, hour=hour,
                              user_id=data["user_id"],
                              stadium_id=data["stadium_id"])
        try:
            async with Session() as db:
                db.add(new_order)
                await db.commit()
            await bot.answer_callback_query(call.id, f"Bajarildi✅")
            await bot.send_message(chat_id, "Stadion bron qilindi", reply_markup=main_menu_markup())
            await bot.set_state(user_id, user_sts.main, chat_id)

        except Exception as e:
            print(e)
    else:
        await bot.answer_callback_query(call.id, f"Lokatsiya")
        async with bot.retrieve_data(user_id, chat_id) as bdata:
            location = bdata["location"]
        await bot.send_location(chat_id, **location, reply_markup=book_inline(True))
