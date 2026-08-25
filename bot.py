import asyncio
import logging
import os
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from dotenv import load_dotenv
import sqlite3
from datetime import datetime

# ============================================
# LOAD ENVIRONMENT VARIABLES
# ============================================

load_dotenv()

# Required settings
API_ID = int(os.getenv('API_ID', '0'))
API_HASH = os.getenv('API_HASH', '')
PHONE_NUMBER = os.getenv('PHONE_NUMBER', '')

# Optional settings
SESSION_NAME = os.getenv('SESSION_NAME', 'user_session')
DB_FILE = os.getenv('DB_FILE', 'images.db')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
COMMANDS_FILE = os.getenv('COMMANDS_FILE', 'commands.txt')

# Validate required settings
if not API_ID or not API_HASH or not PHONE_NUMBER:
    print("❌ Missing required environment variables!")
    print("Please check your .env file contains:")
    print("  API_ID=your_api_id")
    print("  API_HASH=your_api_hash")
    print("  PHONE_NUMBER=+1234567890")
    exit(1)

# ============================================
# LOAD SAVE COMMANDS FROM FILE
# ============================================

def load_commands():
    """Load save commands from commands.txt file"""
    commands = []

    if os.path.exists(COMMANDS_FILE):
        with open(COMMANDS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                cmd = line.strip().lower()
                if cmd and not cmd.startswith('#'):
                    commands.append(cmd)

    return commands

def save_commands_to_file(commands):
    """Save commands to commands.txt file"""
    with open(COMMANDS_FILE, 'w', encoding='utf-8') as f:
        for cmd in commands:
            f.write(f"{cmd}\n")

SAVE_COMMANDS = load_commands()

# ============================================
# LOGGING SETUP
# ============================================

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# DATABASE SETUP
# ============================================

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS saved_media (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            media_type TEXT,
            original_chat_id TEXT,
            original_sender_id TEXT,
            original_sender_name TEXT,
            file_size_mb REAL,
            saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

if not os.path.exists(DB_FILE):
    init_db()
    logger.info("Database created")
else:
    logger.info("Database loaded")

# ============================================
# CLIENT
# ============================================

user_client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_media_type(media):
    """Detect the type of media"""
    if hasattr(media, 'photo'):
        return "📷 Photo"
    elif hasattr(media, 'document'):
        doc = media.document
        if hasattr(doc, 'mime_type'):
            mime = doc.mime_type
            if 'video' in mime:
                if hasattr(doc, 'attributes'):
                    for attr in doc.attributes:
                        if hasattr(attr, 'round_message') and attr.round_message:
                            return "🎥 Video Message (Round)"
                        if hasattr(attr, 'voice') and attr.voice:
                            return "🎤 Voice Message"
                return "🎬 Video"
            elif 'audio' in mime or 'voice' in mime or 'ogg' in mime:
                return "🎤 Voice Message"
            elif 'gif' in mime:
                return "🎞 GIF"
            elif 'image' in mime or 'png' in mime or 'jpg' in mime or 'jpeg' in mime or 'webp' in mime:
                return "🖼 Sticker/Image"
            else:
                return "📎 Document"
    elif hasattr(media, 'geo'):
        return "📍 Location"
    elif hasattr(media, 'contact'):
        return "👤 Contact"
    elif hasattr(media, 'poll'):
        return "📊 Poll"
    else:
        return "📎 Media"

def get_file_extension(media):
    """Get the correct file extension"""
    if hasattr(media, 'photo'):
        return ".jpg"
    elif hasattr(media, 'document'):
        doc = media.document
        if hasattr(doc, 'mime_type'):
            mime = doc.mime_type
            if 'video' in mime:
                return ".mp4"
            elif 'audio' in mime or 'voice' in mime or 'ogg' in mime:
                return ".ogg"
            elif 'gif' in mime:
                return ".gif"
            elif 'png' in mime:
                return ".png"
            elif 'webp' in mime:
                return ".webp"
            elif 'jpg' in mime or 'jpeg' in mime:
                return ".jpg"
        if hasattr(doc, 'attributes'):
            for attr in doc.attributes:
                if hasattr(attr, 'file_name') and attr.file_name:
                    _, ext = os.path.splitext(attr.file_name)
                    if ext:
                        return ext
        return ".bin"
    return ".jpg"

def get_file_size(media):
    """Get file size in MB"""
    try:
        if hasattr(media, 'document'):
            return media.document.size / (1024 * 1024)
        elif hasattr(media, 'photo'):
            if hasattr(media.photo, 'sizes') and media.photo.sizes:
                largest = max(media.photo.sizes, key=lambda s: s.sizes if hasattr(s, 'sizes') else 0)
                if hasattr(largest, 'sizes'):
                    return sum(largest.sizes) / (1024 * 1024)
    except:
        pass
    return 0

# ============================================
# MEDIA SAVING HANDLER
# ============================================

@user_client.on(events.NewMessage(outgoing=True))
async def media_saver(event):
    """Save any media to Saved Messages when you reply with a save command"""

    if not event.message.is_reply:
        return

    if not event.message.text:
        return

    text = event.message.text.strip().lower()

    if text not in SAVE_COMMANDS:
        return

    logger.info(f"Save command '{text}' detected!")

    reply_to_msg = await event.message.get_reply_message()

    if not reply_to_msg:
        return

    if not reply_to_msg.media:
        if reply_to_msg.text:
            await save_text_message(reply_to_msg, event)
            return
        return

    try:
        media_type = get_media_type(reply_to_msg.media)
        file_ext = get_file_extension(reply_to_msg.media)
        file_size = get_file_size(reply_to_msg.media)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"media_{timestamp}{file_ext}"

        file_path = await reply_to_msg.download_media(file=file_name)

        if not file_path:
            return

        sender_name = "Unknown"
        try:
            sender = await reply_to_msg.get_sender()
            if sender:
                sender_name = sender.first_name or ""
                if sender.last_name:
                    sender_name += f" {sender.last_name}"
                if sender.username:
                    sender_name += f" (@{sender.username})"
        except:
            pass

        chat_name = str(event.chat_id)
        try:
            chat = await event.get_chat()
            if hasattr(chat, 'title') and chat.title:
                chat_name = chat.title
            elif hasattr(chat, 'first_name'):
                chat_name = f"{chat.first_name} {chat.last_name or ''}"
        except:
            pass

        caption = (
            f"{media_type}\n"
            f"👤 From: {sender_name}\n"
            f"🆔 User ID: `{reply_to_msg.sender_id}`\n"
            f"💬 Chat: {chat_name}\n"
            f"📏 Size: {file_size:.2f} MB\n"
            f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        if reply_to_msg.text:
            caption += f"\n\n💬 Caption: {reply_to_msg.text[:200]}"

        await user_client.send_file('me', file_path, caption=caption)

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO saved_media (file_name, media_type, original_chat_id, original_sender_id, original_sender_name, file_size_mb)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (os.path.basename(file_path), media_type, str(event.chat_id), str(reply_to_msg.sender_id), sender_name, file_size)
        )
        conn.commit()
        conn.close()

        os.remove(file_path)

        logger.info(f"Saved: {media_type} from {sender_name}")

    except Exception as e:
        logger.error(f"Error: {e}")
        try:
            if 'file_path' in locals() and os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass

async def save_text_message(message, event):
    """Save a text message"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"message_{timestamp}.txt"

        sender_name = "Unknown"
        try:
            sender = await message.get_sender()
            if sender:
                sender_name = sender.first_name or ""
                if sender.last_name:
                    sender_name += f" {sender.last_name}"
                if sender.username:
                    sender_name += f" (@{sender.username})"
        except:
            pass

        chat_name = str(event.chat_id)
        try:
            chat = await event.get_chat()
            if hasattr(chat, 'title') and chat.title:
                chat_name = chat.title
            elif hasattr(chat, 'first_name'):
                chat_name = f"{chat.first_name} {chat.last_name or ''}"
        except:
            pass

        content = (
            f"Message from: {sender_name}\n"
            f"User ID: {message.sender_id}\n"
            f"Chat: {chat_name}\n"
            f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"{'='*50}\n\n"
            f"{message.text}"
        )

        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(content)

        await user_client.send_file(
            'me',
            file_name,
            caption=f"📝 Saved Message\n👤 From: {sender_name}\n💬 Chat: {chat_name}"
        )

        os.remove(file_name)

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO saved_media (file_name, media_type, original_chat_id, original_sender_id, original_sender_name, file_size_mb)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (file_name, "📝 Text", str(event.chat_id), str(message.sender_id), sender_name, 0)
        )
        conn.commit()
        conn.close()

        logger.info(f"Saved text from {sender_name}")

    except Exception as e:
        logger.error(f"Error saving text: {e}")
        try:
            if os.path.exists(file_name):
                os.remove(file_name)
        except:
            pass

# ============================================
# COMMAND MANAGEMENT COMMANDS
# ============================================

@user_client.on(events.NewMessage(pattern='/add', outgoing=True))
async def add_command(event):
    """Add a new save command"""
    global SAVE_COMMANDS

    # Get command from message: /add command_name
    parts = event.message.text.split(maxsplit=1)

    if len(parts) < 2:
        await event.reply("❌ Usage: `/add command_name`\n\nExample: `/add awesome`")
        return

    new_command = parts[1].strip().lower()

    # Check if already exists
    if new_command in SAVE_COMMANDS:
        await event.reply(f"⚠️ Command '{new_command}' already exists!")
        return

    # Add to list
    SAVE_COMMANDS.append(new_command)

    # Save to file
    save_commands_to_file(SAVE_COMMANDS)

    await event.reply(f"✅ Command added: **'{new_command}'**\n\nTotal commands: {len(SAVE_COMMANDS)}")

@user_client.on(events.NewMessage(pattern='/remove', outgoing=True))
async def remove_command(event):
    """Remove a save command"""
    global SAVE_COMMANDS

    # Get command from message: /remove command_name
    parts = event.message.text.split(maxsplit=1)

    if len(parts) < 2:
        await event.reply("❌ Usage: `/remove command_name`\n\nExample: `/remove save`")
        return

    command_to_remove = parts[1].strip().lower()

    # Check if exists
    if command_to_remove not in SAVE_COMMANDS:
        await event.reply(f"⚠️ Command '{command_to_remove}' not found!")
        return

    # Remove from list
    SAVE_COMMANDS.remove(command_to_remove)

    # Save to file
    save_commands_to_file(SAVE_COMMANDS)

    await event.reply(f"✅ Command removed: **'{command_to_remove}'**\n\nTotal commands: {len(SAVE_COMMANDS)}")

@user_client.on(events.NewMessage(pattern='/commands', outgoing=True))
async def show_commands(event):
    """Show all save commands"""
    if not SAVE_COMMANDS:
        await event.reply("📭 No commands set!\n\nUse /add to add commands.")
        return

    commands_list = '\n'.join([f"  {i+1}. {cmd}" for i, cmd in enumerate(SAVE_COMMANDS)])
    await event.reply(f"📋 **Save Commands ({len(SAVE_COMMANDS)}):**\n\n{commands_list}")

@user_client.on(events.NewMessage(pattern='/reload', outgoing=True))
async def reload_commands(event):
    """Reload commands from file"""
    global SAVE_COMMANDS
    old_commands = SAVE_COMMANDS.copy()
    SAVE_COMMANDS = load_commands()

    await event.reply(
        f"🔄 **Commands reloaded from file!**\n\n"
        f"Old ({len(old_commands)}): {', '.join(old_commands) if old_commands else 'None'}\n\n"
        f"New ({len(SAVE_COMMANDS)}): {', '.join(SAVE_COMMANDS) if SAVE_COMMANDS else 'None'}"
    )

# ============================================
# STATS COMMANDS
# ============================================

@user_client.on(events.NewMessage(pattern='/list', outgoing=True))
async def list_media(event):
    """List recently saved media"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM saved_media ORDER BY saved_at DESC LIMIT 10")
    items = cursor.fetchall()
    conn.close()

    if not items:
        await event.reply("📭 No media saved yet!")
        return

    response = f"📦 **Last {len(items)} saved:**\n\n"
    for item in items:
        response += f"{item[2]} | {item[1]}\n👤 {item[5]}\n📅 {item[7]}\n\n"

    await event.reply(response)

@user_client.on(events.NewMessage(pattern='/count', outgoing=True))
async def count_media(event):
    """Count total saved media"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT media_type, COUNT(*) FROM saved_media GROUP BY media_type")
    stats = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) FROM saved_media")
    total = cursor.fetchone()[0]
    conn.close()

    if total == 0:
        await event.reply("📭 No media saved yet!")
        return

    response = f"📊 **Total: {total}**\n\n"
    for media_type, count in stats:
        response += f"{media_type}: {count}\n"

    await event.reply(response)

@user_client.on(events.NewMessage(pattern='/stats', outgoing=True))
async def stats(event):
    """Show detailed statistics"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM saved_media")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(file_size_mb) FROM saved_media")
    total_size = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(DISTINCT original_sender_id) FROM saved_media")
    unique_senders = cursor.fetchone()[0]

    cursor.execute("SELECT original_sender_name, COUNT(*) as cnt FROM saved_media GROUP BY original_sender_id ORDER BY cnt DESC LIMIT 5")
    top_senders = cursor.fetchall()

    conn.close()

    response = (
        f"📊 **Statistics**\n\n"
        f"📦 Total saved: {total}\n"
        f"💾 Total size: {total_size:.2f} MB\n"
        f"👥 Unique senders: {unique_senders}\n\n"
    )

    if top_senders:
        response += "**Top Senders:**\n"
        for name, count in top_senders:
            response += f"👤 {name}: {count}\n"

    await event.reply(response)

# ============================================
# HELP
# ============================================

@user_client.on(events.NewMessage(pattern='/test', outgoing=True))
async def test(event):
    """Test if bot is running"""
    commands_list = ', '.join(SAVE_COMMANDS) if SAVE_COMMANDS else 'None'
    await event.reply(
        f"✅ Bot is online!\n\n"
        f"Save commands: {commands_list}\n\n"
        f"Use /help for all commands"
    )

@user_client.on(events.NewMessage(pattern='/help', outgoing=True))
async def help_cmd(event):
    """Show help"""
    await event.reply(
        f"📸 **Media Saver Bot**\n\n"
        f"**Save Commands Management:**\n"
        f"/add <word> - Add new save command\n"
        f"/remove <word> - Remove save command\n"
        f"/commands - List all save commands\n"
        f"/reload - Reload from file\n\n"
        f"**Statistics:**\n"
        f"/list - Last 10 saved\n"
        f"/count - Count by type\n"
        f"/stats - Detailed stats\n\n"
        f"**Other:**\n"
        f"/test - Check status\n"
        f"/help - This message\n\n"
        f"**Supported Media:**\n"
        f"📷 Photos | 🎬 Videos | 🎥 Video Messages\n"
        f"🎤 Voice | 🎞 GIFs | 🖼 Stickers\n"
        f"📎 Documents | 📝 Text"
    )

# ============================================
# MAIN
# ============================================

async def main():
    await user_client.connect()

    if not await user_client.is_user_authorized():
        logger.info("Logging in...")
        try:
            await user_client.send_code_request(PHONE_NUMBER)
            code = input("📱 Enter verification code: ")
            try:
                await user_client.sign_in(PHONE_NUMBER, code)
            except SessionPasswordNeededError:
                password = input("🔐 2FA password: ")
                await user_client.sign_in(password=password)
            logger.info("Logged in!")
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return
    else:
        logger.info("Session cached - auto login!")

    me = await user_client.get_me()
    commands_list = ', '.join(SAVE_COMMANDS) if SAVE_COMMANDS else 'None'

    print(f"\n{'='*50}")
    print(f"✅ Logged in as: {me.first_name}")
    print(f"📸 Media Saver is running!")
    print(f"\nSave Commands ({len(SAVE_COMMANDS)}): {commands_list}")
    print(f"\nCommand Management:")
    print(f"  /add <word> - Add command")
    print(f"  /remove <word> - Remove command")
    print(f"  /commands - List commands")
    print(f"\nOther: /list | /count | /stats | /test | /help")
    print(f"{'='*50}\n")

    await user_client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped")
