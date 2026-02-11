import os
import asyncio
import re
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError
from telethon.tl.types import DocumentAttributeFilename

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
string_session = os.getenv("STRING_SESSION")

SOURCE_CHATS = [-1003693431295, -1003029961250]
TARGET_CHAT = -1001754899629

FORWARD_DELAY = 2

client = TelegramClient(StringSession(string_session), api_id, api_hash)

def clean_filename(name):
    name = re.sub(r'@\S+', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def get_file_info(message):
    filename = "Unknown"
    size = 0

    if message.document:
        size = message.document.size
        for attr in message.document.attributes:
            if isinstance(attr, DocumentAttributeFilename):
                filename = attr.file_name

    elif message.video:
        size = message.video.size
        filename = "Video_File"

    filename = clean_filename(filename)

    if size >= 1024**3:
        size_text = f"{round(size / (1024**3), 2)} GB"
    else:
        size_text = f"{round(size / (1024**2), 2)} MB"

    return filename, size_text

@client.on(events.NewMessage(chats=SOURCE_CHATS))
async def handler(event):
    message = event.message

    if not (message.video or message.document):
        return

    while True:
        try:
            filename, size_text = get_file_info(message)

            caption = (
                f"📂 File Name : {filename}\n"
                f"⚙️ Size : {size_text}"
            )

            await client.send_message(
                TARGET_CHAT,
                caption,
                file=message.media
            )

            print(f"Sent: {filename}")
            await asyncio.sleep(FORWARD_DELAY)
            break

        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)
        except Exception as e:
            print(e)
            break

async def main():
    await client.start()
    print("Bot running successfully...")
    await client.run_until_disconnected()

asyncio.run(main())
