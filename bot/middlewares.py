# from telebot.async_telebot import AsyncTeleBot, BaseMiddleware
# from telebot.types import Message
#
#
# class AntiFloodMiddleware(BaseMiddleware):
#     def __init__(self, bot: AsyncTeleBot, max_messages: int = 3, cooldown: int = 5):
#         self.max_messages = max_messages
#         self.cooldown = cooldown
#         self.user_messages = {}
#         self.bot = bot
#
#     async def on_pre_process_message(self, message: Message):
#         user_id = message.from_user.id
#
#         if user_id not in self.user_messages:
#             self.user_messages[user_id] = []
#
#         # Remove old messages that are outside the cooldown period
#         current_time = message.date.timestamp()
#         self.user_messages[user_id] = [
#             msg for msg in self.user_messages[user_id]
#             if current_time - msg.date.timestamp() < self.cooldown
#         ]
#
#         # Check if the user has exceeded the maximum allowed messages
#         if len(self.user_messages[user_id]) >= self.max_messages:
#             await self.bot.delete_message(message.chat.id, message.message_id)
#             return False
#
#         # Add the current message to the user's message history
#         self.user_messages[user_id].append(message)
#
#         return True
