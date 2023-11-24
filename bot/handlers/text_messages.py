import asyncio
import io

from telebot.types import Message, ReplyKeyboardRemove
from fastapi.encoders import jsonable_encoder
from sqlalchemy.sql import select, update, or_, and_
from bot.loader import bot, sts
from werkzeug.security import check_password_hash
from database.connection import Session
from database import User, Stadium, Order, StadiumModel, OrderModel
from bot.common.markups import menu, cancel, crud_markup
import json
from pprint import pformat


# cancel button


@bot.message_handler(func=lambda m: m.text in ['Cancel❌', '/cancel'], state='*')
async def cancel_op(msg: Message):
    await bot.set_state(msg.from_user.id, sts.main, msg.chat.id)
    await bot.send_message(msg.chat.id, "Canceled", reply_markup=menu())
    await bot.delete_message(msg.chat.id, msg.message_id)


# ==============================================================================
#                                  TO LOGIN                                    #
# ==============================================================================


@bot.message_handler(content_types=['text'], state=sts.log_in)
async def log_in_start(msg: Message):
    chat_id = msg.chat.id
    user_id = msg.from_user.id
    if msg.text != "Login":
        await bot.send_message(chat_id, "Please choose from keyboard")
    else:

        await bot.send_message(chat_id, "Please Send your username/email", reply_markup=ReplyKeyboardRemove())
        await bot.set_state(user_id, sts.username, chat_id)


@bot.message_handler(content_types=['text'], state=sts.username)
async def get_username(msg: Message):
    chat_id = msg.chat.id
    user_id = msg.from_user.id
    query = select(User).where(or_(User.username == msg.text, User.email == msg.text))
    async with Session.begin() as conn:
        user = (await conn.execute(query)).scalar()
    if user:
        async with bot.retrieve_data(user_id, chat_id) as data:
            data['username'] = msg.text

        await bot.send_message(chat_id, "Now Send your password")
        await bot.set_state(user_id, sts.password, chat_id)
    else:
        await bot.send_message(chat_id,
                               "Please send a valid email/username, User with this username/email doesn't exists")


@bot.message_handler(content_types=["text"], state=sts.password)
async def get_password(msg: Message):
    chat_id = msg.chat.id
    user_id = msg.from_user.id
    async with bot.retrieve_data(user_id, chat_id) as data:
        query = select(User).where(or_(User.email == data["username"], User.username == data["username"]))
    async with Session.begin() as conn:
        user = (await conn.execute(query)).scalar()
        if check_password_hash(user.password, msg.text):
            query = update(User).where(User.id == user.id).values(telegram_id=user_id)
            await conn.execute(query)
            await conn.commit()
            await bot.send_message(chat_id, "You are now loggen in", reply_markup=menu())
            await bot.delete_state(user_id, chat_id)
        else:
            await bot.send_message(chat_id, "Please re-enter your username/email and password")
            await bot.set_state(user_id, sts.username, chat_id)


# ==============================================================================
#                                ORDER-MANAGEMENT                              #
# ==============================================================================

# To get a specific order

@bot.message_handler(func=lambda m: m.text in ["Get Order", "/get_order"])
async def retrieve_order(msg: Message):
    chat_id = msg.chat.id
    user_id = msg.from_user.id
    await bot.send_message(chat_id, "Send the id of the Order to retrieve!", reply_to_message_id=msg.message_id,
                           reply_markup=ReplyKeyboardRemove())
    await bot.set_state(user_id, sts.get_order, chat_id)


@bot.message_handler(content_types=["text"], state=sts.get_order)
async def get_order_id(msg: Message):
    chat_id = msg.chat.id
    user_id = msg.from_user.id
    order_id = int(msg.text)
    query = select(Order).where(Order.id == order_id)
    user_query = select(User).where(User.telegram_id == user_id)

    async with Session.begin() as db:
        user = (await db.execute(user_query)).scalar()
        order = (await db.execute(query)).scalar()
        if order is None:
            await bot.send_message(chat_id,
                                   "There's no order with this id\nPlease re-enter the id or cancel the operation",
                                   reply_markup=cancel())
        elif user.is_staff is False:
            await bot.send_message(chat_id, "You are not permitted to use this command", reply_markup=menu())
            await bot.delete_state(user_id, chat_id)
        else:
            await bot.send_message(chat_id, pformat(jsonable_encoder(order), sort_dicts=False),
                                   reply_markup=crud_markup(order_id, order=True))
            await bot.delete_state(user_id, chat_id)
    await bot.delete_message(chat_id, msg.message_id)


# ==============================================================================
# To add order


@bot.message_handler(func=lambda m: m.text in ["Add Order", "/add_order"])
async def add_order(msg: Message):
    chat_id = msg.chat.id
    user_id = msg.from_user.id
    message = pformat({
        "status": "APPROVED",
        "stadium_id": 1,
        "start_time": "2023-07-08 15:34:33.170394",
        "hour": 1
    }, sort_dicts=False)
    await bot.send_message(chat_id,
                           f"""Please send the order info in json format!
                           Just copy this and change the values
                           <code>{message}</code>""",
                           parse_mode="html")
    await bot.set_state(user_id, sts.get_order_json, chat_id)


@bot.message_handler(content_types=['text'], state=sts.get_order_json)
async def get_order_info_in_json(msg: Message):
    user_id = msg.from_user.id
    chat_id = msg.chat.id
    user_query = select(User.id).where(User.telegram_id == user_id)
    text = msg.text.replace('\'', '"')
    try:
        order = json.loads(text)
        order = OrderModel(**order)

        async with Session.begin() as db:
            users_id = (await db.execute(user_query)).scalar()
            new_order = Order(status=order.status, user_id=users_id, stadium_id=order.stadium_id,
                              start_time=order.start_time, hour=order.hour)
            db.add(new_order)
            await db.commit()
        await bot.send_message(chat_id, f"Created")
        await bot.delete_state(user_id, chat_id)
    except Exception as e:
        await bot.send_message(chat_id, f"Please send a valid data like in an example\nError{e}")


# ==============================================================================
# to edit stadium

@bot.message_handler(content_types=['text'], state=sts.o_edit)
async def update_order(msg: Message):
    chat_id = msg.chat.id
    user_id = msg.from_user.id
    user_query = select(User.id).where(User.telegram_id == user_id)
    text = msg.text.replace('\'', '"')
    try:
        order = json.loads(text)
        async with bot.retrieve_data(user_id, chat_id) as data:
            order_id = data['id']
            message_id = data["message"]
        order_query = select(Order).where(Order.id == int(order_id))
        async with Session.begin() as db:
            users_id = (await db.execute(user_query)).scalar()

            stadium_update_q = update(Order).where(
                and_(Order.id == order_id, Order.user_id == users_id)).values(**order)
            await db.execute(stadium_update_q)
            await db.commit()
        async with Session.begin() as db:
            new_order = (await db.execute(order_query)).scalar()
            result = pformat(jsonable_encoder(new_order), sort_dicts=False)

            try:
                await bot.edit_message_text(text=result, chat_id=chat_id, message_id=message_id, parse_mode='html')
                await bot.edit_message_reply_markup(chat_id, message_id, reply_markup=crud_markup(order_id))
            except Exception as e:
                await bot.send_message(chat_id, f"Nothing was updated\n{e}", reply_markup=menu())
        update_message = await bot.send_message(chat_id, "Updated")
        await asyncio.sleep(0.1)
        await bot.delete_message(chat_id, update_message.message_id)
        await bot.delete_message(chat_id, data['message2'])
        await bot.delete_state(user_id, chat_id)
        await bot.delete_state(user_id, chat_id)

    except Exception as e:
        print(e)
        await bot.send_message(chat_id, f"Please re-enter the data correctly or cancel the operation\n{e}",
                               reply_markup=cancel())
        await bot.set_state(user_id, sts.edit, chat_id)


# ==============================================================================
# To get all stadiums

@bot.message_handler(func=lambda m: m.text in ["All Orders", "/all_orders"])
async def list_orders(msg: Message):
    user_id = msg.from_user.id
    chat_id = msg.chat.id
    user_query = select(User).where(User.telegram_id == user_id)
    orders_query = select(Order)
    async with Session.begin() as db:
        user = (await db.execute(user_query)).scalar()
        if user is None or not user.is_staff:
            await bot.send_message(chat_id, "You are not permitted to use this command", reply_markup=menu())
        else:
            orders = (await db.execute(orders_query)).scalars().all()
            data = json.dumps(jsonable_encoder(orders))
            file = io.BytesIO(data.encode())
            file.name = "orders.json"
            await bot.send_chat_action(chat_id, "UPLOAD_DOCUMENT")
            await bot.send_document(chat_id, file)


# ==============================================================================
#                              STADIUM-MANAGEMENT                              #
# ==============================================================================

# To get a specific stadium

@bot.message_handler(func=lambda m: m.text in ["Get Stadium", "/get_stadium"])
async def get_stadium_by_id(msg: Message):
    chat_id = msg.chat.id
    user_id = msg.from_user.id
    await bot.send_message(chat_id, "Send the id of the stadium to retrieve!", reply_to_message_id=msg.message_id,
                           reply_markup=ReplyKeyboardRemove())
    await bot.set_state(user_id, sts.get_stadium, chat_id)


@bot.message_handler(content_types=["text"], state=sts.get_stadium)
async def get_stadium_id(msg: Message):
    chat_id = msg.chat.id
    user_id = msg.from_user.id
    stadium_id = int(msg.text) if msg.text.isdigit() else msg.text
    query = select(Stadium).where(or_(Stadium.id == stadium_id, Stadium.name == stadium_id))
    user_query = select(User).where(User.telegram_id == user_id)

    async with Session.begin() as db:
        user = (await db.execute(user_query)).scalar()
        stadium = (await db.execute(query)).scalar()
        if stadium is None:
            await bot.send_message(chat_id,
                                   "There's no stadium with this id\nPlease re-enter the id or cancel the operation",
                                   reply_markup=cancel())
        elif user.is_staff is False or user.id != stadium.user_id:
            await bot.send_message(chat_id, "You are not permitted to use this command", reply_markup=menu())
            await bot.delete_state(user_id, chat_id)
        else:
            await bot.send_message(chat_id, pformat(jsonable_encoder(stadium), sort_dicts=False),
                                   reply_markup=crud_markup(stadium_id))
            await bot.delete_state(user_id, chat_id)
    await bot.delete_message(chat_id, msg.message_id)


# ==============================================================================
# To add stadium


@bot.message_handler(func=lambda m: m.text in ["Add Stadium", "/add_stadium"])
async def add_stadium(msg: Message):
    chat_id = msg.chat.id
    user_id = msg.from_user.id
    message = pformat({
        "name": "name",
        "description": "description",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Example_image.svg/600px-Example_image.svg.png",
        "price": 100.23,
        "opening_time": "00:00:00",
        "closing_time": "00:00:00",
        "is_active": True,
        "region": "Tashkent",
        "district": "Yakka Saroy",
        "location": {
            "longitude": 22,
            "latitude": 23
        }
    }, sort_dicts=False)
    await bot.send_message(chat_id,
                           f"""Please send the stadium info in json format!\nJust copy this and change the 
                           values\n```{message}```""",
                           parse_mode="html")
    await bot.set_state(user_id, sts.get_stadium_json, chat_id)


@bot.message_handler(content_types=['text'], state=sts.get_stadium_json)
async def get_stadium_info_in_json(msg: Message):
    user_id = msg.from_user.id
    chat_id = msg.chat.id
    user_query = select(User.id).where(User.telegram_id == user_id)
    text = msg.text.replace('\'', '"')
    try:
        stadium = json.loads(text)
        stadium = StadiumModel(**stadium)

        async with Session.begin() as db:
            users_id = (await db.execute(user_query)).scalar()
            new_stadium = Stadium(
                name=stadium.name, description=stadium.description, image_url=stadium.image_url, price=stadium.price,
                opening_time=stadium.opening_time, closing_time=stadium.closing_time, is_active=stadium.is_active,
                region=stadium.region, district=stadium.district, location=stadium.location, user_id=users_id
            )
            db.add(new_stadium)
            await db.commit()
        await bot.send_message(chat_id, f"Created")
        await bot.delete_state(user_id, chat_id)
    except Exception as e:
        await bot.send_message(chat_id, f"Please send a valid data like in an example\nError{e}")


# ==============================================================================
# To get all stadiums

@bot.message_handler(func=lambda m: m.text in ["All Stadiums", "/all_stadiums"])
async def list_stadiums(msg: Message):
    user_id = msg.from_user.id
    chat_id = msg.chat.id
    user_query = select(User).where(User.telegram_id == user_id)
    stadiums_query = select(Stadium)
    async with Session.begin() as db:
        user = (await db.execute(user_query)).scalar()
        if user is None:
            await bot.send_message(chat_id, "You are not permitted to use this command", reply_markup=menu())
        else:
            stadiums = (await db.execute(stadiums_query)).scalars().all()
            data = json.dumps(jsonable_encoder(stadiums))
            file = io.BytesIO(data.encode())
            file.name = "stadiums.json"
            await bot.send_chat_action(chat_id, "UPLOAD_DOCUMENT")
            await bot.send_document(chat_id, file)


# ==============================================================================
# to edit stadium

@bot.message_handler(content_types=['text'], state=sts.edit)
async def update_stadium(msg: Message):
    chat_id = msg.chat.id
    user_id = msg.from_user.id
    user_query = select(User.id).where(User.telegram_id == user_id)
    text = msg.text.replace('\'', '"')
    try:
        stadium = json.loads(text)
        async with bot.retrieve_data(user_id, chat_id) as data:
            stadium_id = data['id']
            message_id = data["message"]
        stadium_query = select(Stadium).where(Stadium.id == int(stadium_id))
        async with Session.begin() as db:
            users_id = (await db.execute(user_query)).scalar()

            stadium_update_q = update(Stadium).where(
                and_(Stadium.id == stadium_id, Stadium.user_id == users_id)).values(**stadium)
            await db.execute(stadium_update_q)
            await db.commit()
        async with Session.begin() as db:
            new_stadium = (await db.execute(stadium_query)).scalar()
            result = pformat(jsonable_encoder(new_stadium), sort_dicts=False)

            try:
                await bot.edit_message_text(text=result, chat_id=chat_id, message_id=message_id, parse_mode='html')
                await bot.edit_message_reply_markup(chat_id, message_id, reply_markup=crud_markup(stadium_id))
            except Exception as e:
                await bot.send_message(chat_id, f"Nothing was updated\n{e}", reply_markup=menu())
        update_message = await bot.send_message(chat_id, "Updated")
        await asyncio.sleep(0.1)
        await bot.delete_message(chat_id, update_message.message_id)
        await bot.delete_message(chat_id, data['message2'])
        await bot.delete_state(user_id, chat_id)
        await bot.delete_state(user_id, chat_id)

    except Exception as e:
        print(e)
        await bot.send_message(chat_id, f"Please re-enter the data correctly or cancel the operation\n{e}",
                               reply_markup=cancel())
        await bot.set_state(user_id, sts.edit, chat_id)
