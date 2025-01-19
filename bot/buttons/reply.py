from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from db.models import User


def registration_menu():
    rkb = ReplyKeyboardBuilder()
    rkb.add(*[
        KeyboardButton(text="Share Phone number", request_contact=True),
    ])
    rkb.adjust(1, 1)
    return rkb.as_markup(resize_keyboard=True)


def admin_panel_keyboard():
    rkb = ReplyKeyboardBuilder()
    rkb.add(*[
        KeyboardButton(text="➕ Add Category"),
        KeyboardButton(text="🗑️ Delete Category"),
        KeyboardButton(text="✏️ Edit Category")
    ])
    rkb.adjust(2)
    return rkb.as_markup(resize_keyboard=True)


def main_menu():
    rkb = ReplyKeyboardBuilder()
    rkb.add(*[
        KeyboardButton(text="Cabinet"),
        KeyboardButton(text="🚬 Drug"),
        KeyboardButton(text="👨‍💻 My Codes"),
        KeyboardButton(text="my musics"),
        KeyboardButton(text="💸 Manage Monthly Spendings"),
        KeyboardButton(text="📅 Routine")
    ])
    rkb.adjust(3)
    return rkb.as_markup(resize_keyboard=True)


def code_menu():
    rkb = ReplyKeyboardBuilder()
    rkb.add(*[
        KeyboardButton(text="📜 My Codes"),  # Kodlar ro'yxati
        KeyboardButton(text="➕ Add Codes"),  # Yangi kod qo'shish
    ])
    rkb.add(*[
        KeyboardButton(text="⚙️ Settings"),  # Sozlamalar
        KeyboardButton(text="🔙 Back"),  # Ortga qaytish
    ])
    rkb.adjust(2)  # Har bir qatorda maksimal 2 ta tugma
    return rkb.as_markup(resize_keyboard=True)


def money_usage_menu():
    rkb = ReplyKeyboardBuilder()
    rkb.add(*[
        KeyboardButton(text="🔄 Create Monthly Spending"),
        KeyboardButton(text="🔙 Back")
    ])
    rkb.adjust(3)
    return rkb.as_markup(resize_keyboard=True)


def money_usage_menu_main():
    rkb = ReplyKeyboardBuilder()
    rkb.add(*[
        KeyboardButton(text="➕ Add Plan"),
        KeyboardButton(text="📄 My Plans"),
        KeyboardButton(text="💰 Money Remaining"),
        KeyboardButton(text="⚙️ Money Settings"),
        KeyboardButton(text="🔙 Back")
    ])
    rkb.adjust(3)
    return rkb.as_markup(resize_keyboard=True)


def routine_menu():
    rkb = ReplyKeyboardBuilder()
    rkb.add(*[
        KeyboardButton(text="📝 Create Routine"),
        KeyboardButton(text="📋 My Routines"),
        KeyboardButton(text="📅 Today's Routines"),
        KeyboardButton(text="⚙️ Settings"),
        KeyboardButton(text="🔙 Back to Main Menu")
    ])
    rkb.adjust(2, 2, 1)
    return rkb.as_markup(resize_keyboard=True)


async def settings_menu_r(user_id):
    user = await User.get(user_id)
    notification_status = user.notifications
    rkb = ReplyKeyboardBuilder()
    rkb.add(
        KeyboardButton(text="🗑 Delete Routine"),
        KeyboardButton(text="🔔 Turn On Notification" if not notification_status else "🔕 Turn Off Notification"),
        KeyboardButton(text="✏️ Change Routine"),
        KeyboardButton(text="🔙 Back to Settings Menu")
    )
    rkb.adjust(2, 1)
    return rkb.as_markup(resize_keyboard=True)


def currency_menu():
    rkb = ReplyKeyboardBuilder()
    rkb.add(*[
        KeyboardButton(text="💵 USD ($)"),
        KeyboardButton(text="🇺🇿 UZS (сум)"),
        KeyboardButton(text="🔙 Back")
    ])
    rkb.adjust(2, 1)
    return rkb.as_markup(resize_keyboard=True)



