import os
import asyncio
from mutagen.mp3 import MP3
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from database import get_last_tracks, get_all_tracks
from metrics import TRACKS_SENT

CHANNEL_CHAT_ID = os.getenv("CHANNEL_CHAT_ID")


async def send_menu_to_channel(app):
    keyboard = [
        [
            InlineKeyboardButton("NITRO⚡️PULSE", callback_data="pulse"),
            InlineKeyboardButton("NITRO⚡️BEAT", callback_data="beat")
        ]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await app.bot.send_message(chat_id=CHANNEL_CHAT_ID,
                               text="Выберите плейлист:",
                               reply_markup=markup)


async def play_radio(context: ContextTypes.DEFAULT_TYPE, chat_id: int, playlist_name: str):
    """Continuously stream playlist tracks to the given chat."""
    tracks = get_all_tracks(playlist_name)
    if not tracks:
        await context.bot.send_message(chat_id=chat_id, text="Треков пока нет")
        return
    await context.bot.send_message(chat_id=chat_id,
                                   text=f"▶️ Радио {playlist_name.upper()} запущено")
    while True:
        for track in tracks:
            with open(track["file_path"], "rb") as audio:
                await context.bot.send_audio(chat_id=chat_id,
                                             audio=audio,
                                             title=track["title"])
            TRACKS_SENT.labels(playlist_name).inc()
            try:
                duration = MP3(track["file_path"]).info.length
            except Exception:
                duration = 0
            await asyncio.sleep(duration)
        tracks = get_all_tracks(playlist_name)


async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    playlist_name = query.data
    tracks = get_last_tracks(playlist_name, 3)
    if not tracks:
        await query.edit_message_text("Треков пока нет")
        return

    for track in tracks:
        with open(track["file_path"], "rb") as audio:
            await context.bot.send_audio(chat_id=query.from_user.id,
                                         audio=audio,
                                         title=track["title"])
        TRACKS_SENT.labels(playlist_name).inc()

    await query.edit_message_text(f"Отправлено {len(tracks)} трек(а)")
    context.application.create_task(play_radio(context, query.from_user.id, playlist_name))


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Нажмите кнопку в канале, чтобы получить треки")
