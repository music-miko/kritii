import datetime

from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardMarkup, Message

from config import Config
from Music.core.calls import hellmusic
from Music.core.clients import hellbot
from Music.core.database import db
from Music.core.decorators import UserWrapper, check_mode
from Music.helpers.buttons import Buttons
from Music.helpers.formatters import formatter
from Music.helpers.strings import TEXTS
from Music.helpers.users import MusicUser
from Music.utils.youtube import ytube


@hellbot.app.on_message(filters.command(["start", "alive"]) & ~Config.BANNED_USERS)
@check_mode
async def start(_, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        if len(message.command) > 1:
            deep_cmd = message.text.split(None, 1)[1]

            # /start song_xxx deep-link
            if deep_cmd.startswith("song"):
                results = await ytube.get_data(deep_cmd.split("_", 1)[1], True)
                about = TEXTS.ABOUT_SONG.format(
                    results[0]["title"],
                    results[0]["channel"],
                    results[0]["published"],
                    results[0]["views"],
                    results[0]["duration"],
                    hellbot.app.mention,
                )
                await message.reply_photo(
                    results[0]["thumbnail"],
                    caption=about,
                    reply_markup=InlineKeyboardMarkup(
                        Buttons.song_details_markup(
                            results[0]["link"],
                            results[0]["ch_link"],
                        )
                    ),
                )
                return

            # /start user_123 deep-link (from leaderboard etc.)
            elif deep_cmd.startswith("user"):
                userid = int(deep_cmd.split("_", 1)[1])
                userdbs = await db.get_user(userid)

                # user not found in db
                if not userdbs:
                    await message.reply_text(
                        "This user is not registered in my database yet or was removed."
                    )
                    return

                # Safely fetch fields with defaults to avoid KeyError
                songs = int(userdbs.get("songs_played", 0) or 0)
                level = MusicUser.get_user_level(songs)

                user_name = (
                    userdbs.get("user_name")
                    or userdbs.get("first_name")
                    or "Unknown User"
                )
                user_id = userdbs.get("user_id", userid)
                join_date = userdbs.get("join_date") or "Unknown"

                to_send = TEXTS.ABOUT_USER.format(
                    user_name,
                    user_id,
                    level,
                    songs,
                    join_date,
                    hellbot.app.mention,
                )
                await message.reply_text(
                    to_send,
                    reply_markup=InlineKeyboardMarkup(Buttons.close_markup()),
                    disable_web_page_preview=True,
                )
                return

            # /start help deep-link
            elif deep_cmd.startswith("help"):
                await message.reply_text(
                    TEXTS.HELP_PM.format(hellbot.app.mention),
                    reply_markup=InlineKeyboardMarkup(Buttons.help_pm_markup()),
                )
                return

        # Normal /start in PM
        await message.reply_text(
            TEXTS.START_PM.format(
                message.from_user.first_name,
                hellbot.app.mention,
                hellbot.app.username,
            ),
            reply_markup=InlineKeyboardMarkup(
                Buttons.start_pm_markup(hellbot.app.username)
            ),
            disable_web_page_preview=True,
        )

    elif message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        await message.reply_text(TEXTS.START_GC)


@hellbot.app.on_message(filters.command("help") & ~Config.BANNED_USERS)
async def help(_, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        await message.reply_text(
            TEXTS.HELP_PM.format(hellbot.app.mention),
            reply_markup=InlineKeyboardMarkup(Buttons.help_pm_markup()),
        )
    elif message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        await message.reply_text(
            TEXTS.HELP_GC,
            reply_markup=InlineKeyboardMarkup(
                Buttons.help_gc_markup(hellbot.app.username)
            ),
        )


@hellbot.app.on_message(filters.command("ping") & ~Config.BANNED_USERS)
async def ping(_, message: Message):
    start_time = datetime.datetime.now()
    hell = await message.reply_text("Pong!")
    calls_ping = await hellmusic.ping()
    stats = await formatter.system_stats()
    end_time = (datetime.datetime.now() - start_time).microseconds / 1000
    await hell.edit_text(
        TEXTS.PING_REPLY.format(end_time, stats["uptime"], calls_ping),
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(Buttons.close_markup()),
    )


@hellbot.app.on_message(filters.command("sysinfo") & ~Config.BANNED_USERS)
@check_mode
@UserWrapper
async def sysinfo(_, message: Message):
    stats = await formatter.system_stats()
    await message.reply_text(
        TEXTS.SYSTEM.format(
            stats["core"],
            stats["cpu"],
            stats["disk"],
            stats["ram"],
            stats["uptime"],
            hellbot.app.mention,
        ),
        reply_markup=InlineKeyboardMarkup(Buttons.close_markup()),
    )
