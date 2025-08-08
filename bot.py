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
                'genres': ", ".join([g['name'] for g in anime['genres'][:6]]),
                'episodes': str(anime['episodes']) if anime['episodes'] else "N/A"
            }
    except Exception as e:
        print(f"API Error: {e}")
    return None

def generate_main_post(details, watch_link):
    quoted_part = f"""
*╭───────────────────
├ ✨ Ratings - {details.get('ratings', 'N/A')} IMDB
├ ❄️ Season - {details['season'].replace('S', '')}
├ ⚡️ Episodes - {details.get('episodes', 'N/A')}
├ 🔈 Audio - Hindi #Official 
├ 📸 Quality - Multi 
├ 🎭 Genres - {details.get('genres', 'Action, Comedy, Supernatural')}
├───────────────────
├[⭕️ Watch & Download ⭕️]({watch_link})
╰──────────────────*
""".strip()
    
    return f"""
*⛩ {details['title']} [{details['season']}]*
`{quoted_part}`
*New Anime In Official Hindi Dub* 🔥
""".strip()

def generate_powered_by_post(details):
    quoted_part = f"""
*╭───────────────────
├ ✨ Ratings - {details.get('ratings', 'N/A')} IMDB
├ ❄️ Season - {details['season'].replace('S', '')} 
├ ⚡️ Episodes - {details.get('episodes', 'N/A')}
├ 🔈 Audio - Hindi #Official 
├ 📸 Quality - Multi 
├ 🎭 Genres - {details.get('genres', 'Action, Comedy, Supernatural')}
├───────────────────*
""".strip()
    
    return f"""
*⛩ {details['title']} [{details['season']}]*

`{quoted_part}`

*Powered By:
@CrunchyRollChannel*
""".strip()

def anime_command(update: Update, context: CallbackContext):
    try:
        # Check if replying to a thumbnail
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
            'genres': 'Action, Comedy, Supernatural'
        }

        fetched_data = fetch_anime_details(title)
        if fetched_data:
            details.update(fetched_data)

        # Get the thumbnail from replied message
        thumbnail = update.message.reply_to_message.photo[-1].file_id

        # Generate and send posts
        main_post = generate_main_post(details, watch_link)
        powered_post = generate_powered_by_post(details)

        # Send main post with thumbnail
        update.message.reply_photo(
            photo=thumbnail,
            caption=main_post,
            parse_mode="Markdown"
        )
        
        # Send powered by post
        update.message.reply_text(
            powered_post,
            parse_mode="Markdown"
        )

    except Exception as e:
        update.message.reply_text(f"❌ Error: {str(e)}")

def start(update: Update, context: CallbackContext):
    help_text = """
🎌 *Anime Post Generator Bot* 🎌

📌 *How to Use:*
1. Send your thumbnail image
2. *Reply* to that image with:
   `/anime "<Title>" <Season> <WatchLink>`
   
Example:
1. Send a photo
2. Reply to it with:
   `/anime "Attack on Titan" S04 https://t.me/AOT_Hindi`

📌 *Features:*
✔ Thumbnail support (must reply to image)
✔ Clickable watch/download link
✔ Perfect quoted formatting
✔ Auto-fetches ratings/genres
✔ Bold text (except links)
✔ Two-post system (Main + Powered By)
"""
    update.message.reply_text(help_text, parse_mode="Markdown")

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
