from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import LabeledPrice, PreCheckoutQuery, Message

from bot.buttons.inline import inline_advertisement_button
from bot.buttons.reply import main_menu
from db.models import User
from utils.config import PaymentConfig

payment = Router()

advertisement_text = (
    "🔔 **Check out our limited time offer**\n\n"
    "💥 **50% discount** on premium subscription for this month\n"
    "🎉 Don't miss this chance to unlock exclusive features at half the price"
)


@payment.message(Command(commands=["pay"]))
async def initiate_payment(message: Message):
    prices = [
        LabeledPrice(label='VIP Membership 🏅', amount=50000),
    ]
    await message.answer_invoice(
        title='VIP Membership 🚀',
        description="Unlock premium features and special content with VIP Membership. Exclusive access to webinars, discounts, and more",
        payload='1',
        provider_token=PaymentConfig.PAY_APP,
        currency="UZS",
        prices=prices
    )


@payment.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery) -> None:
    await pre_checkout_query.answer(True)


@payment.message(lambda message: bool(message.successful_payment))
async def payment_success_handler(message: Message, state: FSMContext):
    if message.successful_payment:
        total_amount = message.successful_payment.total_amount
        order_id = int(message.successful_payment.invoice_payload)
        await User.update(id_=message.from_user.id, premium=True)
        await message.answer(
            text=(
                "🎉 **To'lov muvaffaqiyatli amalga oshirildi**\n\n"
                f"🪙 **To'lov miqdori**: UZS {total_amount}\n"
                f"🆔 **Buyurtma ID**: {order_id}\n\n"
                "🎈 Sizning premium obunangiz muvaffaqiyatli faollashtirildi \n"
                "🔑 Qo'shimcha imkoniyatlar va foydalar uchun tayyor bo'ling 🌟\n\n"
                "Biz bilan qoling va ajoyib tajribadan bahramand bo'ling 🙌"
            ),
            parse_mode='Markdown', reply_markup=inline_advertisement_button()
        )
    else:
        await message.answer(
            text="To'lov muvaffaqiyatli amalga oshirilmadi. Iltimos, qayta urinib ko'ring",
            reply_markup=main_menu()
        )

