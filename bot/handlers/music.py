import os

from aiogram import Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from yt_dlp import YoutubeDL

music = Router()


@music.message(Command(commands=['download']))
async def start_download(message: types.Message, state: FSMContext):
    await message.reply("YouTube linkni yuboring.")
    await state.set_state("waiting_for_link")


@music.message(StateFilter("waiting_for_link"))
async def download_and_send_video(message: types.Message, state: FSMContext):
    url = message.text.strip()
    await message.reply("Video yuklanmoqda...")
    ydl_opts = {
        'format': 'bestvideo[height<=2160]+bestaudio/best',
        'outtmpl': 'output/%(title)s.%(ext)s',
        'merge_output_format': 'mp4',
        'cookiefile': 'cokies.txt'
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_file = ydl.prepare_filename(info_dict).replace('.webm', '.mp4')
        if os.path.exists(video_file):
            await message.reply("Video yuklandi, yuborilmoqda...")
            await message.answer_document(FSInputFile(video_file))
        else:
            await message.reply("Yuklangan video topilmadi.")
    except Exception as e:
        await message.reply(f"Xatolik yuz berdi: {str(e)}")
    finally:
        await state.clear()
