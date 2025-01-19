from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from utils.config import CF as conf

TOKEN = conf.bot.TOKEN
# dockerda
# redis_ = Redis(host='redis', port=6379)

# main da
# redis = Redis()
#
#
# redis_storage = RedisStorage(redis)
# dp = Dispatcher(storage=redis_storage)
dp = Dispatcher()
