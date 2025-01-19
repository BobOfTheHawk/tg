from aiogram import Router, F
from aiogram import types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.buttons.reply import main_menu, money_usage_menu, currency_menu, money_usage_menu_main
from bot.state import MoneyPlanes, MoneyPlane, AddMoney
from db.models import Money, Moneyplan
from text import WEEKDAYS

money = Router()


@money.message(F.text == "💸 Manage Monthly Spendings")
async def manage_monthly_spendings(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_money_plan = await Money.get_all_copy(user_id=user_id)
    await state.set_state(MoneyPlanes.back)
    if user_money_plan:
        await message.answer(
            "Here are your options:",
            reply_markup=money_usage_menu_main()
        )
    else:
        await message.answer(
            "Let’s manage those spendings! Pick an option to proceed.",
            reply_markup=money_usage_menu()
        )


@money.message(F.text == "🔄 Create Monthly Spending")
async def back_to_main_menu(message: types.Message, state: FSMContext):
    await state.set_state(MoneyPlanes.back)
    await message.answer("Please select your currency:", reply_markup=currency_menu())


@money.message(F.text == "💵 USD ($)")
@money.message(F.text == "🇺🇿 UZS (сум)")
async def currency_selected(message: types.Message, state: FSMContext):
    await state.update_data(selected_currency=message.text)
    if message.text == "💵 USD ($)":
        await message.answer(
            "💵 **You selected USD.**\n\n"
            "👉 *Please enter the amount in whole numbers, e.g.,* `250`.",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown"
        )
    elif message.text == "🇺🇿 UZS (сум)":
        await message.answer(
            "🇺🇿 **You selected UZS.**\n\n"
            "👉 *Please enter the amount with thousands separated by periods, e.g.,* `2.500.000`.",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown"
        )
    await state.set_state(MoneyPlanes.enter_amount)


def days_inline_keyboard():
    builder = InlineKeyboardBuilder()
    for day in range(1, 32):
        builder.add(InlineKeyboardButton(text=str(day), callback_data=f"days_{day}"))
    builder.adjust(5)
    return builder.as_markup()


@money.message(StateFilter(MoneyPlanes.enter_amount))
async def enter_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.replace(".", ""))
        user_data = await state.get_data()
        selected_currency = user_data.get("selected_currency")

        if selected_currency == "💵 USD ($)":
            formatted_amount = f"${amount:,.0f}".replace(",", ".")
        elif selected_currency == "🇺🇿 UZS (сум)":
            formatted_amount = f"{amount:,.0f} UZS".replace(",", ".")

        await message.answer(
            f"✅ You entered: {formatted_amount} in {selected_currency}\n"
            "Now, please select the number of days you plan to use this amount:",
            reply_markup=days_inline_keyboard()
        )
        await state.update_data(spending_amount=amount)
        await state.set_state(MoneyPlanes.enter_days)
    except ValueError:
        await message.answer("❌ Please enter a valid number in the correct format.")


@money.callback_query(StateFilter(MoneyPlanes.enter_days), F.data.startswith("days_"))
async def select_days(callback: types.CallbackQuery, state: FSMContext):
    days = int(callback.data.split("_")[1])
    user_data = await state.get_data()
    formatted_amount = user_data.get("spending_amount")
    selected_currency = user_data.get("selected_currency")
    user_id = callback.from_user.id
    await Money.create(
        user_id=user_id,
        amount=formatted_amount,
        currency=selected_currency,
        days=days
    )
    await callback.message.edit_text(
        f"📅 You entered {days} days for using {formatted_amount} {selected_currency}.\n"
        "Your spending plan has been saved. What would you like to do next?"
    )
    await callback.message.answer("Main Menu:", reply_markup=main_menu())
    await state.set_state(MoneyPlane.back)


@money.message(F.text == "➕ Add Plan")
async def add_plan_start(message: types.Message, state: FSMContext):
    await message.answer("Please enter the name of the plane")
    await state.set_state(AddMoney.name)


@money.message(StateFilter(AddMoney.name))
async def add_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    mon = await Money.get_user_id(id_=message.from_user.id)
    cr = mon.currency
    if cr == "💵 USD ($)":
        await message.answer(
            "💵 **Yor currency is 💵 USD ($)**\n\n"
            "👉 *Please enter the amount in whole numbers, e.g.,* `10`.",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown"
        )
    elif cr == "🇺🇿 UZS (сум)":
        await message.answer(
            "🇺🇿 **You selected UZS.**\n\n"
            "👉 *Please enter the amount with thousands separated by periods, e.g.,* `15.000`.",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown"
        )
    await state.set_state(AddMoney.money)


async def days(selected_days):
    builder = InlineKeyboardBuilder()
    for i, day in enumerate(WEEKDAYS):
        if day in selected_days:
            builder.button(text=f"{day} ✅", callback_data=f"d_{day}")
        else:
            builder.button(text=day, callback_data=f"d_{day}")
        if (i + 1) % 3 == 0:
            builder.adjust(3)
    builder.button(text="✅ Tugallash", callback_data="fs")
    builder.button(text="❌ Bekor qilish", callback_data="cancel")
    builder.adjust(3, 3, 1, 2)
    return builder.as_markup()


@money.message(StateFilter(AddMoney.money))
async def add_price(message: types.Message, state: FSMContext):
    mon = await Money.get_user_id(id_=message.from_user.id)
    try:
        cr = mon.currency
        amount = message.text
        cleaned_amount = int(amount.replace(".", "").replace(",", ""))
        if cr == "💵 USD ($)":
            formatted_amount = f"${cleaned_amount:,.0f}".replace(".", "")
        elif cr == "🇺🇿 UZS (сум)":
            formatted_amount = f"{cleaned_amount:,.0f} UZS".replace(".", "")
        await state.update_data(money=amount)
        await state.set_state(AddMoney.plan_time)
        selected_days = []
        keyboard = await days(selected_days)
        await message.answer(
            f"✅ You entered: {formatted_amount} in {mon.currency}\n",
            reply_markup=keyboard
        )

    except ValueError:
        await message.answer("EEEE Xato..........")


@money.callback_query(lambda c: c.data.startswith("d_"))
async def process_day_selection(callback_query: types.CallbackQuery, state: FSMContext):
    selected_day = callback_query.data.split("_")[1]
    data = await state.get_data()
    selected_days = data.get("selected_days", [])

    if selected_day in selected_days:
        selected_days.remove(selected_day)
    else:
        selected_days.append(selected_day)

    await state.update_data(selected_days=selected_days)
    keyboard = await days(selected_days)
    await callback_query.message.edit_reply_markup(reply_markup=keyboard)


@money.callback_query(lambda c: c.data == "fs")
async def finish_days_selection(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_days = data.get("selected_days", [])
    if not selected_days:
        await callback.message.answer("Iltimos, hech bo'lmaganda bir kun tanlang.")
        return
    user_money_data = await state.get_data()
    name = user_money_data.get("name")
    price = user_money_data.get("money")
    sa = ",".join(selected_days)
    await Moneyplan.create(
        user_id=int(callback.from_user.id),
        plan_name=name,
        plan_price=int(price),
        days=sa
    )
    await callback.message.answer("plan has saved", reply_markup=money_usage_menu_main())
