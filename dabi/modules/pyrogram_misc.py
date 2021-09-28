import os
import sys

from pyrogram import Client, filters
from pyrogram.types import User, Message

from dabi import SUDO_USERS, pbot


@pbot.on_message(filters.command("restart") & filters.user(SUDO_USERS))
async def restart(c: Client, m: Message):
    await m.reply_text("Restarting...")
    args = [sys.executable, "-m", "dabi"]
    os.execl(sys.executable, *args)