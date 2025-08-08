import re
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = ""  # Replace with your bot token

def fetch_anime_details(title):
    """Fetch ratings, genres and episodes (but keep original title)"""
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
    """Generate the main post with perfect formatting"""
    return f"""
⛩ {details['title']} [{details['season']}]
╭───────────────────
├ ✨ Ratings - {details.get('ratings', 'N/A')} IMDB
├ ❄️ Season - {details['season'].replace('S', '')}
├ ⚡️ Episodes - {details.get('episodes', 'N/A')}
├ 🔈 Audio - Hindi #Official 
├ 📸 Quality - Multi 
├ 🎭 Genres - {details.get('genres', 'Action, Comedy, Supernatural')}
├───────────────────
├[⭕️ Watch & Download ⭕️]({watch_link})
╰──────────────────
New Anime In Official Hindi Dub 🔥
""".strip()

def generate_powered_by_post(details):
    """Generate the 'Powered By' post"""
    return f"""
⛩ {details['title']} [{details['season']}]
╭───────────────────
├ ✨ Ratings - {details.get('ratings', 'N/A')} IMDB
├ ❄️ Season - {details['season'].replace('S', '')} 
├ ⚡️ Episodes - {details.get('episodes', 'N/A')}
├ 🔈 Audio - Hindi #Official 
├ 📸 Quality - Multi 
├ 🎭 Genres - {details.get('genres', 'Action, Comedy, Supernatural')}
├───────────────────
• Powered By:
@CrunchyRollChannel
""".strip()

def anime_command(update: Update, context: CallbackContext):
    try:
        # Command format: /anime <Title> <Season> <WatchLink>
        args = context.args
        if len(args) < 3:
            update.message.reply_text("❌ Usage: /anime <Title> <Season> <WatchLink>\nExample: /anime \"Demon Slayer\" S02 https://t.me/DemonSlayerHD")
            return

        title = ' '.join(args[:-2])  # Keep original title
        season = args[-2].upper()    # Format season as S01, S02 etc.
        watch_link = args[-1]        # Watch/download link

        if not re.match(r'^S\d+$', season, re.IGNORECASE):
            update.message.reply_text("❌ Season must be in format: S01, S02, etc.")
            return

        details = {
            'title': title,
            'season': season,
            'ratings': 'N/A',
            'episodes': 'N/A',
            'genres': 'Action, Comedy, Supernatural'
        }

        # Fetch additional details (except title)
        fetched_data = fetch_anime_details(title)
        if fetched_data:
            details.update(fetched_data)

        # Generate both posts
        main_post = generate_main_post(details, watch_link)
        powered_post = generate_powered_by_post(details)

        # Send with thumbnail if provided
        if update.message.photo:
            photo = update.message.photo[-1].file_id
            update.message.reply_photo(
                photo=photo,
                caption=main_post,
                parse_mode="Markdown"
            )
        else:
            update.message.reply_text(
                main_post,
                parse_mode="Markdown"
            )
        
        # Always send powered by post
        update.message.reply_text(
            powered_post,
            parse_mode="Markdown"
        )

    except Exception as e:
        update.message.reply_text(f"❌ Error: {str(e)}")

def start(update: Update, context: CallbackContext):
    """Help menu"""
    help_text = """
🎌 *Anime Post Generator Bot* 🎌

📌 *Commands:*
- /anime "<Title>" <Season> <WatchLink>  
  Example:  
  `/anime "Attack on Titan" S04 https://t.me/AOT_Hindi`

📌 *Features:*
✔ Uses *your exact title* (no auto-translation)  
✔ Auto-fetches: Ratings • Genres • Episode count  
✔ Perfect formatting with emojis ⭕️🔥👑  
✔ Supports thumbnails (attach image)  
✔ Generates both main post + "Powered By" post  
✔ Error-resistant design  

📌 *Post Formatting:*
- Clean box borders (╭ ─ ╮)  
- Proper Markdown links  
- Consistent spacing  
- "Powered By" positioned correctly  
- Watch link with ⭕️ emojis  
"""
    update.message.reply_text(help_text, parse_mode="Markdown")

def main():
    """Start the bot"""
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
