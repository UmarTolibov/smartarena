from telebot.asyncio_handler_backends import BaseMiddleware, CancelUpdate
from telebot.types import Message


class SimpleMiddleware(BaseMiddleware):
    def __init__(self, limit, bot) -> None:
        self.last_time = {}
        self.limit = limit
        self.update_types = ['message']
        self.bot = bot

    async def pre_process(self, message: Message, data):
        chat_id = message.chat.id
        user_id = message.from_user.id
        async with self.bot.retrieve_data(user_id, chat_id) as rdata:
            try:
                user = rdata["user_id"]
            except KeyError:
                await self.bot.send_message(chat_id, "Bu xizmatdan foydalanishingiz uchun tizimga kirishingiz kerak")
        if not message.from_user.id in self.last_time:
            self.last_time[message.from_user.id] = message.date
            return
        if message.date - self.last_time[message.from_user.id] < self.limit:
            await self.bot.delete_message(message.chat.id, message.message_id)
            return CancelUpdate()
        self.last_time[message.from_user.id] = message.date

    async def post_process(self, message, data, exception):
        pass
