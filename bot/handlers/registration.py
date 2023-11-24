from telebot.types import Message, CallbackQuery, ReplyKeyboardRemove
import re
from sqlalchemy.sql import update, select, and_, or_, exists
from bot.common.bot_config import __
from bot.loader import bot, reg_state, sts
from bot.keyboards import *
from database import User, UserSessions, Session


async def edit_info(user_id, lang, chat_id):
    markup = await confirmation_inline(lang)
    async with bot.retrieve_data(user_id, chat_id) as data:
        email = data['email']
        name = data['name']
        gender = data['gender']
        number = data['contact']
        info_confirmation = __('confirm', lang).format(email=email, name=name, gender=gender, number=number)
        return info_confirmation, markup


@bot.message_handler(content_types=['text'], state=reg_state.lang)
async def chosen_lang_ask_name(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    lang = message.text[:2]
    async with bot.retrieve_data(user_id, chat_id) as data:
        data['lang'] = lang
    if lang == "asdasdad":
        mark_up = main_menu(lang)
        await bot.send_message(chat_id, __('lang_success', lang), reply_markup=mark_up)
        await bot.set_state(user_id, sts.menu, chat_id)
    else:
        markup = ReplyKeyboardRemove()
        await bot.send_message(chat_id, __('auth', lang), reply_markup=markup)
        await bot.send_message(chat_id, __('name', lang))
        await bot.set_state(user_id, reg_state.name, chat_id)


@bot.message_handler(content_types=['text'], state=reg_state.name)
async def ask_gender(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text

    async with bot.retrieve_data(user_id, chat_id) as data:
        lang = data["lang"]
        markup = gender_keyboard(lang)
        if len(data.keys()) == 6:
            conf, mark_up = await edit_info(user_id, lang, chat_id)
            data['name'] = text
            await bot.send_message(chat_id, conf, reply_markup=mark_up)
            await bot.set_state(user_id, reg_state.confirm, chat_id)
        else:
            data['name'] = text
            await bot.send_message(chat_id, __('gender', lang), reply_markup=markup)
            await bot.set_state(user_id, reg_state.gender, chat_id)


@bot.message_handler(content_types=['text'], state=reg_state.gender)
async def ask_email(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text
    markup = ReplyKeyboardRemove()
    async with bot.retrieve_data(user_id, chat_id) as data:
        lang = data['lang']
        if len(data.keys()) == 6:
            conf, mark_up = await edit_info(user_id, lang, chat_id)
            data['gender'] = text[-2]
            await bot.send_message(chat_id, conf, reply_markup=mark_up)
            await bot.set_state(user_id, reg_state.confirm, chat_id)
        else:
            data['gender'] = text[:-2]
            await bot.send_message(chat_id, __('email', lang), reply_markup=markup)
            await bot.set_state(user_id, reg_state.email, chat_id)


@bot.message_handler(content_types=['text'], state=reg_state.email)
async def ask_number(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text
    regex = re.match(r"[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+", text)
    async with Session.begin() as db:
        check = (await db.execute(select(exists().where(User.email == text)))).scalar()

    async with bot.retrieve_data(user_id, chat_id) as data:
        lang = data["lang"]
        if regex and not check:
            markup = contact_number_keyboard(lang)
            if len(data.keys()) == 6:
                conf, mark_up = await edit_info(user_id, lang, chat_id)
                data['email'] = text
                await bot.send_message(chat_id, conf, reply_markup=mark_up)
                await bot.set_state(user_id, reg_state.confirm, chat_id)
            else:
                data['email'] = text
                await bot.send_message(chat_id, __('number', lang), reply_markup=markup)
                await bot.set_state(user_id, reg_state.number, chat_id)

        else:
            await bot.send_message(chat_id, __('re_email', lang))
            await bot.set_state(user_id, reg_state.email, chat_id)


@bot.message_handler(content_types=['text', 'contact'], state=reg_state.number)
async def confirmation(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text if message.content_type == 'text' else message.contact.phone_number
    regex = re.match(r"^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$", text)
    markup = ReplyKeyboardRemove()
    async with Session.begin() as db:
        check = (await db.execute(select(exists().where(User.number == text)))).scalar()

    async with bot.retrieve_data(user_id, chat_id) as data:
        lang = data["lang"]
        if regex and not check:
            if len(data.keys()) == 5:
                conf, mark_up = await edit_info(user_id, lang, chat_id)
                data['email'] = text
                await bot.send_message(chat_id, conf, reply_markup=mark_up)
                await bot.set_state(user_id, reg_state.confirm, chat_id)
            else:
                data['contact'] = text
                email = data['email']
                name = data['name']
                gender = data['gender']
                info_confirmation = __('confirm', lang).format(email=email, name=name, gender=gender, number=text)
                markup = confirmation_inline(lang)
                await bot.send_message(chat_id, info_confirmation, reply_markup=markup)
                await bot.set_state(user_id, reg_state.confirm, chat_id)

        else:
            await bot.send_message(chat_id, __('re_number', lang))
            await bot.set_state(user_id, reg_state.number, chat_id)


@bot.callback_query_handler(func=None, state=reg_state.confirm)
async def register_confirm(call: CallbackQuery):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    data = call.data
    state = sts.menu
    if data == 'confirm':
        async with bot.retrieve_data(user_id, chat_id) as data:
            lang = data['lang']
            mark_up = main_menu(lang)
            email = data['email']
            name = data['name']
            gender = data['gender']
            number = data['contact']
            new_user = User(username=name.replace(" ", "_"), number=number, email=email, gender=gender, lang=lang)
            await bot.answer_callback_query(call.id, __('confirmed', lang) + '✅')
        async with Session.begin() as db:
            db.add(new_user)
            await db.commit()

        async with Session.begin() as db:
            new_user_id = (await db.execute(select(User.id).where(User.number == number))).scalar()
            new_session = UserSessions(user_id=new_user_id, telegram_id=user_id, logged=True)
            db.add(new_session)
            await bot.delete_state(user_id, chat_id)
            await bot.send_message(chat_id, __('success', lang), reply_markup=mark_up)
            await bot.set_state(user_id, state, chat_id)
    else:
        async with bot.retrieve_data(user_id, chat_id) as data:
            lang = data['lang']
            edit_this = data.split('_')[1]
            if edit_this == 'name':
                await bot.send_message(chat_id, __('name', lang))
                await bot.set_state(chat_id, reg_state.name, chat_id)
            if edit_this == 'number':
                markup = contact_number_keyboard(lang)
                await bot.send_message(chat_id, __('number', lang), reply_markup=markup)
                await bot.set_state(user_id, reg_state.number, chat_id)
            if edit_this == 'email':
                await bot.send_message(chat_id, __('email', lang))
                await bot.set_state(user_id, reg_state.email, chat_id)
            if edit_this == 'gender':
                markup = gender_keyboard(lang)
                await bot.send_message(chat_id, __('gender', lang), reply_markup=markup)
                await bot.set_state(user_id, reg_state.gender, chat_id)
