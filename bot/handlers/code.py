from math import ceil

from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.buttons.reply import code_menu, main_menu
from bot.state import AddCodeState
from db.models import Code

code = Router()
ITEMS_PER_PAGE = 6  # Har bir sahifada maksimal 6 ta tugma


@code.message(F.text == "👨‍💻 My Codes")
async def code_main(message: types.Message):
    await message.answer("Code menu", reply_markup=code_menu())


@code.message(F.text == "🔙 Back")
async def back_to_main(message: types.Message):
    await message.answer("Main menu", reply_markup=main_menu())


@code.message(F.text == "📜 My Codes")
async def show_my_codes(message: types.Message):
    user_id = message.from_user.id
    try:
        raw_codes = await Code.get_all_copy(user_id=user_id)
        codes = [{"id": code.id, "title": code.title} for code in raw_codes]

        if not codes:
            await message.answer("You don't have any codes yet.")
            return
        await send_code_list(message, codes, page=1)
    except Exception as e:
        await message.answer("An error occurred while fetching your codes.")
        print(f"Error: {e}")


async def send_code_list(message: types.Message, codes, page=1):
    total_pages = ceil(len(codes) / ITEMS_PER_PAGE)
    start_index = (page - 1) * ITEMS_PER_PAGE
    end_index = start_index + ITEMS_PER_PAGE
    current_codes = codes[start_index:end_index]
    builder = InlineKeyboardBuilder()
    for code in current_codes:
        builder.add(InlineKeyboardButton(text=code["title"], callback_data=f"show_code_{code['id']}"))
    if page > 1:
        builder.add(InlineKeyboardButton(text="⬅️ Previous", callback_data=f"codes_page_{page - 1}"))
    if page < total_pages:
        builder.add(InlineKeyboardButton(text="➡️ Next", callback_data=f"codes_page_{page + 1}"))
    await message.answer(f"Page {page}/{total_pages}: Select a code to view.", reply_markup=builder.as_markup())


@code.callback_query(F.data.startswith("show_code_"))
async def show_code(callback_query: types.CallbackQuery, message: types.Message):
    code_id = int(callback_query.data.split("_")[-1])
    try:
        code = await Code.get(code_id)
        if not code:
            await callback_query.message.answer("Code not found.")
            return
        code_text = f"```\n{code.code}\n```"
        await callback_query.answer(code_text, reply_markup=code_menu())
    except Exception as e:
        await callback_query.message.answer("An error occurred while fetching the code.")
        print(f"Error in show_code: {e}")


@code.callback_query(F.data.startswith("codes_page_"))
async def paginate_codes(callback_query: types.CallbackQuery):
    page = int(callback_query.data.split("_")[-1])
    user_id = callback_query.from_user.id
    try:
        codes = await Code.get_all_copy(user_id=user_id)
        if not codes:
            await callback_query.message.answer("You don't have any codes yet.")
            return
        await send_code_list(callback_query.message, codes, page)
    except Exception as e:
        await callback_query.message.answer("An error occurred while paginating codes.")


@code.message(F.text == "➕ Add Codes")
async def start_add_code(message: types.Message, state: FSMContext):
    await message.answer("Please send the title for your code:")
    await state.set_state(AddCodeState.waiting_for_title)


@code.message(StateFilter(AddCodeState.waiting_for_title))
async def add_code_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✅ Complete", callback_data="complete_code"))
    builder.add(InlineKeyboardButton(text="❌ Don't Save", callback_data="dont_save_code"))

    await message.answer(
        "Now send the code (send in multiple messages if needed). When done, click 'Complete' or 'Don't Save'.",
        reply_markup=builder.as_markup())
    await state.set_state(AddCodeState.waiting_for_code)


@code.message(StateFilter(AddCodeState.waiting_for_code))
async def collect_code_parts(message: types.Message, state: FSMContext):
    data = await state.get_data()
    code_parts = data.get("code_parts", [])
    code_parts.append(message.text)
    await state.update_data(code_parts=code_parts)


@code.callback_query(F.data == "complete_code")
async def save_complete_code(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    title = data.get("title")
    code_parts = data.get("code_parts", [])
    user_id = callback_query.from_user.id

    if not code_parts:
        await callback_query.message.answer("No code provided. Saving canceled.")
    else:
        code_text = "```\n" + "\n".join(code_parts) + "\n```"
        try:
            await Code.create(user_id=user_id, title=title, code=code_text)
            await callback_query.message.answer(
                f"Your code has been saved successfully!\n\nTitle: {title}\n{code_text}")
        except Exception as e:
            await callback_query.message.answer("Failed to save your code. Please try again.")

    await state.clear()


@code.callback_query(F.data == "dont_save_code")
async def discard_code(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Code entry has been canceled.")
    await state.clear()


@code.message(F.text == "⚙️ Settings")
async def open_settings(message: types.Message):
    await message.answer("Settings menu")
