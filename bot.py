import re
import requests
from telegram import Update, InputMediaPhoto
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Bot Token (Replace with yours)
TOKEN = ""

# Fetch anime details from MyAnimeList API
def fetch_anime_details(title):
    try:
        url = f"https://api.jikan.moe/v4/anime?q={title}&limit=1"
        response = requests.get(url).json()
        
        if response.get('data'):
            anime = response['data'][0]
            return {
                'title': anime['title'],
                'ratings': anime['score'] or "N/A",
                'genres': ", ".join([g['name'] for g in anime['genres']]),
                'episodes': anime['episodes'] or "N/A"
            }
    except:
        return None

# Generate Main Post (with watch link)
def generate_main_post(anime_details, watch_link):
    return f"""
⛩ {anime_details['title']} [{anime_details['season']}]
╭───────────────────
├ ✨ Ratings - {anime_details.get('ratings', 'N/A')} IMDB
├ ❄️ Season - {anime_details['season'].replace('S', '')}
├ ⚡️ Episodes - {anime_details.get('episodes', 'N/A')}
├ 🔈 Audio - Hindi #Official 
├ 📸 Quality - Multi 
├ 🎭 Genres - {anime_details.get('genres', 'Action, Comedy, Slice of Life, Supernatural')}
├───────────────────
├ ⭕️ [Watch & Download]({watch_link}) ⭕️ 
╰──────────────────
New Anime In Official Hindi Dub 🔥
""".strip()

# Generate Powered By Post (fixed @CrunchyRollChannel)
def generate_powered_by_post(anime_details):
    return f"""
⛩ {anime_details['title']} [{anime_details['season']}]
╭───────────────────
├ ✨ Ratings - {anime_details.get('ratings', 'N/A')} IMDB
├ ❄️ Season - {anime_details['season'].replace('S', '')} 
├ ⚡️ Episodes - {anime_details.get('episodes', 'N/A')}
├ 🔈 Audio - Hindi #Official 
├ 📸 Quality - Multi 
├ 🎭 Genres - {anime_details.get('genres', 'Action, Comedy, Slice of Life, Supernatural')}
├───────────────────
• 𝗣𝗼𝘄𝗲𝗿𝗲𝗱 𝗕𝘆: @CrunchyRollChannel
""".strip()

# Handle /anime command
def anime_command(update: Update, context: CallbackContext):
    try:
        args = context.args
        if len(args) < 3:
            raise ValueError("Missing arguments. Usage: /anime <Title> <Season> <WatchLink>")
        
        title = ' '.join(args[:-2])
        season = args[-2]
        watch_link = args[-1]
        
        if not re.match(r'^S\d+$', season, re.IGNORECASE):
            raise ValueError("❌ Season must be in format: S01, S02, etc.")
        
        anime_details = {'title': title, 'season': season.upper()}
        fetched_data = fetch_anime_details(title)
        if fetched_data:
            anime_details.update(fetched_data)
        
        main_post = generate_main_post(anime_details, watch_link)
        powered_post = generate_powered_by_post(anime_details)
        
        if update.message.photo:
            photo = update.message.photo[-1].get_file()
            update.message.reply_photo(
                photo=photo.file_id,
                caption=main_post,
                parse_mode="Markdown"
            )
            update.message.reply_text(
                powered_post,
                parse_mode="Markdown"
            )
        else:
            update.message.reply_text(main_post, parse_mode="Markdown")
            update.message.reply_text(powered_post, parse_mode="Markdown")
            
    except Exception as e:
        update.message.reply_text(f"❌ Error: {str(e)}\n\nUsage:\n/anime <Title> <Season> <WatchLink>\nExample:\n/anime \"Attack on Titan\" S04 https://t.me/AOT_Hindi")

# Start Command
def start(update: Update, context: CallbackContext):
    help_text = """
🎌 *Anime Post Generator Bot* 🎌

📌 *Commands:*
- `/anime <Title> <Season> <WatchLink>` - Create anime post  
  (Example: `/anime "Naruto" S01 https://t.me/AnimeLinks`)  
- `/help` - Show this message  

📌 *Features:*
✔ Auto-fetches ratings & genres  
✔ Supports thumbnails  
✔ Clean, formatted posts  
✔ Powered by @CrunchyRollChannel  
"""
    update.message.reply_text(help_text, parse_mode="Markdown")

# Main Bot Setup
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler("anime", anime_command, pass_args=True))
    
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    print("Bot is running...")
    main()
