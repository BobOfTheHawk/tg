import os
import subprocess
from os.path import join

from aiogram import Router, types, F, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ContentType, ParseMode
from aiogram.filters import Command
from aiogram.types import FSInputFile

from bot.dispacher import TOKEN

backup = Router()

# media_handlers = {
#     ContentType.PHOTO: lambda message: message.answer_photo(message.photo[-1].file_id,
#                                                             caption="Siz yuborgan rasm qaytmoqda!"),
#     ContentType.VIDEO: lambda message: message.answer_video(message.video.file_id,
#                                                             caption="Siz yuborgan video qaytmoqda!"),
#     ContentType.AUDIO: lambda message: message.answer_audio(message.audio.file_id,
#                                                             caption="Siz yuborgan audio qaytmoqda!"),
#     ContentType.VOICE: lambda message: message.answer_voice(message.voice.file_id,
#                                                             caption="Siz yuborgan ovoz qaytmoqda!"),
#     ContentType.DOCUMENT: lambda message: message.answer_document(message.document.file_id,
#                                                                   caption="Siz yuborgan hujjat qaytmoqda!"),
# }
#
#
# @backup.message(F.content_type.in_(
#     [ContentType.PHOTO, ContentType.VIDEO, ContentType.AUDIO, ContentType.VOICE, ContentType.DOCUMENT]))
# async def handle_media(message: types.Message):
#     handler = media_handlers.get(message.content_type)
#     if handler:
#         await handler(message)


async def send_doc(bot: Bot, my_id, path):
    file = FSInputFile(join(path), "backupfile.tar")
    await bot.send_document(chat_id=my_id, document=file)


@backup.message(Command(commands=["backup"]))
async def backup1(message: types.Message):
    await message.answer("Starting backup process...")
    await message.answer("FAQAT DOCKER COMPOSE BILAN ISHLAYDI")
    await message.answer("FAQAT DOCKER COMPOSE BILAN ISHLAYDI")
    bash_script_path = r'/app/backup_script.sh'
    bash_script_content = """
    BACKUP_DIR='/app/backup'
    FILE_NAME=$BACKUP_DIR/$(date +'%d-%m-%Y-%H-%M-%S').tar
    PGPASSWORD='1'
    docker exec -e PGPASSWORD=$PGPASSWORD pg pg_dump -U postgres -h localhost -p 5432 -d mybotmain -F tar -f /tmp/db_backup.tar
    docker cp pg:/tmp/db_backup.tar $FILE_NAME
    echo $FILE_NAME
    """
    with open(bash_script_path, 'w') as file:
        file.write(bash_script_content)
    os.chmod(bash_script_path, 0o755)
    try:
        result = subprocess.run(
            ['/bin/bash', bash_script_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        output = result.stdout.decode('utf-8').strip()
        error_output = result.stderr.decode('utf-8')

        if output:
            backup_file_path = output
            await message.answer(f"Backup completed successfully! File: {backup_file_path}")
            bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
            my_id = message.from_user.id
            await send_doc(bot, my_id, backup_file_path)

        if error_output:
            await message.answer(f"Errors: {error_output}")

    except subprocess.CalledProcessError as e:
        await message.answer(f"An error occurred during the backup process: {e.stderr.decode('utf-8')}")


@backup.message(Command(commands=["send_10msg"]))
async def sendmsg(message: types.Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply("Iltimos, foydalanuvchi ID-ni kiriting. Misol: /send_10msg <user_id>")
        return

    try:
        user_id = int(args[1])  # Extract user ID
    except ValueError:
        await message.reply("Iltimos, to'g'ri foydalanuvchi ID-ni kiriting.")
        return

    try:
        for i in range(10):
            await message.bot.send_message(chat_id=user_id, text="Salom!")
        await message.reply(f"10 ta 'Salom!' xabar {user_id} ga yuborildi.")
    except Exception as e:
        await message.reply(f"Xatolik yuz berdi: {str(e)}")
