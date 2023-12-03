import telebot.types
from sqlalchemy import select
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateMemoryStorage
from telebot import asyncio_filters
from telebot.types import Update, BotCommand

from database import Session, User, UserSessions
from .states import Auth, UserState, StadiumState, ManageStadiums, MyBookings, Settings, Help, SuperUserState
from .antiflood import SimpleMiddleware, HandleException
from utils import TOKEN

bot = AsyncTeleBot(TOKEN, state_storage=StateMemoryStorage(), colorful_logs=True, exception_handler=HandleException())
bot.add_custom_filter(asyncio_filters.StateFilter(bot))
bot.add_custom_filter(asyncio_filters.ChatFilter())
bot.setup_middleware(SimpleMiddleware(1, bot))
auth_sts = Auth()
user_sts = UserState()
stadium_sts = StadiumState()
manage_sts = ManageStadiums()
booking_sts = MyBookings()
settings_sts = Settings()
help_sts = Help()
admin_sts = SuperUserState()


async def bot_meta():
    await bot.delete_my_commands()
    await bot.set_my_commands(commands=[BotCommand("start", "Botni boshlash"),
                                        BotCommand("cancel", "Bekor qilish"),
                                        BotCommand("logout", "Tizimdan chiqish")
                                        ])


class IsAdmin(asyncio_filters.SimpleCustomFilter):
    key = 'is_admin'

    async def check(self, message):
        user_id = message.from_user.id
        chat_id = message.chat.id if type(message) != telebot.types.CallbackQuery else message.message.chat.id
        print(user_id, chat_id)
        try:
            async with bot.retrieve_data(user_id, chat_id) as data:
                if data and "is_admin" in data:
                    return data["is_admin"]

        except KeyError as e:
            print(e)
        try:
            async with Session() as db:
                admin_q = select(User.is_staff).join(UserSessions, User.id == UserSessions.user_id).where(
                    UserSessions.telegram_id == int(user_id))
                admin = (await db.execute(admin_q)).scalar()
                if admin is not None:
                    if data is not None:
                        data["is_admin"] = admin
                    return admin
        except IndexError as e:
            print(56, e)
        except Exception as e:
            print(61, e)
        print("filtered")
        return False


bot.add_custom_filter(IsAdmin())


async def response_to_update(update: Update):
    message = update.message
    callback = update.callback_query

#    BotCommand("add_stadium", "to get specific order"),
#    BotCommand("get_stadium", "to get specific order"),
#    BotCommand("all_stadiums", "to get all stadiums"),
#    BotCommand("add_order", "to add stadium"),
#    BotCommand("get_order", "to get specific order"),
#    BotCommand("all_orders", "to get all orders"),
#
