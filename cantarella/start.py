import os
import asyncio
import html as html_mod
import random
import time
import shutil
import subprocess
import pyrogram
from pyrogram import Client, filters, enums
from pyrogram.errors import (
    FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant,
    InviteHashExpired, UsernameNotOccupied, AuthKeyUnregistered, UserDeactivated, UserDeactivatedBan
)
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery, InputMediaPhoto
from config import API_ID, API_HASH, ERROR_MESSAGE
from database.db import db
import math
from logger import LOGGER
logger = LOGGER(__name__)

FREE_LIMIT_SIZE = 2 * 1024 * 1024 * 1024
FREE_LIMIT_DAILY = 10

# Optional: Set your own admin username for premium payments
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "YOUR_ADMIN_USERNAME")

REACTIONS = [
    "👍", "❤️", "🔥", "🥰", "👏", "😁", "🤔", "🤯", "😱",
    "😢", "🎉", "🤩", "🙏", "👌", "🕊", "🥱",
    "😍", "🐳", "❤️‍🔥", "🌚", "💯", "🤣", "⚡",
    "🏆", "💔", "🤨", "😐", "🍓", "🍾", "💋", "😈", "😴",
    "😭", "🤓", "👻", "👨‍💻", "👀", "🎃", "🙈", "😇", "😨", "🤝",
    "✍", "🤗", "🫡", "🎅", "🎄", "☃", "💅", "🤪", "🗿", "🆒",
    "💘", "🙉", "🦄", "😘", "🙊", "😎", "👾", "🤷‍♂️", "🤷‍♀️",
    "😡"
]


class script(object):
   
    START_TXT = """<b>👋 Hello {},</b>
<b>🤖 I am <a href=https://t.me/{}>{}]</a></b>
<i>Your Restricted Content Saver Bot.</i>
<blockquote><b>🚀 System Status: 🟢 Online</b>
<b>⚡ Performance: High-Speed Processing</b>
<b>🔐 Security: End-to-End Encrypted</b></blockquote>
<b>👇 Select an Option Below to Get Started:</b>
"""
    HELP_TXT = """<b>📚 Comprehensive Help & User Guide</b>
<blockquote><b>1️⃣ Public Channels (No Login Required)</b></blockquote>
• Forward or send the post link directly.
• Compatible with any public channel or group.
• <i>Example Link:</i> <code>https://t.me/channel/123</code>
<blockquote><b>2️⃣ Private/Restricted Channels (Login Required)</b></blockquote>
• Use <code>/login</code> to securely connect your Telegram account.
• Send the private link (e.g., <code>t.me/c/123...</code>).
• Bot accesses content using your authenticated session.
<blockquote><b>3️⃣ Batch Downloading Mode</b></blockquote>
• Initiate with <code>/batch</code> for multiple files.
• Follow interactive prompts for seamless processing.
<blockquote><b>🛑 Free User Limitations:</b></blockquote>
• <b>Daily Quota:</b> 10 Files / 24 Hours
• <b>File Size Cap:</b> 2GB Maximum
<blockquote><b>💎 Premium Membership Benefits:</b></blockquote>
• Unlimited Downloads & No Restrictions.
• Priority Support & Advanced Features.
"""
    ABOUT_TXT = """<b>ℹ️ About This Bot</b>
<blockquote><b>╭────[ 🧩 Technical Stack ]────⍟</b>
<b>├⍟ 🤖 Bot Name : Save Restricted Content</b>
<b>├⍟ 📚 Library : <a href='https://docs.pyrogram.org/'>Pyrogram Async</a></b>
<b>├⍟ 🐍 Language : <a href='https://www.python.org/'>Python 3.11+</a></b>
<b>├⍟ 🗄 Database : <a href='https://www.mongodb.com/'>MongoDB Atlas</a></b>
<b>╰───────────────⍟</b></blockquote>
"""
    PREMIUM_TEXT = """<b>💎 Premium Membership Plans</b>
<b>Unlock Unlimited Access & Advanced Features!</b>
<blockquote><b>✨ Key Benefits:</b>
<b>♾️ Unlimited Daily Downloads</b>
<b>📂 Support for 4GB+ File Sizes</b>
<b>⚡ Instant Processing (Zero Delay)</b>
<b>🖼 Customizable Thumbnails</b>
<b>📝 Personalized Captions</b>
<b>🛂 24/7 Priority Support</b></blockquote>
<i>Contact the admin to purchase premium.</i>
"""
    PROGRESS_BAR = """\
<b>⚡ Processing Task...</b>
<blockquote>
<b>Progress: {bar} {percentage:.1f}%</b>
<b>🚀 Speed:</b> <code>{speed}/s</code>
<b>💾 Size:</b> <code>{current} of {total}</code>
<b>⏱ Elapsed:</b> <code>{elapsed}</code>
<b>⏳ ETA:</b> <code>{eta}</code>
</blockquote>
"""
    CAPTION = ""
    LIMIT_REACHED = """<b>🚫 Daily Limit Exceeded</b>
<b>Your 10 free saves for today have been used.</b>
<i>Quota resets automatically after 24 hours from first download.</i>
<blockquote><b>🔓 Upgrade to Premium for Unlimited Access!</b></blockquote>
Remove all restrictions and enjoy seamless downloading.
"""
    SIZE_LIMIT = """<b>⚠️ File Size Exceeded</b>
<b>Free tier limited to 2GB per file.</b>
<blockquote><b>🔓 Upgrade to Premium</b></blockquote>
Download files up to 4GB and beyond with no limits!
"""

def humanbytes(size):
    if not size:
        return "0B"
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'

def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s, ") if seconds else "")
    return tmp[:-2] if tmp else "0s"

class batch_temp(object):
    IS_BATCH = {}

def get_message_type(msg):
    if getattr(msg, 'document', None): return "Document"
    if getattr(msg, 'video', None): return "Video"
    if getattr(msg, 'photo', None): return "Photo"
    if getattr(msg, 'audio', None): return "Audio"
    if getattr(msg, 'animation', None): return "Animation"
    if getattr(msg, 'sticker', None): return "Sticker"
    if getattr(msg, 'voice', None): return "Voice"
    if getattr(msg, 'video_note', None): return "VideoNote"
    if getattr(msg, 'text', None): return "Text"
    return None

async def downstatus(client, statusfile, message, chat):
    while not os.path.exists(statusfile):
        await asyncio.sleep(3)
    while os.path.exists(statusfile):
        try:
            with open(statusfile, "r", encoding='utf-8') as downread:
                txt = downread.read()
            await client.edit_message_text(chat, message.id, f"{txt}")
            await asyncio.sleep(5)
        except Exception:
            await asyncio.sleep(5)

async def upstatus(client, statusfile, message, chat):
    while not os.path.exists(statusfile):
        await asyncio.sleep(3)
    while os.path.exists(statusfile):
        try:
            with open(statusfile, "r", encoding='utf-8') as upread:
                txt = upread.read()
            await client.edit_message_text(chat, message.id, f"{txt}")
            await asyncio.sleep(5)
        except Exception:
            await asyncio.sleep(5)

def progress(current, total, message, type):
    if batch_temp.IS_BATCH.get(message.from_user.id):
        raise Exception("Cancelled")
    if not hasattr(progress, "cache"):
        progress.cache = {}
   
    now = time.time()
    task_id = f"{message.id}{type}"
    last_time = progress.cache.get(task_id, 0)
   
    if not hasattr(progress, "start_time"):
        progress.start_time = {}
    if task_id not in progress.start_time:
        progress.start_time[task_id] = now
       
    if (now - last_time) > 5 or current == total:
        try:
            percentage = current * 100 / total
            speed = current / (now - progress.start_time[task_id]) if (now - progress.start_time[task_id]) > 0 else 0
            eta = (total - current) / speed if speed > 0 else 0
            elapsed = now - progress.start_time[task_id]
           
            filled_length = int(percentage / 5)
            bar = '█' * filled_length + ' ' * (20 - filled_length)
           
            status = script.PROGRESS_BAR.format(
                bar=bar,
                percentage=percentage,
                current=humanbytes(current),
                total=humanbytes(total),
                speed=humanbytes(speed),
                elapsed=TimeFormatter(elapsed * 1000),
                eta=TimeFormatter(eta * 1000)
            )
           
            with open(f'{message.id}{type}status.txt', "w", encoding='utf-8') as fileup:
                fileup.write(status)
               
            progress.cache[task_id] = now
           
            if current == total:
                progress.start_time.pop(task_id, None)
                progress.cache.pop(task_id, None)
        except Exception:
            pass


@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
    try:
        await message.react(emoji=random.choice(REACTIONS), big=True)
    except Exception:
        pass

    buttons = [
        [
            InlineKeyboardButton("💎 Buy Premium", callback_data="buy_premium"),
            InlineKeyboardButton("🆘 Help & Guide", callback_data="help_btn")
        ],
        [
            InlineKeyboardButton("⚙️ Settings Panel", callback_data="settings_btn"),
            InlineKeyboardButton("ℹ️ About Bot", callback_data="about_btn")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    bot = await client.get_me()
    await client.send_message(
        chat_id=message.chat.id,
        text=script.START_TXT.format(message.from_user.mention, bot.username, bot.first_name),
        reply_markup=reply_markup,
        reply_to_message_id=message.id,
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True
    )


@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    buttons = [[InlineKeyboardButton("❌ Close Menu", callback_data="close_btn")]]
    await client.send_message(
        chat_id=message.chat.id,
        text=script.HELP_TXT,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_message(filters.command(["plan"]))
async def send_plan(client: Client, message: Message):
    buttons = [
        [InlineKeyboardButton("📞 Contact Admin", url=f"https://t.me/{ADMIN_USERNAME}")],
        [InlineKeyboardButton("❌ Close Menu", callback_data="close_btn")]
    ]
    await client.send_message(
        chat_id=message.chat.id,
        text=script.PREMIUM_TEXT,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):
    batch_temp.IS_BATCH[message.from_user.id] = True
    await message.reply_text("❌ Batch Process Cancelled Successfully.")


async def settings_panel(client, callback_query):
    """
    Renders the Settings Menu with professional layout.
    """
    user_id = callback_query.from_user.id
    is_premium = await db.check_premium(user_id)
    badge = "💎 Premium Member" if is_premium else "👤 Standard User"
   
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📜 Command List", callback_data="cmd_list_btn")],
        [InlineKeyboardButton("📊 Usage Stats", callback_data="user_stats_btn")],
        [InlineKeyboardButton("🗑 Dump Chat Settings", callback_data="dump_chat_btn")],
        [InlineKeyboardButton("🖼 Manage Thumbnail", callback_data="thumb_btn")],
        [InlineKeyboardButton("📝 Edit Caption", callback_data="caption_btn")],
        [InlineKeyboardButton("⬅️ Return to Home", callback_data="start_btn")]
    ])
   
    text = f"<b>⚙️ Settings Dashboard</b>\n\n<b>Account Status:</b> {badge}\n<b>User ID:</b> <code>{user_id}</code>\n\n<i>Customize and manage your bot preferences below:</i>"
   
    try:
        await callback_query.edit_message_text(
            text=text,
            reply_markup=buttons,
            parse_mode=enums.ParseMode.HTML
        )
    except Exception:
        await callback_query.edit_message_caption(
            caption=text,
            reply_markup=buttons,
            parse_mode=enums.ParseMode.HTML
        )


@Client.on_message(filters.text & filters.private & ~filters.regex("^/"))
async def save(client: Client, message: Message):
    if "https://t.me/" not in message.text:
        return

    try:
        is_limit_reached = await db.check_limit(message.from_user.id)
        if is_limit_reached:
            btn = InlineKeyboardMarkup([[InlineKeyboardButton("💎 Upgrade to Premium", callback_data="buy_premium")]])
            return await message.reply_text(
                script.LIMIT_REACHED,
                reply_markup=btn,
                parse_mode=enums.ParseMode.HTML
            )

        # Resolve destination: dump chat if set, otherwise current chat
        dump_chat = await db.get_dump_chat(message.from_user.id)
        dest_chat = dump_chat if dump_chat else message.chat.id

        # Validate dump chat is reachable by the bot
        if dump_chat:
            try:
                await client.get_chat(dump_chat)
            except Exception as e:
                logger.warning(f"Dump chat {dump_chat} unreachable for user {message.from_user.id}: {e}")
                await message.reply(
                    f"<b>⚠️ Dump chat <code>{dump_chat}</code> is unreachable.</b>\n"
                    "<i>Make sure the bot is a member/admin of that chat.</i>\n"
                    "<i>Falling back to this chat for now.</i>",
                    parse_mode=enums.ParseMode.HTML
                )
                dest_chat = message.chat.id

        if batch_temp.IS_BATCH.get(message.from_user.id) == False:
            return await message.reply_text("<b>⚠️ A Task is Currently Processing.</b>\n<i>Please wait for completion or use /cancel to stop.</i>", parse_mode=enums.ParseMode.HTML)
        datas = message.text.split("/")
        temp = datas[-1].replace("?single", "").split("-")
        fromID = int(temp[0].strip())
        try:
            toID = int(temp[1].strip())
        except Exception:
            toID = fromID
        batch_temp.IS_BATCH[message.from_user.id] = False
        is_private_link = "https://t.me/c/" in message.text
        is_batch = "https://t.me/b/" in message.text
        is_public_link = not is_private_link and not is_batch

        # Log what we're doing
        logger.info(f"User {message.from_user.id}: Processing link | type={'public' if is_public_link else 'private'} | dest={dest_chat} | msgs={fromID}-{toID}")

        # Pre-connect user session ONCE (if needed for private/restricted content)
        acc = None
        needs_session = not is_public_link  # Private links always need session

        for msgid in range(fromID, toID + 1):
           
            if batch_temp.IS_BATCH.get(message.from_user.id):
                break
           
            if is_public_link:
                username = datas[3]
                try:
                    await client.copy_message(
                        chat_id=dest_chat,
                        from_chat_id=username,
                        message_id=msgid
                    )
                    await db.add_traffic(message.from_user.id)
                    await asyncio.sleep(1)
                    continue
                except Exception as e:
                    logger.error(f"copy_message failed for {username}/{msgid} -> {dest_chat}: {e}")
                    needs_session = True
                    # Fall through to try with user session

            # Connect user session once (lazy — only when first needed)
            if acc is None and needs_session:
                user_data = await db.get_session(message.from_user.id)
                if user_data is None:
                    await message.reply(
                        "<b>🔒 Authentication Required</b>\n\n"
                        "<i>Access to this content requires login.</i>\n"
                        "<i>Use /login to securely authorize your account.</i>",
                        parse_mode=enums.ParseMode.HTML
                    )
                    batch_temp.IS_BATCH[message.from_user.id] = True
                    return
                try:
                    acc = Client(
                        "saverestricted",
                        session_string=user_data,
                        api_hash=API_HASH,
                        api_id=API_ID,
                        in_memory=True,
                        max_concurrent_transmissions=10
                    )
                    await acc.connect()
                    acc.me = await acc.get_me()
                except Exception as e:
                    batch_temp.IS_BATCH[message.from_user.id] = True
                    return await message.reply(f"<b>❌ Authentication Failed</b>\n\n<i>Your session may have expired. Please /logout and /login again.</i>\n<i>Error: {e}</i>", parse_mode=enums.ParseMode.HTML)

            if acc is None:
                # No session and public copy failed — skip this message
                await message.reply(f"<b>⚠️ Could not process message {msgid}.</b>\n<i>Try /login for restricted content.</i>", parse_mode=enums.ParseMode.HTML)
                continue

            try:
                if is_private_link:
                    chatid = int("-100" + datas[4])
                    await handle_restricted_content(client, acc, message, chatid, msgid, dest_chat)
                elif is_batch:
                    username = datas[4]
                    await handle_restricted_content(client, acc, message, username, msgid, dest_chat)
                else:
                    username = datas[3]
                    await handle_restricted_content(client, acc, message, username, msgid, dest_chat)
            except Exception as e:
                logger.error(f"handle_restricted_content failed for msgid {msgid}: {e}")
                await message.reply(f"<b>❌ Failed to process message {msgid}</b>\n<i>{e}</i>", parse_mode=enums.ParseMode.HTML)
            await asyncio.sleep(2)

        # Disconnect user session ONCE after the loop
        if acc is not None:
            try:
                await acc.disconnect()
            except Exception:
                pass

        batch_temp.IS_BATCH[message.from_user.id] = True
    except Exception as e:
        logger.error(f"save() crashed for user {message.from_user.id}: {e}")
        batch_temp.IS_BATCH[message.from_user.id] = True
        # Make sure to disconnect session on crash too
        if 'acc' in dir() and acc is not None:
            try:
                await acc.disconnect()
            except Exception:
                pass
        await message.reply(f"<b>❌ Error processing link</b>\n<i>{e}</i>", parse_mode=enums.ParseMode.HTML)


async def handle_restricted_content(client: Client, acc, message: Message, chat_target, msgid, dest_chat):
    try:
        msg: Message = await acc.get_messages(chat_target, msgid)
    except Exception as e:
        logger.error(f"Error fetching message: {e}")
        await message.reply(f"<b>❌ Failed to fetch message {msgid}</b>\n<i>{e}</i>", parse_mode=enums.ParseMode.HTML)
        return
    if msg.empty:
        logger.info(f"Skipped message {msgid}: empty or deleted")
        return
   
    msg_type = get_message_type(msg)
    if not msg_type:
        logger.info(f"Skipped message {msgid}: unsupported content type (contact/poll/location/service message)")
        return
    file_size = 0
    if msg_type == "Document": file_size = msg.document.file_size or 0
    elif msg_type == "Video": file_size = msg.video.file_size or 0
    elif msg_type == "Audio": file_size = msg.audio.file_size or 0
    elif msg_type == "Animation": file_size = msg.animation.file_size or 0
    elif msg_type == "Voice": file_size = msg.voice.file_size or 0
    elif msg_type == "VideoNote": file_size = msg.video_note.file_size or 0
    elif msg_type == "Sticker": file_size = msg.sticker.file_size or 0
   
    if file_size > FREE_LIMIT_SIZE:
        if not await db.check_premium(message.from_user.id):
            btn = InlineKeyboardMarkup([[InlineKeyboardButton("💎 Upgrade to Premium", callback_data="buy_premium")]])
            await message.reply(
                script.SIZE_LIMIT,
                reply_markup=btn,
                parse_mode=enums.ParseMode.HTML
            )
            return
    if msg_type == "Text":
        try:
            await client.send_message(dest_chat, msg.text, entities=msg.entities, parse_mode=enums.ParseMode.HTML)
            return
        except Exception as e:
            logger.error(f"Failed to send text to {dest_chat}: {e}")
            await message.reply(f"<b>❌ Failed to send text</b>\n<i>{e}</i>", parse_mode=enums.ParseMode.HTML)
            return

    # Stickers can be forwarded directly without download
    if msg_type == "Sticker":
        try:
            await client.send_sticker(dest_chat, msg.sticker.file_id)
            await db.add_traffic(message.from_user.id)
            return
        except Exception as e:
            logger.error(f"Failed to send sticker to {dest_chat}: {e}")
            # Fall through to download method

    await db.add_traffic(message.from_user.id)
    # Send status message to USER's chat (not dump chat) so they can see progress
    smsg = await message.reply('<b>⬇️ Starting Download...</b>', parse_mode=enums.ParseMode.HTML)
   
    temp_dir = f"downloads/{message.id}_{msgid}"
    if not os.path.exists(temp_dir): os.makedirs(temp_dir)
    try:
        asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', smsg, message.chat.id))
       
        file = await acc.download_media(
            msg,
            file_name=f"{temp_dir}/",
            progress=progress,
            progress_args=[message, "down"]
        )
       
        if os.path.exists(f'{message.id}downstatus.txt'): os.remove(f'{message.id}downstatus.txt')
    except Exception as e:
        if batch_temp.IS_BATCH.get(message.from_user.id) or "Cancelled" in str(e):
            if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
            return await smsg.edit("❌ **Task Cancelled**")
        if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
        logger.error(f"Download failed for {chat_target}/{msgid}: {e}")
        return await smsg.edit(f"<b>❌ Download Failed</b>\n<i>{e}</i>")

    # Critical: download_media can return None silently
    if not file or not os.path.exists(file):
        logger.error(f"Download returned None or file missing for {chat_target}/{msgid}")
        if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
        await smsg.edit("<b>❌ Download Failed</b>\n<i>File could not be downloaded (media may be unavailable or too large for download).</i>")
        return

    try:
        asyncio.create_task(upstatus(client, f'{message.id}upstatus.txt', smsg, message.chat.id))
       
        ph_path = None
        thumb_id = await db.get_thumbnail(message.from_user.id)
       
        if thumb_id:
            try:
                ph_path = await client.download_media(thumb_id, file_name=f"{temp_dir}/custom_thumb.jpg")
            except Exception as e:
                logger.error(f"Failed to download custom thumb: {e}")
        if not ph_path:
            try:
                if msg_type == "Video" and msg.video.thumbs:
                    ph_path = await acc.download_media(msg.video.thumbs[0].file_id, file_name=f"{temp_dir}/thumb.jpg")
                elif msg_type == "Document" and msg.document.thumbs:
                    ph_path = await acc.download_media(msg.document.thumbs[0].file_id, file_name=f"{temp_dir}/thumb.jpg")
            except Exception:
                pass
        custom_caption = await db.get_caption(message.from_user.id)
        if custom_caption:
            final_caption = custom_caption.format(filename=file.split("/")[-1], size=humanbytes(file_size))
        else:
            # No default promotional caption — just use original caption if available
            final_caption = ""
            if msg.caption:
                final_caption = msg.caption

        # Use ACTUAL file size on disk for upload decision (metadata can be wrong)
        actual_size = os.path.getsize(file) if (file and os.path.exists(file)) else file_size
        SAFE_BOT_LIMIT = 1950 * 1024 * 1024  # 1950 MiB (safe margin under Telegram's 2000 MiB limit)
        logger.info(f"Upload decision: metadata_size={humanbytes(file_size)}, actual_size={humanbytes(actual_size)}, limit={humanbytes(SAFE_BOT_LIMIT)}")

        if actual_size <= SAFE_BOT_LIMIT:
            # File fits within bot limit — upload directly, fall back to split if it fails
            try:
                await _do_upload(client, dest_chat, file, msg, msg_type, ph_path, final_caption, message)
            except Exception as bot_err:
                logger.warning(f"Bot upload failed ({type(bot_err).__name__}): {bot_err}, falling back to split")
                await smsg.edit("<b>📦 Upload failed, splitting file into parts...</b>")
                await _split_and_upload(client, dest_chat, file, actual_size, final_caption, message, temp_dir)
        else:
            # File exceeds bot limit — split into parts and upload via bot
            # (User session uploads are unreliable in Docker due to MTProto connection timeouts)
            logger.info(f"File {humanbytes(actual_size)} exceeds bot limit, splitting into parts")
            await smsg.edit("<b>📦 File too large for single upload. Splitting into parts...</b>")
            await _split_and_upload(client, dest_chat, file, actual_size, final_caption, message, temp_dir)
       
    except Exception as e:
        logger.error(f"Upload failed to {dest_chat} ({type(e).__name__}): {repr(e)}")
        raw_err = str(e) if str(e) else f"{type(e).__name__}: {repr(e)}"
        safe_err = html_mod.escape(raw_err)  # Escape < > & so they show in Telegram
        try:
            await smsg.edit(f"<b>❌ Upload Failed</b>\n<i>{safe_err}</i>", parse_mode=enums.ParseMode.HTML)
        except Exception:
            await smsg.edit(f"❌ Upload Failed\n{raw_err}")
        try:
            await message.reply(f"<b>❌ Failed to upload to destination</b>\n<i>{safe_err}</i>\n\n<i>Make sure the bot is an admin of the dump chat.</i>", parse_mode=enums.ParseMode.HTML)
        except Exception:
            await message.reply(f"❌ Failed to upload to destination\n{raw_err}\n\nMake sure the bot is an admin of the dump chat.")
    if os.path.exists(f'{message.id}upstatus.txt'): os.remove(f'{message.id}upstatus.txt')
    if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
    try:
        await smsg.delete()
    except Exception:
        pass


async def _do_upload(uploader, dest_chat, file, msg, msg_type, ph_path, caption, message):
    """Upload a file using the given client (bot or user session)."""
    if msg_type == "Document":
        await uploader.send_document(dest_chat, file, thumb=ph_path, caption=caption, progress=progress, progress_args=[message, "up"])
    elif msg_type == "Video":
        await uploader.send_video(dest_chat, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=ph_path, caption=caption, progress=progress, progress_args=[message, "up"])
    elif msg_type == "Audio":
        await uploader.send_audio(dest_chat, file, thumb=ph_path, caption=caption, progress=progress, progress_args=[message, "up"])
    elif msg_type == "Photo":
        await uploader.send_photo(dest_chat, file, caption=caption)
    elif msg_type == "Animation":
        await uploader.send_animation(dest_chat, file, caption=caption)
    elif msg_type == "Voice":
        await uploader.send_voice(dest_chat, file, caption=caption)
    elif msg_type == "VideoNote":
        await uploader.send_video_note(dest_chat, file)
    elif msg_type == "Sticker":
        await uploader.send_sticker(dest_chat, file)


async def _split_and_upload(client, dest_chat, file_path, file_size, caption, message, temp_dir):
    """Split a large file into <=1.95GB parts and upload each."""
    PART_SIZE = 1950 * 1024 * 1024  # 1950 MiB per part
    filename = os.path.basename(file_path)
    name, ext = os.path.splitext(filename)
    
    is_video = ext.lower() in ('.mp4', '.mkv', '.avi', '.mov', '.webm', '.flv', '.ts')
    
    if is_video:
        # For videos: use ffmpeg to produce streamable segments
        parts = await _ffmpeg_split_video(file_path, temp_dir, PART_SIZE)
        if parts:
            total = len(parts)
            for i, part_path in enumerate(parts, 1):
                part_caption = f"{caption}\n\n📦 <b>Part {i}/{total}</b>" if caption else f"📦 <b>Part {i}/{total}</b>"
                try:
                    await client.send_video(
                        dest_chat, part_path,
                        caption=part_caption,
                        parse_mode=enums.ParseMode.HTML,
                        supports_streaming=True,
                        progress=progress, progress_args=[message, "up"]
                    )
                except Exception as e:
                    # If send_video fails (e.g. codec issue), try as document
                    logger.warning(f"send_video failed for part {i}, trying as document: {e}")
                    await client.send_document(
                        dest_chat, part_path,
                        caption=part_caption,
                        parse_mode=enums.ParseMode.HTML,
                        progress=progress, progress_args=[message, "up"]
                    )
                # Clean up part after upload to save disk
                try:
                    os.remove(part_path)
                except Exception:
                    pass
                await asyncio.sleep(2)
            return
        else:
            logger.warning("ffmpeg split returned no parts, falling back to binary split")
    
    # Binary split fallback (for non-video files or if ffmpeg fails)
    part_num = 0
    total_parts = math.ceil(file_size / PART_SIZE)
    
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(PART_SIZE)
            if not chunk:
                break
            part_num += 1
            part_filename = f"{name}.part{part_num}of{total_parts}{ext}"
            part_path = os.path.join(temp_dir, part_filename)
            
            with open(part_path, 'wb') as pf:
                pf.write(chunk)
            
            part_caption = f"{caption}\n\n📦 <b>Part {part_num}/{total_parts}</b>" if caption else f"📦 <b>Part {part_num}/{total_parts}</b>"
            await client.send_document(
                dest_chat, part_path,
                caption=part_caption,
                parse_mode=enums.ParseMode.HTML,
                progress=progress, progress_args=[message, "up"]
            )
            os.remove(part_path)
            await asyncio.sleep(2)


async def _ffmpeg_split_video(file_path, temp_dir, part_size):
    """Split a video into streamable segments using ffmpeg.
    
    Each output segment is a complete, playable .mp4 file with proper
    headers — can be streamed directly in Telegram.
    """
    # Check if ffmpeg is available
    try:
        proc = await asyncio.create_subprocess_exec(
            'ffmpeg', '-version',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await proc.wait()
        if proc.returncode != 0:
            logger.warning("ffmpeg not available")
            return None
    except FileNotFoundError:
        logger.warning("ffmpeg not found on system")
        return None
    
    filename = os.path.basename(file_path)
    name, _ = os.path.splitext(filename)
    
    # Get video duration using ffprobe
    try:
        probe = await asyncio.create_subprocess_exec(
            'ffprobe', '-v', 'quiet',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            file_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await probe.communicate()
        total_duration = float(stdout.decode().strip())
    except Exception as e:
        logger.error(f"ffprobe failed: {e}")
        return None
    
    total_size = os.path.getsize(file_path)
    
    # Calculate how many parts we need and the duration per segment
    num_parts = math.ceil(total_size / part_size)
    segment_duration = int(total_duration / num_parts)
    
    if segment_duration < 10:
        logger.warning(f"Segment duration too short ({segment_duration}s), aborting ffmpeg split")
        return None
    
    logger.info(f"Splitting {humanbytes(total_size)} video ({int(total_duration)}s) into ~{num_parts} parts of ~{segment_duration}s each")
    
    # Split using ffmpeg segment muxer — outputs proper .mp4 files
    output_pattern = os.path.join(temp_dir, f"{name}_part%03d.mp4")
    proc = await asyncio.create_subprocess_exec(
        'ffmpeg', '-i', file_path,
        '-c', 'copy',           # No re-encoding (fast, lossless)
        '-map', '0',            # Include all streams (video + audio)
        '-segment_time', str(segment_duration),
        '-f', 'segment',
        '-reset_timestamps', '1',  # Reset timestamps for each segment
        '-movflags', '+faststart',  # Enable streaming (moov atom at start)
        output_pattern,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    _, stderr = await proc.communicate()
    
    if proc.returncode != 0:
        logger.error(f"ffmpeg split failed (exit {proc.returncode}): {stderr.decode()[-500:]}")
        return None
    
    # Collect output files sorted by name
    parts = sorted([
        os.path.join(temp_dir, f) for f in os.listdir(temp_dir)
        if f.startswith(f"{name}_part") and f.endswith('.mp4')
    ])
    
    if not parts:
        logger.error("ffmpeg produced no output files")
        return None
    
    logger.info(f"ffmpeg split produced {len(parts)} streamable segments")
    return parts


@Client.on_callback_query()
async def button_callbacks(client: Client, callback_query: CallbackQuery):
    data = callback_query.data
    message = callback_query.message
    if not message: return

    if data == "settings_btn":
        await settings_panel(client, callback_query)
    elif data == "buy_premium":
        buttons = [
            [InlineKeyboardButton("📞 Contact Admin", url=f"https://t.me/{ADMIN_USERNAME}")],
            [InlineKeyboardButton("⬅️ Back to Home", callback_data="start_btn")]
        ]
        try:
            await callback_query.edit_message_text(
                text=script.PREMIUM_TEXT,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.HTML
            )
        except Exception:
            await callback_query.edit_message_caption(
                caption=script.PREMIUM_TEXT,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.HTML
            )
    elif data == "help_btn":
        buttons = [[InlineKeyboardButton("⬅️ Back to Home", callback_data="start_btn")]]
        try:
            await callback_query.edit_message_text(
                text=script.HELP_TXT,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.HTML
            )
        except Exception:
            await callback_query.edit_message_caption(
                caption=script.HELP_TXT,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.HTML
            )
  
    elif data == "about_btn":
        buttons = [[InlineKeyboardButton("⬅️ Back to Home", callback_data="start_btn")]]
        try:
            await callback_query.edit_message_text(
                text=script.ABOUT_TXT,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.HTML
            )
        except Exception:
            await callback_query.edit_message_caption(
                caption=script.ABOUT_TXT,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.HTML
            )
    elif data == "start_btn":
        bot = await client.get_me()
        buttons = [
            [
                InlineKeyboardButton("💎 Buy Premium", callback_data="buy_premium"),
                InlineKeyboardButton("🆘 Help & Guide", callback_data="help_btn")
            ],
            [
                InlineKeyboardButton("⚙️ Settings Panel", callback_data="settings_btn"),
                InlineKeyboardButton("ℹ️ About Bot", callback_data="about_btn")
            ]
        ]
        try:
            await callback_query.edit_message_text(
                text=script.START_TXT.format(callback_query.from_user.mention, bot.username, bot.first_name),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.HTML,
                disable_web_page_preview=True
            )
        except Exception:
            await callback_query.edit_message_caption(
                caption=script.START_TXT.format(callback_query.from_user.mention, bot.username, bot.first_name),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.HTML
            )
    elif data == "close_btn":
        await message.delete()
    elif data in ["cmd_list_btn", "user_stats_btn", "dump_chat_btn", "thumb_btn", "caption_btn"]:
        # These are handled by settings.py callbacks
        pass
    await callback_query.answer()
