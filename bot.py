import re
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes
from telegram.ext import filters  # Lowercase 'filters' in v20+

TOKEN = ""  # Replace with your actual token

async def fetch_anime_details(title):
    try:
        url = f"https://api.jikan.moe/v4/anime?q={title}&limit=1"
        response = requests.get(url).json()
        if response.get('data'):
            anime = response['data'][0]
            return {
                'ratings': str(round(anime['score'], 1)) if anime['score'] else "N/A",
                'genres': ", ".join([g['name'] for g in anime['genres'][:6]]),
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
├<a href="{watch_link}">⭕️ Watch & Download ⭕️</a> 
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
<b>• 𝗣𝗼𝘄𝗲𝗿𝗲𝗱 𝗕𝘆: 
@CrunchyRollChannel</b>
""".strip()

async def anime_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Check if replying to thumbnail
        if not update.message.reply_to_message or not update.message.reply_to_message.photo:
            await update.message.reply_text("❌ Please reply to a thumbnail image with your command!")
            return

        args = context.args
        if len(args) < 3:
            await update.message.reply_text("❌ Usage: Reply to thumbnail with:\n/anime <Title> <Season> <WatchLink>\nExample: /anime \"Demon Slayer\" S02 https://t.me/DemonSlayerHD")
            return

        title = ' '.join(args[:-2])
        season = args[-2].upper()
        watch_link = args[-1]

        if not re.match(r'^S\d+$', season, re.IGNORECASE):
            await update.message.reply_text("❌ Season format must be like S01, S02, etc.")
            return

        details = {
            'title': title,
            'season': season,
            'ratings': 'N/A',
            'episodes': 'N/A',
            'genres': 'Action, Comedy, Supernatural'
        }

        # Fetch details
        fetched_data = await fetch_anime_details(title)
        if fetched_data:
            details.update(fetched_data)

        thumbnail = update.message.reply_to_message.photo[-1].file_id

        # Send both posts
        await update.message.reply_photo(
            photo=thumbnail,
            caption=generate_main_post(details, watch_link),
            parse_mode="HTML"
        )
        await update.message.reply_photo(
            photo=thumbnail,
            caption=generate_powered_by_post(details),
            parse_mode="HTML"
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
<b>🎌 Anime Post Generator Bot �</b>

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
    await update.message.reply_text(help_text, parse_mode="HTML")

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("anime", anime_command))
    
    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
