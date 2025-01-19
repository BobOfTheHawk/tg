from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.buttons.inline import skip_description_button, delete_category_buttons, edit_category_buttons, \
    user_category_buttons
from bot.buttons.reply import admin_panel_keyboard
from bot.state import AddCategoryState, EditCategoryState
from db.models import Category

drugs = Router()


@drugs.message(F.text == "🚬 Drug")
async def drugmainmenu(message: Message):
    buttons = await user_category_buttons(page=1)  # Birinchi sahifani ko'rsatamiz
    if buttons.inline_keyboard:  # Agar kategoriyalar mavjud bo'lsa
        await message.answer(
            "📂 Choose a category:",
            reply_markup=buttons
        )
    else:
        await message.answer("❌ No categories available.")


@drugs.callback_query(F.data.startswith("category_page:"))
async def change_category_page(callback: CallbackQuery):
    page = int(callback.data.split(":")[1])  # Sahifa raqamini olish
    buttons = await user_category_buttons(page=page)  # Tegishli sahifa tugmalarini yaratish
    await callback.message.edit_reply_markup(reply_markup=buttons)  # Xabarni yangilash
    await callback.answer()  # Callbackni tasdiqlash


@drugs.callback_query(F.data.startswith("user_category:"))
async def show_category_info(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split(":")[1])  # Callbackdan kategoriya ID ni olish
    category = await Category.get(category_id)  # Kategoriya haqida ma'lumot olish

    if category:
        # Kategoriya haqida ma'lumotni ko'rsatish
        caption = (
            f"🗂 *Category:* {category.name}\n"
            f"📝 *Description:* {category.description or 'No description'}"
        )
        if category.photo:  # Agar rasm mavjud bo'lsa
            await callback.message.answer_photo(
                photo=category.photo, caption=caption, parse_mode='Markdown'
            )
        else:
            await callback.message.answer(caption, parse_mode='Markdown')
    else:
        await callback.message.answer("❌ Category not found.")

    await callback.answer()


@drugs.message(Command(commands=["adminpanel"]))
async def admin_panel(message: Message):
    if message.from_user.id == 7636819128 or message.from_user.id == 6635413428:
        await message.answer(
            "Welcome to the Admin Panel! 👨‍💻\nChoose an option below:",
            reply_markup=admin_panel_keyboard()
        )
    else:
        await message.answer("❌ You are not authorized to access the admin panel.")


@drugs.message(F.text == "➕ Add Category")
async def start_add_category(message: Message, state: FSMContext):
    if message.from_user.id == 7636819128 or message.from_user.id == 6635413428:
        await message.answer(
            "Please enter the **name** of the category:",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode='Markdown'
        )
        await state.set_state(AddCategoryState.name)
    else:
        await message.answer("❌ You are not authorized to add categories.")


@drugs.message(AddCategoryState.name)
async def add_category_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(
        "Please send a **photo** for the category:",
        parse_mode='Markdown'
    )
    await state.set_state(AddCategoryState.photo)


@drugs.message(AddCategoryState.photo, F.content_type == "photo")
async def add_category_photo(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(photo=photo_id)
    await message.answer(
        "Please enter a **description** for the category, or you can skip this step:",
        reply_markup=skip_description_button(),
        parse_mode='Markdown'
    )
    await state.set_state(AddCategoryState.description)


@drugs.message(AddCategoryState.description)
async def add_category_description(message: Message, state: FSMContext):
    description = message.text
    data = await state.get_data()
    await Category.create(
        name=data["name"],
        photo=data["photo"],
        description=description,
        parent_id=None
    )
    await message.answer(
        "✅ *Category successfully added!*",
        parse_mode='Markdown',
        reply_markup=admin_panel_keyboard()
    )
    await state.clear()


@drugs.callback_query(F.data == "asass")
async def skip_description(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await Category.create(
        name=data["name"],
        photo=data["photo"],
        description=None,
        parent_id=None
    )
    await callback.message.answer(
        "✅ *Category successfully added without a description!*",
        parse_mode='Markdown',
        reply_markup=admin_panel_keyboard()
    )
    await state.clear()
    await callback.answer()


@drugs.message(F.text == "🗑️ Delete Category")
async def start_delete_category(message: Message):
    if message.from_user.id == 7636819128 or message.from_user.id == 6635413428:
        buttons = await delete_category_buttons()
        if buttons.inline_keyboard:
            await message.answer(
                "Please select a category to delete:",
                reply_markup=buttons
            )
        else:
            await message.answer("❌ No categories found.")
    else:
        await message.answer("❌ You are not authorized to delete categories.")


@drugs.callback_query(F.data.startswith("delete_category:"))
async def delete_category(callback: CallbackQuery):
    category_id = int(callback.data.split(":")[1])
    category = await Category.get(category_id)
    if category:
        caption = (
            f"🗂 *Name:* {category.name}\n"
            f"📝 *Description:* {category.description or 'No description'}"
        )
        if category.photo:
            await callback.message.answer_photo(
                photo=category.photo, caption=caption, parse_mode='Markdown'
            )
        else:
            await callback.message.answer(
                text=caption, parse_mode='Markdown'
            )
        buttons = InlineKeyboardBuilder()
        buttons.add(
            InlineKeyboardButton(
                text="✅ Confirm Delete",
                callback_data=f"confirm_delete:{category_id}"
            ),
            InlineKeyboardButton(
                text="❌ Cancel",
                callback_data="cancel_delete"
            )
        )
        await callback.message.answer(
            "Do you really want to delete this category?",
            reply_markup=buttons.as_markup()
        )
    else:
        await callback.message.answer("❌ Category not found.")

    await callback.answer()


@drugs.callback_query(F.data.startswith("confirm_delete:"))
async def confirm_delete_category(callback: CallbackQuery):
    category_id = int(callback.data.split(":")[1])
    category = await Category.get(category_id)

    if category:
        await Category.delete(category_id)
        await callback.message.answer(
            f"✅ *Category '{category.name}' has been successfully deleted!*",
            parse_mode='Markdown'
        )
    else:
        await callback.message.answer("❌ Category not found.")

    await callback.answer()


@drugs.callback_query(F.data == "cancel_delete")
async def cancel_delete_category(callback: CallbackQuery):
    await callback.message.answer("❌ *Category deletion cancelled.*", parse_mode='Markdown')
    await callback.answer()


@drugs.message(F.text == "✏️ Edit Category")
async def start_edit_category(message: Message, state: FSMContext):
    if message.from_user.id == 7636819128 or message.from_user.id == 6635413428:  # Admin ID tekshiruvi
        buttons = await edit_category_buttons()
        if buttons.inline_keyboard:
            await message.answer(
                "Please select a category to edit:",
                reply_markup=buttons
            )
        else:
            await message.answer("❌ No categories found.")
    else:
        await message.answer("❌ You are not authorized to edit categories.")


# Callback for editing a specific category
@drugs.callback_query(F.data.startswith("edit_category:"))
async def edit_category(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split(":")[1])  # Extract category ID
    category = await Category.get(category_id)  # Get category from DB

    if category:
        # Save category_id to state
        await state.update_data(category_id=category_id)

        # Create inline buttons for editing options
        buttons = InlineKeyboardBuilder()
        buttons.add(
            InlineKeyboardButton(text="Edit Name", callback_data="edit_name"),
            InlineKeyboardButton(text="Edit Photo", callback_data="edit_photo"),
            InlineKeyboardButton(text="Edit Description", callback_data="des"),
            InlineKeyboardButton(text="❌ Cancel", callback_data="edd")
        )
        buttons.adjust(3)  # Arrange buttons in rows of 3

        # Send current category info and options
        await callback.message.answer(
            f"🗂 *Current Category Info:*\n"
            f"📌 *Name:* {category.name}\n"
            f"📝 *Description:* {category.description or 'No description'}\n",
            reply_markup=buttons.as_markup(),
            parse_mode='Markdown'
        )
    else:
        await callback.message.answer("❌ Category not found.")

    await callback.answer()  # Acknowledge callback query


@drugs.callback_query(F.data == "edit_name")
async def edit_name(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Please enter the new name for the category:")
    await state.set_state(EditCategoryState.edit_name)
    await callback.answer()


@drugs.message(EditCategoryState.edit_name)
async def update_name(message: Message, state: FSMContext):
    data = await state.get_data()
    category_id = data["category_id"]

    # Name yangilash
    await Category.update(category_id, name=message.text)
    await message.answer("✅ Category name successfully updated!")
    await state.clear()


@drugs.callback_query(F.data == "edit_photo")
async def edit_photo(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Please send the new photo for the category:")
    await state.set_state(EditCategoryState.edit_photo)
    await callback.answer()


@drugs.message(EditCategoryState.edit_photo, F.content_type == "photo")
async def update_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    category_id = data["category_id"]

    # Photo ID yangilash
    photo_id = message.photo[-1].file_id
    await Category.update(category_id, photo=photo_id)
    await message.answer("✅ Category photo successfully updated!")
    await state.clear()


# Callback to edit category description
@drugs.callback_query(F.data == "des")
async def edit_description(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Please enter the new description for the category:")
    await state.set_state(EditCategoryState.edit_description)
    await callback.answer()


# Message handler to update the category description
@drugs.message(EditCategoryState.edit_description)
async def update_description(message: Message, state: FSMContext):
    # Get category_id from state
    data = await state.get_data()
    category_id = data.get("category_id")

    if category_id:
        # Update category description
        await Category.update(category_id, description=message.text)
        await message.answer("✅ Category description successfully updated!")
    else:
        await message.answer("❌ Error: Category ID not found.")

    await state.clear()  # Clear state


@drugs.callback_query(F.data == "edd")
async def edd(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("❌ Edit operation cancelled.")
    await state.clear()
    await callback.answer()
