import os
import asyncio
from dotenv import load_dotenv
from pyrogram import Client
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
from pytgcalls.types import StreamType
import ffmpeg
from database import get_full_playlist

load_dotenv()

API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
CHANNEL_CHAT_ID = os.getenv("CHANNEL_CHAT_ID")


def get_duration(path: str) -> float:
    try:
        probe = ffmpeg.probe(path)
        for stream in probe["streams"]:
            if stream.get("codec_type") == "audio":
                return float(stream.get("duration", 0))
    except Exception:
        pass
    return 0.0


async def stream_playlist(playlist_name: str = "pulse"):
    if not (API_ID and API_HASH and SESSION_STRING and CHANNEL_CHAT_ID):
        raise RuntimeError("Env variables for userbot are not set")

    client = Client("userbot", session_string=SESSION_STRING, api_id=API_ID, api_hash=API_HASH)
    await client.start()

    group = PyTgCalls(client)
    await group.start()

    playlist = get_full_playlist(playlist_name)
    if not playlist:
        print("Playlist empty")
        return

    index = 0
    chat_id = CHANNEL_CHAT_ID
    await group.join_group_call(chat_id, AudioPiped(playlist[index], file_parameters=["-re"]), stream_type=StreamType().pulse_stream)
    duration = get_duration(playlist[index])
    await asyncio.sleep(duration + 1)

    index = (index + 1) % len(playlist)
    while True:
        file_path = playlist[index]
        try:
            await group.change_stream(chat_id, AudioPiped(file_path, file_parameters=["-re"]))
            duration = get_duration(file_path)
            await asyncio.sleep(duration + 1)
        except Exception as e:
            print("Stream error", e)
            await asyncio.sleep(5)
            try:
                await group.join_group_call(chat_id, AudioPiped(file_path, file_parameters=["-re"]), stream_type=StreamType().pulse_stream)
            except Exception:
                pass
        index = (index + 1) % len(playlist)


if __name__ == "__main__":
    asyncio.run(stream_playlist())
