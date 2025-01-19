from datetime import datetime

import pytz
from aiogram import Router, F, Bot
from aiogram import types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from bot.buttons.reply import routine_menu, main_menu, settings_menu_r
from bot.dispacher import TOKEN
from bot.state import RoutineStates
from db.models import Routine, User
from text import CHECK_EMOJI, CLOCK_EMOJI, CALENDAR_EMOJI, DESCRIPTION_EMOJI, WEEKDAY_MAP, NO_DATA_EMOJI, WEEKDAYS, \
    DELETE_CHECK_EMOJI

routine = Router()


@routine.message(F.text == "🔙 Back to Main Menu")
async def back_to_main_menu(message: types.Message):
    await message.answer("Welcome back to the main menu!", reply_markup=main_menu())


@routine.message(F.text == "🔙 Back to Settings Menu")
async def back_to_settings_menu(message: types.Message):
    await message.answer("🔄 *Settings menyuga qaytish:*", parse_mode="Markdown")
    await message.answer("Welcome back to the settings menu!", reply_markup=routine_menu())


async def build_weekday_keyboard(selected_days):
    builder = InlineKeyboardBuilder()
    for i, day in enumerate(WEEKDAYS):
        if day in selected_days:
            builder.button(text=f"{day} ✅", callback_data=f"day_{day}")
        else:
            builder.button(text=day, callback_data=f"day_{day}")
        if (i + 1) % 3 == 0:
            builder.adjust(3)
    builder.button(text="✅ Tugallash", callback_data="finish_days")
    builder.button(text="❌ Bekor qilish", callback_data="cancel")
    builder.adjust(3, 3, 1, 2)
    return builder.as_markup()


async def delete_previous_messages(message: types.Message, state: FSMContext):
    data = await state.get_data()
    previous_message_id = data.get("previous_message_id")
    user_message_ids = data.get("user_message_ids", [])
    for msg_id in [previous_message_id] + user_message_ids:
        try: await message.bot.delete_message(message.chat.id, msg_id)
        except: pass
    await state.update_data(previous_message_id=None, user_message_ids=[])


@routine.message(F.text == "📝 Create Routine")
async def routine_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user = await User.get(user_id)
    if not user:
        await User.create(id=user_id, fullname=message.from_user.full_name, phone_number=None, language="EN")
    await delete_previous_messages(message, state)
    sent_message = await message.answer("📋 *Iltimos, rutinga nom kiriting:*", parse_mode="Markdown")
    await state.update_data(previous_message_id=sent_message.message_id, user_message_ids=[message.message_id])
    await state.set_state(RoutineStates.awaiting_routine_title)


@routine.message(F.text == "📅 Routine")
async def routine_handler(message: Message):
    await message.answer("📋 *Rutinani tanlang:*", parse_mode="Markdown", reply_markup=routine_menu())


@routine.message(RoutineStates.awaiting_routine_title)
async def process_routine_title(message: Message, state: FSMContext):
    data = await state.get_data()
    user_message_ids = data.get("user_message_ids", [])
    user_message_ids.append(message.message_id)
    await state.update_data(user_message_ids=user_message_ids)

    await delete_previous_messages(message, state)
    await state.update_data(title=message.text)

    builder = InlineKeyboardBuilder()
    builder.button(text="⏭️ Skip", callback_data="skip_description")
    builder.button(text="❌ Bekor qilish", callback_data="cancel")

    sent_message = await message.answer("📝 *Rutinga tavsif kiriting yoki 'skip' tugmasini bosing:*",
                                        reply_markup=builder.as_markup(), parse_mode="Markdown")
    await state.update_data(previous_message_id=sent_message.message_id)
    await state.set_state(RoutineStates.awaiting_routine_description)


@routine.callback_query(lambda c: c.data == "skip_description")
async def skip_description(callback_query: types.CallbackQuery, state: FSMContext):
    await delete_previous_messages(callback_query.message, state)
    await state.update_data(description=None)

    selected_days = []
    keyboard = await build_weekday_keyboard(selected_days)
    sent_message = await callback_query.message.answer("📅 *Hafta kunlarini tanlang:*", reply_markup=keyboard,
                                                       parse_mode="Markdown")
    await state.update_data(previous_message_id=sent_message.message_id)
    await state.set_state(RoutineStates.awaiting_routine_days)
    await callback_query.answer()


@routine.callback_query(lambda c: c.data == "cancel")
async def cancel(callback_query: types.CallbackQuery, state: FSMContext):
    await delete_previous_messages(callback_query.message, state)
    await state.clear()
    await callback_query.message.answer("🛑 *Canceling... *", reply_markup=routine_menu(),
                                        parse_mode="Markdown")


@routine.message(StateFilter(RoutineStates.awaiting_routine_description))
async def process_description(message: Message, state: FSMContext):
    data = await state.get_data()
    user_message_ids = data.get("user_message_ids", [])
    user_message_ids.append(message.message_id)
    await state.update_data(user_message_ids=user_message_ids)

    await delete_previous_messages(message, state)
    await state.update_data(description=message.text)

    selected_days = []
    keyboard = await build_weekday_keyboard(selected_days)
    sent_message = await message.answer("📅 *Hafta kunlarini tanlang:*", reply_markup=keyboard, parse_mode="Markdown")
    await state.update_data(previous_message_id=sent_message.message_id)
    await state.set_state(RoutineStates.awaiting_routine_days)


@routine.callback_query(lambda c: c.data.startswith("day_"))
async def process_day_selection(callback_query: types.CallbackQuery, state: FSMContext):
    selected_day = callback_query.data.split("_")[1]
    data = await state.get_data()
    selected_days = data.get("selected_days", [])

    if selected_day in selected_days:
        selected_days.remove(selected_day)
    else:
        selected_days.append(selected_day)

    await state.update_data(selected_days=selected_days)
    keyboard = await build_weekday_keyboard(selected_days)
    await callback_query.message.edit_reply_markup(reply_markup=keyboard)


async def ask_routine_hour(message):
    builder = InlineKeyboardBuilder()
    for hour in range(0, 25):
        builder.button(text=f"🕒 {hour:02d}:00", callback_data=f"hour_{hour:02d}")
        if (hour + 1) % 6 == 0:
            builder.adjust(6)
    builder.button(text="❌ Bekor qilish", callback_data="cancel")
    builder.adjust(5)
    sent_message = await message.answer("⌛ *Soatni tanlang:*", reply_markup=builder.as_markup(), parse_mode="Markdown")
    return sent_message


@routine.callback_query(lambda c: c.data == "finish_days")
async def finish_days_selection(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_days = data.get("selected_days", [])

    if not selected_days:
        await callback_query.message.answer("Iltimos, hech bo'lmaganda bir kun tanlang.")
        return

    await delete_previous_messages(callback_query.message, state)
    sent_message = await callback_query.message.answer(f"📅 *Tanlangan kunlar:* {', '.join(selected_days)}",
                                                       parse_mode="Markdown")
    await state.update_data(previous_message_id=sent_message.message_id)
    await state.set_state(RoutineStates.awaiting_routine_end_time)
    await ask_routine_hour(callback_query.message)


@routine.callback_query(lambda c: c.data.startswith("hour_"))
async def process_hour_selection(callback_query: types.CallbackQuery, state: FSMContext):
    hour = callback_query.data.split("_")[1]
    await state.update_data(hour=hour)

    builder = InlineKeyboardBuilder()
    builder.button(text="00", callback_data=f"minute_00")
    builder.button(text="30", callback_data=f"minute_30")
    builder.button(text="❌ Bekor qilish", callback_data="cancel")
    builder.adjust(3)

    sent_message = await callback_query.message.answer("🕑 *Daqiqani tanlang:*", reply_markup=builder.as_markup(),
                                                       parse_mode="Markdown")
    await state.update_data(previous_message_id=sent_message.message_id)


@routine.callback_query(lambda c: c.data.startswith("minute_"))
async def process_minute_selection(callback_query: types.CallbackQuery, state: FSMContext):
    minute = callback_query.data.split("_")[1]
    data = await state.get_data()
    hour = data['hour']
    time_str = f"{hour}:{minute}"
    await state.update_data(end_time=time_str)

    user_id = callback_query.from_user.id
    title = data.get('title')
    description = data.get('description')
    selected_days = data.get('selected_days', [])

    end_time = datetime.strptime(time_str, "%H:%M").time()
    days_str = ",".join(selected_days)

    await Routine.create(
        user_id=user_id,
        title=title,
        description=description,
        end_time=end_time,
        days=days_str
    )

    await delete_previous_messages(callback_query.message, state)
    await callback_query.message.answer(
        f"✅ *Routine {title} yaratildi!* \n🕓 *Vaqt:* {end_time}\n📅 *Kunlar:* {', '.join(selected_days)}",
        parse_mode="Markdown", reply_markup=routine_menu())
    await state.clear()


@routine.message(F.text == "📋 My Routines")
async def show_user_routines(message: types.Message):
    routines = await Routine.get_all_copy(user_id=message.from_user.id)
    if not routines:
        await message.answer(f"{NO_DATA_EMOJI} *Sizda hozircha hech qanday routine mavjud emas.*",
                             parse_mode="Markdown")
        return
    routine_texts = []
    for routine in routines:
        title = routine.title
        end_time = routine.end_time.strftime("%H:%M")
        days = routine.days.split(",")
        days_text = ', '.join(days)
        description = routine.description or "Yo'q"

        routine_texts.append(
            f"{CHECK_EMOJI} *{title}*\n"
            f"{CLOCK_EMOJI} *Vaqt:* {end_time}\n"
            f"{CALENDAR_EMOJI} *Kunlar:* {days_text}\n"
            f"{DESCRIPTION_EMOJI} *Tavsif:* {description}\n"
        )
    response_text = "\n\n".join(routine_texts)
    await message.answer(response_text, parse_mode="Markdown")


@routine.message(F.text == "📅 Today's Routines")
async def show_today_routines(message: types.Message):
    today_weekday = WEEKDAY_MAP[datetime.now().weekday()]
    routines = await Routine.get_all(order_fields=["created_at"])
    today_routines = []
    for routine in routines:
        days = routine.days.split(",")
        if today_weekday in days:
            end_time = routine.end_time.strftime("%H:%M")
            description = routine.description if routine.description else "Yo'q"
            today_routines.append(
                f"{CHECK_EMOJI} *{routine.title}*\n"
                f"{CLOCK_EMOJI} *Vaqt:* {end_time}\n"
                f"{CALENDAR_EMOJI} *Kunlar:* {', '.join(days)}\n"
                f"📝 *Tavsif:* {description}\n"
            )
    if not today_routines:
        await message.answer(f"{NO_DATA_EMOJI} *Bugungi routine mavjud emas.*", parse_mode="Markdown")
    else:
        response_text = "\n\n".join(today_routines)
        await message.answer(response_text, parse_mode="Markdown")


@routine.message(F.text == "⚙️ Settings")
async def settings_handler(message: Message):
    user_id = message.from_user.id
    await message.answer("⚙️ *Settings Menu:*", reply_markup=await settings_menu_r(user_id), parse_mode="Markdown")


@routine.message(F.text.in_({"🔔 Turn On Notification", "🔕 Turn Off Notification"}))
async def toggle_notification_handler(message: Message):
    user_id = message.from_user.id
    user = await User.get(user_id)
    new_status = not user.notifications
    await User.update(user_id, notifications=new_status)
    status_text = "on" if new_status else "off"
    await message.answer(f"Notifications have been turned {status_text}.")
    await message.answer("⚙️ *Settings Menu:*", reply_markup=await settings_menu_r(user_id), parse_mode="Markdown")


@routine.message(F.text == "🗑 Delete Routine")
async def display_routines_for_deletion(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    routines = await Routine.get_all(order_fields=["created_at"])

    if not routines:
        await message.answer(f"🚫 *Sizda hozircha hech qanday routine mavjud emas.*", parse_mode="Markdown")
        return

    builder = InlineKeyboardBuilder()
    selected_routines = []
    routine_buttons = []

    for index, routine in enumerate(routines, start=1):
        button_text = f"{index}. {routine.title}"
        builder.button(text=button_text, callback_data=f"select_routine_{routine.id}")

    builder.button(text="🗑 Delete All Selected", callback_data="delete_all_routines")
    builder.adjust(1)

    await state.update_data(selected_routines=selected_routines, routine_buttons=routine_buttons)
    await message.answer("📋 *Rutinani o'chirish uchun tanlang:*", reply_markup=builder.as_markup(),
                         parse_mode="Markdown")


@routine.callback_query(lambda c: c.data.startswith("select_routine_"))
async def select_routine_for_deletion(callback_query: types.CallbackQuery, state: FSMContext):
    routine_id = int(callback_query.data.split("_")[2])
    data = await state.get_data()
    selected_routines = data.get("selected_routines", [])
    routine_buttons = data.get("routine_buttons", [])

    if routine_id in selected_routines:
        selected_routines.remove(routine_id)
        routine_buttons = [r for r in routine_buttons if r["id"] != routine_id]
    else:
        selected_routines.append(routine_id)
        routine_buttons.append({"id": routine_id, "selected": True})

    await state.update_data(selected_routines=selected_routines, routine_buttons=routine_buttons)

    builder = InlineKeyboardBuilder()
    routines = await Routine.get_all(order_fields=["created_at"])

    for index, routine in enumerate(routines, start=1):
        selected = DELETE_CHECK_EMOJI if routine.id in selected_routines else ""
        button_text = f"{index}. {routine.title} {selected}"
        builder.button(text=button_text, callback_data=f"select_routine_{routine.id}")

    builder.button(text="🗑 Delete All Selected", callback_data="delete_all_routines")
    builder.adjust(1)

    await callback_query.message.edit_reply_markup(reply_markup=builder.as_markup())
    await callback_query.answer()


@routine.callback_query(lambda c: c.data == "delete_all_routines")
async def delete_selected_routines(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_routines = data.get("selected_routines", [])

    if not selected_routines:
        await callback_query.answer("Hech qanday routine tanlanmagan.", show_alert=True)
        return

    for routine_id in selected_routines:
        await Routine.delete(routine_id)

    await callback_query.message.answer(f"🗑 *{len(selected_routines)} ta routine muvaffaqiyatli o'chirildi.*",
                                        parse_mode="Markdown")
    await state.clear()
    await callback_query.message.delete()


@routine.message(F.text == "✏️ Change Routine")
async def display_routines_for_editing(message: types.Message, state: FSMContext):
    routines = await Routine.get_all(order_fields=["created_at"])

    if not routines:
        await message.answer(f"🚫 *Sizda hozircha hech qanday routine mavjud emas.*", parse_mode="Markdown")
        return

    builder = InlineKeyboardBuilder()

    for index, routine in enumerate(routines, start=1):
        button_text = f"{index}. {routine.title}"
        builder.button(text=button_text, callback_data=f"edit_routine_{routine.id}")

    builder.adjust(1)
    await message.answer("✏️ *Rutinani tahrirlash uchun tanlang:*", reply_markup=builder.as_markup(),
                         parse_mode="Markdown")


# Step 2: Select the routine for editing
@routine.callback_query(lambda c: c.data.startswith("edit_routine_"))
async def select_routine_for_editing(callback_query: types.CallbackQuery, state: FSMContext):
    routine_id = int(callback_query.data.split("_")[2])
    routine = await Routine.get(routine_id)

    await state.update_data(selected_routine_id=routine_id)

    builder = InlineKeyboardBuilder()
    builder.button(text="📝 Title", callback_data="edit_title")
    builder.button(text="⏰ End Time", callback_data="edit_end_time")
    builder.button(text="📅 Days", callback_data="edit_days")
    builder.button(text="📝 Description", callback_data="edit_description")
    builder.button(text="🔙 Bekor qilish", callback_data="cancel_edit")

    builder.adjust(2, 2, 1)
    await callback_query.message.answer(f"✏️ *{routine.title} tahrirlanmoqda:*", reply_markup=builder.as_markup(),
                                        parse_mode="Markdown")
    await callback_query.answer()


# Step 3a: Edit Title
@routine.callback_query(lambda c: c.data == "edit_title")
async def edit_routine_title(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("✏️ Yangi nomni kiriting:")
    await state.set_state(RoutineStates.awaiting_new_title)


@routine.message(RoutineStates.awaiting_new_title)
async def process_new_title(message: types.Message, state: FSMContext):
    data = await state.get_data()
    routine_id = data.get("selected_routine_id")
    new_title = message.text

    await Routine.update(routine_id, title=new_title)
    await message.answer(f"✅ Title yangilandi: {new_title}")
    await state.clear()


@routine.callback_query(lambda c: c.data == "edit_description")
async def edit_routine_description(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("📝 Yangi tavsifni kiriting:")
    await state.set_state(RoutineStates.awaiting_new_description)


@routine.message(RoutineStates.awaiting_new_description)
async def process_new_description(message: types.Message, state: FSMContext):
    data = await state.get_data()
    routine_id = data.get("selected_routine_id")
    new_description = message.text

    await Routine.update(routine_id, description=new_description)
    await message.answer(f"✅ Tavsif yangilandi: {new_description}")
    await state.clear()


# Cancel Editing
@routine.callback_query(lambda c: c.data == "cancel_edit")
async def cancel_editing(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_query.message.answer("✏️ Tahrirlash bekor qilindi.",
                                        reply_markup=settings_menu_r(callback_query.from_user.id))


async def notify_user_of_routine():
    tashkent_timezone = pytz.timezone('Asia/Tashkent')
    current_time = datetime.now(tashkent_timezone).strftime("%H:%M")

    routines = await Routine.get_all()
    for routine in routines:
        if routine.end_time.strftime("%H:%M") == current_time:
            try:
                message_text = (
                    f"Did you finish your routine *{routine.title}* scheduled for `{routine.end_time.strftime('%H:%M')}`\\?\n\n"
                    "Please click one of the buttons below to respond:"
                )
                bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
                await bot.send_message(
                    routine.user_id,
                    message_text,
                    reply_markup=InlineKeyboardBuilder()
                    .button(text="✅ Yes, I did!", callback_data="routine_done")
                    .button(text="❌ Not yet", callback_data="routine_not_done")
                    .as_markup(),
                    parse_mode=ParseMode.MARKDOWN_V2
                )
            except Exception as e:
                print(f"Failed to send message to user {routine.user_id}: {str(e)}")


scheduler = AsyncIOScheduler()
scheduler.add_job(notify_user_of_routine, CronTrigger(minute='*'), timezone='Asia/Tashkent')


@routine.callback_query(lambda c: c.data == "routine_done")
async def routine_done(callback_query: types.CallbackQuery):
    await callback_query.message.answer(
        "🎉 Great! Keep up the good work! 💪"
    )

    await callback_query.answer()


@routine.callback_query(lambda c: c.data == "routine_not_done")
async def routine_not_done(callback_query: types.CallbackQuery):
    await callback_query.message.answer(
        "Please 🙏 Don't Skip Your Routine 📋"
    )
    await callback_query.answer()
