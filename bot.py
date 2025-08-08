import re
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = ""

def fetch_anime_details(title):
    try:
        url = f"https://api.jikan.moe/v4/anime?q={title}&limit=1"
        response = requests.get(url).json()
        if response.get('data'):
            anime = response['data'][0]
            return {
                'ratings': str(round(anime['score'], 2)) if anime['score'] else "N/A",
                'genres': ", ".join([g['name'] for g in anime['genres'][:6]]),  # Increased to 6 genres
                'episodes': str(anime['episodes']) if anime['episodes'] else "N/A"
            }
    except Exception as e:
        print(f"API Error: {e}")
    return None

def generate_main_post(details, watch_link):
    return f"""
<b>⛩ {details['title']} [{details['season']}]</b> 
<b>╭───────────────────
├ ✨ Ratings - {details.get('ratings', 'N/A')} IMDB
├ ❄️ Season - {details['season'].replace('S', '')}
├ ⚡️ Episodes - {details.get('episodes', 'N/A')}
├ 🔈 Audio - Hindi #Official 
├ 📸 Quality - Multi 
├ 🎭 Genres - {details.get('genres', 'Action, Comedy, Supernatural')}
├───────────────────
├ ⭕️ <a href="{watch_link}">Watch & Download</a> ⭕️
╰──────────────────</b>
<b>New Anime In Official Hindi Dub 🔥</b>
""".strip()

def generate_powered_by_post(details):
    return f"""
<b>⛩ {details['title']} [{details['season']}]</b>
<b>╭───────────────────
├ ✨ Ratings - {details.get('ratings', 'N/A')} IMDB
├ ❄️ Season - {details['season'].replace('S', '')} 
├ ⚡️ Episodes - {details.get('episodes', 'N/A')}
├ 🔈 Audio - Hindi #Official 
├ 📸 Quality - Multi 
├ 🎭 Genres - {details.get('genres', 'Action, Comedy, Supernatural')}
╰───────────────────</b>
<b>Powered By: 
@CrunchyRollChannel</b>
""".strip()

def anime_command(update: Update, context: CallbackContext):
    try:
        # Check if replying to thumbnail
        if not update.message.reply_to_message or not update.message.reply_to_message.photo:
            update.message.reply_text("❌ Please reply to a thumbnail image with your command!")
            return

        args = context.args
        if len(args) < 3:
            update.message.reply_text("❌ Usage: Reply to thumbnail with:\n/anime <Title> <Season> <WatchLink>\nExample: /anime \"Demon Slayer\" S02 https://t.me/DemonSlayerHD")
            return

        title = ' '.join(args[:-2])
        season = args[-2].upper()
        watch_link = args[-1]

        if not re.match(r'^S\d+$', season, re.IGNORECASE):
            update.message.reply_text("❌ Season format must be like S01, S02, etc.")
            return

        details = {
            'title': title,
            'season': season,
            'ratings': 'N/A',
            'episodes': 'N/A',
            'genres': 'Action, Comedy, Supernatural'  # Default if API fails
        }

        # Fetch details (will update genres up to 6 if available)
        fetched_data = fetch_anime_details(title)
        if fetched_data:
            details.update(fetched_data)

        thumbnail = update.message.reply_to_message.photo[-1].file_id

        # Send both posts with thumbnails
        update.message.reply_photo(
            photo=thumbnail,
            caption=generate_main_post(details, watch_link),
            parse_mode="HTML"
        )
        update.message.reply_photo(
            photo=thumbnail,
            caption=generate_powered_by_post(details),
            parse_mode="HTML"
        )

    except Exception as e:
        update.message.reply_text(f"❌ Error: {str(e)}")

def start(update: Update, context: CallbackContext):
    help_text = """
<b>🎌 Anime Post Generator Bot 🎌</b>

<b>📌 How to Use:</b>
1. Send thumbnail image
2. Reply with:
   <code>/anime "Title" S01 https://t.me/link</code>

<b>📌 Features:</b>
✔ Thumbnail on both posts
✔ Up to 6 genres
✔ Bold HTML formatting
✔ Safe clickable links
✔ Auto-fetched details
✔ Clean box formatting
"""
    update.message.reply_text(help_text, parse_mode="HTML")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler("anime", anime_command, pass_args=True))
    
    print("🤖 Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
