import logging
import os
import requests
from tqdm import tqdm
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import Client, filters
from script import *
from config import *

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Function to download a file and show progress
def download_file(url, dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    
    local_filename = os.path.join(dest_folder, url.split('/')[-1])
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 Kibibyte

    with open(local_filename, 'wb') as file, tqdm(
        desc=local_filename,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(block_size):
            bar.update(len(data))
            file.write(data)

    return local_filename

# Function to upload a file to a Telegram chat with progress
async def upload_to_telegram(bot, message, file_path):
    file_type = file_path.split('.')[-1]

    async def progress(current, total):
        await message.edit(f"Uploading: {current * 100 / total:.1f}%")

    with open(file_path, 'rb') as file:
        if file_type in ['mp4', 'avi', 'mkv']:
            await bot.send_video(chat_id=message.chat.id, video=file, progress=progress)
        elif file_type in ['mp3', 'wav']:
            await bot.send_audio(chat_id=message.chat.id, audio=file, progress=progress)
        elif file_type in ['pdf', 'doc', 'docx', 'txt']:
            await bot.send_document(chat_id=message.chat.id, document=file, progress=progress)
        else:
            await bot.send_message(chat_id=message.chat.id, text="Unsupported file type")

@Client.on_callback_query(filters.regex('about'))
async def about(bot, update):
    text = script.ABOUT_TXT
    keybord = InlineKeyboardMarkup([  
                    [InlineKeyboardButton("🔙 Back", callback_data="home")]
                  ])
    await update.message.edit(text=text, reply_markup=keybord)

@Client.on_message(filters.private & filters.command(["donate"]))
async def donatecm(bot, message):
    text = script.DONATE_TXT
    keybord = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🦋 Admin", url="https://t.me/Kirodewal"), 
                    InlineKeyboardButton("✖️ Close", callback_data="cancel")]])
    await message.reply_text(text=text, reply_markup=keybord)

@Client.on_message(filters.private & filters.user(OWNER) & filters.command(["admin"]))
async def admincm(bot, message):
    text = script.ADMIN_TXT
    keybord = InlineKeyboardMarkup([
                    [InlineKeyboardButton("✖️ Close ✖️", callback_data="cancel")]])
    await message.reply_text(text=text, reply_markup=keybord)

@Client.on_callback_query(filters.regex('help'))
async def help(bot, update):
    text = script.HELP_TXT.format(update.from_user.mention)
    keybord = InlineKeyboardMarkup([ 
                    [InlineKeyboardButton('🏞 Thumbnail', callback_data='thumbnail'),
                    InlineKeyboardButton('✏ Caption', callback_data='caption')],
                    [InlineKeyboardButton('🏠 Home', callback_data='home'),
                    InlineKeyboardButton('💵 Donate', callback_data='donate')]
                   ])
    await update.message.edit(text=text, reply_markup=keybord)

@Client.on_callback_query(filters.regex('thumbnail'))
async def thumbnail(bot, update):
    text = script.THUMBNAIL_TXT
    keybord = InlineKeyboardMarkup([  
                    [InlineKeyboardButton("🔙 Back", callback_data="help")]
                  ])
    await update.message.edit(text=text, reply_markup=keybord)

@Client.on_callback_query(filters.regex('caption'))
async def caption(bot, update):
    text = script.CAPTION_TXT
    keybord = InlineKeyboardMarkup([  
                    [InlineKeyboardButton("🔙 Back", callback_data="help")]
                  ])
    await update.message.edit(text=text, reply_markup=keybord)

@Client.on_callback_query(filters.regex('donate'))
async def donate(bot, update):
    text = script.DONATE_TXT
    keybord = InlineKeyboardMarkup([  
                    [InlineKeyboardButton("🔙 Back", callback_data="help")]
                  ])
    await update.message.edit(text=text, reply_markup=keybord)

@Client.on_callback_query(filters.regex('home'))
async def home_callback_handler(bot, query):
    text = f"""Hello {query.from_user.mention} \n\n➻ This Is An Advanced And Yet Powerful Rename Bot.\n\n➻ Using This Bot You Can Rename And Change Thumbnail Of Your Files.\n\n➻ You Can Also Convert Video To File Aɴᴅ File To Video.\n\n➻ This Bot Also Supports Custom Thumbnail And Custom Caption.\n\n<b>Bot Is Made By @HxBots</b>"""
    keybord = InlineKeyboardMarkup([  
                    [InlineKeyboardButton("📢 Updates", url="https://t.me/HxBots"),
                    InlineKeyboardButton("💬 Support", url="https://t.me/HxSupport")],
                    [InlineKeyboardButton("🛠️ Help", callback_data='help'),
                    InlineKeyboardButton("❤️‍🩹 About", callback_data='about')],
                    [InlineKeyboardButton("🧑‍💻 Developer 🧑‍💻", url="https://t.me/Kirodewal")]
                  ])
    await query.message.edit_text(text=text, reply_markup=keybord)

@Client.on_message(filters.private & filters.command("download"))
async def download_command(bot, message):
    url = message.text.split(" ", 1)[1]  # Extract URL from the message
    dest_folder = "./downloads"
    
    # Download the file and upload to Telegram
    downloaded_file = download_file(url, dest_folder)
    await upload_to_telegram(bot, message, downloaded_file)
