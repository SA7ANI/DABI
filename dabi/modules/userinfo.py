#HP Sytem from https://github.com/AnimeKaizoku/SaitamaRobot

import html
import os
import requests

from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import ChannelParticipantsAdmins
from telethon import events

from telegram import MAX_MESSAGE_LENGTH, ParseMode, Update
from telegram.ext import CallbackContext
from telegram.ext.dispatcher import run_async
from telegram.error import BadRequest
from telegram.utils.helpers import escape_markdown, mention_html

from dabi import (client, OWNER_ID, SUDO_USERS, SUPPORT_USERS, WHITELIST_USERS,
                    dispatcher, spamwtc)
from dabi.__main__ import TOKEN, USER_INFO
import dabi.modules.sql.userinfo_sql as sql
from dabi.modules.disable import DisableAbleCommandHandler
from dabi.modules.sql.global_bans_sql import is_user_gbanned
from dabi.modules.sql.afk_sql import is_afk, check_afk_status
from dabi.modules.sql.users_sql import get_user_num_chats
from dabi.modules.helper_funcs.extraction import extract_user


def no_by_per(totalhp, percentage):
    """
    rtype: num of `percentage` from total
    eg: 1000, 10 -> 10% of 1000 (100)
    """
    return totalhp * percentage / 100


def get_percentage(totalhp, earnedhp):
    """
    rtype: percentage of `totalhp` num
    eg: (1000, 100) will return 10%
    """

    matched_less = totalhp - earnedhp
    per_of_totalhp = 100 - matched_less * 100.0 / totalhp
    per_of_totalhp = str(int(per_of_totalhp))
    return per_of_totalhp


def hpmanager(user):
    total_hp = (get_user_num_chats(user.id) + 10) * 10

    if not is_user_gbanned(user.id):

        # Assign new var `new_hp` since we need `total_hp` in
        # end to calculate percentage.
        new_hp = total_hp

        # if no username decrease 25% of hp.
        if not user.username:
            new_hp -= no_by_per(total_hp, 25)
        try:
            dispatcher.bot.get_user_profile_photos(user.id).photos[0][-1]
        except IndexError:
            # no profile photo ==> -25% of hp
            new_hp -= no_by_per(total_hp, 25)
        # if no /setme exist ==> -20% of hp
        if not sql.get_user_me_info(user.id):
            new_hp -= no_by_per(total_hp, 20)
        # if no bio exsit ==> -10% of hp
        if not sql.get_user_bio(user.id):
            new_hp -= no_by_per(total_hp, 10)

        if is_afk(user.id):
            afkst = check_afk_status(user.id)
            # if user is afk and no reason then decrease 7%
            # else if reason exist decrease 5%
            if not afkst.reason:
                new_hp -= no_by_per(total_hp, 7)
            else:
                new_hp -= no_by_per(total_hp, 5)

        # fbanned users will have (2*number of fbans) less from max HP
        # Example: if HP is 100 but user has 5 diff fbans
        # Available HP is (2*5) = 10% less than Max HP
        # So.. 10% of 100HP = 90HP


# Commenting out fban health decrease cause it wasnt working and isnt needed ig.
#_, fbanlist = get_user_fbanlist(user.id)
#new_hp -= no_by_per(total_hp, 2 * len(fbanlist))

# Bad status effects:
# gbanned users will always have 5% HP from max HP
# Example: If HP is 100 but gbanned
# Available HP is 5% of 100 = 5HP

    else:
        new_hp = no_by_per(total_hp, 5)

    return {
        "earnedhp": int(new_hp),
        "totalhp": int(total_hp),
        "percentage": get_percentage(total_hp, new_hp)
    }


def make_bar(per):
    done = min(round(per / 10), 10)
    return "■" * done + "□" * (10 - done)


@run_async
def get_id(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message
    chat = update.effective_chat
    msg = update.effective_message
    user_id = extract_user(msg, args)

    if user_id:

        if msg.reply_to_message and msg.reply_to_message.forward_from:

            user1 = message.reply_to_message.from_user
            user2 = message.reply_to_message.forward_from

            msg.reply_text(
                f"<b>Telegram ID:</b>,"
                f"• {html.escape(user2.first_name)} - <code>{user2.id}</code>.\n"
                f"• {html.escape(user1.first_name)} - <code>{user1.id}</code>.",
                parse_mode=ParseMode.HTML)

        else:

            user = bot.get_chat(user_id)
            msg.reply_text(
                f"{html.escape(user.first_name)}'s id is <code>{user.id}</code>.",
                parse_mode=ParseMode.HTML)

    else:

        if chat.type == "private":
            msg.reply_text(
                f"Your id is <code>{chat.id}</code>.",
                parse_mode=ParseMode.HTML)

        else:
            msg.reply_text(
                f"This group's id is <code>{chat.id}</code>.",
                parse_mode=ParseMode.HTML)


@client.on(
    events.NewMessage(
        pattern='/ginfo ',
        from_users=(WHITELIST_USERS or []) + (SUDO_USERS or []) + (SUPPORT_USERS or [])))
async def group_info(event) -> None:
    chat = event.text.split(' ', 1)[1]
    try:
        entity = await event.client.get_entity(chat)
        totallist = await event.client.get_participants(
            entity, filter=ChannelParticipantsAdmins)
        ch_full = await event.client(GetFullChannelRequest(channel=entity))
    except:
        await event.reply(
            "Can't for some reason, maybe it is a private one or that I am banned there."
        )
        return
    msg = f"**ID**: `{entity.id}`"
    msg += f"\n**Title**: `{entity.title}`"
    msg += f"\n**Datacenter**: `{entity.photo.dc_id}`"
    msg += f"\n**Video PFP**: `{entity.photo.has_video}`"
    msg += f"\n**Supergroup**: `{entity.megagroup}`"
    msg += f"\n**Restricted**: `{entity.restricted}`"
    msg += f"\n**Scam**: `{entity.scam}`"
    msg += f"\n**Slowmode**: `{entity.slowmode_enabled}`"
    if entity.username:
        msg += f"\n**Username**: {entity.username}"
    msg += "\n\n**Member Stats:**"
    msg += f"\n`Admins:` `{len(totallist)}`"
    msg += f"\n`Users`: `{totallist.total}`"
    msg += "\n\n**Admins List:**"
    for x in totallist:
        msg += f"\n• [{x.id}](tg://user?id={x.id})"
    msg += f"\n\n**Description**:\n`{ch_full.full_chat.about}`"
    await event.reply(msg)


@run_async
def gifid(update: Update, context: CallbackContext):
    msg = update.effective_message
    if msg.reply_to_message and msg.reply_to_message.animation:
        update.effective_message.reply_text(
            f"Gif ID:\n<code>{msg.reply_to_message.animation.file_id}</code>",
            parse_mode=ParseMode.HTML)
    else:
        update.effective_message.reply_text(
            "Please reply to a gif to get its ID.")


@run_async
def info(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message
    chat = update.effective_chat
    user_id = extract_user(update.effective_message, args)

    if user_id:
        user = bot.get_chat(user_id)

    elif not message.reply_to_message and not args:
        user = message.from_user

    elif not message.reply_to_message and (
            not args or
        (len(args) >= 1 and not args[0].startswith("@") and
         not args[0].isdigit() and
         not message.parse_entities([MessageEntity.TEXT_MENTION]))):
        message.reply_text("I can't extract a user from this.")
        return

    else:
        return

    rep = message.reply_text(
        "<code>Appraising...</code>", parse_mode=ParseMode.HTML)

    text = (f"╒═══「<b> Appraisal results:</b> 」\n"
            f"ID: <code>{user.id}</code>\n"
            f"First Name: {html.escape(user.first_name)}")

    if user.last_name:
        text += f"\nLast Name: {html.escape(user.last_name)}"

    if user.username:
        text += f"\nUsername: @{html.escape(user.username)}"

    text += f"\nPermalink: {mention_html(user.id, 'link')}"

    if chat.type != "private" and user_id != bot.id:
        _stext = "\nPresence: <code>{}</code>"

        afk_st = is_afk(user.id)
        if afk_st:
            text += _stext.format("AFK")
        else:
            status = status = bot.get_chat_member(chat.id, user.id).status
            if status:
                if status in {"left", "kicked"}:
                    text += _stext.format("Not here")
                elif status == "member":
                    text += _stext.format("Detected")
                elif status in {"administrator", "creator"}:
                    text += _stext.format("Admin")
    if user_id not in [bot.id, 777000, 1087968824]:
        userhp = hpmanager(user)
        text += f"\n\n<b>Health:</b> <code>{userhp['earnedhp']}/{userhp['totalhp']}</code>\n[<i>{make_bar(int(userhp['percentage']))} </i>{userhp['percentage']}%]"

    try:
        spamwatch = spamwtc.get_ban(int(user.id))
        if spamwatch:
            text += "\n\n<b>This person is Spamwatched!</b>"
            text += f"\nReason: <pre>{spamwatch.reason}</pre>"
            text += "\nAppeal at @SpamWatchSupport"
        else:
            pass
    except:
        pass  # don't crash if api is down somehow...

    power_level_present = False

    if user.id == OWNER_ID:
        text += "\n\nAye this guy is my owner.\nI would never do anything against him!"
        power_level_present = True
    elif user.id in SUDO_USERS:
        text += (
            "\n\nThis person is one of my sudo users! "
            "Nearly as powerful as my owner - so watch it."
        )
        power_level_present = True
    elif user.id in SUPPORT_USERS:
        text += (
            "\n\nThis person is one of my support users! "
            "Not quite a sudo user, but can still gban you off the map."
        )
        power_level_present = True
    elif user.id in WHITELIST_USERS:
        text += (
            "\n\nThis person has been whitelisted! "
            "That means I'm not allowed to ban/kick them."
        )
        power_level_present = True

    if power_level_present:
        text += ' [<a href="https://t.me/PatrickUniverse/24">?</a>]'.format(
            bot.username)

    try:
        user_member = chat.get_member(user.id)
        if user_member.status == 'administrator':
            result = requests.post(
                f"https://api.telegram.org/bot{TOKEN}/getChatMember?chat_id={chat.id}&user_id={user.id}"
            )
            result = result.json()["result"]
            if "custom_title" in result.keys():
                custom_title = result['custom_title']
                text += f"\n\nTitle:\n<b>{custom_title}</b>"
    except BadRequest:
        pass

    for mod in USER_INFO:
        try:
            mod_info = mod.__user_info__(user.id).strip()
        except TypeError:
            mod_info = mod.__user_info__(user.id, chat.id).strip()
        if mod_info:
            text += "\n\n" + mod_info

    if None:
        try:
            profile = context.bot.get_user_profile_photos(user.id).photos[0][-1]
            _file = bot.get_file(profile["file_id"])
            _file.download(f"{user.id}.png")

            message.reply_document(
                document=open(f"{user.id}.png", "rb"),
                caption=(text),
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True)

            os.remove(f"{user.id}.png")
        # Incase user don't have profile pic, send normal text
        except IndexError:
            message.reply_text(
                text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

    else:
        message.reply_text(
            text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

    rep.delete()


@run_async
def about_me(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message
    user_id = extract_user(message, args)

    if user_id:
        user = bot.get_chat(user_id)
    else:
        user = message.from_user

    info = sql.get_user_me_info(user.id)

    if info:
        update.effective_message.reply_text(
            f"*{user.first_name}*:\n{escape_markdown(info)}",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True)
    elif message.reply_to_message:
        username = message.reply_to_message.from_user.first_name
        update.effective_message.reply_text(
            f"{username} hasn't set an info message about themselves yet!")
    else:
        update.effective_message.reply_text(
            "There isnt one, use /setme to set one.")


@run_async
def set_about_me(update: Update, context: CallbackContext):
    message = update.effective_message
    user_id = message.from_user.id
    if user_id in [777000, 1087968824]:
        message.reply_text("Error! Unauthorized")
        return
    bot = context.bot
    if message.reply_to_message:
        repl_message = message.reply_to_message
        repl_user_id = repl_message.from_user.id
        if repl_user_id in [bot.id, 777000, 1087968824]:
            user_id = repl_user_id
    text = message.text
    info = text.split(None, 1)
    if len(info) == 2:
        if len(info[1]) < MAX_MESSAGE_LENGTH // 4:
            sql.set_user_me_info(user_id, info[1])
            if user_id in [777000, 1087968824]:
                message.reply_text("Authorized...Information updated!")
            elif user_id == bot.id:
                message.reply_text(
                    "I have updated my info with the one you provided!")
            else:
                message.reply_text("Information updated!")
        else:
            message.reply_text(
                "The info needs to be under {} characters! You have {}.".format(
                    MAX_MESSAGE_LENGTH // 4, len(info[1])))


@run_async
def about_bio(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message

    user_id = extract_user(message, args)
    if user_id:
        user = bot.get_chat(user_id)
    else:
        user = message.from_user

    info = sql.get_user_bio(user.id)

    if info:
        update.effective_message.reply_text(
            "*{}*:\n{}".format(user.first_name, escape_markdown(info)),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True)
    elif message.reply_to_message:
        username = user.first_name
        update.effective_message.reply_text(
            f"{username} hasn't had a message set about themselves yet!\nSet one using /setbio"
        )
    else:
        update.effective_message.reply_text(
            "You haven't had a bio set about yourself yet!")


@run_async
def set_about_bio(update: Update, context: CallbackContext):
    message = update.effective_message
    bot = context.bot

    if message.reply_to_message:
        repl_message = message.reply_to_message
        user_id = repl_message.from_user.id

        if user_id == message.from_user.id:
            message.reply_text(
                "Ha, you can't set your own bio! You're at the mercy of others here..."
            )
            return

        if user_id in [777000, 1087968824]:
            message.reply_text("You are not authorised")
            return

        if user_id == bot.id:
            message.reply_text(
                "Erm... yeah, I only trust Heroes Association to set my bio.")
            return

        text = message.text
        bio = text.split(
            None, 1
        )  # use python's maxsplit to only remove the cmd, hence keeping newlines.

        if len(bio) == 2:
            if len(bio[1]) < MAX_MESSAGE_LENGTH // 4:
                sql.set_user_bio(user_id, bio[1])
                message.reply_text("Updated {}'s bio!".format(
                    repl_message.from_user.first_name))
            else:
                message.reply_text(
                    "Bio needs to be under {} characters! You tried to set {}."
                    .format(MAX_MESSAGE_LENGTH // 4, len(bio[1])))
    else:
        message.reply_text("Reply to someone to set their bio!")


def __user_info__(user_id):
    bio = html.escape(sql.get_user_bio(user_id) or "")
    me = html.escape(sql.get_user_me_info(user_id) or "")
    result = ""
    if me:
        result += f"<b>About user:</b>\n{me}\n"
    if bio:
        result += f"<b>What others say:</b>\n{bio}\n"
    result = result.strip("\n")
    return result


__help__ = """
*AFK:*
When marked as AFK, any mentions will be replied to with a message to say you're not available!

 • /afk <reason>: Mark yourself as AFK.
 • brb <reason>: Same as the afk command - but not a command.

*ID:*
 • /id: get the current group id. If used by replying to a message, gets that user's id.
 • /gifid: reply to a gif to me to tell you its file ID.

*Self addded information:* 
 • /setme <text>: will set your info
 • /me: will get your or another user's info.

Examples:
 `/setme I am a Naruto.`
 `/me @username(defaults to yours if no user specified)`

*Information others add on you:* 
 • /bio: will get your or another user's bio. This cannot be set by yourself.
 • /setbio <text>: while replying, will save another user's bio

Examples:
 `/bio @username(defaults to yours if not specified).`
 `/setbio This user is a wolf` (reply to the user)

*Overall Information about you:*
 • /info: get information about a user. 
 
*What is that health thingy?*
 Come and see [HP System explained](https://telegram.dog/PatrickUniverse/25)
"""

__mod_name__ = "AFK & Info"

SET_BIO_HANDLER = DisableAbleCommandHandler("setbio", set_about_bio)
GET_BIO_HANDLER = DisableAbleCommandHandler("bio", about_bio)

ID_HANDLER = DisableAbleCommandHandler("id", get_id)
GIFID_HANDLER = DisableAbleCommandHandler("gifid", gifid)
INFO_HANDLER = DisableAbleCommandHandler(("info", "book"), info)

SET_ABOUT_HANDLER = DisableAbleCommandHandler("setme", set_about_me)
GET_ABOUT_HANDLER = DisableAbleCommandHandler("me", about_me)

dispatcher.add_handler(ID_HANDLER)
dispatcher.add_handler(GIFID_HANDLER)
dispatcher.add_handler(INFO_HANDLER)
dispatcher.add_handler(SET_BIO_HANDLER)
dispatcher.add_handler(GET_BIO_HANDLER)
dispatcher.add_handler(SET_ABOUT_HANDLER)
dispatcher.add_handler(GET_ABOUT_HANDLER)