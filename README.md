# 📸 Save Telegram View Once

A lightweight **Telegram userbot** built with [Telethon](https://github.com/LonamiWebs/Telethon) that lets you save view once messages directly to your **Saved Messages** by replying to them with a custom save command.

Supports photos, videos, round video messages, voice messages, GIFs, stickers, documents, and text messages — with metadata tracking and built-in statistics.

> ⚠️ **This is a userbot.** It operates through your personal Telegram account using Telegram API credentials. Use it responsibly and at your own risk.

---

## ✨ Features

### 📦 Media Support

* 📷 Photos
* 🎬 Videos
* 🎥 Round video messages
* 🎤 Voice messages
* 🎞 GIFs
* 🖼 Stickers / images
* 📎 Documents
* 📝 Text messages
* 💥 View-once media where Telegram/Telethon allows it to be downloaded

### ⚙️ Built-in Features

* ⌨️ **Custom save commands**
* ➕ Add commands directly from Telegram
* ➖ Remove commands directly from Telegram
* 🔄 Reload commands without restarting
* 💾 SQLite database for save history
* 📊 Media statistics
* 👥 Sender tracking
* 📏 File-size tracking
* 🕒 Save timestamps
* 🗑️ Temporary files are deleted after being sent
* 🔐 Telethon session is cached for automatic login
* 🔄 Can run continuously with `systemd`
* 📝 Configurable logging

---

## 🧠 How It Works

The bot watches for **outgoing messages from your own Telegram account**.

For example, if you reply to a photo with:

```text
save
```

the userbot will:

1. Detect the save command.
2. Get the message you're replying to.
3. Download the media temporarily.
4. Collect metadata such as:

   * Media type
   * Original sender
   * Sender ID
   * Chat
   * File size
   * Timestamp
5. Send the file to your **Saved Messages**.
6. Store metadata in SQLite.
7. Delete the temporary file from the server.

### Example

```text
┌─────────────────────────────┐
│       Telegram Chat         │
│                             │
│  👤 Someone                 │
│  📷 [Photo]                 │
│                             │
│  You: save                  │
└──────────────┬──────────────┘
               │
               ▼
        📥 Download
               │
               ▼
        📊 Collect metadata
               │
               ▼
      💾 Send to Saved Messages
               │
               ▼
        🗑️ Delete temp file
```

---

# 📋 Requirements

* 🐍 Python **3.8+**
* 🔑 Telegram API credentials
* 📱 A Telegram account
* 🖥️ Linux server recommended for 24/7 usage
* 💾 Enough temporary disk space for the largest media you want to save

### Telegram API Credentials

Get your `API_ID` and `API_HASH` from:

https://my.telegram.org

You will need to create an application under **API Development Tools**.

---

# 🚀 Installation

## 1. Clone the Repository

```bash
git clone https://github.com/DaniyalAjalloueian/Save-Telegram-View-Once.git
cd Save-Telegram-View-Once
```

## 2. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure Environment Variables

Copy the example configuration:

```bash
cp example.env .env
```

Edit it:

```bash
nano .env
```

Example:

```env
API_ID=12345678
API_HASH=your_api_hash
PHONE_NUMBER=+1234567890

SESSION_NAME=user_session
DB_FILE=images.db
LOG_LEVEL=INFO
COMMANDS_FILE=commands.txt
```

---

# ⌨️ Save Commands

Save commands are stored in `commands.txt`.

Add one command per line:

```text
save
```

Lines beginning with `#` are ignored:

```text
save
keep
grab
# My custom commands
```

Commands are case-insensitive.

For example:

```text
SAVE
Save
sAvE
```

will all be treated as:

```text
save
```

---

# 🎮 Usage

Reply to any supported message with one of your configured save commands.

For example:

```text
save
```

The replied message will be sent to your **Saved Messages**.

You can also use any custom command you've configured:

```text
keep
grab
```

---

# 🤖 Commands

All management commands are sent from your own Telegram account.

| Command          | Description                             |
| ---------------- | --------------------------------------- |
| `/add <word>`    | ➕ Add a new save command                |
| `/remove <word>` | ➖ Remove a save command                 |
| `/commands`      | 📋 Show all save commands               |
| `/reload`        | 🔄 Reload commands from `commands.txt`  |
| `/list`          | 📦 Show the last 10 saved items         |
| `/count`         | 🔢 Count saved items by media type      |
| `/stats`         | 📊 Show detailed statistics             |
| `/test`          | ❤️ Check whether the userbot is running |
| `/help`          | ❓ Show available commands               |

### Add a Command

```text
/add awesome
```

Now replying with:

```text
awesome
```

will trigger the saver.

### Remove a Command

```text
/remove awesome
```

### Show Commands

```text
/commands
```

### Reload Commands

If you manually edit `commands.txt`:

```text
/reload
```

You don't need to restart the userbot.

---

# 📊 Statistics

The userbot keeps a local SQLite database containing metadata about saved items.

Example:

```text
📊 Statistics

📦 Total saved: 152
💾 Total size: 847.32 MB
👥 Unique senders: 38

Top Senders:
👤 John: 21
👤 Alice: 17
👤 Bob: 13
```

The database tracks:

* File name
* Media type
* Original chat ID
* Original sender ID
* Original sender name
* File size
* Save timestamp

### Important

The database stores **metadata**, not the actual media files.

---

# 🔧 Configuration

## `.env`

| Variable        | Required | Default        | Description           |
| --------------- | :------: | -------------- | --------------------- |
| `API_ID`        |     ✅    | —              | Telegram API ID       |
| `API_HASH`      |     ✅    | —              | Telegram API hash     |
| `PHONE_NUMBER`  |     ✅    | —              | Telegram phone number |
| `SESSION_NAME`  |     ❌    | `user_session` | Telethon session name |
| `DB_FILE`       |     ❌    | `images.db`    | SQLite database path  |
| `LOG_LEVEL`     |     ❌    | `INFO`         | Logging level         |
| `COMMANDS_FILE` |     ❌    | `commands.txt` | Save commands file    |

Example:

```env
API_ID=12345678
API_HASH=0123456789abcdef0123456789abcdef
PHONE_NUMBER=+1234567890

SESSION_NAME=user_session
DB_FILE=images.db
LOG_LEVEL=INFO
COMMANDS_FILE=commands.txt
```

---

# 🔐 First Login

Start the application:

```bash
python bot.py
```

On the first run, Telethon will ask for your Telegram verification code:

```text
📱 Enter verification code:
```

If your account has 2FA enabled:

```text
🔐 2FA password:
```

After successful authentication, Telethon creates a session file.

Future launches can use the cached session:

```text
Session cached - auto login!
```

This means you normally won't need to enter the verification code again.

---

# 🖥️ Run 24/7 on Ubuntu

For a server, **systemd is recommended**.

## 1. Create a Service

```bash
sudo nvim /etc/systemd/system/media-saver.service
```

Use:

```ini
[Unit]
Description=Telegram Media Saver
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/path/to/telegram-media-saver
ExecStart=/path/to/telegram-media-saver/venv/bin/python /path/to/telegram-media-saver/bot.py
Restart=always
RestartSec=10
StandardOutput=append:/path/to/telegram-media-saver/bot.log
StandardError=append:/path/to/telegram-media-saver/bot.log

[Install]
WantedBy=multi-user.target
```

Replace:

```text
YOUR_USERNAME
```

and:

```text
/path/to/telegram-media-saver
```

with the actual values.

## 2. Enable the Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable media-saver
sudo systemctl start media-saver
```

Check the status:

```bash
sudo systemctl status media-saver
```

View logs:

```bash
journalctl -u media-saver -f
```

Or:

```bash
tail -f /path/to/telegram-media-saver/bot.log
```

---

# 🖥️ Running with `screen`

For a simpler setup:

```bash
sudo apt install screen -y
```

Start a session:

```bash
screen -S mediabot
```

Run the application:

```bash
source venv/bin/activate
python bot.py
```

Detach:

```text
Ctrl+A
D
```

Reattach later:

```bash
screen -r mediabot
```

---

# 🔒 Security

This project uses your **personal Telegram account session**, so security is important.

### ⚠️ Keep these files private

```text
.env
*.session
*.session-journal
```

Your `.session` file can provide access to your authenticated Telegram session.

**Do not:**

* ❌ Commit your session file to Git
* ❌ Share your `.session` file
* ❌ Share your `API_HASH`
* ❌ Upload your `.env`
* ❌ Run an untrusted version of the code with your Telegram session

### Temporary Files

Media is downloaded temporarily to the server, uploaded to Saved Messages, and then deleted.

The SQLite database stores metadata only.

---

# ⚠️ Telegram Terms & Account Safety

This project uses **Telegram's user API through a personal account**, rather than the official Bot API.

Using automated clients/userbots may be subject to Telegram's Terms of Service and anti-abuse systems.

Use this project responsibly.

**You are responsible for your own account and how you use this software.**

---

# 🛠️ Troubleshooting

## Login fails

Make sure your `.env` contains valid credentials:

```env
API_ID=...
API_HASH=...
PHONE_NUMBER=...
```

Then run:

```bash
python bot.py
```

---

## Commands aren't working

Check:

```bash
cat commands.txt
```

Then reload:

```text
/reload
```

Or restart the application.

Make sure you're replying to the message:

```text
         📷 Photo
            ↑
            │ reply
            │
          save
```

The command must be sent as an **outgoing message from your own account**.

---

## Service isn't starting

Check:

```bash
sudo systemctl status media-saver
```

Then:

```bash
journalctl -u media-saver -n 100 --no-pager
```

---

# 📜 License

This project is licensed under the **MIT License**.

You are free to:

* ✅ Use it
* ✅ Modify it
* ✅ Fork it
* ✅ Redistribute it
* ✅ Use it in your own projects

See the `LICENSE` file for the full license text.

---

# ⭐ Support

If this project is useful to you:

* ⭐ Star the repository
* 🍴 Fork it
* 🐛 Open an issue if you find a bug
* 💡 Submit improvements through pull requests

---

## 📸 Save Anything. Keep Everything.

**Telegram → Reply → Save command → Saved Messages**

Simple, fast, and automatic. 🚀
