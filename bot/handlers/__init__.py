from bot.dispacher import dp
from bot.handlers.backup import backup
from bot.handlers.drugs import drugs
from bot.handlers.main_handler import main_router
from bot.handlers.money_plans import money
from bot.handlers.music import music
from bot.handlers.payment import payment
from bot.handlers.routine import routine
from bot.handlers.code import code
from bot.handlers.api import api

dp.include_routers(*[
    main_router,
    routine,
    payment,
    backup,
    money,
    music,
    code,
    api,
    drugs
])
