from aiogram import Router, types, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.buttons.reply import registration_menu, main_menu
from bot.state import RegistrationStates, MoneyPlanes, RoutineStates
from db.models import User

main_router = Router()


@main_router.message(StateFilter(MoneyPlanes.back) and F.text == "🔙 Back")
@main_router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    user = await User.get(id_=message.from_user.id)
    await state.clear()
    if not user:
        await state.clear()
        await message.answer("Please enter your full name:")
        await state.set_state(RegistrationStates.waiting_for_fullname)
    else:
        await message.answer("Hello, {fullname}!".format_map({"fullname": message.from_user.full_name}),
                             reply_markup=main_menu())


@main_router.message(StateFilter(RegistrationStates.waiting_for_fullname))
async def fullname_handler(message: types.Message, state: FSMContext):
    fullname = message.text
    await state.update_data(fullname=fullname)
    await message.answer("Please enter your phone number:", reply_markup=registration_menu())
    await state.set_state(RegistrationStates.waiting_for_phone)


@main_router.message(StateFilter(RegistrationStates.waiting_for_phone))
async def phone_handler(message: types.Message, state: FSMContext):
    phone_number = message.contact.phone_number
    if phone_number is None:
        await message.reply("Please provide a valid phone number.")
        return
    if message.contact.phone_number.startswith("+"):
        phone_number = message.contact.phone_number[1:]
    else:
        phone_number = message.text
    data = await state.get_data()
    fullname = data['fullname']
    await User.create(id=message.from_user.id, fullname=fullname, phone_number=phone_number, language="EN")
    await state.clear()
    await message.answer("You have been registered successfully!", reply_markup=main_menu())


@main_router.message(StateFilter(RegistrationStates.waiting_for_phone))
async def phone_handler(message: types.Message, state: FSMContext):
    phone_number = message.contact.phone_number if message.contact else message.text
    if not phone_number:
        await message.reply("Please provide a valid phone number.")
        return
    if phone_number.startswith("+"):
        phone_number = phone_number[1:]
    if not phone_number.isdigit() or len(phone_number) < 10:  # Example validation
        await message.reply("Please provide a valid phone number.")
        return
    data = await state.get_data()
    fullname = data.get('fullname')
    try:
        await User.create(id=message.from_user.id, fullname=fullname, phone_number=phone_number, language="EN")
        await state.clear()
        await message.answer("You have been registered successfully!", reply_markup=main_menu())
    except Exception as e:
        print(f"Error occurred during database insertion: {e}")
        await message.reply("Registration failed. Please try again.")
