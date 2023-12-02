from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateMemoryStorage
from telebot import asyncio_filters
from telebot.types import Update, BotCommand

from .states import Auth, UserState, StadiumState, ManageStadiums, MyBookings, Settings, Help
from .antiflood import SimpleMiddleware
from utils import TOKEN

bot = AsyncTeleBot(TOKEN, state_storage=StateMemoryStorage(), colorful_logs=True)
bot.add_custom_filter(asyncio_filters.StateFilter(bot))
bot.add_custom_filter(asyncio_filters.ChatFilter())
bot.setup_middleware(SimpleMiddleware(2, bot))
auth_sts = Auth()
user_sts = UserState()
stadium_sts = StadiumState()
manage_sts = ManageStadiums()
booking_sts = MyBookings()
settings_sts = Settings()
help_sts = Help()


async def bot_meta():
    await bot.delete_my_commands()
    await bot.set_my_commands(commands=[BotCommand("start", "Botni boshlash"),
                                        BotCommand("cancel", "Bekor qilish")
                                        ])


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
