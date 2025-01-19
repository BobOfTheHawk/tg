import openai
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

# Initialize the router
api = Router()

#
# @api.message(Command(commands=["api"]))
# async def gpt(message: Message):
#     await message.reply("Please send your query, and I'll forward it to ChatGPT!")
#
#
# @api.message()
# async def gpt_response(message: Message):
#     user_input = message.text
#
#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant."},
#                 {"role": "user", "content": user_input},
#             ],
#         )
#         chat_response = response.choices[0].message["content"]
#         await message.reply(chat_response)
#     except Exception as e:
#         await message.reply(f"An error occurred while processing your request: {str(e)}")
