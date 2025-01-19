from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db.models import Category


def inline_advertisement_button():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="Get 50% Off Now!", url="https://your-promo-link.com")
    )
    return builder.as_markup()


def skip_description_button():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="➡️ Skip Description", callback_data="asass")
    )
    return builder.as_markup()


async def edit_category_buttons():
    builder = InlineKeyboardBuilder()
    categories = await Category.get_all(order_fields=["name"])
    for category in categories:
        builder.add(
            InlineKeyboardButton(text=category.name, callback_data=f"edit_category:{category.id}")
        )
    builder.adjust(3)
    return builder.as_markup()


async def delete_category_buttons():
    builder = InlineKeyboardBuilder()
    categories = await Category.get_all(order_fields=["name"])
    for category in categories:
        builder.add(
            InlineKeyboardButton(text=category.name, callback_data=f"delete_category:{category.id}")
        )
    builder.adjust(3, 3)
    return builder.as_markup()


async def user_category_buttons(page: int = 1, per_page: int = 8):
    builder = InlineKeyboardBuilder()
    categories = await Category.get_all(order_fields=["name"])  # Barcha kategoriyalarni olamiz

    # Sahifalash
    start = (page - 1) * per_page
    end = start + per_page
    paginated_categories = categories[start:end]

    # Tugmalarni qo'shish
    for category in paginated_categories:
        builder.add(
            InlineKeyboardButton(text=category.name, callback_data=f"user_category:{category.id}")
        )

    # Next va Previous tugmalarini qo'shish
    if page > 1:
        builder.add(InlineKeyboardButton(text="⬅️ Previous", callback_data=f"category_page:{page - 1}"))
    if end < len(categories):
        builder.add(InlineKeyboardButton(text="➡️ Next", callback_data=f"category_page:{page + 1}"))

    builder.adjust(2)  # Har bir qatorga 2 tadan tugma joylashtirish
    return builder.as_markup()
